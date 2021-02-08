import datetime
import os
import re

import discord
from discord.utils import get
from singleton_decorator import singleton

from yvondir_ateldil.lists import Raidlist
from yvondir_ateldil.messages import Messages
from yvondir_ateldil.raid import Raid
from yvondir_ateldil.user import User
from yvondir_ateldil.utils import extract_command_args, find_raid_from_message


@singleton
class YvondirAteldil:
    emoji_prefix = 'ya'
    emojis = {
        'tank': {'name': "tank", 'role': "Tank", 'image_path': 'assets/tank.png'},
        'heal': {'name': "heal", 'role': "Heal", 'image_path': 'assets/heal.png'},
        'dd': {'name': "dd", 'role': "DD", 'image_path': 'assets/dd.png'},
        'time': {'name': "time", 'image_path': 'assets/time.png'},
    }

    def __init__(self):
        self._token = os.getenv('DISCORD_TOKEN')
        self._guild_name = os.getenv('DISCORD_GUILD')
        self._raid_channel = os.getenv('RAIDS_VOCAL_CATEGORY')

        intents = discord.Intents.all()
        self._bot = discord.Client(intents=intents)
        self._guild = None
        self._raid_list = {}

    async def __setup(self):
        print("Setting up bot.")

        self._guild = discord.utils.get(self._bot.guilds, name=self._guild_name)
        await self.__setup_emoji()
        print("Done setting up bot")

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

    def get_emoji_from_name(self, name):
        name = name.replace(f"{self.emoji_prefix}_", "")
        return self.emojis.get(name)['id']

    def get_role_from_emoji(self, emoji):
        name = emoji.name.replace(f"{self.emoji_prefix}_", "")
        return self.emojis.get(name)['role']

    def add_events(self):
        self._bot.event(self.on_ready)
        self._bot.event(self.on_message)
        self._bot.event(self.on_raw_reaction_add)
        self._bot.event(self.on_raw_reaction_remove)

    async def on_ready(self):
        await self.__setup()

        print(f'Bot connected as {self._bot.user}')
        print(
            f'{self._bot.user} is connected to the following guild:\n'
            f'{self._guild.name}(id: {self._guild.id})'
        )

    async def on_message(self, message):

        # Match either "/h" or "/help"
        if re.match('^/(h|help)$', message.content):
            await message.channel.send(Messages.get('help'))
            await message.delete()

        # Match "/end <arg>"
        if re.match(r'^/(end)\s', message.content):
            if message.author.guild_permissions.manage_roles and message.author.guild_permissions.manage_channels:
                raid_identifier, *others = extract_command_args(message.content)
                raid = self._raid_list.get(raid_identifier)

                if raid is None:
                    await message.reply(content=Messages.get('raid_not_found') % raid_identifier)
                    return

                await raid.end(guild=self._guild, original_message=message)
                self._raid_list.pop(raid_identifier)

        if re.match(r'^/(sd|set_date)\s?', message.content):
            raid_identifier, date, hour, *others = extract_command_args(message.content)
            raid = self._raid_list[raid_identifier]

            if raid is None:
                await message.reply(content=Messages.get('raid_not_found') % raid_identifier)
                return

            raid.date = datetime.datetime.fromisoformat(f"{date} {hour}")
            raid_message = await message.channel.fetch_message(raid.identifier)

            await raid_message.edit(embed=raid.render())
            await message.delete()

        if re.match(r'^/(r|raid)\s?', message.content):
            raid_identifier, *others = extract_command_args(message.content)

            if Raidlist.get(raid_identifier) is None:
                await message.reply(content=Messages.get('raid_not_found') % raid_identifier)
                return

            await message.delete()

            raid = Raid(raid_fr_name=raid_identifier, global_identifier=f"{raid_identifier}_{len(self._raid_list) + 1}",
                        date=None)
            channel_category = list(filter(lambda category: self._raid_channel == category.name, self._guild.categories))[0]

            await raid.setup(discord_client=self._bot, guild=self._guild, channel_category=channel_category,
                             original_message=message)
            self._raid_list[raid.identifier] = raid

    async def on_raw_reaction_add(self, payload):
        chan = self._guild.get_channel(payload.channel_id)
        user = self._bot.get_user(payload.user_id)
        msg = await chan.fetch_message(payload.message_id)

        raid = find_raid_from_message(self._raid_list, payload.message_id)
        if raid is None:
            print(f"Failed to find raid {payload.message_id}")
            print(self._raid_list)
            return

        if user.id != self._bot.user.id:
            [succeed, role] = raid.add_member(payload.emoji, User(id=payload.user_id, user=user))

            if succeed:
                guild_role = get(self._guild.roles, name=role)
                await payload.member.add_roles(guild_role)

            else:
                await user.send(content=Messages.get('role_full'))

        await msg.edit(embed=await raid.render())

    async def on_raw_reaction_remove(self, payload):
        chan = self._guild.get_channel(payload.channel_id)
        user = self._bot.get_user(payload.user_id)
        msg = await chan.fetch_message(payload.message_id)

        raid = find_raid_from_message(self._raid_list, payload.message_id)
        if raid is None:
            print(f"Failed to find raid {payload.message_id}")
            print(self._raid_list)
            return

        if user.id != self._bot.user.id:
            [succeed, role] = raid.remove_member(payload.emoji, User(id=payload.user_id, user=user))

            if succeed:
                # Don't know why but payload.member here is None, so need to get mamber from the guild
                member = self._guild.get_member(user.id)
                guild_role = get(self._guild.roles, name=role)
                await member.remove_roles(guild_role)

            else:
                await user.send(content=Messages.get('internal_error'))

        await msg.edit(embed=await raid.render())

    def run(self):
        self.add_events()
        self._bot.run(self._token)
