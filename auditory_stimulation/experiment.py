from typing import List

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.stimulus import Stimulus
from auditory_stimulation.view.view import AView

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5


class Experiment:
    __model: Model
    __view: AView
    __stimuli: List[Stimulus]

    def __init__(self, model: Model, view: AView, stimuli: List[Stimulus]) -> None:
        self.__model = model
        self.__view = view
        self.__stimuli = stimuli  # TODO: need to actually create the stimulus somewhere

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
        for stimulus in self.__stimuli:
            self.__model.new_primer(stimulus.primer)
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.new_stimulus(stimulus)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)
