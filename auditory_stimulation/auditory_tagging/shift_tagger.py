from numbers import Complex

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


class ShiftSumTagger(AAudioTagger):
    """A tagger, which works by first shifting the provided audio by the specified frequency and then overlaying
    (summing) the original and the shifted audio together. This produces a signal with an apparent frequency of the
    shifted amount.
    """

    __shift_by: int

    def __init__(self, shift_by: int) -> None:
        """Constructs the ShiftSumTagger object

        :param shift_by: The amount by which original audio will be shifted, before being added to the signal again.
         This can also be interpreted as the tagging frequency.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        shift_multiplier = _get_shift_multiplier(self.__shift_by, audio_array_chunk.shape[0], fs)

        audio_array_shifted = np.array(np.abs(audio_array_chunk * shift_multiplier), dtype=np.float32)
        audio_array_combined = audio_array_shifted + audio_array_chunk
        audio_array_combined_scaled = _scale_down_signal(audio_array_combined)

        return audio_array_combined_scaled

    def __repr__(self) -> str:
        return self._get_repr("ShiftSumTagger", shift_by=str(self.__shift_by))


class SpectrumShiftTagger(AAudioTagger):
    """A tagger, which works  by simply shifting the audio by the desired frequency. This does not add anything to the
    signal, but simply shifts the spectrum of the desired parts by the desired value."""

    def __init__(self, shift_by: int) -> None:
        """Constructs the SpectrumShiftTagger object

        :param shift_by: The amount by which original audio will be shifted.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        shift_multiplier = _get_shift_multiplier(self.__shift_by, audio_array_chunk.shape[0], fs)

        audio_array_shifted = np.array(np.abs(audio_array_chunk * shift_multiplier), dtype=np.float32)
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

    def __init__(self, shift_by: int) -> None:
        """Constructs the SpectrumShiftTagger object

        :param shift_by: The amount by which original audio will be shifted.
        """
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by

    def _modify_chunk(self, audio_array_chunk: npt.NDArray[np.float32], fs: int) -> npt.NDArray[np.float32]:
        shift_multiplier = _get_shift_multiplier(self.__shift_by, audio_array_chunk.shape[0], fs)

        audio_array_shifted = np.array(np.abs(audio_array_chunk * shift_multiplier), dtype=np.float32)
        audio_array_shifted_scaled = _scale_down_signal(audio_array_shifted)

        audio_combined = audio_array_shifted_scaled
        audio_combined[:, 0] = audio_array_chunk[:, 0]

        return audio_combined

    def __repr__(self) -> str:
        return self._get_repr("BinauralTagger", shift_by=str(self.__shift_by))
