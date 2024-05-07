from numbers import Complex
from typing import Callable

import numpy as np
import numpy.typing as npt

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, _duplicate_signal, _scale_down_signal


def _get_shift_multiplier(shift_by: int, length: int, fs: int) -> npt.NDArray[Complex]:
    n = np.arange(length)

    multiplier = np.e ** ((1j * 2 * np.pi * shift_by * n) / fs)
    multiplier_duplicated = _duplicate_signal(multiplier)

    assert multiplier_duplicated.shape[0] == length
    assert multiplier_duplicated.shape[1] == 2

    return multiplier_duplicated


def _shift_signal_legacy(signal: npt.NDArray[np.number], fs: int, shift_by: int) -> npt.NDArray[np.number]:
    """LEGACY FUNCTION. THIS DOES NOT REALLY SHIFT THE FREQUENCY SIGNAL!

    The effect by this function is the following:
     1. Compute the "shift_multiplier" this essentially is a complex signal, which in the frequency spectrum corresponds
      to an impulse at the target shift frequency.
     2. Multiply the shift_multiplier with the to be shifted signal. Since multiplication in the time domain is
      convolution in the frequency domain this basically re-centers the spectrum at the shift_by frequency. NOTE HOWEVER
      THAT THIS ALSO SHIFTS THE NEGATIVE FREQUENCIES!
     3. Take the real valued signal only. This cuts off the negative frequency components and mirrors the positive freq.
      into the negative.
    The resulting effect is quite similar to an AM tagger.
    """
    shift_multiplier = _get_shift_multiplier(shift_by, signal.shape[0], fs)
    audio_array_shifted = np.array(np.real(signal * shift_multiplier), dtype=np.float32)
    return audio_array_shifted


def _shift_signal(signal: npt.NDArray[np.number], fs: int, shift_by: int) -> npt.NDArray[np.number]:
    f_resolution = fs / signal.shape[0]
    n_shift_by = int(shift_by / f_resolution)
    spectrum_mid = signal.shape[0] // 2

    signal_spectrum = np.fft.fftshift(np.fft.fft(signal, axis=0))
    signal_spectrum_positive = signal_spectrum[spectrum_mid:, :]

    signal_spectrum_positive_shifted = np.zeros_like(signal_spectrum_positive)
    signal_spectrum_positive_shifted[n_shift_by:, :] = signal_spectrum_positive[:-n_shift_by, :]
    assert np.all(signal_spectrum_positive_shifted[:n_shift_by, :] == 0)

    signal_spectrum_shifted = np.zeros_like(signal_spectrum)
    signal_spectrum_shifted[spectrum_mid:, :] = signal_spectrum_positive_shifted

    # rescale the signal, as I am cutting away the entire negative frequency part
    signal_spectrum_shifted_scaled = signal_spectrum_shifted * 2

    signal_shifted = np.real(np.fft.ifft(np.fft.fftshift(signal_spectrum_shifted_scaled), axis=0))

    assert signal_shifted.shape == signal.shape
    return signal_shifted


class ShiftSumTagger(AAudioTagger):
    """A tagger, which works by first shifting the provided audio by the specified frequency and then overlaying
    (summing) the original and the shifted audio together. This produces a signal with an apparent frequency of the
    shifted amount.
    """

    __shift_by: int
    __shift_signal: Callable[[npt.NDArray[np.number], int, int], npt.NDArray[np.number]]

    def __init__(self, shift_by: int, legacy_mode: bool = False) -> None:
        """Constructs the ShiftSumTagger object

        :param shift_by: The amount by which original audio will be shifted, before being added to the signal again.
         This can also be interpreted as the tagging frequency.
        :param legacy_mode: whether to run the legacy shift_signal function or the regular. Any new experiment should
         set this to False. The purpose of this is to keep the old, faulty, results reproducible.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by
        self.__shift_signal = _shift_signal if not legacy_mode else _shift_signal_legacy

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        audio_array_shifted = self.__shift_signal(audio_array_chunk, fs, self.__shift_by)
        audio_array_combined = audio_array_shifted + audio_array_chunk
        audio_array_combined_scaled = _scale_down_signal(audio_array_combined)

        return audio_array_combined_scaled

    def __repr__(self) -> str:
        return self._get_repr("ShiftSumTagger", shift_by=str(self.__shift_by))


class SpectrumShiftTagger(AAudioTagger):
    """A tagger, which works  by simply shifting the audio by the desired frequency. This does not add anything to the
    signal, but simply shifts the spectrum of the desired parts by the desired value."""

    def __init__(self, shift_by: int, legacy_mode: bool = False) -> None:
        """Constructs the SpectrumShiftTagger object

        :param shift_by: The amount by which original audio will be shifted.
        :param legacy_mode: whether to run the legacy shift_signal function or the regular. Any new experiment should
         set this to False. The purpose of this is to keep the old, faulty, results reproducible.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by
        self.__shift_signal = _shift_signal if not legacy_mode else _shift_signal_legacy

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        audio_array_shifted = self.__shift_signal(audio_array_chunk, fs, self.__shift_by)
        audio_array_shifted_scaled = _scale_down_signal(audio_array_shifted)

        return audio_array_shifted_scaled

    def __repr__(self) -> str:
        return self._get_repr("SpectrumShiftTagger", shift_by=str(self.__shift_by))


class BinauralTagger(AAudioTagger):
    """A tagger, which works  by combining both the original audio and the shifted audio at the same time. For this, it
    creates an Audio object, which contains the original audio in channel 0 and the shifted audio in channel 1.

    This tagger only utilizes audio channel 0 (the resulting audio is audio channel 0 of the original in output
    channel 0 and modified audio channel 0 of the modified one in output channel 1).
    """

    def __init__(self, shift_by: int, legacy_mode: bool = False) -> None:
        """Constructs the SpectrumShiftTagger object

        :param shift_by: The amount by which original audio will be shifted.
        :param legacy_mode: whether to run the legacy shift_signal function or the regular. Any new experiment should
         set this to False. The purpose of this is to keep the old, faulty, results reproducible.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by
        self.__shift_signal = _shift_signal if not legacy_mode else _shift_signal_legacy

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        audio_array_shifted = self.__shift_signal(audio_array_chunk, fs, self.__shift_by)

        audio_combined = audio_array_shifted
        audio_combined[:, 1] = audio_array_chunk[:, 1]

        return _scale_down_signal(audio_combined)

    def __repr__(self) -> str:
        return self._get_repr("BinauralTagger", shift_by=str(self.__shift_by))
