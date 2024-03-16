# About

This project was developed as part of my [master thesis](TODO) - Title. The thesis aims to investigate and lay the
groundwork for a potential future brain-computer interface (BCI) paradigm, where a system could decode an attended
stimulus given sequentially presented auditory stimuli.
The code in this repository contains all the necessary files to reproduce and re-run the experiment.

## Abstract

...

# Installation

The repository uses Poetry as its dependency management system. The code should work on Windows, Linux, and MacOS,
however, Linux and macOS may require additional steps. `Python 3.8` is used as it is the recommended distribution
for `Psychopy`.

To install Poetry follow the instructions at <https://python-poetry.org/docs/#installation>.
Once installed, navigate to the root of the repository and run:

```
poetry install
```

This should automatically create a virtual environment of the required Python version and install all dependencies.

**Note 1:** The project requires a `Python 3.8` installation on your system.

**Note 2:** I prefer to have my virtual environment saved in the repository folder, which is not the default behavior of
Poetry. To change this, follow the instructions outlined
in: <https://python-poetry.org/docs/configuration/#virtualenvsin-project>
---
This project further requires a lot of sound files, which would be too large to include in GitHub. Hence, please
**download the required sound files** from:
<https://www.dropbox.com/scl/fo/ho3jkefzlyecmx5554b2t/h?rlkey=xg5qemxm9e57bsmqot4owovv8&dl=0>
and extract them to the `stimumli_sounds` folder. After extracting the files, the resulting folder structure should look
like this:

```
stimuli_sounds
├── eric
│   ├── ...
│   └── ...
├── legacy
│   ├── ...
│   └── ...
├── natasha
│   ├── ...
│   └── ...
└── intro-transcriptions.yaml
```

## Linux:

### wxPython

Unfortunately, `Psychopy` requires `wxPython`, which is relatively annoying to install on Linux as pre-build Linux
wheels are **not** provided in `PyPi`. This means that running `poetry install` will most likely fail, as there probably
will be some build dependencies missing.

#### Building wxPython:

One solution is to build `wxPython` yourself. For this install
all [required build-dependencies](https://wxpython.org/blog/2017-08-17-builds-for-linux-with-pip/index.html) (different
for each distro) and then run

```
poetry install
```

#### Prebuilt wheels:

If you are using a popular distro, chances are `wxPython` provides pre-built wheels for it which can be used instead of
the `PyPi` wheels. For this check whether <https://extras.wxpython.org/wxPython4/extras/linux/gtk3/> contains your
distro. If yes, you can run the following commands from the root of the repository to install `wxPython`:

```
source .venv/bin/activate

pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/<your-distro> \
    wxPython

deactivate

poetry install
```

**Note:** This requires that your virtual environment folder is located inside the repository. If it isn't, navigate
to its location and activate the environment there, before navigating to the root of the repository.

**TODO: test if this actually works**

### Psychopy

After successfully installing all dependencies, you have to allow Psychopy access to the keyboard, to be able to run the
experiment. You can do this via the following commands on any Linux distribution using `system.d`:

```
sudo groupadd --force psychopy
sudo usermod -a -G psychopy $USER

sudo vim /etc/security/limits.d/99-psychopylimits.conf and copy/paste in the following text to that file:
```

And paste the following into the opened file:

```
@psychopy   -  nice       -20
@psychopy   -  rtprio     50
@psychopy   -  memlock    unlimited
```

After saving the file, restart the computer

## macOS

macOS is technically untested, but running this repository should be largely without problems. Note, however, that you
cannot use the `BittiumNeurOneTrigger`, as this class requires a parallel port interface, which isn't present on any
Macs.

# Launching

To launch the script execute:

```
poetry run python -m auditory_stimulation.main
```

## Running in Pycharm

If you want to run the script using Pycharm make sure to set the working directory to the root of the repository and not
to the root of the code `.../auditory-stimulation` vs. `.../auditory-stimulation/audiory_stimulation`.

# Usage

TODO: extend when I make some introduction stuff

## Quitting the application:

The application either quits automatically once the experiment is over, or you can force the application to quit by
pressing `ESC` at any time during the experiment.

**Note:** Pressing `ESC` quits the application after the current stimulus is finished presenting, so be a little
patient.

# Adding stimuli:

To add new stimuli or change the existing stimuli simply edit the file [stimuli.yaml](auditory_stimulation/stimuli.yaml)
. For the structure of the file, best look at the existing entries. A formal definition is outlined below:

```yaml
<name of stimulus>:
  file: <path to wav file>
  prompt: <text, containing the transcription of the wav file>
  primer: <Text which is shown before the stimulus is played, priming the subject for one of the options>
  options:
    - <option A>
    - <option B>
    - <option C>
    - <etc.>
  time-stamps:
    - [ <left A>, <right A> ]
    - [ <left B>, <right B> ]
    - [ <left C>, <right C> ]
    - [ <left etc.>, <right etc.> ]
```

Note that even though you can specify an arbitrary amount of options and time-stamps, the amount of options must match
the amount of time-stamps.

The time-stamps highlight when the given option was said inside of the wav file and are used to apply a tagger to that
portion of the audio.

# Changing the shown experiment text

The text shown during the experiment is defined inside
of [experiment_texts.yaml](auditory_stimulation/experiment_texts.yaml). It defines what text is shown for each entry
of [EExperimentState](auditory_stimulation/model/experiment_state.py). The order of the shown `EExperimentState` is
defined inside the [Experiment](auditory_stimulation/experiment.py). Leaving the option empty indicates that
no-update should happen when this option is presented.

```yaml
inactive: <text or empty>
introduction: <text or empty>
resting-state-eyes-open: <text or empty>
resting-state-eyes-closed: <text or empty>
experiment-introduction: <text or empty>
experiment: <text or empty>
break: <text or empty>
```

# Changing the experiment flow

To change the experiment flow, edit [Experiment](auditory_stimulation/experiment.py). This class acts as
the `Controller` of the `MVC` pattern and guards when what happens during the experiment. Note that updates to the model
are propagated to the view using the Observer pattern, hence it is not necessary to update the view manually from
the `Experiment`
