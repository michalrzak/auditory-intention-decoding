import wave
from dataclasses import dataclass
from os import PathLike

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class Audio:
    """A store of all audio related information.

    :param array: An array storing the actual audio information. Needs to be between -1 and 1
    :param sampling_frequency: The sampling frequency of the used audio. Needs to be a positive integer.
    """
    array: npt.NDArray[np.float32]
    sampling_frequency: int

    def __post_init__(self):
        if len(self.array.shape) != 2 or self.array.shape[1] != 2:
            raise ValueError("The supplied audio must be of shape Nx2!")

        if self.sampling_frequency <= 0:
            raise ValueError("The sampling frequency must be a positive integer!")

        if np.any(self.array > 1) or np.any(self.array < -1):
            raise ValueError("The supplied audio must be in the range -1 and 1")

    @property
    def secs(self) -> float:
        return self.array.shape[0] / self.sampling_frequency

    def __copy__(self) -> "Audio":
        return Audio(np.copy(self.array), self.sampling_frequency)

    def __eq__(self, other: "Audio") -> bool:
        return np.all(self.array == other.array) and self.sampling_frequency == other.sampling_frequency

    def __hash__(self):
        return hash(str(self.array) + str(self.sampling_frequency))

    def __repr__(self) -> str:
        return f"Audio(audio-shape={self.array.shape}, sampling_frequency={self.sampling_frequency})"


def load_wav_as_audio(wav_path: PathLike) -> Audio:
    """Opens the specified wav file and creates an Audio class. wav must be a PCM-wav file

    :param wav_path: Path to the to be opened wav file
    :return: An Audio object created from the wav file.
    """
    with wave.open(str(wav_path)) as f:
        buffer = f.readframes(f.getnframes())
        bit_depth = f.getsampwidth() * 8
        frequency = f.getframerate()
        interleaved = np.frombuffer(buffer, dtype=f"int{f.getsampwidth() * 8}")
        audio_data = np.reshape(interleaved, (-1, f.getnchannels()))

    return Audio(audio_data.astype(np.float32) / 2 ** (bit_depth - 1), frequency)


def save_audio_as_wav(audio: Audio, target_file_path: PathLike) -> None:
    """Saves the given audio as a 16 bit PCM wav file in the specified target location.

    :param audio: The to be saved audio.
    :param target_file_path: The target file, where the audio will be saved.
    :return: None
    """
    audio_bytes = (audio.array * (2 ** 15 - 1)).astype("<h")

    with wave.open(str(target_file_path), "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(audio.sampling_frequency)
        f.writeframes(audio_bytes.tobytes())
