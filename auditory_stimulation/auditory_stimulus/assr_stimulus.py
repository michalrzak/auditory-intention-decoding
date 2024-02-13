from typing import List, Tuple, Callable

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
        return np.sin(2 * np.pi * self.__frequency * np.array(range(length)))

    def _create_modified_audio(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> Audio:
        audio_copy = np.copy(audio.audio)

        for interval in stimuli_intervals:
            sample_range = (int(interval[0] * audio.sampling_frequency), int(interval[1] * audio.sampling_frequency))

            # generate sine of the appropriate frequency
            added_signal = self.__generate_added_signal(sample_range[1] - sample_range[0])

            audio_copy[sample_range[0]:sample_range[1]] += added_signal

        return Audio(audio_copy, audio.sampling_frequency)
