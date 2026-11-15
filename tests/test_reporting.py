"""Exercise actual pytest/Allure failure serialization in an isolated process."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def test_credentials_redacted_in_failure_reports():
    root = Path(__file__).resolve().parents[1]
    (root / 'reports').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='redaction-', dir=root / 'reports') as directory:
        folder = Path(directory)
        probe = folder / 'test_probe.py'
        probe.write_text('''
import os
import pytest
import logging
from src.secrets import VALUES
SECRET = os.environ['REPORT_PROBE_SECRET']
VALUES.add(SECRET)
@pytest.fixture
def setup_error():
    raise RuntimeError(SECRET)
@pytest.fixture
def teardown_error():
    yield
    raise RuntimeError(SECRET)
def test_setup(setup_error): pass
def test_call():
    logging.error('Credential: %s', SECRET)
    raise RuntimeError(SECRET)
def test_teardown(teardown_error): pass
''', encoding='utf-8')
        secret = 'ProbeCredential-7a31c5e8'
        result = subprocess.run([sys.executable, '-m', 'pytest', str(probe),
            '--alluredir=' + str(folder / 'allure'), '--tb=long', '-q'],
            cwd=root, env={**os.environ, 'REPORT_PROBE_SECRET': secret},
            capture_output=True, timeout=60)
        assert result.returncode == 1
        assert secret.encode() not in result.stdout + result.stderr
        files = list((folder / 'allure').glob('*.json'))
        assert files
        for path in files:
            assert secret.encode() not in path.read_bytes(), path.name
