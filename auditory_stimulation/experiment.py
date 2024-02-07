from auditory_stimulation.model.experiment_state import ExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import View


class Experiment:
    model: Model
    view: View

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view

    def run(self) -> None:
        self.model.new_prompt("YO!")
        self.view.get_confirmation()
        self.model.new_prompt("How you doing bro?")
        self.model.change_experiment_state(ExperimentState.RESTING_STATE)
        self.view.get_confirmation()