import pathlib
import random
from typing import List, Optional

import psychopy.visual
import yaml

from auditory_stimulation.audio import load_wav_as_audio
from auditory_stimulation.auditory_tagging.assr_tagger import AMTaggerFactory, FlippedFMTaggerFactory, FMTaggerFactory
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTaggerFactory
from auditory_stimulation.auditory_tagging.raw_tagger import RawTaggerFactory
from auditory_stimulation.auditory_tagging.shift_tagger import ShiftSumTaggerFactory
from auditory_stimulation.auditory_tagging.tag_generators import sine_signal
from auditory_stimulation.experiment import Experiment
from auditory_stimulation.model.experiment_state import load_experiment_texts
from auditory_stimulation.model.logging import Logger
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import Stimulus, generate_stimulus
from auditory_stimulation.view.psychopy_view import PsychopyView
from auditory_stimulation.view.sound_players import psychopy_player

LOGGING_DIRECTORY = pathlib.Path("logs/")


def generate_stimuli(n: int, n_number_stimuli: int = 3, pause_secs: float = 0.5,
                     seed: Optional[int] = None) -> List[Stimulus]:
    """Generates n stimuli, consisting of n_number_stimuli options.

    :param n: The amount of stimuli to be generated
    :param n_number_stimuli: The amount of options generated in each stimulus.
    :param pause_secs: Define how long the pause is between two adjacent numbers.
    :param seed: The seed for the random number generation.
    :return: A list of the generated stimuli.
    """

    if n <= 0:
        raise ValueError("n must be a positive integer!")

    if n_number_stimuli <= 0:
        raise ValueError("n_number_stimuli must be a positive integer!")

    if seed is not None:
        random.seed(seed)

    with open("stimuli_sounds/intro-transcriptions.yaml", 'r') as file:
        input_text_dict_raw = yaml.safe_load(file)
    input_text_dict = {key: input_text_dict_raw[key][0] for key in input_text_dict_raw}

    stimuli: List[Stimulus] = []
    for i in range(n):

        # randomly draw, whether eric, or natasha voice is used
        is_eric = bool(random.randint(0, 1))
        folder = "eric" if is_eric else "natasha"

        # randomly draw which of the intros will be used
        intro = random.choice(list(input_text_dict.keys()))

        # randomly draw what numbers will be contained within the stimulus
        number_stimuli = [str(random.randint(100, 1000)) for _ in range(n_number_stimuli)]

        # load the necessary audios to construct the stimulus
        try:
            loaded_intro = load_wav_as_audio(pathlib.Path(f"stimuli_sounds/{folder}/{intro}.wav"))
            loaded_numbers = [load_wav_as_audio(pathlib.Path(f"stimuli_sounds/{folder}/{num}.wav"))
                              for num in number_stimuli]
            assert all(loaded_intro.sampling_frequency == audio.sampling_frequency for audio in loaded_numbers)

        except FileNotFoundError as e:
            raise FileNotFoundError(str(e) + f"\nAre you sure you downloaded and extracted the stimuli correctly?"
                                             f" Please check the installation section of the README!")

        # randomly draw which of the numbers is the target
        target = random.randint(0, n_number_stimuli - 1)

        # generate stimulus
        stimulus = generate_stimulus(loaded_intro,
                                     input_text_dict[intro],
                                     loaded_numbers,
                                     number_stimuli,
                                     target,
                                     pause_secs)
        stimuli.append(stimulus)

    assert len(stimuli) == n
    return stimuli


def main() -> None:
    # stimuli = load_stimuli(pathlib.Path("auditory_stimulation/stimuli.yaml"))
    stimuli = generate_stimuli(12, 3, seed=100)
    model = Model(stimuli, [AMTaggerFactory(42, sine_signal),
                            FlippedFMTaggerFactory(40),
                            NoiseTaggingTaggerFactory(126, 256),
                            FMTaggerFactory(40, 100),
                            ShiftSumTaggerFactory(40),
                            RawTaggerFactory()])

    logger = Logger(LOGGING_DIRECTORY)
    model.register(logger)

    experiment_texts = load_experiment_texts(pathlib.Path("auditory_stimulation/experiment_texts.yaml"))
    window = psychopy.visual.Window(fullscr=True)
    view = PsychopyView(psychopy_player, experiment_texts, window)

    model.register(view, 99)  # set the lowest possible priority as the view is blocking and should get updated last

    experiment = Experiment(model, view)
    experiment.run()


if __name__ == "__main__":
    main()
