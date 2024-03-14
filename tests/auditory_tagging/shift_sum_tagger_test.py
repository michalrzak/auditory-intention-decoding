import numpy as np
import pytest

from auditory_stimulation.auditory_tagging.shift_sum_tagger import ShiftSumTagger
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def similarity_metric_checks(similarity_metric, similarity_cutoff):
    assert len(similarity_metric[0].shape) == 1 and len(similarity_metric[1].shape) == 1
    assert similarity_metric[0].shape[0] == 1 and similarity_metric[1].shape[0] == 1
    assert similarity_metric[0][0] > similarity_cutoff and similarity_metric[1][0] > similarity_cutoff


def test_shift_sum_tagger_valid_call():
    similarity_cutoff = 15

    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    shift_by = 40

    tagger = ShiftSumTagger(audio, [(0, n_input / sampling_frequency)], shift_by)
    modified_audio = tagger.create()

    similarity_metric = (
        np.correlate(modified_audio.array[:, 0], audio.array[:, 0]),
        np.correlate(modified_audio.array[:, 1], audio.array[:, 1])
    )
    similarity_metric_checks(similarity_metric, similarity_cutoff)

    modified_spectrum = (
        np.fft.fft(modified_audio.array[:, 0]),
        np.fft.fft(modified_audio.array[:, 1])
    )
    original_spectrum = (
        np.fft.fft(audio.array[:, 0]),
        np.fft.fft(audio.array[:, 1])
    )
    similarity_metric_spectrum = (
        np.correlate(modified_spectrum[0], original_spectrum[0]),
        np.correlate(modified_spectrum[1], original_spectrum[1])
    )
    similarity_metric_checks(similarity_metric_spectrum, similarity_cutoff)


def test_shift_sum_tagger_invalid_shift_by_should_fail():
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    shift_by = -10

    with pytest.raises(ValueError):
        ShiftSumTagger(audio, [(0, n_input / sampling_frequency)], shift_by)
