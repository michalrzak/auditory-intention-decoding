import numpy.typing as npt
import numpy as np

from psychopy.sound.backend_pygame import SoundPygame


def psychopy_player(audio: npt.NDArray[np.float32], sampling_rate: int = 44100) -> None:
    """ Plays the given audio. Function is blocking and returns after the audio has finished playing

    :param audio: Nx2 dimensional numpy array of the audio. Audio needs to be in the range [-1, 1]
    :param sampling_rate: integer of the sampling rate of the audio. Default is 44100.
    :return:
    """

    if audio.shape[1] != 2:
        raise ValueError("The audio has to be stereo! I.e. in the shape Nx2")

    if audio.dtype != np.float32:
        raise ValueError("The audio has to be of the type np.float32!")

    assert np.max(audio) <= 1
    assert np.min(audio) >= -1

    if sampling_rate <= 0:
        raise ValueError("Sampling rate has to be > 0")

    # use the pygame backend, as it allows to play sounds from arrays, not only from files
    sound = SoundPygame(value=audio)
    sound.play()
