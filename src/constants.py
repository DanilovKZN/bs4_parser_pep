from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'

PEPS_URL = 'https://peps.python.org/'

BASE_DIR = Path(__file__).parent

PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'parser.log'

RESULTS_DIR = BASE_DIR / 'results'

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
