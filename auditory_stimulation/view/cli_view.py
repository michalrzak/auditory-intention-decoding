import time

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.stimulus import CreatedStimulus
from auditory_stimulation.view.view import AView


class CLIView(AView):
    """Simple view, utilizing the console as its output. Can be used for debugging."""

    def _update_new_stimulus(self, stimulus: CreatedStimulus) -> None:
        print(f"Prompt: {stimulus.prompt}")

    def _update_new_primer(self, primer: str) -> None:
        print(f"Primer: {primer}")

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        print(f"New State: {data}")

    def get_confirmation(self) -> bool:
        input("Please press the enter key")
        return True

    def wait(self, secs: int) -> None:
        time.sleep(secs)
