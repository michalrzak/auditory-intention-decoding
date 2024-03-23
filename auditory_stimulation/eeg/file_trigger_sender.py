from os import PathLike

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.eeg.trigger_sender import ATriggerSender


class FileTriggerSender(ATriggerSender):
    """Constructs a FileTriggerSender object, which writes all acquired triggers to a file.

    For further documentation, please refer to the super class (ATriggerSender).
    """
    __target_file: PathLike

    def __init__(self, thread_timeout_secs: float, target_file: PathLike):
        """Constructs a FileTriggerSender object.

        :param target_file: The target file, where the triggers will be written.
        """
        super().__init__(thread_timeout_secs)
        self.__file = open(target_file, "w")

    def __del__(self):
        super().__del__()
        self.__file.close()

    def _send_trigger(self, trigger: ETrigger, timestamp: float) -> None:
        self.__file.write(f"{timestamp},{str(trigger)}\n")