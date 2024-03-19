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

    @abstractmethod
    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        """Modifies the given chunk of audio, with the paradigm of the tagger.

        :param audio_array_chunk: The to be modified chunk of audio.
        :param fs: The sampling frequency of the audio.
        :return: The resulting, modified chunk.
        """
        ...

    def create(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> Audio:
        """Constructs the modified audio.

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        """

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

        audio_copy = np.copy(audio.array)

        for interval in stimuli_intervals:
            sample_range = (int(interval[0] * audio.sampling_frequency),
                            int(interval[1] * audio.sampling_frequency))

            audio_array_chunk = audio_copy[sample_range[0]:sample_range[1]]

            audio_copy[sample_range[0]:sample_range[1]] = self._modify_chunk(audio_array_chunk,
                                                                             audio.sampling_frequency)

        assert audio_copy.shape == audio.array.shape
        return Audio(audio_copy, audio.sampling_frequency)

    @staticmethod
    def _get_repr(class_name: str, **kwargs) -> str:
        args = ""
        for key in kwargs:
            if len(args) != 0:
                args += ", "
            args += f"{key}={kwargs[key]}"

        return f"{class_name}({args})"
