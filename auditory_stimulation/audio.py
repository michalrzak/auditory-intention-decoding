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
