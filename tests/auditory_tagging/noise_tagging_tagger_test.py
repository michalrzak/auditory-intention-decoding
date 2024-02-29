import numpy as np
import pytest

from auditory_stimulation.auditory_tagging.noise_tagging_tagger import NoiseTaggingTagger
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio, get_mock_ones_audio

SEED = 123


def test_create_validCall_channelsShouldBeTheSame():
    n_input = 100
    sampling_frequency = 12
    audio = get_mock_audio(n_input, sampling_frequency)

    bits_per_second = 6
    length_bit = 20

    stimulus = NoiseTaggingTagger(audio,
                                  [(0, n_input / sampling_frequency)],
                                  bits_per_second,
                                  length_bit,
                                  SEED)
    stimulus.create()
    code = stimulus.code

    assert np.all(code[:, 0] == code[:, 1])


def test_create_validCall_codeHasCorrectResolution():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 5
    length = bits_per_second * 2
    stimulus = NoiseTaggingTagger(audio,
                                  [labeled_interval],
                                  bits_per_second,
                                  length,
                                  SEED)

    stimulus.create()
    code = stimulus.code

    bit_width = sampling_frequency / bits_per_second

    assert code.shape[0] == bit_width * length


def test_create_validCall_codeRepeatsCorrectly():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_ones_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 5
    length = bits_per_second  # code of length 1 second

    stimulus = NoiseTaggingTagger(audio,
                                  [labeled_interval],
                                  bits_per_second,
                                  length,
                                  SEED)
    modified_audio = stimulus.create()

    # since the code is 1 second and the interval is 2 seconds, the code should repeat twice
    code = stimulus.code

    assert np.all(
        modified_audio.audio[labeled_interval[0] * sampling_frequency:labeled_interval[1] * sampling_frequency // 2, :]
        == code)
    assert np.all(
        modified_audio.audio[labeled_interval[1] * sampling_frequency // 2:labeled_interval[1] * sampling_frequency, :]
        == code)


def test_create_shouldThrow_bitsPerSecondDoesNotDivideSamplingFrequency():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 3
    length = bits_per_second  # code of length 1 second

    with pytest.raises(ValueError):
        stimulus = NoiseTaggingTagger(audio,
                                      [labeled_interval],
                                      bits_per_second,
                                      length,
                                      SEED)


def test_create_shouldThrow_bitsPerSecondZero():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = 0
    length = bits_per_second  # code of length 1 second

    with pytest.raises(ValueError):
        stimulus = NoiseTaggingTagger(audio,
                                      [labeled_interval],
                                      bits_per_second,
                                      length,
                                      SEED)


def test_create_shouldThrow_bitsPerSecondBellowZero():
    n_input = 100
    sampling_frequency = 10
    audio = get_mock_audio(n_input, sampling_frequency)

    labeled_interval = (0, 2)  # 2 seconds labeled
    bits_per_second = -1
    length = bits_per_second  # code of length 1 second

    with pytest.raises(ValueError):
        stimulus = NoiseTaggingTagger(audio,
                                      [labeled_interval],
                                      bits_per_second,
                                      length,
                                      SEED)