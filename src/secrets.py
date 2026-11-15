"""Redact registered test credentials before Allure serializes results."""
import allure_commons

VALUES = set()


def redact(text):
    for value in VALUES:
        text = text.replace(value, '[REDACTED]')
    return text


def scrub(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    if hasattr(value, '__dict__'):
        for key, item in vars(value).items():
            setattr(value, key, scrub(item))
    return value


class AllureRedactor:
    @allure_commons.hookimpl(tryfirst=True)
    def report_result(self, result):
        scrub(result)

    @allure_commons.hookimpl(tryfirst=True)
    def report_container(self, container):
        scrub(container)
