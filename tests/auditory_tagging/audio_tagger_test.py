import numpy as np
import numpy.typing as npt
import pytest

from auditory_stimulation.auditory_tagging.assr_tagger import AMTaggerFactory, FlippedFMTaggerFactory, FMTaggerFactory
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTaggerFactory
from auditory_stimulation.auditory_tagging.shift_sum_tagger import ShiftSumTaggerFactory
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def mock_tag_generation(length: int, frequency: int, sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Generates a mock stimulus generation function. consisting of only -1. -1 is picked so that the signal is
    modified.
    """
    return -np.ones(length, dtype=np.float32)


AUDIO_TAGGER_FACTORIES = [
    AMTaggerFactory(1, mock_tag_generation),
    FMTaggerFactory(42, 100),
    FlippedFMTaggerFactory(42),
    NoiseTaggingTaggerFactory(2, 10),
    ShiftSumTaggerFactory(3)
]


@pytest.mark.parametrize("audio_tagger_factory", AUDIO_TAGGER_FACTORIES)
def test_audio_taggers_create_valid_call_audio_should_be_modified_to_half_point(audio_tagger_factory):
    n_input = 100
    sampling_frequency = 2
    audio = get_mock_audio(n_input, sampling_frequency)

    stimuli_intervals = [(0, n_input / sampling_frequency / 2)]

    tagger = audio_tagger_factory.create_auditory_tagger(audio, stimuli_intervals)
    modified_audio = tagger.create()

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array[:n_input // 2, :] != audio.array[:n_input // 2, :])
    assert np.all(modified_audio.array[n_input // 2:, :] == audio.array[n_input // 2:, :])
