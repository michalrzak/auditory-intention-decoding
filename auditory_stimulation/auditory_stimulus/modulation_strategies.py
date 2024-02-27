from numbers import Number
from typing import Callable

import numpy.typing as npt
import numpy as np

modulate_signal = Callable[[npt.NDArray[np.float32], npt.NDArray[Number]], npt.NDArray[npt.NDArray[np.float32]]]


def __duplicate_signal(signal: npt.NDArray[Number]) -> npt.NDArray[Number]:
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


def amplitude_modulation(signal: npt.NDArray[np.float32],
                         modulation_code: npt.NDArray[Number]
                         ) -> npt.NDArray[npt.NDArray[np.float32]]:
    """Applies amplitude modulation to signal and modulation code and returns the resulting signal. The modulation code
    has to be of the same length as the signal.

    :param signal: The base signal. Needs to be of the shape Nx2
    :param modulation_code: The modulation code. Needs to be of the shape N
    :return: the resulting, modulated signal
    """

    if len(signal.shape) != 2 or signal.shape[1] != 2:
        raise ValueError("Signal must have dimensions Nx2!")

    if len(modulation_code.shape) != 1:
        raise ValueError("Modulation code must have dimensions Nx1!")

    if signal.shape[0] != modulation_code.shape[0]:
        raise ValueError("Signal and modulation_code must match in their first dimension!")

    duplicate_code = __duplicate_signal(modulation_code)

    output = signal * duplicate_code
    assert output.shape == signal.shape

    return output


def frequency_modulation(signal: npt.NDArray[np.float32],
                         modulation_code: npt.NDArray[Number]
                         ) -> npt.NDArray[npt.NDArray[np.float32]]:
    """

    :param signal:
    :param modulation_code:
    :return:
    """
    ...


# TODO: the last modulation technique
