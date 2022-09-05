from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'

PEPS_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent 

PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}

PEP_STATUS = [
    'Active', 
    'Accepted',
    'Deferred',
    'Final',
    'Provisional',
    'Rejected',
    'Superseded',
    'Withdrawn',
    'Draft',
]
