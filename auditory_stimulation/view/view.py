from abc import ABC, abstractmethod
from typing import Any

from auditory_stimulation.model.model_update_identifier import ModelUpdateIdentifier


class View(ABC):
    @abstractmethod
    def update(self, data: Any, identifier: ModelUpdateIdentifier) -> None:
        ...