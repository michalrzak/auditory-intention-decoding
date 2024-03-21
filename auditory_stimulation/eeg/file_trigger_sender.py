from datetime import datetime
from os import PathLike

from auditory_stimulation.eeg.common import ETrigger
from auditory_stimulation.eeg.trigger_sender import ATriggerSender


class FileTriggerSender(ATriggerSender):
    """Constructs a FileTriggerSender object, which writes all acquired triggers to a file.

    The structure of this object is relatively complicated, as to make it non-blocking, the file operations are executed
    on separate threads. This requires locking/unlocking the written file.

    The class works by enqueuing timestamps + triggers and opening write_file workers, where each pops an item from the
    queue and writes it to the file. This should ensure that the triggers are always in correct order in the file.
    """
    __target_file: PathLike

    def __init__(self, thread_timout: int, target_file: PathLike):
        """Constructs a FileTriggerSender object.

        :param target_file: The target file, where the triggers will be written.
        """
        super().__init__(thread_timout)
        self.__file = open(target_file, "w")

    def __del__(self):
        super().__del__()
        self.__file.close()

    def _send_trigger(self, trigger: ETrigger) -> None:
        self.__file.write(f"{datetime.timestamp(datetime.today()) * 1000}: {str(trigger)}\n")
