from auditory_stimulation.model.experiment_state import ExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import View


class Experiment:
    __model: Model
    __view: View

    def __init__(self, model: Model, view: View) -> None:
        self.__model = model
        self.__view = view

    def run(self) -> None:
        self.__model.new_prompt("YO!")
        self.__view.get_confirmation()
        self.__model.new_prompt("How you doing bro?")
        self.__model.change_experiment_state(ExperimentState.RESTING_STATE)
        self.__view.get_confirmation()