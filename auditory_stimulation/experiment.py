import copy
import random
from typing import List, Optional

from auditory_stimulation.auditory_stimulus.auditory_stimulus import AAuditoryStimulusFactory
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import Model
from auditory_stimulation.stimulus import Stimulus, CreatedStimulus
from auditory_stimulation.view.view import AView

STIMULUS_REPEAT = 5

RESTING_STATE_SECS = 5
PRIMER_SECS = 5


class Experiment:
    __model: Model
    __view: AView
    __stimuli: List[Stimulus]
    __auditory_stimulus_factories: List[AAuditoryStimulusFactory]
    __created_stimuli: Optional[List[CreatedStimulus]]

    def __init__(self, model: Model, view: AView, stimuli: List[Stimulus],
                 auditory_stimulus_factories: List[AAuditoryStimulusFactory]) -> None:
        self.__model = model
        self.__view = view
        self.__stimuli = stimuli

        if len(auditory_stimulus_factories) == 0:
            raise ValueError("At least one auditory stimulus factory needs to be supplied!")
        if len(stimuli) % len(auditory_stimulus_factories) != 0:
            # this can potentially be changed if I e.g. change it to replay the stimuli for each stimulus
            raise ValueError("The amount of factories must fully divide the amount of stimuli,"
                             " to avoid having one stimulus type less!")
        self.__auditory_stimulus_factories = copy.copy(auditory_stimulus_factories)

        self.__created_stimuli = None

        assert self.__model.experiment_state == EExperimentState.INACTIVE

    def create_stimuli(self) -> None:
        if self.__created_stimuli is not None:
            raise RuntimeError("You can only call create_stimuli() once!")

        assert len(self.__stimuli) % len(self.__auditory_stimulus_factories) == 0

        repeats = len(self.__stimuli) // len(self.__auditory_stimulus_factories)

        applied_factories = []
        for factory in self.__auditory_stimulus_factories:
            applied_factories += [factory] * repeats

        random.shuffle(applied_factories)

        created_stimuli = []
        for factory, stimulus in zip(applied_factories, self.__stimuli):
            auditory_stimulus = factory.create_auditory_stimulus(stimulus.audio, stimulus.time_stamps, )
            auditory_stimulus.create()
            modified_audio = auditory_stimulus.modified_audio
            created_stimuli.append(CreatedStimulus.from_stimulus(stimulus, modified_audio))

        self.__created_stimuli = created_stimuli

    def run(self) -> None:
        if self.__created_stimuli is None:
            raise RuntimeError("Need to run create_stimuli() first!")

        self.__model.change_experiment_state(EExperimentState.INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT_INTRODUCTION)
        self.__view.get_confirmation()

        self.__model.change_experiment_state(EExperimentState.EXPERIMENT)
        for stimulus in self.__created_stimuli:
            self.__model.new_primer(stimulus.primer)
            self.__view.wait(PRIMER_SECS)

            for i in range(STIMULUS_REPEAT):
                self.__model.new_stimulus(stimulus)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_OPEN)
        self.__view.wait(RESTING_STATE_SECS)

        self.__model.change_experiment_state(EExperimentState.RESTING_STATE_EYES_CLOSED)
        self.__view.wait(RESTING_STATE_SECS)
