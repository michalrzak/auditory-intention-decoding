from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional, Callable

import numpy.typing as npt
import numpy as np

Audio = npt.NDArray[np.float32]


class AAuditoryStimulus(ABC):
    __audio: Audio
    __stimuli_intervals: List[Tuple[float, float]]  # in seconds
    __modified_audio: Optional[Audio]
    __audio_player: Callable[[Audio], None]

    # TODO: specify type
    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]],
                 audio_player: Callable[[Audio], None]) -> None:
        if audio is None:
            raise ValueError("audio cannot be none!")

        if stimuli_intervals is None:
            raise ValueError("stimuli_intervals cannot be none!")

        if len(stimuli_intervals) == 0:
            raise ValueError("Must supply at least one stimulus")

        self.__audio = audio
        self.__stimuli_intervals = stimuli_intervals
        self.__modified_audio = None
        self.__audio_player = audio_player

    @abstractmethod
    def _create_modified_audio(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> Audio:
        ...

    def create(self):
        self.__audio = self._create_modified_audio(self.__audio, self.__stimuli_intervals)

    def present(self):
        if self.__modified_audio is None:
            raise RuntimeError("create() has to be run before the stimulus can be presented!")

        self.__audio_player(self.__modified_audio)
