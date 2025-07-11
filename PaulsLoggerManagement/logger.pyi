import logging

session_file_created: bool
is_alerted: bool

def setup_logger(name: str | None, log_file: str = 'events.log', level: int = logging.DEBUG) -> logging.Logger: ...
def email_if_alerted(address: str, subject: str = '', body: str = '', ext: str = '') -> None: ...
