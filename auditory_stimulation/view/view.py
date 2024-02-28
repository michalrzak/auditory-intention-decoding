from abc import ABC, abstractmethod
from typing import Callable, Any

from auditory_stimulation.auditory_stimulus.auditory_stimulus import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.stimulus import CreatedStimulus


class AView(ABC):
    _sound_player: Callable[[Audio], None]

    def __init__(self, sound_player: Callable[[Audio], None]) -> None:
        self._sound_player = sound_player

    @abstractmethod
    def _update_new_stimulus(self, stimulus: CreatedStimulus) -> None:
        ...

    @abstractmethod
    def _update_new_primer(self, primer: str) -> None:
        ...

    @abstractmethod
    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        ...

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            # TODO: assert type is correct
            self._update_new_stimulus(data)
        elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
            # TODO: assert type is correct
            self._update_new_primer(data)
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            # TODO: assert type is correct
            self._update_experiment_state_changed(data)
        else:
            # this should never happen
            assert False

    @abstractmethod
    def get_confirmation(self) -> bool:
        ...

    @abstractmethod
    def wait(self, secs: int) -> None:
        ...
