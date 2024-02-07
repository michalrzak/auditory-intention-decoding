from abc import ABC, abstractmethod
from typing import Any

from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class AView(ABC):
    @abstractmethod
    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        ...

    @abstractmethod
    def get_confirmation(self) -> bool:
        ...