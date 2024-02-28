import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable

import numpy as np
import numpy.typing as npt


def to_sample(time: float, sampling_frequency: int) -> int:
    """Function, which converts the given time to a sample

    :param time: The to be converted time.
    :param sampling_frequency: The sampling frequency based on which the sample is computed.
    :return: The converted sample.
    """
    return int(time * sampling_frequency)


@dataclass
class Audio:
    audio: npt.NDArray[np.float32]
    sampling_frequency: int

    def __copy__(self) -> "Audio":
        return Audio(np.copy(self.audio), self.sampling_frequency)

    def __eq__(self, other: "Audio") -> bool:
        return np.all(self.audio == other.audio) and self.sampling_frequency == other.sampling_frequency


class AAuditoryStimulus(ABC):
    _audio: Audio
    _stimuli_intervals: List[Tuple[float, float]]  # in seconds
    _modified_audio: Optional[Audio]
    __audio_player: Callable[[Audio], None]

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> None:
        if audio is None:
            raise ValueError("audio cannot be none!")

        if stimuli_intervals is None:
            raise ValueError("stimuli_intervals cannot be none!")

        if len(stimuli_intervals) == 0:
            raise ValueError("Must supply at least one stimulus")

        # check whether all intervals are contained in the audio
        # check whether all left intervals are < right intervals
        for stimulus in stimuli_intervals:
            if stimulus[0] >= stimulus[1]:
                raise ValueError("All intervals must have their beginning < end")

            if to_sample(stimulus[1], audio.sampling_frequency) > audio.audio.shape[0]:
                raise ValueError(f"The stimuli intervals must be contained within the audio. ")

        self._audio = audio
        self._stimuli_intervals = stimuli_intervals
        self._modified_audio = None

    @abstractmethod
    def _create_modified_audio(self) -> Audio:
        ...

    def create(self):
        self._modified_audio = self._create_modified_audio()

    @property
    def modified_audio(self) -> Optional[Audio]:
        if self._modified_audio is None:
            return None

        return copy.copy(self._modified_audio)


class AAuditoryStimulusFactory(ABC):
    @abstractmethod
    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAuditoryStimulus:
        ...
