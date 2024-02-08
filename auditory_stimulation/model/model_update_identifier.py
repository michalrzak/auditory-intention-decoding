from enum import Enum, auto


class EModelUpdateIdentifier(Enum):
    NEW_PROMPT = auto()
    EXPERIMENT_STATE_CHANGED = auto()