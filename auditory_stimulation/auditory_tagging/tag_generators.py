from typing import Callable

import numpy as np
import numpy.typing as npt

Length = int
Frequency = int
SamplingFrequency = int
TagGenerator = Callable[[Length, Frequency, SamplingFrequency], npt.NDArray[np.float32]]


def __common_stimulus_generation_tests(length: int,
                                       frequency: int,
                                       sampling_frequency: int) -> None:
    if length <= 0:
        raise ValueError("Length must be a positive integer!")

    if frequency <= 0:
        raise ValueError("Frequency must be a positive integer!")

    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be a positive integer!")


def sine_signal(length: int,
                frequency: int,
                sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Used to generate the modulating sine signal of the given length.

    :param length: The length in samples of the modulating ASSR signal.
    :param frequency: The frequency of the sine wave.
    :param sampling_frequency: The sampling frequency of the signal.
    :return: The modulating ASSR sine wave.
    """
    __common_stimulus_generation_tests(length, frequency, sampling_frequency)

    signal = np.sin(frequency / sampling_frequency * 2 * np.pi * np.arange(length))
    assert signal.shape[0] == length
    assert len(signal.shape) == 1

    return signal


def clicking_signal(length: int,
                    frequency: int,
                    sampling_frequency: int) -> npt.NDArray[np.float32]:
    """ Used to generate the modulating ASSR signal of the given length.

    :param length: The length in samples of the modulating ASSR signal.
    :param frequency: The frequency of the to be generated signal.
    :param sampling_frequency: The sampling frequency of the signal.
    :return: The modulating ASSR clicking signal.
    """
    __common_stimulus_generation_tests(length, frequency, sampling_frequency)

    # in order to be able to generate the altering signal properly, the 2 x frequency needs to divide the
    #  sampling rate of the original audio signal. if this is not the case, one of the saw-teeth will be longer
    #  than other, which may mess with the frequency
    if sampling_frequency // (frequency * 2) != sampling_frequency / (frequency * 2):
        raise ValueError("The frequency has to be fully divisible by the audio sampling frequency!")

    # set all values to 1 as default
    signal = np.ones(length)

    # set all necessary to -1
    first = sampling_frequency // (frequency * 2)
    step = sampling_frequency // frequency
    for i in range(first, length, step):
        # calculate modified interval end. If the interval end is out of range, set it to the range
        interval_end = i + step // 2
        if i + step // 2 > length:
            interval_end = length

        signal[i:interval_end] = -np.ones(interval_end - i)

    return signal
