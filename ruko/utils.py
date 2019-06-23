def recursive_merge(a, b):
    """
    Returns generator for merged dict of a and b
    Usage:
        >>> dict(recursive_merge({'a': {'b': 2}}, {'a': {'c': 3}}))
        {'a': {'c': 3, 'b': 2}}
    """
    for k in set(a.keys()) | set(b.keys()):
        if k in a and k in b:
            if isinstance(a[k], dict) and isinstance(b[k], dict):
                yield k, dict(recursive_merge(a[k], b[k]))
            else:
                yield k, b[k]
        elif k in a:
            yield k, a[k]
        else:
            yield k, b[k]
