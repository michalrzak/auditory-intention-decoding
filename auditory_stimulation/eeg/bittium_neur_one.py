"""
Unfortunately, the psychopy implementation of the parallel port really seems to be the best one out there, hence this
also has to depend on psychopy.

The regular `PyParallel` is in beta and had the last commit 5 years ago.
"""
import time
from typing import Any, Protocol, Dict

from psychopy.parallel import ParallelPort

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier


class IParallelPort(Protocol):
    def setData(self, data: int) -> None:
        ...


class BittiumTriggerSender(AObserver):
    """Can be used to observe the model and send relevant triggers to the data for analysis. Requires a parallel port.

    CAREFUL: This class is blocking whenever an update is received which triggers a trigger to be sent for the seconds
    specified in `trigger_duration_s`

    You should always use `getBittiumTriggerSender(...)` to initialize this class and never the constructor!
    """

    __parallel_port: IParallelPort
    __trigger_duration_s: float

    def __init__(self, parallel_port: IParallelPort, trigger_duration_s: float) -> None:
        """Constructs a BittiumTriggerSender object.
        You should always use `getBittiumTriggerSender(...)` to initialize this class and never the constructor!

        :param parallel_port: An object allowing to setData to a parallel port
        :param trigger_duration_s: How long the trigger pins are set to high when sending a trigger.
        """
        self.__parallel_port = parallel_port
        self.__trigger_duration_s = trigger_duration_s

    def __send_trigger(self, trigger: ETrigger) -> None:
        assert isinstance(trigger.value, int)
        self.__parallel_port.setData(trigger.value)
        time.sleep(self.__trigger_duration_s)
        self.__parallel_port.setData(0)

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        self.__send_trigger(ETrigger.get_trigger(data, identifier))


__trigger_sender_cache: Dict[int, BittiumTriggerSender] = {}
TRIGGER_DURATION_S = 0.001


def get_bittium_trigger_sender(address: int) -> BittiumTriggerSender:
    """Gets an instance of the BittiumTriggerSender. Each address is treated as a singleton (if this function is called
    twice, with the same address, the same object is returned. This is to avoid having two object which can write onto
    the same address of the parallel port).

    :param address: The address of the parallel port where triggers will be sent
    :return: A BittiumTriggerSender instance
    """
    if address not in __trigger_sender_cache:
        parallel_port = ParallelPort(address=address)
        __trigger_sender_cache[address] = BittiumTriggerSender(parallel_port, TRIGGER_DURATION_S)

    return __trigger_sender_cache[address]
