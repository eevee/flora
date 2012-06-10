class Direction(object):
    _instances = dict()

    @classmethod
    def by_name(cls, name):
        return cls._instances[name]

    def __init__(self, name, vector):
        self.name = name
        self.vector = vector

        self._instances[name] = self

    def __repr__(self):
        return "<{cls} {name}>".format(
            cls=type(self).__name__, name=self.name)

UP = Direction('UP', (0, 1))
DOWN = Direction('DOWN', (0, -1))
LEFT = Direction('LEFT', (-1, 0))
RIGHT = Direction('RIGHT', (1, 0))
