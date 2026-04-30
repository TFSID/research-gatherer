"""
Queue-based logging handler for the Streamlit Research Gatherer dashboard.

Attaches to the root logger so all named loggers (Search Engine, ImageGatherer,
etc.) are captured via Python's default propagation — no changes to existing code.
"""

import logging
import queue
from typing import List


class QueueHandler(logging.Handler):
    """Logging handler that puts formatted records into a thread-safe queue."""

    def __init__(self, log_queue: queue.Queue):
        super().__init__()
        self.log_queue = log_queue
        self.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s [%(name)s] %(message)s',
            datefmt='%H:%M:%S',
        ))

    def emit(self, record: logging.LogRecord):
        try:
            self.log_queue.put_nowait(self.format(record))
        except Exception:
            self.handleError(record)


def attach_queue_handler(log_queue: queue.Queue) -> QueueHandler:
    """Attach a QueueHandler to the root logger. Returns handler for later removal."""
    handler = QueueHandler(log_queue)
    handler.setLevel(logging.DEBUG)
    root = logging.getLogger()
    # Lower root level so DEBUG records propagate when debug_mode is on
    if root.level == logging.NOTSET or root.level > logging.DEBUG:
        root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    return handler


def detach_queue_handler(handler: QueueHandler) -> None:
    """Remove the QueueHandler from the root logger."""
    logging.getLogger().removeHandler(handler)


def drain_queue(log_queue: queue.Queue, existing: List[str]) -> List[str]:
    """Pull all currently available messages from queue into a list."""
    updated = list(existing)
    while True:
        try:
            updated.append(log_queue.get_nowait())
        except queue.Empty:
            break
    return updated
