from enum import Enum, auto


class EExperimentState(Enum):
    INACTIVE = auto()
    INTRODUCTION = auto()
    RESTING_STATE_EYES_OPEN = auto()
    RESTING_STATE_EYES_CLOSED = auto()
    EXPERIMENT_INTRODUCTION = auto()
    EXPERIMENT = auto()
