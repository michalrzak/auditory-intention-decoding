"""
Unfortunately, the psychopy implementation of the parallel port really seems to be the best one out there, hence this
also has to depend on psychopy.

The regular `PyParallel` is in beta and had the last commit 5 years ago.
"""
import time
from typing import Protocol

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.eeg.trigger_sender import ATriggerSender


class IParallelPort(Protocol):
    def setData(self, data: int) -> None:
        ...


class BittiumTriggerSender(ATriggerSender):
    """Can be used to observe the model and send relevant triggers to the data for analysis. Requires a parallel port.

    For further documentation, please refer to the super class (ATriggerSender).
    """

    __parallel_port: IParallelPort
    __trigger_duration_s: float

    def __init__(self, thread_timeout_secs: float, parallel_port: IParallelPort, trigger_duration_s: float) -> None:
        """Constructs a BittiumTriggerSender object.
        You should always use `get_bittium_trigger_sender(...)` to initialize this class and never the constructor!

        :param parallel_port: An object allowing to setData to a parallel port
        :param trigger_duration_s: How long the trigger pins are set to high when sending a trigger.
        """
        super().__init__(thread_timeout_secs)
        self.__parallel_port = parallel_port
        self.__trigger_duration_s = trigger_duration_s

    def _send_trigger(self, trigger: ETrigger, timestamp: float) -> None:
        assert isinstance(trigger.value, int)
        self.__parallel_port.setData(trigger.value)
        time.sleep(self.__trigger_duration_s)
        self.__parallel_port.setData(0)
        time.sleep(self.__trigger_duration_s)


TRIGGER_DURATION_S = 0.001
