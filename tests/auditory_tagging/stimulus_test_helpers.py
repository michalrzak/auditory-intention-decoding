from typing import Callable

import mockito
import numpy as np

from auditory_stimulation.audio import Audio


def get_mock_audio(n_input: int, sampling_frequency: int, seed: int = 100) -> Audio:
    np.random.seed(seed)

    audio = mockito.mock(Audio)
    audio.audio = np.random.rand(n_input, 2)
    audio.sampling_frequency = sampling_frequency

    return audio


def get_mock_ones_audio(n_input: int, sampling_frequency: int) -> Audio:
    audio = mockito.mock(Audio)
    audio.audio = np.ones((n_input, 2))
    audio.sampling_frequency = sampling_frequency

    return audio


def get_mock_audio_player() -> Callable[[Audio], None]:
    return lambda a: None
