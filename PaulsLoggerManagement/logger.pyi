import logging

session_file_created: bool
is_alerted: bool

def setup_logger(name: str | None,
                 log_file = "events.log",
                 console_log_level: int = logging.DEBUG,
                 file_log_level: int = logging.DEBUG,
                 *,
                 level: int | None = None) -> logging.Logger: ...
def email_if_alerted(address: str, subject: str = '', body: str = '', ext: str = '') -> None: ...
