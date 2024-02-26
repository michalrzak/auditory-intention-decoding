from typing import List, Tuple

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulus, Audio


class RawStimulus(AAuditoryStimulus):
    def _create_modified_audio(self) -> Audio:
        return self._audio
