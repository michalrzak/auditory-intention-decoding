from typing import Callable, Tuple

import numpy as np
import numpy.typing as npt


def __common_stimulus_generation_tests(length: int,
                                       frequency: int,
                                       sampling_frequency: int,
                                       signal_interval: Tuple[float, float]) -> None:
    if length <= 0:
        raise ValueError("Length must be a positive integer!")

    if frequency <= 0:
        raise ValueError("Frequency must be a positive integer!")

    if sampling_frequency <= 0:
        raise ValueError("Sampling frequency must be a positive integer!")

    if signal_interval[0] > signal_interval[1]:
        raise ValueError("The first value of the signal interval needs to be the lower boundary, while the second value"
                         " is the upper boundary, which does not seem to be the case!")

    if signal_interval[0] == signal_interval[1]:
        raise ValueError("The interval cannot have length 0!")


def __shape_signal(signal: npt.NDArray[np.float32], signal_interval: Tuple[float, float]) -> npt.NDArray[np.float32]:
    """Expects a signal in the range -1 to 1"""
    # the following is just an assert statement as checking it could potentially take a very long time
    assert all(-1 <= signal) and all(signal <= 1)

    shaped_signal = abs(signal_interval[1] - signal_interval[0]) * (signal + 1) - signal_interval[0]
    assert shaped_signal.shape[0] == signal.shape[0]
    assert len(shaped_signal.shape) == 1

    return shaped_signal


tag_generator = Callable[[int, int, int, Tuple[float, float]], npt.NDArray[np.float32]]


def sine_signal(length: int,
                frequency: int,
                sampling_frequency: int,
                signal_interval: Tuple[float, float] = (-1, 1)) -> npt.NDArray[np.float32]:
    """Used to generate the modulating sine signal of the given length.

    :param length: The length in samples of the modulating ASSR signal.
    :param frequency: The frequency of the sine wave.
    :param sampling_frequency: The sampling frequency of the signal.
    :param signal_interval: Default = (-1, 1). The interval of the generated signal. The first value specifies the lower
     boundary, the second value of the upper boundary.
    :return: The modulating ASSR sine wave.
    """
    __common_stimulus_generation_tests(length, frequency, sampling_frequency)

    signal = np.sin(frequency / sampling_frequency * 2 * np.pi * np.arange(length))
    assert signal.shape[0] == length
    assert len(signal.shape) == 1

    return __shape_signal(signal, signal_interval)


def clicking_signal(length: int,
                    frequency: int,
                    sampling_frequency: int,
                    signal_interval: Tuple[float, float] = (1, -1)) -> npt.NDArray[np.float32]:
    """ Used to generate the modulating ASSR signal of the given length.

    :param length: The length in samples of the modulating ASSR signal.
    :param frequency: The frequency of the to be generated signal.
    :param sampling_frequency: The sampling frequency of the signal.
    :param signal_interval: Default = (-1, 1). The interval of the generated signal. The first value specifies the lower
     boundary, the second value of the upper boundary.

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

    return __shape_signal(signal, signal_interval)
