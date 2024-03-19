import numpy as np
import numpy.typing as npt
import pytest

from auditory_stimulation.auditory_tagging.assr_tagger import AMTagger, FMTagger, FlippedFMTagger
from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from auditory_stimulation.auditory_tagging.shift_tagger import ShiftSumTagger, SpectrumShiftTagger
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def mock_tag_generation(length: int, frequency: int, sampling_frequency: int) -> npt.NDArray[np.float32]:
    """Generates a mock stimulus generation function. consisting of only -1. -1 is picked so that the signal is
    modified.
    """
    return -np.ones(length, dtype=np.float32)


SAMPLING_FREQUENCY = 2

AUDIO_TAGGERS = [
    AMTagger(1, mock_tag_generation),
    FMTagger(42, 100),
    FlippedFMTagger(42),
    NoiseTaggingTagger(SAMPLING_FREQUENCY, 2, 10),
    ShiftSumTagger(3),
    SpectrumShiftTagger(3)
]


@pytest.mark.parametrize("audio_tagger", AUDIO_TAGGERS)
def test_audio_taggers_create_valid_call_audio_should_be_modified_to_half_point(audio_tagger):
    n_input = 100
    sampling_frequency = SAMPLING_FREQUENCY
    audio = get_mock_audio(n_input, sampling_frequency)

    stimuli_intervals = [(0, n_input / sampling_frequency / 2)]

    modified_audio = audio_tagger.create(audio, stimuli_intervals)

    assert modified_audio is not None
    assert modified_audio.array is not None
    assert modified_audio.sampling_frequency is not None

    assert modified_audio.sampling_frequency == sampling_frequency
    assert np.any(modified_audio.array[:n_input // 2, :] != audio.array[:n_input // 2, :])
    assert np.all(modified_audio.array[n_input // 2:, :] == audio.array[n_input // 2:, :])
