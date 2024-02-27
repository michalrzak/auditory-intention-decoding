from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView

# TODO: this needs to be a lot more complex, linking a primer the audio, the stimuli timestamps
STIMULI = ["Hello, this is pizzeria Romano, how can I help you?"]

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5


class Experiment:
    __model: Model
    __view: AView

    def __init__(self, model: Model, view: AView) -> None:
        self.__model = model
        self.__view = view

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def run(self) -> None:
        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
        for stimulus in STIMULI:
            self.__model.new_primer("Test primer")  # TODO: proper primer
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.new_prompt(stimulus)  # TODO: proper stimulus

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)
