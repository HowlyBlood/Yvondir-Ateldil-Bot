class Instanciable:
    def start(self):
        raise Exception('Not implemented error')

    def end(self):
        raise Exception('Not implemented error')


class Player:
    def __init__(self, discord_user):
        self.user = discord_user

    def __str__(self):
        return ""


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
