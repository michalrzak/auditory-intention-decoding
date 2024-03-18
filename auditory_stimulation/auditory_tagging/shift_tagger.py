from numbers import Complex
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, _duplicate_signal, _scale_down_signal, \
    AAudioTaggerFactory


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

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]], shift_by: int) -> None:
        """Constructs the ShiftSumTagger object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param shift_by: The amount by which original audio will be shifted, before being added to the signal again.
         This can also be interpreted as the tagging frequency.
        """
        super().__init__(audio, stimuli_intervals)
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by

    def create(self) -> Audio:

        audio_copy = np.copy(self._audio.array)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            audio_chunk = audio_copy[sample_range[0]:sample_range[1]]

            shift_multiplier = _get_shift_multiplier(self.__shift_by, audio_chunk.shape[0],
                                                     self._audio.sampling_frequency)

            audio_array_shifted = np.array(np.real(audio_chunk * shift_multiplier), dtype=np.float32)
            audio_array_combined = audio_array_shifted + audio_chunk
            audio_array_combined_scaled = _scale_down_signal(audio_array_combined)

            audio_copy[sample_range[0]:sample_range[1]] = audio_array_combined_scaled

        audio_combined = Audio(audio_copy, self._audio.sampling_frequency)

        return audio_combined

    def __repr__(self) -> str:
        return self._get_repr("ShiftSumTagger", shift_by=str(self.__shift_by))


class SpectrumShiftTagger(AAudioTagger):
    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]], shift_by: int) -> None:
        """Constructs the SpectrumShiftTagger object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param shift_by: The amount by which original audio will be shifted, before being added to the signal again.
         This can also be interpreted as the tagging frequency.
        """
        super().__init__(audio, stimuli_intervals)
        if shift_by < 0:
            raise ValueError("Shift by has to be a non-negative integer")

        self.__shift_by = shift_by

    def create(self) -> Audio:
        audio_copy = np.copy(self._audio.array)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            audio_chunk = audio_copy[sample_range[0]:sample_range[1]]

            shift_multiplier = _get_shift_multiplier(self.__shift_by, audio_chunk.shape[0],
                                                     self._audio.sampling_frequency)

            audio_array_shifted = np.array(np.real(audio_chunk * shift_multiplier), dtype=np.float32)
            audio_array_shifted_scaled = _scale_down_signal(audio_array_shifted)

            audio_copy[sample_range[0]:sample_range[1]] = audio_array_shifted_scaled

        audio_combined = Audio(audio_copy, self._audio.sampling_frequency)

        return audio_combined


class ShiftSumTaggerFactory(AAudioTaggerFactory):
    __shift_by: int

    def __init__(self, shift_by: int):
        self.__shift_by = shift_by

    def create_audio_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return ShiftSumTagger(audio, stimuli_intervals, self.__shift_by)


class SpectrumShiftTaggerFactory(AAudioTaggerFactory):
    __shift_by: int

    def __init__(self, shift_by: int):
        self.__shift_by = shift_by

    def create_audio_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return SpectrumShiftTagger(audio, stimuli_intervals, self.__shift_by)
