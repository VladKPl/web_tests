"""One metrics file pair per test, safe across xdist workers."""
import csv
import json
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from time import perf_counter
import allure
from src.config.settings import METRICS_DIR


class Metrics:
    def __init__(self, test_name, browser, artifact_id):
        self.test_name, self.browser, self.artifact_id = test_name, browser, artifact_id
        self.rows = []

    @contextmanager
    def measure(self, operation):
        start = perf_counter()
        status = 'failed'
        try:
            yield
            status = 'passed'
        finally:
            self.rows.append(dict(timestamp=datetime.now(timezone.utc).isoformat(),
                test_name=self.test_name, browser=self.browser, operation=operation,
                elapsed_ms=round((perf_counter()-start)*1000, 3), status=status,
                worker_id=os.getenv('PYTEST_XDIST_WORKER', 'main')))

    def save(self):
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        data = json.dumps(self.rows, ensure_ascii=False, indent=2)
        (METRICS_DIR / (self.artifact_id + '.json')).write_text(data, encoding='utf-8')
        if self.rows:
            with (METRICS_DIR / (self.artifact_id + '.csv')).open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.rows[0])
                writer.writeheader()
                writer.writerows(self.rows)
        allure.attach(data, 'Operation timings', allure.attachment_type.JSON)
