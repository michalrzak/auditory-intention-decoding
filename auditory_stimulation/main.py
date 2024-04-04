import pathlib
import warnings
from datetime import datetime
from os import PathLike
from random import Random

import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FlippedFMTagger, FMTagger
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.auditory_tagging.shift_tagger import ShiftSumTagger, BinauralTagger, SpectrumShiftTagger
from auditory_stimulation.auditory_tagging.tag_generators import sine_signal
from auditory_stimulation.configurator.configuration_loader import get_configuration_psychopy
from auditory_stimulation.eeg.file_trigger_sender import FileTriggerSender
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import generate_created_stimuli
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player
from auditory_stimulation.view.view import ViewInterrupted

TAGGERS = [AMTagger(42, sine_signal),
           FlippedFMTagger(40, 0.8),
           NoiseTaggingTagger(44100, 126, 256),
           FMTagger(40, 100),
           ShiftSumTagger(40),
           SpectrumShiftTagger(40),
           BinauralTagger(40),
           RawTagger()]


def create_directory_if_not_exists(directory: PathLike) -> None:
    directory_path = pathlib.Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    config = get_configuration_psychopy()

    day_id = f"{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}_subject-{config.subject_ID}"
    logging_folder = config.logging_directory_path / day_id

    create_directory_if_not_exists(config.logging_directory_path)
    create_directory_if_not_exists(logging_folder)
    create_directory_if_not_exists(config.trigger_directory_path)

    # stimuli = load_stimuli(pathlib.Path("auditory_stimulation/stimuli.yaml"))
    stimuli = generate_created_stimuli(n_repetitions=config.repetitions,
                                       taggers=TAGGERS,
                                       n_stimuli=3,
                                       pause_secs=0.5,
                                       number_stimuli_interval=(100, 1000),
                                       intro_transcription_path=pathlib.Path(
                                           "stimuli_sounds/intro-transcriptions.yaml"),
                                       voices_folders=[pathlib.Path(f"stimuli_sounds/eric"),
                                                       pathlib.Path(f"stimuli_sounds/natasha")],
                                       rng=Random(config.subject_ID))
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
                                len(TAGGERS),
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
