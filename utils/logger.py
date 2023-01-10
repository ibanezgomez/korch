import logging
import logging.handlers

log = logging.getLogger("sysloger")
log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)
# Colorful
#formatter = logging.Formatter("\033[92m%(asctime)s - [%(name)s] - [ITSec] - %(levelname)s - %(filename)s - %(lineno)d - %(message)s")
formatter = logging.Formatter("%(asctime)s - [%(name)s] - [ITSec] - %(levelname)s - %(filename)s - %(lineno)d - %(message)s")

# Log to syslog (not works under linux embebed)
#sysloghandler = logging.handlers.SysLogHandler(address = '/dev/log')
#sysloghandler.setLevel(logging.DEBUG)
#sysloghandler.setFormatter(formatter)
#log.addHandler(sysloghandler)

# Log to file
filehandler = logging.FileHandler("debug.txt", "w")
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

# Log to stdout too
streamhandler = logging.StreamHandler()
streamhandler.setLevel(logging.DEBUG)
streamhandler.setFormatter(formatter)
log.addHandler(streamhandler)

