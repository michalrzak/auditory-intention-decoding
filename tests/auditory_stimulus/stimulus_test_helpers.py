from typing import Callable

import numpy as np
import mockito

from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio


def get_mock_audio(n_input: int, sampling_frequency: int, seed: int = 100) -> Audio:
    np.random.seed(seed)

    audio = mockito.mock(Audio)
    audio.audio = np.random.rand(n_input, 2)
    audio.sampling_frequency = sampling_frequency

    return audio


def get_mock_audio_player() -> Callable[[Audio], None]:
    return lambda a: None