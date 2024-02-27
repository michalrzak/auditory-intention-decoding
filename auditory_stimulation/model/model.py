import warnings
from typing import List, Any, Optional

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.view import AView


class Model:
    __prompt_history: List[str]
    __primer_history: List[str]
    __experiment_state: EExperimentState

    __views: List[AView]

    def __init__(self) -> None:
        self.__prompt_history = []
        self.__primer_history = []

        self.__experiment_state = EExperimentState.INACTIVE  # TODO: This one should be passed in the constructor
        self.__views = []

    def __notify(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        for view in self.__views:
            view.update(data, identifier)

    def register(self, view: AView) -> None:
        self.__views.append(view)

    def new_prompt(self, prompt: str) -> None:
        self.__prompt_history.append(prompt)
        self.__notify(prompt, EModelUpdateIdentifier.NEW_PROMPT)

    def new_primer(self, primer: str) -> None:
        self.__primer_history.append(primer)
        self.__notify(primer, EModelUpdateIdentifier.NEW_PRIMER)

    def change_experiment_state(self, new_state: EExperimentState) -> None:
        assert new_state != self.__experiment_state
        if new_state == self.__experiment_state:
            warnings.warn("The state was already at the changed value.")

        self.__experiment_state = new_state
        self.__notify(self.__experiment_state, EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)

    @property
    def current_prompt(self) -> Optional[str]:
        if len(self.__prompt_history) == 0:
            return None
        return self.__prompt_history[-1]

    @property
    def current_primer(self) -> Optional[str]:
        if len(self.__primer_history) == 0:
            return None
        return self.__primer_history[-1]

    @property
    def experiment_state(self) -> EExperimentState:
        return self.__experiment_state
