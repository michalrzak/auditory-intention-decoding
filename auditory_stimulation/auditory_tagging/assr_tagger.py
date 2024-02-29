from numbers import Number
from typing import List, Tuple, Callable

import numpy as np
import numpy.typing as npt

from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger, Audio, AAudioTaggerFactory


class ASSRTagger(AAudioTagger):
    """Creates an auditory ASSR stimulus. The ASSR stimulus is generated by modulating the specified regions of the
    signal, with a signal (between -1 and 1) of the appropriate frequency.
    """
    __frequency: int
    __stimulus_generation: Callable[[int, int, int], npt.NDArray[np.float32]]
    __modulator: Callable[[npt.NDArray[np.float32], npt.NDArray[Number]], npt.NDArray[npt.NDArray[np.float32]]]

    def __init__(self,
                 audio: Audio,
                 stimuli_intervals: List[Tuple[float, float]],
                 frequency: int,
                 stimulus_generation: Callable[[int, int, int], npt.NDArray[np.float32]],
                 modulator: Callable[[npt.NDArray[np.float32], npt.NDArray[Number]],
                                     npt.NDArray[npt.NDArray[np.float32]]]
                 ) -> None:
        """Constructs the ASSRStimulus object

        :param audio: Object containing the audio signal as a numpy array and the sampling frequency of the audio
        :param stimuli_intervals: The intervals given in seconds, which will be modified with the stimulus. The
         intervals must be contained within the audio.
        :param frequency: The frequency of the ASSR stimulus
        :param stimulus_generation: A function, which given the length, stimulus frequency and sampling frequency
         generates the modulating stimulus
        :param modulator: A function, which given the audio signal and the modulating signal generates the modulated
         signal
        """

        super().__init__(audio, stimuli_intervals)

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        self.__frequency = frequency
        self.__stimulus_generation = stimulus_generation
        self.__modulator = modulator

    def create(self) -> Audio:
        """This method is implemented from the abstract super class. When called, it generates the ASSR stimulus
        modified audio.

        :return: The ASSR stimulus modified audio.
        """

        audio_copy = np.copy(self._audio.audio)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            # generate sine of the appropriate frequency
            added_signal = self.__stimulus_generation(sample_range[1] - sample_range[0],
                                                      self.__frequency, self._audio.sampling_frequency)
            modulated_chunk = self.__modulator(audio_copy[sample_range[0]:sample_range[1]], added_signal)
            audio_copy[sample_range[0]:sample_range[1]] = modulated_chunk

        return Audio(audio_copy, self._audio.sampling_frequency)


class ASSRTaggerFactory(AAudioTaggerFactory):
    _frequency: int
    _stimulus_generator: Callable[[int, int, int], npt.NDArray[np.float32]]
    _modulator: Callable[[npt.NDArray[np.float32], npt.NDArray[Number]], npt.NDArray[npt.NDArray[np.float32]]]

    def __init__(self,
                 frequency: int,
                 stimulus_generation: Callable[[int, int, int], npt.NDArray[np.float32]],
                 modulator: Callable[[npt.NDArray[np.float32], npt.NDArray[Number]],
                                     npt.NDArray[npt.NDArray[np.float32]]]
                 ) -> None:
        self._frequency = frequency
        self._stimulus_generator = stimulus_generation
        self._modulator = modulator

    def create_auditory_stimulus(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> AAudioTagger:
        return ASSRTagger(audio,
                          stimuli_intervals,
                          self._frequency,
                          self._stimulus_generator,
                          self._modulator)