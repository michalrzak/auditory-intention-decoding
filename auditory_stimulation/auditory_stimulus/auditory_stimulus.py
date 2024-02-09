from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Optional


class AAuditoryStimulus(ABC):
    __audio: Any  # TODO: specify type
    __stimuli_intervals: List[Tuple[float, float]]  # in seconds
    __modified_audio: Optional[Any]  # TODO: specify type

    # TODO: specify type
    def __init__(self, audio: Any, stimuli_intervals: List[Tuple[float, float]]) -> None:
        if audio is None:
            raise ValueError("audio cannot be none!")

        if stimuli_intervals is None:
            raise ValueError("stimuli_intervals cannot be none!")

        if len(stimuli_intervals) == 0:
            raise ValueError("Must supply at least one stimulus")

        self.__audio = audio
        self.__stimuli_intervals = stimuli_intervals
        self.__modified_audio = None

    # TODO: specify type
    @abstractmethod
    def _create_modified_audio(self, audio: Any, stimuli_intervals: List[Tuple[float, float]]) -> Any:
        ...

    def create(self):
        self.__audio = self._create_modified_audio(self.__audio, self.__stimuli_intervals)

    def present(self):
        if self.__modified_audio is None:
            raise RuntimeError("create() has to be run before the stimulus can be presented!")

        raise NotImplementedError()

