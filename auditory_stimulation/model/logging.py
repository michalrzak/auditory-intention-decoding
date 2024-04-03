import logging
import pathlib
import threading
from os import PathLike
from typing import Any, Set

from auditory_stimulation.audio import save_audio_as_wav
from auditory_stimulation.model.model import AObserver
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.model.stimulus import CreatedStimulus


class Logger(AObserver):
    """ Observer class, used to log the Observed object.

    INSTANTIATING MULTIPLE INSTANCES OF THIS CLASS WILL BREAK THE PREVIOUS LOGGING!
    FIXME: THIS SHOULD NOT HAPPEN
    """

    __exported_stimuli: Set[CreatedStimulus] = set()
    __exports_directory: pathlib.Path

    def __init__(self, target_folder: PathLike):
        self.__exports_directory = pathlib.Path(target_folder)

        logging.basicConfig(filename=str(self.__exports_directory / "logs.log"),
                            filemode='w',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    def update(self, data: Any, identifier: EModelUpdateIdentifier) -> None:
        if identifier == EModelUpdateIdentifier.NEW_PRIMER:
            logging.info(f"Added new primer {data}")

        elif identifier == EModelUpdateIdentifier.NEW_STIMULUS:
            logging.info(f"Added new stimulus {data}")

            assert isinstance(data, CreatedStimulus)
            stimulus: CreatedStimulus = data

            if stimulus not in self.__exported_stimuli:
                export_file_name = self.__exports_directory / f"stim_audio_{len(self.__exported_stimuli)}.wav"

                # run the audio saving in another thread to not force the application to wait until in exists
                thread = threading.Thread(target=save_audio_as_wav, args=(stimulus.modified_audio, export_file_name))
                thread.start()

                self.__exported_stimuli.add(stimulus)
                logging.info(f"Exported stimulus audio to: {export_file_name}")

        elif identifier == EModelUpdateIdentifier.EXPERIMENT_STATE_CHANGED:
            logging.info(f"Changing experiment state to {data}")

        else:
            assert False, f"Unexpected identifier: {identifier}"
