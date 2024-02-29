from abc import ABC, abstractmethod
from typing import List, Tuple

from auditory_stimulation.audio import Audio


def to_sample(time: float, sampling_frequency: int) -> int:
    """Function, which converts the given time to a sample

    :param time: The to be converted time.
    :param sampling_frequency: The sampling frequency based on which the sample is computed.
    :return: The converted sample.
    """
    return int(time * sampling_frequency)


class AAudioTagger(ABC):
    _audio: Audio
    _stimuli_intervals: List[Tuple[float, float]]  # in seconds

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
    def create(self) -> Audio:
        """Constructs the modified audio."""
        ...


class AAudioTaggerFactory(ABC):
    """Class, used to construct AuditoryStimuli."""

    @abstractmethod
    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        ...
