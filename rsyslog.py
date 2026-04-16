"""Send a message to a syslog server."""

from __future__ import annotations

import argparse
import logging
import logging.handlers
import os


def build_logger(host: str, port: int) -> logging.Logger:
	logger = logging.getLogger("MyApp")
	logger.setLevel(logging.DEBUG)

	if not logger.handlers:
		handler = logging.handlers.SysLogHandler(address=(host, port))
		handler.setFormatter(logging.Formatter(fmt="%(name)s: %(message)s"))
		logger.addHandler(handler)

	return logger


def main() -> None:
	parser = argparse.ArgumentParser(description="Send a log message to a syslog server.")
	parser.add_argument("--host", default=os.getenv("SYSLOG_HOST", "127.0.0.1"), help="Syslog server host")
	parser.add_argument("--port", default=int(os.getenv("SYSLOG_PORT", "514")), type=int, help="Syslog server port")
	parser.add_argument("--message", default="Riad is a remote test from Python to rsyslog", help="Message to send")
	parser.add_argument("--level", default="error", choices=["debug", "info", "warning", "error", "critical"], help="Log level")
	args = parser.parse_args()

	logger = build_logger(args.host, args.port)
	getattr(logger, args.level)(args.message)


if __name__ == "__main__":
	main()