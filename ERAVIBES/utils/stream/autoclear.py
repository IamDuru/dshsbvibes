import os

from config import autoclean


async def auto_clean(popped):
    try:
        rem = popped["file"]
        autoclean.remove(rem)
        count = autoclean.count(rem)
        if count == 0:
            if "vid_" not in rem or "live_" not in rem or "index_" not in rem:
                try:
                    os.remove(rem)
                except:
                    pass
    except:
        pass

    if isinstance(popped, dict):
        _auto_clean(popped)
    elif isinstance(popped, list):
        for pop in popped:
            _auto_clean(pop)
    else:
        raise ValueError("Expected popped to be a dict or list.")
