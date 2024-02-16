import copy
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass

import numpy.typing as npt
import numpy as np


@dataclass
class Audio:
    audio: npt.NDArray[np.float32]
    sampling_frequency: int

    def __copy__(self) -> "Audio":
        return Audio(np.copy(self.audio), self.sampling_frequency)


class AAuditoryStimulus(ABC):
    _audio: Audio
    _stimuli_intervals: List[Tuple[float, float]]  # in seconds
    _modified_audio: Optional[Audio]
    __audio_player: Callable[[Audio], None]

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]],
                 audio_player: Callable[[Audio], None]) -> None:
        if audio is None:
            raise ValueError("audio cannot be none!")

        if stimuli_intervals is None:
            raise ValueError("stimuli_intervals cannot be none!")

        if len(stimuli_intervals) == 0:
            raise ValueError("Must supply at least one stimulus")

        self._audio = audio
        self._stimuli_intervals = stimuli_intervals
        self._modified_audio = None
        self.__audio_player = audio_player

    @abstractmethod
    def _create_modified_audio(self) -> Audio:
        ...

    def create(self):
        self._modified_audio = self._create_modified_audio()

    def present(self):
        if self._modified_audio is None:
            raise RuntimeError("create() has to be run before the stimulus can be presented!")

        self.__audio_player(self._modified_audio)

    @property
    def modified_audio(self) -> Optional[Audio]:
        if self._modified_audio is None:
            return None

        return copy.copy(self._modified_audio)
