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
