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
        return np.sin(2 * np.pi * self.__frequency * np.array(range(length)) / 44100)

    def __duplicate_to_audio_channels(self, signal: npt.NDArray[Any], audio: npt.NDArray[np.float32]):
        if len(signal.shape) != 1:
            raise ValueError("Signal has to have zero dimensions in the second dimension")

        if audio.shape[1] != 2:
            raise NotImplementedError("Sorry, but only audio of size Nx2 is supported at the moment")

        return np.array([np.copy(signal), np.copy(signal)]).T

    def _create_modified_audio(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> Audio:
        audio_copy = np.copy(audio.audio)

        for interval in stimuli_intervals:
            sample_range = (int(interval[0] * audio.sampling_frequency), int(interval[1] * audio.sampling_frequency))

            # generate sine of the appropriate frequency
            added_signal = self.__generate_added_signal(sample_range[1] - sample_range[0])

            duplicated_signal = self.__duplicate_to_audio_channels(added_signal, audio.audio)
            audio_copy[sample_range[0]:sample_range[1]] += duplicated_signal

        new_max = np.max([np.abs(np.min(audio_copy)), np.max(audio_copy)])
        return Audio(audio_copy / new_max, audio.sampling_frequency)
