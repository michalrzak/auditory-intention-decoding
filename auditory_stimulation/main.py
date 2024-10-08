import pathlib
import warnings
from datetime import datetime
from os import PathLike
from random import Random

import psychopy.parallel
import psychopy.visual

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FMTagger
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.auditory_tagging.shift_tagger import BinauralTagger
from auditory_stimulation.auditory_tagging.tag_generators import sine_signal
from auditory_stimulation.configuration import get_configuration_psychopy, get_configuration_yaml
from auditory_stimulation.eeg.bittium_neur_one import BittiumTriggerSender
from auditory_stimulation.eeg.file_trigger_sender import FileTriggerSender
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import generate_example_stimuli, generate_stimuli
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
               FMTagger(40, 100),
               BinauralTagger(40),
               RawTagger(),
               AMTagger(42, sine_signal),
               FMTagger(40, 100),
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
                               intros_indices=config.intro_indices,
                               number_stimuli_interval=config.stimuli_numbers_interval,
                               intro_transcription_path=config.intros_transcription_path,
                               voices_folders=config.voices_folders,
                               rng=Random(config.subject_id))

    stimuli_prefixes = [
        "Each round starts with a primer number. Focus on this number, while you listen to the audio.",
        "The primer number does not change, but the audio changes.",
        "The sentences are usually distorted using various distortion techniques."]
    attention_check_prefixes = [
        "Sometimes the audio is missing the primer number. In that case the audio is invalid and you must hit "
        "'spacebar' after the audio is finished."]
    example_stimuli = generate_example_stimuli(regular_stimuli_primer_prefix=stimuli_prefixes,
                                               attention_check_stimuli_primer_prefix=attention_check_prefixes,
                                               taggers=[RawTagger(), RawTagger(), taggers[0]],
                                               n_stimuli=config.n_stimuli,
                                               pause_secs=config.pause_secs,
                                               intros_indices=config.intro_indices,
                                               number_stimuli_interval=config.stimuli_numbers_interval,
                                               intro_transcription_path=config.intros_transcription_path,
                                               voices_folders=config.voices_folders,
                                               rng=Random(config.subject_id))

    model = Model(stimuli, example_stimuli)

    logger = Logger(logging_folder)
    model.register(logger, 10)

    window = psychopy.visual.Window(fullscr=True, screen=1, color='black')
    experiment_texts = load_experiment_texts(config.experiment_texts_file_path)
    view = PsychopyView(psychopy_player, experiment_texts, window)
    model.register(view, 99)  # set the lowest possible priority as the view is blocking and should get updated last

    trigger_sender = FileTriggerSender(5, config.trigger_directory_path / (day_id + ".csv"))

    parport = psychopy.parallel.ParallelPort(0x378)
    parport_sender = BittiumTriggerSender(5, parport, 0.001)

    with trigger_sender.start() as ts, parport_sender.start() as ps:
        model.register(ts, 1)
        model.register(ps, 1)
        experiment = Experiment(model, view, len(taggers) + 1, config)  # + 1 due to attention check stimulus

        try:
            experiment.run()
        except ViewInterrupted:
            warnings.warn("Experiment interrupted by user!")
            pass


if __name__ == "__main__":
    main()
