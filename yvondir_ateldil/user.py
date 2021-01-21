class User:
    def __init__(self, id, user):
        self.id = id
        self.discord_user = user

    def __str__(self):
        return self.discord_user.mention
