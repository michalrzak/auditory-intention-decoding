from enum import Enum, auto


class EModelUpdateIdentifier(Enum):
    NEW_PROMPT = auto()
    NEW_PRIMER = auto()
    EXPERIMENT_STATE_CHANGED = auto()
