import numbers
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import yaml

from auditory_stimulation.auditory_tagging.auditory_tagger import Audio
from auditory_stimulation.auditory_tagging.helper.load_wav_as_numpy_array import load_wav_as_numpy_array


@dataclass
class Stimulus:
    """Simple data class, used to store all information of a stimulus. Should contain the same information as the
    stimulus YAML file, but this is not explicitly checked."""
    audio: Audio
    prompt: str
    primer: str
    options: List[str]
    time_stamps: List[Tuple[float, float]]


@dataclass
class CreatedStimulus(Stimulus):
    """Extends the Stimulus class with the modified audio field. To be used once an auditory stimulation technique
     is applied"""
    modified_audio: Audio

    @staticmethod
    def from_stimulus(stimulus: Stimulus, modified_audio: Audio) -> "CreatedStimulus":
        """Helps to construct a CreatedStimulus from a Stimulus + a modified audio

        :param stimulus: A stimulus instance, which fields will be copied.
        :param modified_audio: The modified_audio to be added to the class.
        :return: A new instance of CreatedStimulus with the specified fields in stimulus and the modified_audio
        """
        return CreatedStimulus(stimulus.audio,
                               stimulus.prompt,
                               stimulus.primer,
                               stimulus.options,
                               stimulus.time_stamps,
                               modified_audio)


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


def load_stimuli(path_to_yaml: str) -> List[Stimulus]:
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

        audio = load_wav_as_numpy_array(stimulus_raw["file"])
        time_stamps = [(time_stamp[0], time_stamp[1]) for time_stamp in stimulus_raw["time-stamps"]]

        stimulus = Stimulus(audio,
                            stimulus_raw["prompt"],
                            stimulus_raw["primer"],
                            stimulus_raw["options"],
                            time_stamps)
        stimuli.append(stimulus)

    return stimuli
