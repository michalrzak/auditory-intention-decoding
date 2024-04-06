import yaml

from auditory_stimulation.configuration import get_configuration_yaml


def create_yaml(contents, file):
    with open(file, "w") as f:
        yaml.safe_dump(contents, f)


def create_test_configuration_file(tmp_path,
                                   subject_id,
                                   logging_directory_path,
                                   trigger_directory_path,
                                   n_stimuli,
                                   pause_secs,
                                   stimuli_numbers_interval,
                                   intros_transcription_path,
                                   voices_folders,
                                   repetitions,
                                   resting_state_secs,
                                   primer_secs,
                                   break_secs,
                                   experiment_texts_file_path):
    contents = {"subject_id": subject_id,
                "logging_directory_path": logging_directory_path,
                "trigger_directory_path": trigger_directory_path,
                "n_stimuli": n_stimuli,
                "pause_secs": pause_secs,
                "stimuli_numbers_interval": stimuli_numbers_interval,
                "intros_transcription_path": intros_transcription_path,
                "voices_folders": voices_folders,
                "repetitions": repetitions,
                "resting_state_secs": resting_state_secs,
                "primer_secs": primer_secs,
                "break_secs": break_secs,
                "experiment_texts_file_path": experiment_texts_file_path
                }
    file = tmp_path / "test.yaml"
    create_yaml(contents, file)
    return file


def test_get_configuration_yaml_valid_call(tmp_path):
    subject_id = 1
    logging_directory_path = "some_logging_path"
    trigger_directory_path = "some_trigger_path"
    n_stimuli = 3
    pause_secs = 1
    stimuli_numbers_interval = (10, 100)
    intros_transcription_path = "some_transcription_path"
    voices_folders = ("voice1_path", "voice2_path")
    repetitions = 1
    resting_state_secs = 1
    primer_secs = 1
    break_secs = 1
    experiment_texts_file_path = "some_texts_path"

    file = create_test_configuration_file(tmp_path,
                                          subject_id,
                                          logging_directory_path,
                                          trigger_directory_path,
                                          n_stimuli,
                                          pause_secs,
                                          stimuli_numbers_interval,
                                          intros_transcription_path,
                                          voices_folders,
                                          repetitions,
                                          resting_state_secs,
                                          primer_secs,
                                          break_secs,
                                          experiment_texts_file_path)

    config = get_configuration_yaml(file)

    assert config.subject_id == subject_id
    assert str(config.logging_directory_path) == logging_directory_path
    assert str(config.trigger_directory_path) == trigger_directory_path
    assert config.n_stimuli == n_stimuli
    assert config.pause_secs == pause_secs
    assert all(lop == rop for lop, rop in zip(config.stimuli_numbers_interval, stimuli_numbers_interval))
    assert str(config.intros_transcription_path) == intros_transcription_path
    assert all(str(lop) == rop for lop, rop in zip(config.voices_folders, voices_folders))
    assert config.repetitions == repetitions
    assert config.resting_state_secs == resting_state_secs
    assert config.primer_secs == primer_secs
    assert config.break_secs == break_secs
    assert str(config.experiment_texts_file_path) == experiment_texts_file_path
