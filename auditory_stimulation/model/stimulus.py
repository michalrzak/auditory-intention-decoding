import numbers
import pathlib
from dataclasses import dataclass
from os import PathLike
from typing import List, Dict, Any, Tuple, Collection, Optional, Final

import yaml

from auditory_stimulation.audio import Audio, load_wav_as_numpy_array


@dataclass(frozen=True)
class Stimulus:
    """Simple data class, used to store all information of a stimulus. Should contain the same information as the
    stimulus YAML file, but this is not explicitly checked."""
    audio: Audio
    prompt: str
    primer: str
    options: Collection[str]
    time_stamps: Collection[Tuple[float, float]]

    def __post_init__(self):
        if len(self.options) != len(self.time_stamps):
            raise LookupError("For every option specified, there needs to be a time-stamp specified!")

        for ts in self.time_stamps:
            if ts[0] > ts[1]:
                raise ValueError("The time-stamp needs to be a proper interval, having the lower interval index at "
                                 "pos. 0 and the higher interval index at pos. 1")

    def __hash__(self):
        return hash((self.audio, self.prompt, self.primer, str(self.options), str(self.time_stamps)))


class CreatedStimulus:
    """Wraps the stimulus class and adds a modified audio and an optional label, to denote what tagging technique was
    used.

    The used tagger is sort of a bad solution and this should be done a bit differently
    """
    __stimulus: Stimulus
    modified_audio: Final[Audio]
    used_tagger_label: Final[Optional[str]]

    def __init__(self, stimulus: Stimulus, modified_audio: Audio,
                 used_tagger_label: Optional[str] = None) -> None:
        """Helps to construct a CreatedStimulus from a Stimulus + a modified audio

        :param stimulus: A stimulus instance, which fields will be copied.
        :param modified_audio: The modified_audio to be added to the class.
        :param used_tagger_label: An optional parameter, which can be used to add a label denoting which tagger was used
         to create an audio.
        :return: A new instance of CreatedStimulus with the specified fields in stimulus and the modified_audio
        """
        self.__stimulus = stimulus
        self.modified_audio = modified_audio
        self.used_tagger_label = used_tagger_label

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

    def __hash__(self):
        return hash((hash(self.__stimulus), self.modified_audio))


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


def load_stimuli(path_to_yaml: PathLike) -> List[Stimulus]:
    """Function, which loads all stimuli contained in the provided YAML file. For the syntax of the YAML file, please
    refer to the examples.
    TODO: Probably need to make the syntax explicit somewhere

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

        audio = load_wav_as_numpy_array(pathlib.Path(stimulus_raw["file"]))
        time_stamps = [(time_stamp[0], time_stamp[1]) for time_stamp in stimulus_raw["time-stamps"]]

        stimulus = Stimulus(audio,
                            stimulus_raw["prompt"],
                            stimulus_raw["primer"],
                            stimulus_raw["options"],
                            time_stamps)
        stimuli.append(stimulus)

    return stimuli
