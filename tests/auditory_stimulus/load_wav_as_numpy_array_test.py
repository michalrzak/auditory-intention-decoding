from auditory_stimulation.auditory_stimulus.load_wav_as_numpy_array import load_wav_as_numpy_array


def test_load_wav_as_numpy_array_valid_call():
    path = "tests/auditory_stimulus/test.wav"

    result = load_wav_as_numpy_array(path)

    assert result.audio is not None
    assert result.sampling_frequency is not None
    assert len(result.audio) > 0
    assert result.sampling_frequency == 44100
