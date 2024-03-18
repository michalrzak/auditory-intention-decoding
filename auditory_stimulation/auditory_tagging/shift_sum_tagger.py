from typing import List, Tuple

import numpy as np

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, _duplicate_signal, _scale_down_signal, \
    AAudioTaggerFactory


class ShiftSumTagger(AAudioTagger):
    """A tagger, which works by first shifiting the provided audio by the specified frequency and then overlaying
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

            n = np.arange(audio_chunk.shape[0])
            multiplier = np.e ** ((1j * 2 * np.pi * self.__shift_by * n) / self._audio.sampling_frequency)
            multiplier_duplicated = _duplicate_signal(multiplier)

            audio_array_shifted = np.array(np.real(audio_chunk * multiplier_duplicated), dtype=np.float32)
            audio_array_combined = audio_array_shifted + audio_chunk
            audio_array_combined_scaled = _scale_down_signal(audio_array_combined)

            audio_copy[sample_range[0]:sample_range[1]] = audio_array_combined_scaled

        audio_combined = Audio(audio_copy, self._audio.sampling_frequency)

        return audio_combined

    def __repr__(self) -> str:
        return f"ShiftSumTagger({super().__repr__()}, shift_by={self.__shift_by})"


class ShiftSumTaggerFactory(AAudioTaggerFactory):
    __shift_by: int

    def __init__(self, shift_by: int):
        self.__shift_by = shift_by

    def create_auditory_tagger(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return ShiftSumTagger(audio, stimuli_intervals, self.__shift_by)
