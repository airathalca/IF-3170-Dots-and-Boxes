class TimeoutHandler(Exception):
    def timeout_handler(signum, *args):
        raise TimeoutHandler
