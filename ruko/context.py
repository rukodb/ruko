from functools import wraps

from ruko.ruko_client import RukoClient


class RContext:
    """
    Class to handle database connection contexts. Using
    explicit contexts is not mandatory

    Usage:
        with db.context:
            db['notes'].append({})

        @db.context
        def get_notes():
            return db['notes'].get()
    """

    def __init__(self, *params, obj=None):
        self.params = params
        self.obj = obj or self

    def create_conn(self):
        return RukoClient(*self.params)

    def get(self):
        if not hasattr(self.obj, 'rkconn'):
            self.obj.rkconn = self.create_conn()
        return self.obj.rkconn

    def __call__(self, *args, **kwargs):  # As decorator
        if kwargs or len(args) != 1 or not callable(args[0]):
            raise ValueError('Improper usage of context. Check docstring')

        func = args[0]

        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper

    def __enter__(self):
        if not hasattr(self.obj, 'rkconn'):
            self.obj.rkconn = self.create_conn()

    def close(self):
        if hasattr(self.obj, 'rkconn'):
            self.obj.rkconn.close()
            del self.obj.rkconn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
