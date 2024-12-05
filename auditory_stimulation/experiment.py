from typing import Protocol

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.model.stimulus import AStimulus
from auditory_stimulation.view.view import AView


class ExperimentDurations(Protocol):
    resting_state_secs: float
    primer_secs: float
    break_secs: float
    attention_check_secs: float


class Experiment:
    """A controller class of the MVC pattern, responsible for handling the experiment logic, updating the model and
    calling blocking operations (wait for keypress, wait) on the view.
    """
    __model: Model
    __view: AView
    __block_size: int
    __experiment_durations: ExperimentDurations

    def __init__(self,
                 model: Model,
                 view: AView,
                 block_size: int,
                 experiment_durations: ExperimentDurations) -> None:
        """Constructs an Experiment instance.

        :param model: The underlying model of the experiment, saving all relevant experiment data.
        :param view: The used view of the experiment, showing the current state of the model and interacting with users
        :param block_size: The size of one block. After each block a break happens.
        :param experiment_durations: Structure, defining various durations of the experiment
        """
        self.__model = model
        self.__view = view

        if block_size <= 0:
            raise ValueError("block_size must be a positive integer!")
        self.__block_size = block_size

        self.__experiment_durations = experiment_durations

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def __present_stimulus(self, stimulus: AStimulus) -> None:
        self.__model.present_primer(stimulus.primer)
        self.__view.wait(self.__experiment_durations.primer_secs)
        self.__model.present_stimulus(stimulus)

    def __resting_state(self) -> None:
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(self.__experiment_durations.resting_state_secs)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED_INTRODUCTION)
        self.__view.get_confirmation()
        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(self.__experiment_durations.resting_state_secs)

    def __attention_check(self, stimulus_id: int) -> None:
        self.__model.change_experiment_state(EExperimentState.ATTENTION_CHECK)
        self.__view.wait(self.__experiment_durations.attention_check_secs)
        if self.__view.attention_check():
            self.__model.add_attention_check(stimulus_id)

    def run(self) -> None:
        """Runs the experiment.
        """
        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__resting_state()

        # example
        self.__model.change_experiment_state(EExperimentState.EXAMPLE_INTRODUCTION)
        self.__view.get_confirmation()

        for i, stimulus in enumerate(self.__model.example_stimuli):
            self.__model.change_experiment_state(EExperimentState.EXAMPLE)
            self.__present_stimulus(stimulus)
            self.__attention_check(i)

        # experiment
        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        for i, stimulus in enumerate(self.__model.created_stimuli):
            self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
            self.__present_stimulus(stimulus)
            self.__attention_check(i)

            if (i + 1) % self.__block_size == 0:
                self.__model.change_experiment_state(EExperimentState.BREAK)
                self.__view.show_progress((i + 1) // self.__block_size,
                                          len(self.__model.created_stimuli) // self.__block_size)
                self.__view.wait(self.__experiment_durations.break_secs)
                self.__view.get_confirmation()

        self.__resting_state()

        self.__model.change_experiment_state(EExperimentState.OUTRO)
        self.__view.get_confirmation()
