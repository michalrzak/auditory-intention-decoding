import numpy as np
import pytest

from auditory_stimulation.audio import Audio, load_wav_as_numpy_array, save_audio_as_wav

rng = np.random.default_rng(123)


@pytest.mark.parametrize("shape", [(100, 2), (1000, 2), (1, 2), (10000, 2)])
@pytest.mark.parametrize("fs", [1, 2, 10, 20, 100, 1000])
def test_audio_valid_call(shape, fs):
    audio_array = np.zeros(shape)
    audio = Audio(audio_array, fs)

    assert np.all(audio.array == audio_array)
    assert audio.sampling_frequency == fs


def test_audio_sampling_frequency_zero_should_fail():
    audio_array = np.zeros((100, 2))
    fs = 0

    with pytest.raises(ValueError):
        audio = Audio(audio_array, fs)


@pytest.mark.parametrize("fs", [-1, -2, -10, -100, -1000])
def test_audio_sampling_frequency_bellow_zero_should_fail(fs):
    audio_array = np.zeros((100, 2))

    with pytest.raises(ValueError):
        audio = Audio(audio_array, fs)


@pytest.mark.parametrize("shape", [(100, 3), (100, 1), (100, 1000), (100, 0)])
def test_audio_array_invalid_shape_should_fail(shape):
    audio_array = np.zeros(shape)
    fs = -1

    with pytest.raises(ValueError):
        audio = Audio(audio_array, fs)


@pytest.mark.parametrize("sample", [2, 3, 1.1, 1.01, -2, -3, -1.1, -1.01])
def test_audio_array_sample_too_out_of_bounds(sample):
    audio_array = np.ones((100, 2)) * sample
    fs = 10

    with pytest.raises(ValueError):
        audio = Audio(audio_array, fs)


def test_load_wav_as_numpy_array_valid_call():
    path = "stimuli_sounds/test.wav"

    result = load_wav_as_numpy_array(path)

    assert result.array is not None
    assert result.sampling_frequency is not None
    assert len(result.array) > 0
    assert result.sampling_frequency == 44100


@pytest.mark.parametrize("shape", [(100, 2), (1000, 2), (1, 2), (10000, 2)])
@pytest.mark.parametrize("fs", [1, 2, 10, 20, 100, 1000])
def test_save_audio_as_wav_valid_call(tmp_path, shape, fs):
    audio_array = rng.random(shape, dtype=np.float32) * 2 - 1
    audio = Audio(audio_array, fs)

    file = tmp_path / "out.wav"

    save_audio_as_wav(audio, str(file))
    assert file.exists()

    loaded_audio = load_wav_as_numpy_array(str(file))
    # cannot just do loaded_audio == audio as there may be slight differences between the audios
    allowed_delta = 0.001
    assert np.all(np.abs(loaded_audio.array - audio.array) <= allowed_delta)
    assert loaded_audio.sampling_frequency == audio.sampling_frequency
