from abyss.dispatchers.dispatcher import Dispatcher
from abyss.dispatchers.fifo_dispatcher import FIFODispatcher
from abyss.dispatchers.max_first_dispatcher import MaxFirstDispatcher
from abyss.dispatchers.max_min_dispatcher import MaxMinDispatcher
from abyss.dispatchers.min_first_dispatcher import MinFirstDispatcher

DISPATCHER_NAME_MAPPING = {
    "fifo": FIFODispatcher,
    "max-first": MaxFirstDispatcher,
    "max-min": MaxMinDispatcher,
    "min-first": MinFirstDispatcher
}


def get_dispatcher(dispatcher_name: str) -> Dispatcher:
    """Returns a dispatchers by name.

    Parameters
    ----------
    dispatcher_name : str
        Name of dispatchers to return.

    Returns
    -------
    Dispatcher
        Member of Dispatcher subclass.
    """
    try:
        return DISPATCHER_NAME_MAPPING[dispatcher_name]
    except KeyError:
        raise ValueError(f"{dispatcher_name} dispatchers does not exist")