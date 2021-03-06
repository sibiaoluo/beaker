# -*- coding: utf-8 -*-


import os
import syslog
import codecs
import logging

def log_to_stream(stream, level=logging.WARNING):
    """
    Configures the logging module to send messages to the given stream (for
    example, sys.stderr). By default only WARNING and ERROR level messages are
    logged; pass the level argument to override this.

    Suitable for use in command-line programs.
    """
    stream_handler = logging.StreamHandler(stream)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s'))
    logging.getLogger().handlers = [stream_handler]

def log_to_syslog(program_name, facility=syslog.LOG_DAEMON):
    syslog.openlog(program_name, syslog.LOG_PID, facility)
    syslog_handler = SysLogHandler()
    syslog_handler.setLevel(logging.DEBUG) # syslog can do the filtering instead
    syslog_handler.setFormatter(logging.Formatter('%(name)s %(levelname)s %(message)s'))
    logging.getLogger().handlers = [syslog_handler]

# Like logging.handlers.SysLogHandler, but uses libc syslog(3) and splits
# multi-line messages into separate log entries.
class SysLogHandler(logging.Handler):

    _level_to_priority = {
        logging.CRITICAL: syslog.LOG_CRIT,
        logging.ERROR: syslog.LOG_ERR,
        logging.WARNING: syslog.LOG_WARNING,
        logging.INFO: syslog.LOG_INFO,
        logging.DEBUG: syslog.LOG_DEBUG,
    }

    def emit(self, record):
        priority = self._level_to_priority.get(record.levelno, syslog.LOG_WARNING)
        msg = self.format(record)
        for i, line in enumerate(msg.splitlines()):
            if isinstance(line, unicode):
                line = codecs.BOM_UTF8 + line.encode('utf8')
            if i > 0:
                line = ' ' + line
            try:
                syslog.syslog(priority, line)
            except Exception:
                self.handleError(record)
