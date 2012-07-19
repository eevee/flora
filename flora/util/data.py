"""General-purpose data utilities.
"""

class reify(object):
    """Decorator much like `@property`, except on the first call, the return
    value is stored on the object as a regular attribute.  And, obviously, the
    property must be immutable.
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val
