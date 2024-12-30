import logging

import colorlog

__all__ = [
    "PackageNameInserter",
    "setup_loggers",
    "create_logging_stream_handler",
]


class PackageNameInserter(logging.Filter):
    CACHES = {}

    def __init__(self, size=30):
        logging.Filter.__init__(self)
        self.size = size

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            name = self.CACHES[record.name]
        except KeyError:
            name = record.name
            parts = name.split(".")
            idx = 1
            while self.size < len(".".join(parts)) and idx < len(parts):
                parts[idx] = parts[idx][:2]
                idx += 1

            name = ".".join(parts)
            name += " " * (self.size - len(name))
            self.CACHES[record.name] = name

        record.logname = name
        return True


def setup_loggers(log_: str | logging.Logger, log_level: str | int):
    if not isinstance(log_, logging.Logger):
        log_ = logging.getLogger(log_)
    log_.setLevel(-1)
    handler = create_logging_stream_handler()
    handler.setLevel(log_level)
    log_.addHandler(handler)


def create_logging_stream_handler(spacing_size=30):
    prefix = "{log_color}[\033[90m{asctime}{log_color}] " \
             "\033[90m{lineno:4} {log_color}| " \
             "\033[90m{logname} {log_color}"

    sh = logging.StreamHandler()
    sh.addFilter(PackageNameInserter(spacing_size))
    # noinspection PyTypeChecker
    sh.setFormatter(colorlog.LevelFormatter(
        fmt=dict(DEBUG=f"{prefix}| D: {{message}}",
                 INFO=f"{prefix}| I: {{message}}",
                 WARNING=f"{prefix}| W: {{message}}",
                 ERROR=f"{prefix}| E: {{message}}",
                 CRITICAL=f"{prefix}| E: {{message}}"),
        log_colors=dict(DEBUG="purple", INFO="white", WARNING="yellow", ERROR="red", CRITICAL="red"),
        datefmt="%H:%M:%S", style="{", reset=True))
    return sh
