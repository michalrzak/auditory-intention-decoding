import warnings
from typing import List, Any

from auditory_stimulation.model.experiment_state import ExperimentState
from auditory_stimulation.view.view import View
from auditory_stimulation.model.model_update_identifier import ModelUpdateIdentifier


class Model:
    prompt_history: List[str]
    current_prompt: str
    experiment_state: ExperimentState

    views: List[View]

    def __init__(self) -> None:
        self.prompt_history = []
        self.current_prompt = None  # TODO: not sure how to best initialize this
        self.experiment_state = None  # TODO: I think this one should be passed in the constructor
        self.views = []

    def __notify(self, data: Any, identifier: ModelUpdateIdentifier) -> None:
        for view in self.views:
            view.update(data, identifier)

    def register(self, view: View) -> None:
        self.views.append(view)

    def new_prompt(self, prompt: str) -> None:
        self.prompt_history.append(self.current_prompt)
        self.current_prompt = prompt

        self.__notify(prompt, ModelUpdateIdentifier.NEW_PROMPT)

    def change_experiment_state(self, new_state: ExperimentState) -> None:
        assert new_state != self.experiment_state
        if new_state == self.experiment_state:
            warnings.warn("The state was already at the changed value.")

        self.experiment_state = new_state
        self.__notify(self.experiment_state, ModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED)
