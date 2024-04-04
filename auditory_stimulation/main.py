import pathlib
import random
import warnings
from datetime import datetime
from os import PathLike
from typing import List, Optional

import psychopy.visual
import yaml

from auditory_stimulation.audio import load_wav_as_audio
from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FlippedFMTagger, FMTagger
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from auditory_stimulation.auditory_tagging.raw_tagger import RawTagger
from auditory_stimulation.auditory_tagging.shift_tagger import ShiftSumTagger, BinauralTagger, SpectrumShiftTagger
from auditory_stimulation.auditory_tagging.tag_generators import sine_signal
from auditory_stimulation.eeg.file_trigger_sender import FileTriggerSender
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import generate_stimulus, CreatedStimulus
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player
from auditory_stimulation.view.view import ViewInterrupted

LOGGING_DIRECTORY = pathlib.Path("logs/")
TRIGGER_DIRECTORY = pathlib.Path("triggers/")

EXPERIMENT_TEXTS = pathlib.Path("auditory_stimulation/experiment_texts.yaml")

PARPORT_TRIGGER_DURATION_SECS = 0.001

N_REPETITIONS = 2
RESTING_STATE_SECS = 5
PRIMER_SECS = 5
BREAK_SECS = 5

TAGGERS = [AMTagger(42, sine_signal),
           FlippedFMTagger(40, 0.8),
           NoiseTaggingTagger(44100, 126, 256),
           FMTagger(40, 100),
           ShiftSumTagger(40),
           SpectrumShiftTagger(40),
           BinauralTagger(40),
           RawTagger()]


def generate_stimuli(n_repetitions: int,
                     taggers: List[AAudioTagger],
                     n_stimuli: int = 3,
                     pause_secs: float = 0.5,
                     seed: Optional[int] = None) -> List[CreatedStimulus]:
    """Generates $len(taggers) * n_repetitions$ stimuli. The stimuli are generated in the following way:
     1. Repeat n_repetition times:
        2. A target number is generated.
        3. For each tagger:
            4. Generate which voice is used
            5. Generate which intro is used
            6. Generate which numbers are added (count: n_stimuli - 1)
            7. Shuffle everything
            8. Construct a stimulus with the given parameters

    :param n_repetitions: How often each block will be repeated
    :param taggers: The used taggers.
    :param n_stimuli: The amount of options generated in each stimulus.
    :param pause_secs: Define how long the pause is between two adjacent numbers.
    :param seed: The seed for the random number generation.
    :return: A list of the generated stimuli.
    """

    if n_stimuli <= 0:
        raise ValueError("n_stimuli must be a positive integer!")

    if seed is not None:
        random.seed(seed)

    with open("stimuli_sounds/intro-transcriptions.yaml", 'r') as file:
        input_text_dict_raw = yaml.safe_load(file)
    input_text_dict = {key: input_text_dict_raw[key][0] for key in input_text_dict_raw}

    stimuli: List[CreatedStimulus] = []
    for i in range(n_repetitions):

        # draw what target is used
        target_number = str(random.randint(100, 1000))

        taggers_clone = taggers.copy()
        random.shuffle(taggers_clone)
        for tagger in taggers_clone:
            # randomly draw, whether eric, or natasha voice is used
            is_eric = bool(random.randint(0, 1))
            folder = "eric" if is_eric else "natasha"

            # randomly draw which of the intros will be used
            intro = random.choice(list(input_text_dict.keys()))

            # draw what numbers will be contained within the stimulus (minus the target which is already chosen)
            number_stimuli = []
            first = True
            while first or target_number in number_stimuli:
                first = False
                number_stimuli = [str(random.randint(100, 1000)) for _ in range(n_stimuli - 1)]

            # append the target to the number stimuli and get the index of the target
            number_stimuli.append(target_number)
            random.shuffle(number_stimuli)
            target = number_stimuli.index(target_number)

            # load the necessary audios to construct the stimulus
            try:
                loaded_intro = load_wav_as_audio(pathlib.Path(f"stimuli_sounds/{folder}/{intro}.wav"))
                loaded_numbers = [load_wav_as_audio(pathlib.Path(f"stimuli_sounds/{folder}/{num}.wav"))
                                  for num in number_stimuli]
                assert all(loaded_intro.sampling_frequency == audio.sampling_frequency for audio in loaded_numbers)

            except FileNotFoundError as e:
                raise FileNotFoundError(str(e) + f"\nAre you sure you downloaded and extracted the stimuli correctly?"
                                                 f" Please check the installation section of the README!")

            # generate stimulus
            raw_stimulus = generate_stimulus(loaded_intro,
                                             input_text_dict[intro],
                                             loaded_numbers,
                                             number_stimuli,
                                             target,
                                             pause_secs)
            modified_audio = tagger.create(raw_stimulus.audio, raw_stimulus.time_stamps)
            stimulus = CreatedStimulus(raw_stimulus, modified_audio, tagger)
            stimuli.append(stimulus)

    assert len(stimuli) == n_repetitions * len(taggers)
    return stimuli


def create_directory_if_not_exists(directory: PathLike) -> None:
    directory_path = pathlib.Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    str_day = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    logging_folder = LOGGING_DIRECTORY / str_day

    create_directory_if_not_exists(LOGGING_DIRECTORY)
    create_directory_if_not_exists(logging_folder)
    create_directory_if_not_exists(TRIGGER_DIRECTORY)

    # stimuli = load_stimuli(pathlib.Path("auditory_stimulation/stimuli.yaml"))
    stimuli = generate_stimuli(N_REPETITIONS, TAGGERS, 3, seed=100)
    model = Model(stimuli)

    logger = Logger(logging_folder)
    model.register(logger, 10)

    window = psychopy.visual.Window(fullscr=True)
    experiment_texts = load_experiment_texts(EXPERIMENT_TEXTS)
    view = PsychopyView(psychopy_player, experiment_texts, window)
    model.register(view, 99)  # set the lowest possible priority as the view is blocking and should get updated last

    trigger_sender = FileTriggerSender(5, TRIGGER_DIRECTORY / (str_day + ".csv"))

    with trigger_sender.start() as ts:
        model.register(ts, 1)
        experiment = Experiment(model,
                                view,
                                len(TAGGERS),
                                RESTING_STATE_SECS,
                                PRIMER_SECS,
                                BREAK_SECS)
        try:
            experiment.run()
        except ViewInterrupted:
            warnings.warn("Experiment interrupted by user!")
            pass


if __name__ == "__main__":
    main()
