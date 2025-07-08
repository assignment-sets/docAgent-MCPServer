import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # or DEBUG for more verbosity
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # logs to stdout
            # Optionally add FileHandler if you want file logging too
        ],
    )