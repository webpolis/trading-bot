from pathlib import Path


def get_project_root() -> str:
    return str(Path(__file__).parent.parent.parent.parent.parent)


def get_data_path() -> str:
    return get_project_root() + '/data/'
