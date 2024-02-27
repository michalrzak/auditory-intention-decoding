from dataclasses import dataclass
from typing import List

from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio


@dataclass
class Stimulus:
    modified_audio: Audio
    transcript: str
    primer: str
    options: List[str]

    # TODO: This could potentially be modified to also generate the stimulus instead of having to do it outside and then
    #  passing it
