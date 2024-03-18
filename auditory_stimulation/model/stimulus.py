import numbers
import pathlib
from dataclasses import dataclass
from os import PathLike
from typing import List, Dict, Any, Tuple, Collection, Final, Sequence

import numpy as np
import yaml

from auditory_stimulation.audio import Audio, load_wav_as_audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger


@dataclass(frozen=True)
class Stimulus:
    """Simple data class, used to store all information of a stimulus. Should contain the same information as the
    stimulus YAML file, but this is not explicitly checked."""
    audio: Audio
    prompt: str
    primer: str
    options: Collection[str]
    time_stamps: Collection[Tuple[float, float]]
    target: int

    def __post_init__(self):
        if len(self.options) != len(self.time_stamps):
            raise LookupError("For every option specified, there needs to be a time-stamp specified!")

        for ts in self.time_stamps:
            if ts[0] > ts[1]:
                raise ValueError("The time-stamp needs to be a proper interval, having the lower interval index at "
                                 "pos. 0 and the higher interval index at pos. 1")

        if self.target < 0:
            raise ValueError("The target has to be a non-negative integer.")

        if self.target >= len(self.options):
            raise ValueError("The target is not contained within the options.")

    def __hash__(self) -> int:
        return hash((self.audio, self.prompt, self.primer, str(self.options), str(self.time_stamps), self.target))

    def __repr__(self) -> str:
        return f"Stimulus({repr(self.audio)}, prompt={self.prompt}, primer={self.primer}, options={self.options}, " \
               f"time_stamps={self.time_stamps}, target={self.target})"


class CreatedStimulus:
    """Wraps the stimulus class and adds a modified audio and an optional label, to denote what tagging technique was
    used.

    The used tagger is sort of a bad solution and this should be done a bit differently
    """
    __stimulus: Stimulus
    modified_audio: Final[Audio]
    used_tagger: Final[AAudioTagger]

    def __init__(self, stimulus: Stimulus, modified_audio: Audio, used_tagger: AAudioTagger) -> None:
        """Helps to construct a CreatedStimulus from a Stimulus + a modified audio

        :param stimulus: A stimulus instance, which fields will be copied.
        :param modified_audio: The modified_audio to be added to the class.
        :param used_tagger: Denotes which tagger was used to create the modified audio.
        :return: A new instance of CreatedStimulus with the specified fields in stimulus and the modified_audio
        """
        self.__stimulus = stimulus
        self.modified_audio = modified_audio
        self.used_tagger = used_tagger

    @property
    def audio(self) -> Audio:
        return self.__stimulus.audio

    @property
    def prompt(self) -> str:
        return self.__stimulus.prompt

    @property
    def primer(self) -> str:
        return self.__stimulus.primer

    @property
    def options(self) -> Collection[str]:
        return self.__stimulus.options

    @property
    def time_stamps(self) -> Collection[Tuple[float, float]]:
        return self.__stimulus.time_stamps

    @property
    def target(self) -> int:
        return self.__stimulus.target

    def __hash__(self) -> int:
        return hash((hash(self.__stimulus), self.modified_audio))

    def __repr__(self) -> str:
        return f"CreatedStimulus({repr(self.__stimulus)}, {repr(self.modified_audio)}, {repr(self.used_tagger)})"


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

        stimulus = Stimulus(audio,
                            stimulus_raw["prompt"],
                            stimulus_raw["primer"],
                            stimulus_raw["options"],
                            time_stamps,
                            stimulus_raw["target"])
        stimuli.append(stimulus)

    return stimuli


def __combine_parts(intro: Audio, number_audios: Collection[Audio], break_length: float = 0.5) -> Audio:
    audio_break = np.zeros((int(break_length * intro.sampling_frequency), 2), dtype=np.float32)

    stimulus_array = intro.array
    first = True
    for num in number_audios:
        if not first:
            stimulus_array = np.append(stimulus_array, audio_break, axis=0)

        stimulus_array = np.append(stimulus_array, num.array, axis=0)
        first = False

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
                      pause_secs: float) -> Stimulus:
    """Constructs a stimulus instance by combining the given parameters.

    :param intro_audio: An audio, containing a short introduction to the generated stimulus.
    :param intro_text: The transcription of the given audio
    :param option_audios: A sequence of audios, containing the stimuli options.
    :param option_texts: A sequence of transcriptions of the different options.
    :param target: An index, determining which of the options is the target of the stimulus.
    :param pause_secs: How long, in seconds, the break between two options is.
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

    stimulus = Stimulus(audio=audio,
                        prompt=prompt,
                        primer=primer,
                        options=option_texts,
                        time_stamps=time_stamps,
                        target=target)
    return stimulus
