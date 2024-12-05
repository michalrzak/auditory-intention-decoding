from abc import abstractmethod
from typing import Callable, Any, Dict, Optional

from auditory_stimulation.audio import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import AStimulus


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
    def _update_new_stimulus(self, stimulus: AStimulus) -> None:
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
            self._update_new_stimulus(data)
        elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
            self._update_new_primer(data)
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            self._update_experiment_state_changed(data)
        elif identifier == EModelUpdateIdentifier.ATTENTION_CHECK:
            pass
        else:
            assert False  # this should never happen

    @abstractmethod
    def show_progress(self, n_current: int, n_total: int) -> None:
        """Shows the progress in the format {n_current}/{n_total}

        :param n_current: Current progress number
        :param n_total: Total number
        """

    @abstractmethod
    def get_confirmation(self) -> bool:
        """Wait for the user to confirm with some action.
        """
        ...

    @abstractmethod
    def attention_check(self) -> bool:
        """True, if the specified attention_check_action has been taken."""
        ...

    @abstractmethod
    def wait(self, secs: float) -> None:
        """Wait for the specified amount of time."""
        ...
