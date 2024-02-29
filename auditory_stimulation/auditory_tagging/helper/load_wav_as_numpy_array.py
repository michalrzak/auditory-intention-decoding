import wave

import numpy as np

from auditory_stimulation.auditory_tagging.auditory_tagger import Audio


def load_wav_as_numpy_array(wav_path: str) -> Audio:
    with wave.open(wav_path) as f:
        buffer = f.readframes(f.getnframes())
        bit_depth = f.getsampwidth() * 8
        frequency = f.getframerate()
        interleaved = np.frombuffer(buffer, dtype=f"int{f.getsampwidth() * 8}")
        audio_data = np.reshape(interleaved, (-1, f.getnchannels()))

    return Audio(audio_data.astype(np.float32) / 2 ** (bit_depth - 1), frequency)
