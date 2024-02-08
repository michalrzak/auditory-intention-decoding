from abc import ABC, abstractmethod
from typing import Any

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class AView(ABC):

    @abstractmethod
    def _update_new_prompt(self, data: str) -> None:
        ...

    @abstractmethod
    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        ...

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_PROMPT:
            # TODO: assert type is correct
            self._update_new_prompt(data)
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            # TODO: assert type is correct
            self._update_experiment_state_changed(data)
        else:
            # this should never happen
            assert False

    @abstractmethod
    def get_confirmation(self) -> bool:
        ...

