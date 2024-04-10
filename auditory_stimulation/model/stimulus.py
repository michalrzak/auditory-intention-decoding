import numbers
import pathlib
from abc import ABC
from dataclasses import dataclass
from os import PathLike
from random import Random
from typing import List, Dict, Any, Tuple, Collection, Sequence

import numpy as np
import yaml

from auditory_stimulation.audio import Audio, load_wav_as_audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger


@dataclass(frozen=True)
class AStimulus(ABC):
    audio: Audio
    used_tagger: AAudioTagger
    prompt: str
    primer: str
    options: Collection[str]
    time_stamps: Collection[Tuple[float, float]]

    def __post_init__(self) -> None:
        if len(self.options) != len(self.time_stamps):
            raise LookupError("For every option specified, there needs to be a time-stamp specified!")

        for ts in self.time_stamps:
            if ts[0] > ts[1]:
                raise ValueError("The time-stamp needs to be a proper interval, having the lower interval index at "
                                 "pos. 0 and the higher interval index at pos. 1")

            if ts[1] > self.audio.secs:
                raise ValueError(
                    f"The given timestamp: {ts} is not contained within the audio! Audio length: {self.audio.secs}")

        if any(opt not in self.prompt for opt in self.options):
            raise ValueError("Some of the options are not contained within the prompt!")

    def _common_repr(self) -> str:
        return f"{repr(self.audio)}, prompt={self.prompt}, primer={self.primer}, options={self.options}, " \
               f"time_stamps={self.time_stamps}"


@dataclass(frozen=True)
class Stimulus(AStimulus):
    target_index: int

    def __post_init__(self) -> None:
        super().__post_init__()

        if not (0 <= self.target_index < len(self.options)):
            raise ValueError("The target index is not contained within the options.")

    def __repr__(self):
        return f"Stimulus({self._common_repr()}, target_index={self.target_index})"


@dataclass(frozen=True)
class AttentionCheckStimulus(AStimulus):
    def __repr__(self):
        return f"AttentionCheckStimulus({self._common_repr()})"


def __validate_stimulus_raw(stimulus_raw: Dict[str, Any]) -> None:
    needed_fields = ["file", "prompt", "primer", "options", "time-stamps"]
    for field in needed_fields:
        if field not in stimulus_raw:
            raise KeyError(f"The field {field} was not found in the stimulus!")

    if not isinstance(stimulus_raw["file"], str):
        raise TypeError("The field inside file needs to be a string!")
    if not isinstance(stimulus_raw["prompt"], str):
        raise TypeError("The field inside prompt needs to be a string!")
    if not isinstance(stimulus_raw["primer"], str):
        raise TypeError("The field inside primer needs to be a string!")

    for option in stimulus_raw["options"]:
        if not isinstance(option, str):
            raise TypeError("Each field inside options needs to be a string!")

    if len(stimulus_raw["options"]) != len(stimulus_raw["time-stamps"]):
        raise LookupError("For every option specified, a time stamp needs to be specified")

    for time_stamp in stimulus_raw["time-stamps"]:
        if len(time_stamp) != 2:
            raise ValueError("The time-stamp needs to consist of exactly 2 values")

        if not isinstance(time_stamp[0], numbers.Number) or not isinstance(time_stamp[1], numbers.Number):
            raise TypeError("The time-stamp needs to consist of two numbers")

    if not isinstance(stimulus_raw["target"], int):
        raise TypeError("The target needs to be an integer")


def load_stimuli(path_to_yaml: PathLike) -> List[Stimulus]:
    """Function, which loads all stimuli contained in the provided YAML file. For the syntax of the YAML file, please
    refer to the examples.

    :param path_to_yaml: A system path to a valid yaml file containing the stimuli.
    :return: A list of the loaded stimuli, from the provided file.
    """
    raise NotImplementedError("Unfortunately, this function is currently not functional and requires some changes!")

    with open(path_to_yaml, 'r') as file:
        stimuli_raw = yaml.safe_load(file)

    if len(stimuli_raw) == 0:
        return []

    stimuli = []

    for stimulus_index in stimuli_raw:
        stimulus_raw = stimuli_raw[stimulus_index]
        __validate_stimulus_raw(stimulus_raw)

        audio = load_wav_as_audio(pathlib.Path(stimulus_raw["file"]))
        time_stamps = [(time_stamp[0], time_stamp[1]) for time_stamp in stimulus_raw["time-stamps"]]

        stimulus = Stimulus(audio=...,
                            used_tagger=...,
                            prompt=stimulus_raw["prompt"],
                            primer=stimulus_raw["primer"],
                            options=stimulus_raw["options"],
                            time_stamps=time_stamps,
                            target_index=stimulus_raw["target"])
        stimuli.append(stimulus)

    return stimuli


def __combine_parts(intro: Audio,
                    number_audios: Collection[Audio],
                    break_length: float = 0.5) -> Audio:
    audio_break = np.zeros((int(break_length * intro.sampling_frequency), 2), dtype=np.float32)

    stimulus_array = intro.array
    first = True
    for num in number_audios:
        if not first:
            stimulus_array = np.append(stimulus_array, audio_break, axis=0)

        stimulus_array = np.append(stimulus_array, num.array, axis=0)
        first = False

    # add silence at the end of the audio to pad it
    stimulus_array = np.append(stimulus_array, audio_break, axis=0)

    return Audio(stimulus_array, intro.sampling_frequency)


def __extract_time_stamps(intro: Audio,
                          number_audios: Collection[Audio],
                          break_length: float = 0.5) -> Collection[Tuple[float, float]]:
    previous = intro.secs
    time_stamps = []
    for audio in number_audios:
        time_stamps.append((previous, audio.secs + previous))
        previous = time_stamps[-1][1] + break_length

    return time_stamps


def __look_up_intro_text(n_intro: int, input_text_dict: Dict[str, str]) -> str:
    return input_text_dict[f"intro-{n_intro}"]


def __generate_prompt(input_text: str, prompted_numbers: Collection[str]) -> str:
    prompt = input_text
    assert isinstance(prompt, str)

    first = True
    for num in prompted_numbers:
        if not first:
            prompt += ", "
        prompt += num
        first = False

    prompt += "."

    assert isinstance(prompt, str)
    return prompt


def generate_stimulus(intro_audio: Audio,
                      intro_text: str,
                      option_audios: Sequence[Audio],
                      option_texts: Sequence[str],
                      target: int,
                      pause_secs: float,
                      tagger: AAudioTagger) -> Stimulus:
    """Constructs a stimulus instance by combining the given parameters.

    :param intro_audio: An audio, containing a short introduction to the generated stimulus.
    :param intro_text: The transcription of the given audio
    :param option_audios: A sequence of audios, containing the stimuli options.
    :param option_texts: A sequence of transcriptions of the different options.
    :param target: An index, determining which of the options is the target of the stimulus.
    :param pause_secs: How long, in seconds, the break between two options is.
    :param tagger: The tagger used to generate the stimulus.
    :return:
    """

    if len(option_texts) != len(option_audios):
        raise ValueError("The same number of number_audios and number_texts must be provided")

    if pause_secs < 0:
        raise ValueError("Pause secs must be non-negative")

    if target >= len(option_audios):
        raise ValueError("Target must be contained within number_audios/number_texts")

    if target < 0:
        raise ValueError("Target must be a non-negative integer")

    audio = __combine_parts(intro_audio, option_audios, pause_secs)
    time_stamps = __extract_time_stamps(intro_audio, option_audios, pause_secs)
    prompt = __generate_prompt(intro_text, option_texts)
    primer = option_texts[target]  # given the target, creates a primer sentence

    tagged_audio = tagger.create(audio, time_stamps)

    stimulus = Stimulus(audio=tagged_audio,
                        used_tagger=tagger,
                        prompt=prompt,
                        primer=primer,
                        options=option_texts,
                        time_stamps=time_stamps,
                        target_index=target)
    return stimulus


def generate_stimuli(n_repetitions: int,
                     taggers: List[AAudioTagger],
                     n_stimuli: int,
                     pause_secs: float,
                     number_stimuli_interval: Tuple[int, int],
                     intro_transcription_path: PathLike,
                     voices_folders: List[pathlib.Path],
                     rng: Random) -> List[Stimulus]:
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
    :param number_stimuli_interval: Defines from what number interval the stimuli will be drawn.
    :param intro_transcription_path: The path to the intro transcription file.
    :param voices_folders: Paths to all folders of voices available.
    :param rng: The random number generator, used to generate all items in this function.
    :return: A list of the generated stimuli.
    """

    if n_stimuli <= 0:
        raise ValueError("n_stimuli must be a positive integer!")

    with open(intro_transcription_path, 'r') as file:
        input_text_dict_raw = yaml.safe_load(file)
    input_text_dict = {key: input_text_dict_raw[key][0] for key in input_text_dict_raw}

    stimuli: List[Stimulus] = []
    for i in range(n_repetitions):

        # draw what target is used
        target_number = str(rng.randint(number_stimuli_interval[0], number_stimuli_interval[1]))

        taggers_clone = taggers.copy()
        rng.shuffle(taggers_clone)
        for tagger in taggers_clone:
            # randomly draw, which voice is used
            folder = rng.choice(voices_folders)

            # randomly draw which of the intros will be used
            intro = rng.choice(list(input_text_dict.keys()))

            # draw what numbers will be contained within the stimulus (minus the target which is already chosen)
            number_stimuli = []
            first = True
            while first or target_number in number_stimuli:
                first = False
                number_stimuli = [str(rng.randint(number_stimuli_interval[0], number_stimuli_interval[1]))
                                  for _ in range(n_stimuli - 1)]

            # append the target to the number stimuli and get the index of the target
            number_stimuli.append(target_number)
            rng.shuffle(number_stimuli)
            target = number_stimuli.index(target_number)

            # load the necessary audios to construct the stimulus
            try:
                loaded_intro = load_wav_as_audio(folder / f"{intro}.wav")
                loaded_numbers = [load_wav_as_audio(folder / f"{num}.wav") for num in number_stimuli]
                assert all(loaded_intro.sampling_frequency == audio.sampling_frequency for audio in loaded_numbers)

            except FileNotFoundError as e:
                raise FileNotFoundError(str(e) + f"\nAre you sure you downloaded and extracted the stimuli correctly?"
                                                 f" Please check the installation section of the README!")

            # generate stimulus
            stimulus = generate_stimulus(loaded_intro,
                                         input_text_dict[intro],
                                         loaded_numbers,
                                         number_stimuli,
                                         target,
                                         pause_secs,
                                         tagger)
            stimuli.append(stimulus)

    assert len(stimuli) == n_repetitions * len(taggers)
    return stimuli
