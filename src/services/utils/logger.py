import logging
import os
import platform
import socket
import getpass
import sys
from datetime import datetime

APP_VERSION = "v1.0.0 (Portable)"

# ── Custom log levels ──────────────────────────────────────────────────────
USER_ACTION_LEVEL = 25   # between INFO (20) and WARNING (30)
logging.addLevelName(USER_ACTION_LEVEL, "USER")


def setup_logger(log_folder: str, name: str = "CRAFT") -> logging.Logger:
    os.makedirs(log_folder, exist_ok=True)

    log_file     = os.path.join(log_folder, "craft.log")
    session_file = os.path.join(log_folder, "session.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers on reload
    if logger.handlers:
        return logger

    # ── Formatters ─────────────────────────────────────────────────────
    full_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    simple_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        "%H:%M:%S"
    )

    # ── Persistent log (append) ────────────────────────────────────────
    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setFormatter(full_fmt)
    file_handler.setLevel(logging.INFO)

    # ── Session log (overwrite each launch) ───────────────────────────
    session_handler = logging.FileHandler(session_file, encoding="utf-8", mode="w")
    session_handler.setFormatter(full_fmt)
    session_handler.setLevel(logging.DEBUG)

    # ── Console (warnings and above only) ────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_fmt)
    console_handler.setLevel(logging.WARNING)

    logger.addHandler(file_handler)
    logger.addHandler(session_handler)
    logger.addHandler(console_handler)

    # ── Add .user() convenience method ────────────────────────────────
    def _user(msg, *args, **kwargs):
        if logger.isEnabledFor(USER_ACTION_LEVEL):
            logger._log(USER_ACTION_LEVEL, msg, args, **kwargs)

    logger.user = _user

    # ── Session header ─────────────────────────────────────────────────
    _write_session_header(logger)

    return logger


def _write_session_header(logger: logging.Logger):
    """Write machine/environment info at the top of each session."""
    sep = "=" * 70
    logger.info(sep)
    logger.info(f"  CRAFT {APP_VERSION} — Session started")
    logger.info(f"  Time      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"  Host      : {socket.gethostname()}")
    logger.info(f"  User      : {getpass.getuser()}")
    logger.info(f"  OS        : {platform.system()} {platform.release()} " f"({platform.version()})")
    logger.info(f"  PID       : {os.getpid()}")
    logger.info(sep)


# ── Convenience decorator ──────────────────────────────────────────────────
def log_action(logger: logging.Logger, action: str):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            logger.user(f"[ACTION] {action} — started")
            try:
                result = fn(*args, **kwargs)
                logger.user(f"[ACTION] {action} — completed")
                return result
            except Exception as e:
                logger.error(f"[ACTION] {action} — failed: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


# ── Mixin for controllers and dialogs ──────────────────────────────────────

class LogMixin:

    def log_action(self, action: str, detail: str = ""):
        if not getattr(self, "logger", None):
            return
        msg = f"[ACTION] {action}"
        if detail:
            msg += f" | {detail}"
        self.logger.log(USER_ACTION_LEVEL, msg)

    def log_info(self, msg: str):
        if getattr(self, "logger", None):
            self.logger.info(msg)

    def log_warning(self, msg: str):
        if getattr(self, "logger", None):
            self.logger.warning(msg)

    def log_error(self, msg: str, exc: Exception = None):
        if not getattr(self, "logger", None):
            return
        if exc:
            self.logger.error(f"{msg}: {exc}", exc_info=True)
        else:
            self.logger.error(msg)

    def log_nav(self, page: str):
        """Log a navigation event (page/tab change)."""
        if getattr(self, "logger", None):
            self.logger.log(USER_ACTION_LEVEL, f"[NAV] Navigated to: {page}")