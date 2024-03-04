import wave
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class Audio:
    array: npt.NDArray[np.float32]
    sampling_frequency: int

    def __post_init__(self):
        if len(self.array.shape) != 2 or self.array.shape[1] != 2:
            raise ValueError("The supplied audio must be of shape Nx2!")

        if self.sampling_frequency <= 0:
            raise ValueError("The sampling frequency must be a positive integer!")

    def __copy__(self) -> "Audio":
        return Audio(np.copy(self.array), self.sampling_frequency)

    def __eq__(self, other: "Audio") -> bool:
        return np.all(self.array == other.array) and self.sampling_frequency == other.sampling_frequency

    def __repr__(self) -> str:
        return f"Audio(audio-shape={self.array.shape}, sampling_frequency={self.sampling_frequency})"


def load_wav_as_numpy_array(wav_path: str) -> Audio:
    with wave.open(wav_path) as f:
        buffer = f.readframes(f.getnframes())
        bit_depth = f.getsampwidth() * 8
        frequency = f.getframerate()
        interleaved = np.frombuffer(buffer, dtype=f"int{f.getsampwidth() * 8}")
        audio_data = np.reshape(interleaved, (-1, f.getnchannels()))

    return Audio(audio_data.astype(np.float32) / 2 ** (bit_depth - 1), frequency)


def save_audio_as_wav(audio: Audio, target_file_path: str) -> None:
    audio_bytes = (audio.array * (2 ** 15 - 1)).astype("<h")

    with wave.open(target_file_path, "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(audio.sampling_frequency)
        f.writeframes(audio_bytes.tobytes())
