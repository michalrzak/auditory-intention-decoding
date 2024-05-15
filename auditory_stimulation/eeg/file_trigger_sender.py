from os import PathLike
from typing import IO

from auditory_stimulation.eeg.trigger_sender import ATriggerSender


class FileTriggerSender(ATriggerSender):
    """Constructs a FileTriggerSender object, which writes all acquired triggers to a file.

    For further documentation, please refer to the super class (ATriggerSender).
    """
    __file: IO = None

    def __init__(self, thread_timeout_secs: float, target_file: PathLike):
        """Constructs a FileTriggerSender object.

        :param target_file: The target file, where the triggers will be written.
        """
        super().__init__(thread_timeout_secs)
        self.__file = open(target_file, "w")

    def __del__(self):
        super().__del__()
        if self.__file is None:
            # object not properly initialized
            return

        self.__file.close()

    def _send_trigger(self, trigger: int, timestamp: float) -> None:
        self.__file.write(f"{timestamp},{trigger}\n")
