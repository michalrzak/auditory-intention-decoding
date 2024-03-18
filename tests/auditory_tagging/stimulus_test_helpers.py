from typing import Callable

import mockito
import numpy as np

from auditory_stimulation.audio import Audio


def get_mock_audio(n_input: int, sampling_frequency: int, seed: int = 100) -> Audio:
    np.random.seed(seed)

    audio = mockito.mock(Audio)
    audio.array = np.array(np.random.random_sample((n_input, 2)), dtype=np.float32)
    audio.sampling_frequency = sampling_frequency
    audio.secs = len(audio.array) / sampling_frequency

    return audio


def get_mock_ones_audio(n_input: int, sampling_frequency: int) -> Audio:
    audio = mockito.mock(Audio)
    audio.array = np.ones((n_input, 2), dtype=np.float32)
    audio.sampling_frequency = sampling_frequency

    return audio


def get_mock_audio_player() -> Callable[[Audio], None]:
    return lambda a: None
