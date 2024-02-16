from typing import List, Tuple, Callable, Any

import numpy as np
import numpy.typing as npt

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio


class ASSRStimulus(AAuditoryStimulus):
    __frequency: int

    def __init__(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]],
                 audio_player: Callable[[Audio], None], frequency: int) -> None:
        super().__init__(audio, stimuli_intervals, audio_player)

        if frequency <= 0:
            raise ValueError("The frequency has to be a positive number")

        self.__frequency = frequency

    def __generate_added_signal(self, length: int) -> npt.NDArray[np.float32]:
        return np.sin(2 * np.pi * self.__frequency * np.array(range(length)) / self._audio.sampling_frequency)

    def __generate_added_signal_clicks(self, length: int) -> npt.NDArray[np.float32]:
        # TODO: potentially move this check to the constructor if this becomes the default method for this class
        # TODO: add tests if this becomes the default
        # has to be x2 as we are not only including a positive click every period, but also a negative click every
        #  negative period
        if self._audio.sampling_frequency // (self.__frequency * 2) != \
                self._audio.sampling_frequency / (self.__frequency * 2):
            raise ValueError("The frequency has to be fully divisible by the audio sampling frequency!")

        # set all values to 1 as default
        signal = np.ones(length)

        # set all necessary to -1
        first = self._audio.sampling_frequency // (self.__frequency * 2)
        step = self._audio.sampling_frequency // self.__frequency
        for i in range(first, length, step):
            interval_end = i + step // 2 if i + step // 2 <= length else length
            signal[i:interval_end] = -np.ones(interval_end - i)

        return signal

    def __duplicate_to_audio_channels(self, signal: npt.NDArray[Any], audio: npt.NDArray[np.float32]):
        if len(signal.shape) != 1:
            raise ValueError("Signal has to have zero dimensions in the second dimension")

        if audio.shape[1] != 2:
            raise NotImplementedError("Sorry, but only audio of size Nx2 is supported at the moment")

        return np.array([np.copy(signal), np.copy(signal)]).T

    def _create_modified_audio(self) -> Audio:
        audio_copy = np.copy(self._audio.audio)

        for interval in self._stimuli_intervals:
            sample_range = (int(interval[0] * self._audio.sampling_frequency),
                            int(interval[1] * self._audio.sampling_frequency))

            # generate sine of the appropriate frequency
            added_signal = self.__generate_added_signal_clicks(sample_range[1] - sample_range[0])

            duplicated_signal = self.__duplicate_to_audio_channels(added_signal, self._audio.audio)
            audio_copy[sample_range[0]:sample_range[1]] *= duplicated_signal

        # new_max = np.max([np.abs(np.min(audio_copy)), np.max(audio_copy)])
        # return Audio(audio_copy / new_max, self._audio.sampling_frequency)
        return Audio(audio_copy, self._audio.sampling_frequency)
