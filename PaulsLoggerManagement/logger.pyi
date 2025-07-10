import logging

session_file_created: bool
is_alerted: bool

def setup_logger(name, log_file: str = 'events.log', level=...): ...
def email_if_alerted(address: str, subject: str = '', body: str = '', ext: str = ''): ...
