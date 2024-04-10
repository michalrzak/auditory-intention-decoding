import pathlib
import warnings
from datetime import datetime
from os import PathLike
from random import Random

import numpy as np
import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FlippedFMTagger, FMTagger
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.auditory_tagging.shift_tagger import ShiftSumTagger, BinauralTagger, SpectrumShiftTagger
from auditory_stimulation.auditory_tagging.tag_generators import sine_signal
from auditory_stimulation.configuration import get_configuration_psychopy, get_configuration_yaml
from auditory_stimulation.eeg.file_trigger_sender import FileTriggerSender
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import generate_stimuli
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player
from auditory_stimulation.view.view import ViewInterrupted


def create_directory_if_not_exists(directory: PathLike) -> None:
    directory_path = pathlib.Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    defaults = get_configuration_yaml(pathlib.Path("configuration.yaml"))
    config = get_configuration_psychopy(defaults)

    taggers = [AMTagger(42, sine_signal),
               FlippedFMTagger(40, 0.8),
               NoiseTaggingTagger(44100, 126, 256, np.random.default_rng(config.subject_id)),
               FMTagger(40, 100),
               ShiftSumTagger(40),
               SpectrumShiftTagger(40),
               BinauralTagger(40),
               RawTagger()]

    day_id = f"{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}_subject-{config.subject_id}"
    logging_folder = config.logging_directory_path / day_id

    create_directory_if_not_exists(config.logging_directory_path)
    create_directory_if_not_exists(logging_folder)
    create_directory_if_not_exists(config.trigger_directory_path)

    # stimuli = load_stimuli(pathlib.Path("stimuli.yaml"))
    stimuli = generate_stimuli(n_repetitions=config.repetitions,
                               taggers=taggers,
                               n_stimuli=config.n_stimuli,
                               pause_secs=config.pause_secs,
                               number_stimuli_interval=config.stimuli_numbers_interval,
                               intro_transcription_path=config.intros_transcription_path,
                               voices_folders=config.voices_folders,
                               rng=Random(config.subject_id))
    model = Model(stimuli)

    logger = Logger(logging_folder)
    model.register(logger, 10)

    window = psychopy.visual.Window(fullscr=True)
    experiment_texts = load_experiment_texts(config.experiment_texts_file_path)
    view = PsychopyView(psychopy_player, experiment_texts, window)
    model.register(view, 99)  # set the lowest possible priority as the view is blocking and should get updated last

    trigger_sender = FileTriggerSender(5, config.trigger_directory_path / (day_id + ".csv"))

    with trigger_sender.start() as ts:
        model.register(ts, 1)
        experiment = Experiment(model,
                                view,
                                len(taggers),
                                config.resting_state_secs,
                                config.primer_secs,
                                config.break_secs)
        try:
            experiment.run()
        except ViewInterrupted:
            warnings.warn("Experiment interrupted by user!")
            pass


if __name__ == "__main__":
    main()
