class TimeoutHandler(Exception):
    pass

    def timeout_handler(signum, *args):
        raise TimeoutHandler
