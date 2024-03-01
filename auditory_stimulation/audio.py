import wave
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class Audio:
    audio: npt.NDArray[np.float32]
    sampling_frequency: int

    def __copy__(self) -> "Audio":
        return Audio(np.copy(self.audio), self.sampling_frequency)

    def __eq__(self, other: "Audio") -> bool:
        return np.all(self.audio == other.audio) and self.sampling_frequency == other.sampling_frequency


def save_audio_as_wav(audio: Audio, target_file_path: str) -> None:
    audio_bytes = (audio.audio * (2 ** 15 - 1)).astype("<h")

    with wave.open(target_file_path, "w") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(audio.sampling_frequency)
        f.writeframes(audio_bytes.tobytes())
