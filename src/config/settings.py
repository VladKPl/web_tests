"""Project defaults; CLI overrides environment values."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / '.env')
BASE_URL = os.getenv('BASE_URL', 'https://automationexercise.com')
SELENIUM_GRID_URL = os.getenv('SELENIUM_GRID_URL', 'http://localhost:4444')
BROWSER = os.getenv('BROWSER', 'chrome')
REMOTE_MODE = os.getenv('REMOTE_MODE', 'true').lower() == 'true'
TIMEOUT = float(os.getenv('TIMEOUT', '20'))
IMPLICIT_WAIT = 0
METRICS_DIR = ROOT / os.getenv('METRICS_DIR', 'reports/metrics')
LOGS_DIR = ROOT / os.getenv('LOGS_DIR', 'reports/logs')
SCREENSHOTS_DIR = ROOT / os.getenv('SCREENSHOTS_DIR', 'reports/screenshots')
