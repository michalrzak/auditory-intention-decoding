from enum import Enum, auto


class EModelUpdateIdentifier(Enum):
    NEW_STIMULUS = auto()
    NEW_PRIMER = auto()
    EXPERIMENT_STATE_CHANGED = auto()
