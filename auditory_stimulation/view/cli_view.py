from typing import Any

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.view import AView


class CLIView(AView):

    def _update_new_prompt(self, data: str) -> None:
        print(f"Prompt: {data}")

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        print(f"New State: {data}")

    def get_confirmation(self) -> bool:
        input("Please press the enter key")
        return True
