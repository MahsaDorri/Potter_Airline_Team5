# logging_config.py
# call setup_logging() once at the start of main.py (before importing flight/database)
# so all the logger.debug/info/error calls in the project go to the log file
 
import logging
 
 
def setup_logging(log_file="potter_airlines.log", level=logging.DEBUG, also_console=False):
    # DEBUG = show everything, INFO/WARNING = less noise once it's working
    handlers = [logging.FileHandler(log_file, mode="a")]
    if also_console:
        handlers.append(logging.StreamHandler())
 
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,  # so calling this again (like in tests) doesn't complain
    )
