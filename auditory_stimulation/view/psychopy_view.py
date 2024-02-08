from typing import Protocol

import psychopy
import psychopy.visual
from psychopy.hardware import keyboard

from auditory_stimulation.model.experiment_state import EExperimentState
from auditory_stimulation.model.model_update_identifier import EModelUpdateIdentifier
from auditory_stimulation.view.view import AView


class PsychopyDrawable(Protocol):
    def draw(self) -> None:
        ...


class PsychopyView(AView):

    def __init__(self, window: psychopy.visual.Window):
        self.window = window

    # Overriden methods
    # ---------------------------
    def _update_new_prompt(self, data: str) -> None:
        prompt = self.__create_text_box(data)

        prompt.draw()
        self.window.flip()

    def _update_experiment_state_changed(self, data: EExperimentState) -> None:
        text = self.__create_text_box(str(data))

        text.draw()
        self.window.flip()

    def get_confirmation(self) -> bool:
        kb = keyboard.Keyboard()

        while len(kb.getKeys(["space"])) == 0:
            ...

        return True

    # ---------------------------

    def __create_text_box(self, text: str) -> PsychopyDrawable:
        return psychopy.visual.TextBox2(win=self.window,
                                        text=text,
                                        lineBreaking='uax14',
                                        letterHeight=0.05,
                                        pos=(0, 0),
                                        size=(0.5, 0.5),
                                        color=1.,
                                        colorSpace='rgb',
                                        fillColor=None,
                                        fillColorSpace='rgb',
                                        font='FreeSerif')

    def close_view(self):
        self.window.close()
        # psychopy.core.quit()

    def __del__(self):
        self.close_view()


win = psychopy.visual.Window(
    size=(1024, 768), fullscr=True, screen=0,
    winType='pyglet', allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0, 0, 0], colorSpace='rgb',
    blendMode='avg', useFBO=True,
    units='height')

view = PsychopyView(win)
view.update("test", EModelUpdateIdentifier.NEW_PROMPT)
view.get_confirmation()
view.update(EExperimentState.RESTING_STATE, EModelUpdateIdentifier.NEW_PROMPT)
view.get_confirmation()
