from abc import abstractmethod
from dataclasses import dataclass
from typing import Callable, Any, Dict, Optional, Collection

from auditory_stimulation.audio import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus


class ViewInterrupted(Exception):
    ...


class AView(AObserver):
    """Abstract class, to be implemented by new Views of the MVC pattern.
    Implements the Observer pattern.
    """
    _sound_player: Callable[[Audio], None]
    _experiment_texts: Dict[EExperimentState, Optional[str]]

    def __init__(self,
                 sound_player: Callable[[Audio], None],
                 experiment_texts: Dict[EExperimentState, Optional[str]]) -> None:
        self._sound_player = sound_player
        self._experiment_texts = experiment_texts

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
        """From the observer pattern. To be used by Observables (the model) to notify the view about changes.

        :param data: The changed data.
        :param identifier: An identifier, signal what sort of data got updated.
        :return:
        """
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
        """Wait for the user to confirm with some action.
        """
        ...

    @abstractmethod
    def wait(self, secs: float) -> None:
        """Wait for the specified amount of time."""
        ...


@dataclass
class CheckboxEntry:
    label: str
    key: str
    initial_value: bool


class AConfigurator:

    @abstractmethod
    def add_field(self, label: str, key: str, initial_value: None) -> None:
        pass

    @abstractmethod
    def add_checkboxes(self, label: str, key: str, items: Collection[CheckboxEntry]):
        pass

    @abstractmethod
    def add_dropdown(self, label: str, key: str, options: Collection[str]):
        pass

    @abstractmethod
    def get(self) -> Dict[str, Any]:
        pass
