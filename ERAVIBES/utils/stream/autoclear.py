import os
import logging
from config import autoclean  # Import the entire autoclean module
from ERAVIBES.utils.decorators import asyncify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asyncify
def auto_clean(popped):
    def _auto_clean(popped_item):
        try:
            rem = popped_item["file"]
            autoclean.remove(rem)  # Use autoclean.remove instead of remove
            cnt = autoclean.count(rem)  # Use autoclean.count instead of count
            if cnt == 0:
                if "vid_" not in rem and "live_" not in rem and "index_" not in rem:
                    try:
                        os.remove(rem)
                        logger.info(f"Successfully removed file: {rem}")
                    except Exception as e:
                        logger.error(f"Failed to remove file {rem}: {e}")
        except Exception as e:
            logger.error(f"Error processing popped item {popped_item}: {e}")

    if isinstance(popped, dict):
        _auto_clean(popped)
    elif isinstance(popped, list):
        for pop in popped:
            _auto_clean(pop)
    else:
        raise ValueError("Expected popped to be a dict or list.")

# Example usage:
# auto_clean({"file": "path/to/file.txt"})
# auto_clean([{"file": "path/to/file1.txt"}, {"file": "path/to/file2.txt"}])
