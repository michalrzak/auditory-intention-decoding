from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView


class Experiment:
    __model: Model
    __view: AView

    def __init__(self, model: Model, view: AView) -> None:
        self.__model = model
        self.__view = view

    def run(self) -> None:
        self.__model.new_prompt("YO!")
        self.__view.get_confirmation()
        self.__model.new_prompt("How you doing bro?")
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE)
        self.__view.get_confirmation()
