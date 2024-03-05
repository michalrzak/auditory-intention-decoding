"""
Unfortunately, the psychopy implementation of the parallel port really seems to be the best one out there, hence this
also has to depend on psychopy.

The regular `PyParallel` is in beta and had the last commit 5 years ago.
"""
import time
from typing import Any, Protocol

from psychopy.parallel import ParallelPort

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class IParallelPort(Protocol):
    def setData(self, data: int) -> None:
        ...


class BittiumTriggerSender(AObserver):
    """Can be used to observe the model and send relevant triggers to the data for analysis. Requires a parallel port.

    CAREFUL: This class is blocking whenever an update is received which triggers a trigger to be sent for the seconds
    specified in `trigger_duration_s`

    TODO: This should maybe also be a singleton?
    """

    __parallel_port: IParallelPort
    __trigger_duration_s: float

    def __init__(self, address: int, trigger_duration_s: float = 0.001):
        """Constructs a BittiumTriggerSender object.

        :param address: The address of the parallel port where triggers will be sent
        :param trigger_duration_s: How long the trigger pins are set to high when sending a trigger.
        """
        self.__parallel_port = ParallelPort(address=address)
        self.__trigger_duration_s = trigger_duration_s

    def __send_trigger(self, trigger: ETrigger):
        assert isinstance(trigger.value, int)
        self.__parallel_port.setData(trigger.value)
        time.sleep(self.__trigger_duration_s)
        self.__parallel_port.setData(0)

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            self.__send_trigger(ETrigger.NEW_STIMULUS)
        elif identifier == EModelUpdateIdentifier.NEW_PRIMER:
            self.__send_trigger(ETrigger.NEW_PROMPT)
        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            assert isinstance(data, EExperimentState)
            if data == EExperimentState.EXPERIMENT_INTRODUCTION:
                self.__send_trigger(ETrigger.EXPERIMENT_INTRODUCTION)
            elif data == EExperimentState.RESTING_STATE_EYES_OPEN:
                self.__send_trigger(ETrigger.RESTING_STATE_EYES_OPEN)
            elif data == EExperimentState.RESTING_STATE_EYES_CLOSED:
                self.__send_trigger(ETrigger.RESTING_STATE_EYES_CLOSED)
            elif data == EExperimentState.EXPERIMENT:
                self.__send_trigger(ETrigger.EXPERIMENT)
            elif data == EExperimentState.INACTIVE:
                self.__send_trigger(ETrigger.INACTIVE)
            else:
                assert False
        else:
            assert False
