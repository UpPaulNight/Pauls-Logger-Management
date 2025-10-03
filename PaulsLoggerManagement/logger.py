import logging
import os
from logging.handlers import RotatingFileHandler

import colorlog

session_file_created = False
is_alerted = False
created_loggers: list[logging.Logger] = []

class AlertingHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record):

        global is_alerted
        
        if record.levelno >= logging.WARNING:
            is_alerted = True


def setup_logger(name: str | None, log_file="events.log", level=logging.DEBUG) -> logging.Logger:
    global session_file_created

    if not session_file_created:
        
        # This part ain't gon be multi-threaded so its fine
        session_file_created = True
        open('session.log', 'w').close()

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:

        # Files will not render colors correctly
        file_formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s - %(name)s - %(message)s"
        )

        # Most consoles CAN render colors correctly
        console_formatter = colorlog.ColoredFormatter(
            fmt="%(log_color)s[%(asctime)s] %(levelname)-8s - %(message)s",
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
        stream.setFormatter(console_formatter)

        # Persistent file handler and formatting
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5_000_000_000, backupCount=5
        )
        file_handler.setFormatter(file_formatter)

        # Session file handler and formatting
        session_handler = logging.FileHandler('session.log')
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
