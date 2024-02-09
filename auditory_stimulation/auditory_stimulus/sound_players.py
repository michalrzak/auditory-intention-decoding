from copy import copy

import numpy.typing as npt
import numpy as np
import pyaudio

from psychopy.sound.backend_pygame import SoundPygame


def psychopy_player(audio: npt.NDArray[np.float32]):
    """ Plays the give audio

    :param audio: Nx2 dimensional array of the audio. Audio needs to be in the range [-1, 1]
    :return:
    """

    # use the pygame backend, as it allows to play sounds from arrays, not only from files
    sound = SoundPygame(value = audio)
    sound.play()
    raise NotImplementedError()

CHUNK = 1024
def pyaudio_player(audio: npt.NDArray[np.float32]):

    audio_copy = copy(audio)
    # Insate PyAudio and initialize PortAudio system resources (1)
    p = pyaudio.PyAudio()

    # Open stream (2)
    stream = p.open(format=pyaudio.paFloat32,
                    channels=2,
                    rate=44100,
                    output=True)

    # Play samples from the wave file (3)
    while len(data := audio_copy[:CHUNK]):
        stream.write(data)

    # Close stream (4)
    stream.close()

    # Release PortAudio system resources (5)
    p.terminate()
