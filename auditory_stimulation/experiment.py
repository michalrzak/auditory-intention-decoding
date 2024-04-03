from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.view.view import AView


class Experiment:
    """A controller class of the MVC pattern, responsible for handling the experiment logic, updating the model and
    calling blocking operations (wait for keypress, wait) on the view.
    """
    __model: Model
    __view: AView
    __block_size: int
    __resting_state_secs: float
    __primer_secs: float
    __break_secs: float

    def __init__(self,
                 model: Model,
                 view: AView,
                 block_size: int,
                 resting_state_secs: float,
                 primer_secs: float,
                 break_secs: float) -> None:
        """Constructs an Experiment instance.

        :param model: The underlying model of the experiment, saving all relevant experiment data.
        :param view: The used view of the experiment, showing the current state of the model and interacting with users
        :param block_size: The size of one block. After each block a break happens.
        :param resting_state_secs: How long to measure the resting state
        :param primer_secs: How long the primer is shown
        :param break_secs: How long the break is

        """
        self.__model = model
        self.__view = view

        if block_size <= 0:
            raise ValueError("block_size must be a positive integer!")
        self.__block_size = block_size

        if resting_state_secs < 0:
            raise ValueError("resting_state_secs must be a non-negative number!")
        self.__resting_state_secs = resting_state_secs

        if primer_secs < 0:
            raise ValueError("primer_secs must be a non-negative number!")
        self.__primer_secs = primer_secs

        if primer_secs < 0:
            raise ValueError("break_secs must be a non-negative number!")
        self.__break_secs = break_secs

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def run(self) -> None:
        """Runs the experiment.
        """
        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
        for i, stimulus in enumerate(self.__model.created_stimuli):
            self.__model.present_primer(stimulus.primer)
            self.__view.wait(self.__primer_secs)
            self.__model.present_stimulus(stimulus)

            if (i + 1) % self.__block_size == 0:
                self.__model.change_experiment_state(EExperimentState.BREAK)
                self.__view.wait(self.__break_secs)
                self.__view.get_confirmation()
                self.__model.change_experiment_state(EExperimentState.EXPERIMENT)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(self.__resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(self.__resting_state_secs)
