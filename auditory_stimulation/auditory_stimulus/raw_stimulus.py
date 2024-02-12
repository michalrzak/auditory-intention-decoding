from typing import Any, List, Tuple

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio


class RawStimulus(AAuditoryStimulus):
    def _create_modified_audio(self, audio: Audio, stimuli_intervals: List[Tuple[float, float]]) -> Any:
        return audio
