# About
This project was developed as part of my [master thesis](TODO) - Title. The thesis aims to investigate and lay the groundwork for a potential future brain-computer interface (BCI) paradigm, where a system could decode an attended stimulus given sequentially presented auditory stimuli.
The code in this repository contains all the necessary files to reproduce and re-run the experiment.

## Abstract
...

# Installation
The repository uses Poetry as its dependency management system. The code should work on Windows, Linux, and MacOS, however, Linux and MacOS may require additional steps. `Python 3.8` is used as it is the recommended distribution for `Psychopy`.

To install Poetry follow the instructions at <https://python-poetry.org/docs/#installation>.
Once installed, navigate to the root of the repository and run:
```
poetry install
```
This should automatically create a virtual environment of the required Python version and install all dependencies.

**Note 1:** The project requires a `Python 3.8` installation on your system.
**Note 2:** I prefer to have my virtual environment saved in the repository folder, which is not the default behavior of Poetry. To change this, follow the instructions on the following page: <https://python-poetry.org/docs/configuration/#virtualenvsin-project>

## Linux:

### wxPython
Unfortunately, `Psychopy`, a project dependency, requires `wxPython`, which is relatively annoying to install on Linux, as pre-build Linux wheels are **not** provided in `PyPi`. This means that running `poetry install` will most likely fail, as there probably will be some build dependencies missing.

#### Building wxPython:
One solution is to build `wxPython` yourself. For this install all [required build-dependencies](https://wxpython.org/blog/2017-08-17-builds-for-linux-with-pip/index.html) (different for each distro) and then run 
```
poetry install
```

#### Prebuilt wheels:
If you are using a popular distro, chances are `wxPython` provides pre-built wheels for it which can be used instead of the `PyPi` wheels. For this check whether <https://extras.wxpython.org/wxPython4/extras/linux/gtk3/> contains your distro. If yes you can run the following commands from the root of the repository to install `wxPython`:
```
source .venv/bin/activate

pip install -U \
    -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/<your-distro> \
    wxPython

deactivate

poetry install
```
**Note:** This requires that your virtual environment folder is located inside of the repository. If it isn't, navigate to its location and activate the environment there, before navigating to the root of the repository. 

**TODO: test if this actually works**

### Psychopy
After successfully installing all dependencies, you have to allow psyhopy access to the keyboard, to properly run the experiment. You can do this via the following commands on any Linux distribution using `system.d`:
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

## MacOS
MacOS is technically untested, but running this repository should be largely without problems. Note, however, that you cannot use the `BittiumNeurOneTrigger`, as this class requires a parallel port interface, which isn't present on any Macs.

# Launching
To launch the script execute:
```
poetry run python -m auditory_stimulation.main
```
## Running in Pycharm
If you want to run the script using Pycharm make sure to set the working directory to the root of the repository and not to the root of the code `.../auditory-stimulation` vs. `.../auditory-stimulation/audiory_stimulation`.

# Usage
TODO: extend when I make some introduction stuff

## Quitting the application:
The application either quits automatically once the experiment is over, or you can force the application to quit by pressing `ESC` at any time during the experiment.

**Note:** Pressing `ESC` quits the application after the current stimulus is finished presenting, so be a little patient.


