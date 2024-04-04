from typing import Tuple, List, Callable

import numpy as np
import numpy.typing as npt
import pytest

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FlippedFMTagger, FMTagger
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def mock_stimulus_generation(length: int, frequency: int, sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Generates a mock stimulus generation function. consisting of only -1. -1 is picked so that the signal is
    modified.
    """
    return -np.ones(length, dtype=np.float32)


def get_am_tagger(frequency: int) -> AAudioTagger:
    return AMTagger(frequency, mock_stimulus_generation)


def get_flipped_fm_tagger(frequency: int) -> AAudioTagger:
    return FlippedFMTagger(frequency, 1)


def get_fm_tagger(frequency: int) -> AAudioTagger:
    return FMTagger(frequency, 100)


TAGGER_GETTERS: List[Callable[[int], AAudioTagger]] = [get_am_tagger,
                                                       get_flipped_fm_tagger,
                                                       get_fm_tagger]


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall_audioShouldBeModified(tagger_getter):
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 2

    stimulus = tagger_getter(stimulus_frequency)
    modified_audio = stimulus.create(audio, [(0, n_input / sampling_frequency)])

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array != audio.array)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall_audioShouldBeModifiedToHalfPoint(tagger_getter):
    n_input = 100
    sampling_frequency = 2
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 1

    stimulus = tagger_getter(stimulus_frequency)
    modified_audio = stimulus.create(audio, [(0, n_input / sampling_frequency / 2)])

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array[:n_input // 2, :] != audio.array[:n_input // 2, :])
    assert np.all(modified_audio.array[n_input // 2:, :] == audio.array[n_input // 2:, :])


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_invalidFrequency_0_shouldThrow(tagger_getter):
    audio = get_mock_audio(100, 12)
    stimulus_frequency = 0

    with pytest.raises(ValueError):
        stim = tagger_getter(stimulus_frequency)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_invalidFrequency_negative_shouldThrow(tagger_getter):
    audio = get_mock_audio(100, 12)
    stimulus_frequency = -1

    with pytest.raises(ValueError):
        stim = tagger_getter(stimulus_frequency)


@pytest.mark.parametrize("tagger_getter", TAGGER_GETTERS)
def test_ASSRTagger_create_validCall(tagger_getter):
    n_input = 1000
    sampling_frequency = 20
    audio = get_mock_audio(n_input, sampling_frequency)

    stimulus_frequency = 5

    stim = tagger_getter(stimulus_frequency)
    stim.create(audio, [(0, n_input / sampling_frequency)], )


@pytest.mark.parametrize("signal_interval", [(-1, 1), (-2, 2), (-3, -1), (1, 3), (0.5, 1.7)])
def test_am_tagger_signal_interval_valid_call(signal_interval: Tuple[float, float]):
    stimulus_frequency = 5

    signal = AMTagger(stimulus_frequency,
                      mock_stimulus_generation,
                      signal_interval)


@pytest.mark.parametrize("signal_interval", [(1, -1), (2, -2), (-1, -3), (3, 1), (1.7, 0.5)])
def test_am_tagger_signal_interval_invalid_interval_should_throw(signal_interval: Tuple[float, float]):
    stimulus_frequency = 5

    with pytest.raises(ValueError):
        signal = AMTagger(stimulus_frequency,
                          mock_stimulus_generation,
                          signal_interval)
