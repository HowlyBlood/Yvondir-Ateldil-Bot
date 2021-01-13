from singleton_decorator import singleton


@singleton
class Bot:
    emoji_prefix = 'ya'
    emojis = {
        'tank': {'name': "tank", 'image_path': 'assets/tank.png'},
        'heal': {'name': "heal", 'image_path': 'assets/heal.png'},
        'dd': {'name': "dd", 'image_path': 'assets/dd.png'},
        'time': {'name': "time", 'image_path': 'assets/time.png'},
    }

    def __init__(self):
        self._guild = None

    async def setup(self, guild):
        print('Setting up bot.')
        if guild is None:
            raise Exception('guild is None')

        self._guild = guild
        await self.__setup_emoji()

    async def __setup_emoji(self):
        installed_emojis = await self._guild.fetch_emojis()

        for name, emoji in self.emojis.items():
            found_emoji = list(
                filter(lambda installed_emoji: f"{self.emoji_prefix}_{emoji['name']}" == installed_emoji.name,
                       installed_emojis))
            if len(found_emoji) == 0:
                # install emoji
                with open(emoji['image_path'], "rb") as emoji_file:
                    created_emoji = await self._guild.create_custom_emoji(name=f"{self.emoji_prefix}_{emoji['name']}",
                                                                          image=emoji_file.read())
                    emoji['id'] = created_emoji.id
                    print(f"installed emoji {created_emoji.name}")

            else:
                emoji['id'] = found_emoji[0].id

    def get_emoji(self, name):
        return self.emojis.get(name)['id']
