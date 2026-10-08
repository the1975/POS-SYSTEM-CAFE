import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Log ke stdout (cocok untuk hosting gratis/managed). Detail teknis hanya
    ditulis di log server, tidak pernah dikirim ke client."""
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    )
    root.addHandler(handler)
    root.setLevel(level.upper())
