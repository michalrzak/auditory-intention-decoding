from typing import Callable, Protocol, Dict, Optional, Tuple, List

import psychopy
import psychopy.visual
from psychopy.hardware import keyboard

from auditory_stimulation.auditory_tagging.auditory_tagger import Audio
from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.stimulus import CreatedStimulus
from auditory_stimulation.view.view import AView

LETTER_SIZE = 0.05
TEXT_BOX_COLOR = 1.
TEXT_BOX_COLOR_SPACE = 'rgb'

EXPERIMENT_STATE_TEXT_BOX_POSITION = (0, 0)
EXPERIMENT_STATE_TEXT_BOX_SIZE = (0.8, 0.5)

CONFIRMATION_TEXT = "Please press 'space' to continue"
CONFIRMATION_TEXT_BOX_POSITION = (0, -0.8)


class Drawable(Protocol):
    def draw(self) -> None:
        ...


class PsychopyView(AView):
    """A view, implementing the psychopy frontend.
    """
    __window: psychopy.visual.Window
    __keyboard: psychopy.hardware.keyboard.Keyboard
    __draw_buffer: List[Drawable]

    def __init__(self,
                 sound_player: Callable[[Audio], None],
                 experiment_texts: Dict[EExperimentState, Optional[str]],
                 window: psychopy.visual.Window) -> None:
        """Constructs a PsychopyView object

        :param sound_player: The sound player to be used by the view.
        :param experiment_texts: Dictionary, containing the displayed experiment texts.
        :param window: The psychopy window to be used to display the elements.
        """
        super().__init__(sound_player, experiment_texts)
        self.__window = window
        self.__keyboard = keyboard.Keyboard()
        self.__draw_buffer = []

    def __try_to_quit(self) -> None:
        if len(self.__keyboard.getKeys(["escape"])) != 0:
            self.close_view()

    def __draw(self, item: Drawable, clear_buffer: bool):
        if clear_buffer:
            self.__draw_buffer = []

        self.__draw_buffer.append(item)

        for buffered_item in self.__draw_buffer:
            buffered_item.draw()

        self.__window.flip()

    def _update_new_stimulus(self, stimulus: CreatedStimulus) -> None:
        self.__try_to_quit()

        prompt = self.__create_text_box(stimulus.prompt, EXPERIMENT_STATE_TEXT_BOX_POSITION,
                                        EXPERIMENT_STATE_TEXT_BOX_SIZE[0], EXPERIMENT_STATE_TEXT_BOX_SIZE[1])
        self.__draw(prompt, True)

        self._sound_player(stimulus.modified_audio)

    def _update_new_primer(self, primer: str) -> None:
        self.__try_to_quit()

        prompt = self.__create_text_box(primer, EXPERIMENT_STATE_TEXT_BOX_POSITION,
                                        EXPERIMENT_STATE_TEXT_BOX_SIZE[0], EXPERIMENT_STATE_TEXT_BOX_SIZE[1])
        self.__draw(prompt, True)

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        self.__try_to_quit()

        # if the data was not provided, skip showing anything
        assert data in self._experiment_texts
        if data not in self._experiment_texts or self._experiment_texts[data] is None:
            return

        text = self.__create_text_box(self._experiment_texts[data], EXPERIMENT_STATE_TEXT_BOX_POSITION,
                                      EXPERIMENT_STATE_TEXT_BOX_SIZE[0], EXPERIMENT_STATE_TEXT_BOX_SIZE[1])
        self.__draw(text, True)

    def get_confirmation(self) -> bool:
        self.__try_to_quit()

        text = self.__create_text_box(CONFIRMATION_TEXT, CONFIRMATION_TEXT_BOX_POSITION)
        self.__draw(text, False)

        self.__keyboard.clearEvents()  # clear keys in case the key was already pressed before
        while len(self.__keyboard.getKeys(["space"])) == 0:
            ...

        return True

    def wait(self, secs: int) -> None:
        self.__try_to_quit()

        psychopy.core.wait(secs)

    def __create_text_box(self,
                          text: str,
                          position: Tuple[float, float],
                          width: Optional[float] = None,
                          height: Optional[float] = None) -> Drawable:
        """Creates a drawable TextBox2 stimulus at the specified location and of the specified size.
        Keep in mind that psychopy sets the (0, 0) location to the center of the screen. This function further uses
        normalized units, hence your screen edges are located 1 and -1 each in both dimensions.

        :param text: The drawn text inside the stimulus
        :param position: The relative position on the screen.
        :param width: The width of the created stimulus, if left empty the width is set to a default value by psychopy
         and grows dynamically, with longer text. If specified, fixes a width for the TextBox
        :param height: Same as width, if left empty the height grows dynamically with longer text, otherwise fix a
         height.
        :return: A drawable textbox.
        """

        size = (width, height)

        text_box = psychopy.visual.TextBox2(win=self.__window,
                                            text=text,
                                            letterHeight=LETTER_SIZE,
                                            alignment="center",
                                            pos=position,
                                            size=size,
                                            color=1.,
                                            colorSpace=TEXT_BOX_COLOR_SPACE)

        return text_box

    def close_view(self):
        """Closes the view properly."""
        self.__window.close()

    def __del__(self):
        self.close_view()
