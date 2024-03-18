import mockito
import pytest
import yaml

from auditory_stimulation.audio import Audio
from auditory_stimulation.auditory_tagging.auditory_tagger import AAudioTagger
from auditory_stimulation.model.stimulus import Stimulus, CreatedStimulus, load_stimuli, generate_stimulus
from tests.auditory_tagging.stimulus_test_helpers import get_mock_audio


def get_stimulus_parameters():
    audio = mockito.mock(Audio)
    prompt = "sample string"
    primer = "sample primer"
    options = ["option1", "option2"]
    time_stamps = [(1.0, 2.0), (2.5, 3.0)]
    target = 1

    return audio, prompt, primer, options, time_stamps, target


def get_generate_stimulus_parameters(intro_length: int, option_length: int, fs: int, n_options: int):
    intro_audio = get_mock_audio(intro_length, fs)
    intro_text = "intro"
    option_audios = [get_mock_audio(option_length, fs) for _ in range(n_options)]
    option_texts = [f"option-{i}" for i in range(n_options)]
    target = 0
    pause_secs = 0.5

    return intro_audio, intro_text, option_audios, option_texts, target, pause_secs


def stimulus_checks(stimulus, audio, prompt, primer, options, time_stamps, target):
    assert stimulus.audio == audio
    assert stimulus.prompt == prompt
    assert stimulus.primer == primer
    assert all([opt1 == opt2 for opt1, opt2 in zip(stimulus.options, options)])
    assert all([ts1[0] == ts2[0] and ts1[1] == ts2[1] for ts1, ts2 in zip(stimulus.time_stamps, time_stamps)])
    assert stimulus.target == target


def create_yaml(contents, file):
    with open(file, "w") as f:
        yaml.safe_dump(contents, f)


def create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path):
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        "options": options,
        "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)
    return file


def test_stimulus_valid_call():
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    stimulus = Stimulus(audio, prompt, primer, options, time_stamps, target)
    stimulus_checks(stimulus, audio, prompt, primer, options, time_stamps, target)


def test_created_stimulus_from_stimulus_valid_call():
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    stimulus = Stimulus(audio, prompt, primer, options, time_stamps, target)

    modified_audio = mockito.mock(Audio)
    tagger = mockito.mock(AAudioTagger)
    created_stimulus = CreatedStimulus(stimulus, modified_audio, tagger)

    stimulus_checks(created_stimulus, stimulus.audio, stimulus.prompt, stimulus.primer, stimulus.options,
                    stimulus.time_stamps, target)
    assert created_stimulus.modified_audio == modified_audio


def test_load_stimuli_valid_call(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    stimuli = load_stimuli(file)

    assert len(stimuli) == 1
    assert stimuli[0].prompt == prompt
    assert stimuli[0].primer == primer
    assert all([opt1 == opt2 for opt1, opt2 in zip(stimuli[0].options, options)])
    assert all([ts1 == ts2 for ts1, ts2 in zip(stimuli[0].time_stamps, time_stamps)])
    assert stimuli[0].target == target


def test_load_stimuli_2_options_1_time_stamp_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    # only take first time_stamp
    time_stamps = time_stamps[:1]
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_1_options_2_time_stamp_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    # only take first option
    options = options[:-1]
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_file_none_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": None,
        "prompt": prompt,
        "primer": primer,
        "options": options,
        "time-stamps": time_stamps
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)
    prompt = None
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_prompt_none_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    prompt = None
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_primer_none_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    primer = None
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_options_and_time_stamps_none_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    options = None
    time_stamps = None
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_file_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        # "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        "options": options,
        "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_prompt_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        # "prompt": prompt,
        "primer": primer,
        "options": options,
        "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_primer_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        # "primer": primer,
        "options": options,
        "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_options_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        # "options": options,
        "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_time_stamp_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        "options": options,
        # "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_options_and_time_stamp_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        # "options": options,
        # "time-stamps": time_stamps,
        "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


def test_load_stimuli_options_and_target_missing_should_fail(tmp_path):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    contents = {"test": {
        "file": "stimuli_sounds/legacy/test.wav",  # unfortunately cannot use a temporary audio here
        "prompt": prompt,
        "primer": primer,
        "options": options,
        "time-stamps": time_stamps,
        # "target": target
    }}
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


@pytest.mark.parametrize("new_time_stamp", [[1, 1], [(0, 1, 2), (0, 1, 2)]])
def test_load_stimuli_time_stamps_invalid_format_should_fail(tmp_path, new_time_stamp):
    audio, prompt, primer, options, time_stamps, target = get_stimulus_parameters()
    time_stamps = [1, 1]
    file = create_test_stimulus_file(prompt, primer, options, time_stamps, target, tmp_path)

    with pytest.raises(Exception):
        stimuli = load_stimuli(file)


@pytest.mark.parametrize("n_options", [1, 2, 3, 4, 10])
def test_generate_stimulus_valid_call(n_options: int):
    intro_length = 1000
    option_length = 200
    fs = 100

    intro_audio, intro_text, option_audios, option_texts, target, pause_secs = \
        get_generate_stimulus_parameters(intro_length, option_length, fs, n_options)

    stimulus = generate_stimulus(intro_audio, intro_text, option_audios, option_texts, target, pause_secs)

    assert stimulus.audio.secs == (intro_length / fs) + (option_length / fs) * n_options + (n_options - 1) * pause_secs
    assert intro_text in stimulus.prompt
    assert option_texts[target] in stimulus.primer
    assert stimulus.target == target
    assert len(stimulus.options) == len(option_texts)


@pytest.mark.parametrize("target", [-10, -1, 2, 3, 4])
def test_generate_stimulus_invalid_target_should_fail(target: int):
    intro_length = 1000
    option_length = 200
    fs = 100

    intro_audio, intro_text, option_audios, option_texts, _, pause_secs = \
        get_generate_stimulus_parameters(intro_length, option_length, fs, 2)

    with pytest.raises(ValueError):
        stimulus = generate_stimulus(intro_audio, intro_text, option_audios, option_texts, target, pause_secs)


@pytest.mark.parametrize("pause_secs", [-1000, -10, -1, -0.1, -0.0001])
def test_generate_stimulus_invalid_pause_secs_should_fail(pause_secs: float):
    intro_length = 1000
    option_length = 200
    fs = 100

    intro_audio, intro_text, option_audios, option_texts, target, _ = \
        get_generate_stimulus_parameters(intro_length, option_length, fs, 2)

    with pytest.raises(ValueError):
        stimulus = generate_stimulus(intro_audio, intro_text, option_audios, option_texts, target, pause_secs)
