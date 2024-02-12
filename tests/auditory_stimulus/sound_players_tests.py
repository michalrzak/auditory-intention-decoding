import numpy as np
import pytest

from auditory_stimulation.auditory_stimulus.sound_players import psychopy_player


def test_psychopy_player_valid_call():
    # initialize small test array
    audio = np.array([[-0, -0], [-1, 1]], dtype=np.float32)

    psychopy_player(audio)


def test_psychopy_player_invalid_array_shape_should_throw():
    audio = np.ones((10, 3), dtype=np.float32)

    with pytest.raises(ValueError):
        psychopy_player(audio)


def test_psychopy_player_invalid_array_type_should_throw():
    audio = np.ones((10, 2), dtype=np.int32)

    with pytest.raises(ValueError):
        psychopy_player(audio)


def test_psychopy_player_values_greater_one_should_throw():
    audio = np.ones((10, 2), dtype=np.float32) * 2

    with pytest.raises(AssertionError):
        psychopy_player(audio)


def test_psychopy_player_values_less_then_minus_one_should_throw():
    audio = np.ones((10, 2), dtype=np.float32) * -2

    with pytest.raises(AssertionError):
        psychopy_player(audio)


def test_psychopy_player_values_exactly_one_valid_call():
    audio = np.ones((10, 2), dtype=np.float32)
    psychopy_player(audio)


def test_psychopy_player_values_exactly_minus_one_valid_call():
    audio = np.ones((10, 2), dtype=np.float32) * -1
    psychopy_player(audio)


def test_psychopy_player_sampling_rate_below_zero_should_throw():
    audio = np.ones((10, 2), dtype=np.float32)
    sampling_rate = -1

    with pytest.raises(ValueError):
        psychopy_player(audio, sampling_rate)


def test_psychopy_player_sampling_rate_zero_should_throw():
    audio = np.ones((10, 2), dtype=np.float32)
    sampling_rate = 0

    with pytest.raises(ValueError):
        psychopy_player(audio, sampling_rate)



