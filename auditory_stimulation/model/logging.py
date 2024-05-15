import logging
import pathlib
import threading
from os import PathLike
from typing import Any

from auditory_stimulation.audio import save_audio_as_wav
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import AStimulus


def _get_repr(data: Any) -> str:
    return repr(data).replace("\n", "\\n")


class Logger(AObserver):
    """ Observer class, used to log the Observed object.

    INSTANTIATING MULTIPLE INSTANCES OF THIS CLASS WILL BREAK THE PREVIOUS LOGGING!
    FIXME: THIS SHOULD NOT HAPPEN
    """

    __counter: int
    __exports_directory: pathlib.Path

    def __init__(self, target_folder: PathLike):
        self.__exports_directory = pathlib.Path(target_folder)
        self.__counter = 0

        logging.basicConfig(filename=str(self.__exports_directory / "logs.log"),
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        data_repr = _get_repr(data)

        if identifier == EModelUpdateIdentifier.NEW_PRIMER:
            logging.info(f"Added new primer {data_repr}")

        elif identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            logging.info(f"Added new stimulus {data_repr}")

            assert isinstance(data, AStimulus)
            stimulus: AStimulus = data

            export_file_name = self.__exports_directory / f"stim_audio_{self.__counter}.wav"
            self.__counter += 1

            # run the audio saving in another thread to not force the application to wait until in exists
            thread = threading.Thread(target=save_audio_as_wav, args=(stimulus.audio, export_file_name))
            thread.start()

            logging.info(f"Exported stimulus audio to: {export_file_name}")

        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            logging.info(f"Changing experiment state to {data_repr}")

        elif identifier == EModelUpdateIdentifier.ATTENTION_CHECK:
            logging.info(f"Attention check action conducted")

        else:
            assert False, f"Unexpected identifier: {identifier}"
