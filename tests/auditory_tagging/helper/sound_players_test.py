import mockito
import numpy as np
import numpy.typing as npt
import pytest

from auditory_stimulation.audio import Audio
from auditory_stimulation.view.sound_players import psychopy_player


def mock_audio(array: npt.NDArray, sampling_frequency: int) -> Audio:
    audio = mockito.mock(Audio)
    audio.array = array
    audio.sampling_frequency = sampling_frequency
    return audio


def test_psychopy_player_valid_call():
    # initialize small test array
    audio_raw = np.array([[-0, -0], [-1, 1]], dtype=np.float32)
    audio = mock_audio(audio_raw, 1)

    psychopy_player(audio, False)


def test_psychopy_player_invalid_array_shape_should_throw():
    audio_raw = np.ones((10, 3), dtype=np.float32)
    sampling_frequency = 1
    audio = mock_audio(audio_raw, sampling_frequency)

    with pytest.raises(ValueError):
        psychopy_player(audio, False)


def test_psychopy_player_invalid_array_type_should_throw():
    audio_raw = np.ones((10, 2), dtype=np.int32)
    audio = mock_audio(audio_raw, 1)

    with pytest.raises(ValueError):
        psychopy_player(audio, False)


def test_psychopy_player_values_greater_one_should_throw():
    audio_raw = np.ones((10, 2), dtype=np.float32) * 2
    audio = mock_audio(audio_raw, 1)

    with pytest.raises(AssertionError):
        psychopy_player(audio, False)


def test_psychopy_player_values_less_then_minus_one_should_throw():
    audio_raw = np.ones((10, 2), dtype=np.float32) * -2
    audio = mock_audio(audio_raw, 1)

    with pytest.raises(AssertionError):
        psychopy_player(audio, False)


def test_psychopy_player_values_exactly_one_valid_call():
    audio_raw = np.ones((10, 2), dtype=np.float32)
    audio = mock_audio(audio_raw, 1)

    psychopy_player(audio, False)


def test_psychopy_player_values_exactly_minus_one_valid_call():
    audio_raw = np.ones((10, 2), dtype=np.float32) * -1
    audio = mock_audio(audio_raw, 1)

    psychopy_player(audio, False)


def test_psychopy_player_sampling_rate_below_zero_should_throw():
    audio_raw = np.ones((10, 2), dtype=np.float32)
    sampling_rate = -1
    audio = mock_audio(audio_raw, sampling_rate)

    with pytest.raises(ValueError):
        psychopy_player(audio, False)


def test_psychopy_player_sampling_rate_zero_should_throw():
    audio_raw = np.ones((10, 2), dtype=np.float32)
    sampling_rate = 0
    audio = mock_audio(audio_raw, sampling_rate)

    with pytest.raises(ValueError):
        psychopy_player(audio, False)
