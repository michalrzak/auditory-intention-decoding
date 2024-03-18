from abc import ABC, abstractmethod
from numbers import Number
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from auditory_stimulation.audio import Audio


def to_sample(time: float, sampling_frequency: int) -> int:
    """Function, which converts the given time to a sample

    :param time: The to be converted time.
    :param sampling_frequency: The sampling frequency based on which the sample is computed.
    :return: The converted sample.
    """
    return int(time * sampling_frequency)


def _duplicate_signal(signal: npt.NDArray[Number]) -> npt.NDArray[Number]:
    """Given a one dimensional signal (N/Nx1) returns the signal duplicated to two dimensions (Nx2).

    :param signal: The to be duplicated signal.
    :return: The duplicated signal.
    """
    if len(signal.shape) > 1 or (len(signal.shape) == 2 and signal.shape[1] == 1):
        raise ValueError("The passed signal needs to be one dimensional!")

    output = np.array([np.copy(signal), np.copy(signal)]).T
    assert output.shape[1] == 2
    assert output.shape[0] == signal.shape[0]

    return output


def _scale_down_signal(signal: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
    """Given a signal in an arbitrary range, if any element is > 1 or < -1, scales the signal so that the highest
    element is equal 1/-1.

    :param signal: An arbitrary signal.
    :return: The scaled down signal
    """
    max_value = np.max(np.abs(signal))
    if max_value <= 1:
        return signal

    return_signal = signal / max_value
    assert np.max(np.abs(return_signal))
    return return_signal


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

            if to_sample(stimulus[1], audio.sampling_frequency) > audio.array.shape[0]:
                raise ValueError(f"The stimuli intervals must be contained within the audio. ")

        self._audio = audio
        self._stimuli_intervals = stimuli_intervals
        self._modified_audio = None

    @abstractmethod
    def create(self) -> Audio:
        """Constructs the modified audio."""
        ...

    def _get_repr(self, class_name: str, **kwargs) -> str:
        args = ""
        for key in kwargs:
            args += f", {key}={kwargs[key]}"

        return f"{class_name}(audio={repr(self._audio)}, stimuli_intervals={self._stimuli_intervals}{args}"


class AAudioTaggerFactory(ABC):
    """Class, used to construct AuditoryStimuli."""

    @abstractmethod
    def create_audio_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        ...
