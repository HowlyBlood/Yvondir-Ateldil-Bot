import discord
from discord.utils import get

from enum import Enum

from yvondir_ateldil.lists import Raidlist
from yvondir_ateldil.messages import Messages
from yvondir_ateldil import bot as ya_bot
from yvondir_ateldil.interfaces import Instanciable


class RaidStatus(Enum):
    PLANNED = 0
    STARTED = 1
    ENDED = 2


class Raid(Instanciable):
    TANK_LIMIT = 1
    HEAL_LIMIT = 2
    DD_LIMIT = 9

    def __init__(self, raid, global_identifier, date):
        self.identifier = global_identifier
        self.raid = raid
        self.date = date
        self.status = RaidStatus.PLANNED
        self.discord_message_identifier = None
        self.members = {
            'Tank': [None for i in range(self.TANK_LIMIT)],
            'Heal': [None for i in range(self.HEAL_LIMIT)],
            'DD': [None for i in range(self.DD_LIMIT)],
        }

    def start(self):
        pass

    async def end(self, guild, original_message):
        discord_raid_message = await original_message.channel.fetch_message(self.discord_message_identifier)
        delete_pool = [
            get(guild.voice_channels, name=self.identifier),
            get(guild.roles, name=f"Tank_{self.identifier}"),
            get(guild.roles, name=f"Heal_{self.identifier}"),
            get(guild.roles, name=f"DD_{self.identifier}"),
            original_message,
            discord_raid_message
        ]

        for to_delete_object in delete_pool:
            await to_delete_object.delete()

    async def setup(self, discord_client, guild, channel_category, original_message):
        dd_role = await guild.create_role(name=f"DD_{self.identifier}", colour=discord.Colour(0x2ecc71))
        heal_role = await guild.create_role(name=f"Heal_{self.identifier}", colour=discord.Colour(0x3498db))
        tank_role = await guild.create_role(name=f"Tank_{self.identifier}", colour=discord.Colour(0xe74c3c))
        permissions = {tank_role, heal_role, dd_role}

        vocal = await guild.create_voice_channel(f'{self.identifier}', user_limit=12, category=channel_category)
        await vocal.set_permissions(tank_role, connect=True)
        await vocal.set_permissions(heal_role, connect=True)
        await vocal.set_permissions(dd_role, connect=True)

        embed = await self.render()
        raid_description_message = await original_message.channel.send(embed=embed)
        self.discord_message_identifier = raid_description_message.id

        bot = ya_bot.Bot()
        for role in ["tank", "heal", "dd"]:
            installed_emoji = bot.get_emoji(role)
            await raid_description_message.add_reaction(discord_client.get_emoji(installed_emoji))

    def _member_list(self):
        members = []
        for group in self.members.values():
            members += group
        return members

    def add_member(self, emoji, user):
        bot = ya_bot.Bot()
        role = bot.get_role(emoji)

        try:
            guild_role = f"{role}_{self.identifier}"
            not_assigned_index = self.members[role].index(None)
            self.members[role][not_assigned_index] = user
            return True, guild_role

        except:
            return False, None

    def remove_member(self, emoji, user):
        bot = ya_bot.Bot()
        role = bot.get_role(emoji)
        guild_role = f"{role}_{self.identifier}"

        iterator = (i for i, u in enumerate(self.members[role]) if u is not None and u.id == user.id)
        member_index = next(iterator)

        if member_index is None:
            return False, None

        self.members[role][member_index] = None
        return True, guild_role


    async def render(self):
        if Raidlist[self.raid]['DLC'] == 'Vanilla':
            desc = Messages.get('created_vocal_no_dlc') % (
            Raidlist[self.raid]['fr_name'], Raidlist[self.raid]['fr_sets'])
            embed = discord.Embed(title=self.identifier, description=desc, color=0xfa3232)

        else:
            desc = Messages.get('created_vocal_dlc') % (
            Raidlist[self.raid]['fr_name'], Raidlist[self.raid]['DLC'], Raidlist[self.raid]['fr_sets'])
            embed = discord.Embed(title=self.identifier, description=desc, color=0xfa3232)

        author_message = self.date.strftime("Le %A %d %B %Y à %H:%M") if self.date is not None else Messages.get(
            'explain_date_definition')
        embed.set_author(name=author_message)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/647916987950956554.png?size=64&v=1")

        for role in self.members.keys():
            for index, player in enumerate(self.members.get(role)):
                field_value = Messages.get('empty_role') if player is None else str(player)
                embed.add_field(name=f"{role} {index + 1} :", value=field_value, inline=True)

        embed.set_footer(text=Messages.get('explain_role_pickup'))

        return embed
