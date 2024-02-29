import logging
from typing import List, Any, Optional

from auditory_stimulation.audio import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus
from auditory_stimulation.view.view import AView


class Model:
    """Class, containing all  relevant data for the experiment. Is an observable of the observer pattern
    """
    __stimulus_history: List[CreatedStimulus]
    __primer_history: List[str]
    __experiment_state: EExperimentState

    __views: List[AView]

    __logger: logging.Logger

    def __init__(self, logger: logging.Logger) -> None:
        self.__stimulus_history = []
        self.__primer_history = []
        self.__experiment_state = EExperimentState.INACTIVE  # TODO: This one should be passed in the constructor
        self.__views = []
        self.__logger = logger

    def __notify(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        for view in self.__views:
            view.update(data, identifier)
            self.__logger.info(f"Notifying view {view} with data {data}")

    def register(self, view: AView) -> None:
        """Observable. Register a view, which will get notified about changes in the model."""
        self.__views.append(view)
        self.__logger.info(f"Registered view {view}")

    def new_stimulus(self, stimulus: CreatedStimulus) -> None:
        """ Add a new stimulus to the model.

        :param stimulus: The to be added stimulus.
        :return: None
        """
        self.__logger.info(f"Added new stimulus {stimulus}")

        self.__stimulus_history.append(stimulus)
        self.__notify(stimulus, EModelUpdateIdentifier.NEW_STIMULUS)

    def new_primer(self, primer: str) -> None:
        """Adds a primer statement to the model.

        :param primer: The to be added primer statement.
        :return: None
        """
        self.__logger.info(f"Added new primer {primer}")

        self.__primer_history.append(primer)
        self.__notify(primer, EModelUpdateIdentifier.NEW_PRIMER)

    def change_experiment_state(self, new_state: EExperimentState) -> None:
        """Change the current experiment state

        :param new_state: The to be changed to experiment state.
        :return: None
        """
        self.__logger.info(f"Changing experiment state to {new_state}")
        assert new_state != self.__experiment_state
        if new_state == self.__experiment_state:
            self.__logger.warning("The state was already at the changed value.")

        self.__experiment_state = new_state
        self.__notify(self.__experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

    @property
    def current_prompt(self) -> Optional[str]:
        if len(self.__stimulus_history) == 0:
            return None
        return self.__stimulus_history[-1].prompt

    @property
    def current_audio(self) -> Optional[Audio]:
        if len(self.__stimulus_history) == 0:
            return None
        return self.__stimulus_history[-1].audio

    @property
    def current_primer(self) -> Optional[str]:
        if len(self.__primer_history) == 0:
            return None
        return self.__primer_history[-1]

    @property
    def experiment_state(self) -> EExperimentState:
        return self.__experiment_state
