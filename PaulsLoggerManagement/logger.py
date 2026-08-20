import logging
import os
from logging import FileHandler

import colorlog

session_file_created = False
is_alerted = False
created_loggers: list[logging.Logger] = []

_global_console_level: int = logging.DEBUG
_global_file_level: int = logging.DEBUG
_global_is_set = False

class AlertingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):

        global is_alerted
        
        if record.levelno >= logging.WARNING:
            is_alerted = True


def setup_logger(name: str | None,
                 log_file="events.log",
                 console_log_level: int = logging.DEBUG,
                 file_log_level: int = logging.DEBUG,
                 *,
                 level: int | None = None,
                 set_global = False) -> logging.Logger:

    global session_file_created, _global_console_level, _global_file_level, _global_is_set

    if not session_file_created:
        
        # This part ain't gon be multi-threaded so its fine
        session_file_created = True
        open('session.log', 'w').close()

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # `level` arg is there for backwards compatibility, so default to it if it
    # is provided.
    console_log_level = level if level is not None else console_log_level

    if _global_is_set:
        console_log_level = _global_console_level
        file_log_level = _global_file_level

    if set_global:
        _global_is_set = True
        _global_console_level = console_log_level
        _global_file_level = file_log_level
    
    if not logger.handlers:

        # Files will not render colors correctly
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(levelname)-5s %(filename)s:%(funcName)s:%(lineno)d - %(message)s"
        )

        # Most consoles CAN render colors correctly
        console_formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s[%(asctime)s] %(levelname)-5s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG":    "cyan",
                "INFO":     "green",
                "WARNING":  "yellow",
                "ERROR":    "red",
                "CRITICAL": "bold_red",
            }
        )

        # Grab the output stream and set the formatting
        stream = logging.StreamHandler()
        stream.setLevel(console_log_level)
        stream.setFormatter(console_formatter)

        # Persistent file handler and formatting
        file_handler = FileHandler(log_file)
        file_handler.setLevel(file_log_level)
        file_handler.setFormatter(file_formatter)

        # Session file handler and formatting
        session_handler = logging.FileHandler('session.log')
        session_handler.setLevel(file_log_level)
        session_handler.setFormatter(file_formatter)

        # Trigger a flag if a message "warning" or higher gets logged
        alert_handler = AlertingHandler()

        logger.addHandler(stream)
        logger.addHandler(file_handler)
        logger.addHandler(session_handler)
        logger.addHandler(alert_handler)

        session_file_created = True

    created_loggers.append(logger)

    return logger


def email_if_alerted(address: str, subject="", body="", ext="") -> None:
    """
    If the alert handler was triggered during execution, send the session log
    file to an address
    """

    if not is_alerted:
        return
    
    from PaulsEmailManagement import send_email
    
    abs_path = os.path.abspath("session.log")
    send_email(to=address,
               email_ext=ext,
               subject=subject,
               body=body,
               email_attachment_files=[abs_path])
