import numpy as np
import psychopy.core
from psychopy.sound.backend_pygame import SoundPygame

from auditory_stimulation.audio import Audio


def psychopy_player(audio: Audio, play_audio: bool = True) -> None:
    """ Plays the given audio. Function is blocking and returns after the audio has finished playing

    :param audio: a dataclass consisting of
     * audio: Nx2 dimensional numpy array of the audio. Audio needs to be in the range [-1, 1]
     * sampling frequency: positive integer
    :param play_audio: a flag to be used when debugging and testing to disable the playing of the audio
    :return:
    """

    if audio.array.shape[1] != 2:
        raise ValueError("The audio has to be stereo! I.e. in the shape Nx2")

    if audio.array.dtype != np.float32:
        raise ValueError("The audio has to be of the type np.float32!")

    assert np.max(audio.array) <= 1
    assert np.min(audio.array) >= -1

    if audio.sampling_frequency <= 0:
        raise ValueError("Sampling rate has to be > 0")

    if not play_audio:
        return

    # use the pygame backend, as it allows to play sounds from arrays, not only from files
    sound = SoundPygame(value=audio.array)
    sound.play()
    duration = sound.getDuration()
    psychopy.core.wait(duration)
