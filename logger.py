import logging
import os

# make sure logs directory exists
os.makedirs('logs', exist_ok=True)

# main pipeline logger - goes to console AND file
pipeline_logger = logging.getLogger('pipeline')
pipeline_logger.setLevel(logging.DEBUG)

# console handler - only INFO and above, no point flooding the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(console_fmt)

# file handler - DEBUG and above so we have the full picture if something goes wrong
file_handler = logging.FileHandler('logs/pipeline.log')
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s')
file_handler.setFormatter(file_fmt)

pipeline_logger.addHandler(console_handler)
pipeline_logger.addHandler(file_handler)

# separate error logger - only rejected records go here, makes debugging easy
error_logger = logging.getLogger('pipeline.errors')
error_logger.setLevel(logging.WARNING)

error_file_handler = logging.FileHandler('logs/errors.log')
error_file_handler.setLevel(logging.WARNING)
error_file_handler.setFormatter(file_fmt)
error_logger.addHandler(error_file_handler)

# don't propagate errors up to the root logger, we handle it ourselves
error_logger.propagate = False

logger = pipeline_logger
