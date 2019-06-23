class EmptyType(object):
    """A sentinel value when nothing is returned from the database"""

    def __new__(cls):
        return Empty

    def __reduce__(self):
        return EmptyType, ()

    def __bool__(self):
        return False

    def __repr__(self):
        return 'Empty'


Empty = object.__new__(EmptyType)
