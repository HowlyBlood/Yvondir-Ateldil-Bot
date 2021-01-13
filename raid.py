import discord

import config
from interfaces import Instanciable
from enum import Enum

from lists import Raidlist
from messages import Messages
from yvondil_ateldil import bot as ya_bot

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
            'tank': [],
            'heal': [],
            'dd': []
        }

    def start(self):
        pass

    def end(self):
        pass

    async def setup(self, discord_client, guild, channel_category, original_message):
        dd_role = await guild.create_role(name=f"DD_{self.identifier}", colour=discord.Colour(0x2ecc71))
        heal_role = await guild.create_role(name=f"Heal_{self.identifier}", colour=discord.Colour(0x3498db))
        tank_role = await guild.create_role(name=f"Tank_{self.identifier}", colour=discord.Colour(0xe74c3c))
        permissions = {tank_role, heal_role, dd_role}

        vocal = await guild.create_voice_channel(f'{self.identifier}', user_limit=12, category=channel_category)
        await vocal.set_permissions(tank_role, connect=True)
        await vocal.set_permissions(heal_role, connect=True)
        await vocal.set_permissions(dd_role, connect=True)

        if Raidlist[self.raid]['DLC'] == 'Vanilla':
            desc = Messages.get('created_vocal_no_dlc') % (Raidlist[self.raid]['fr_name'], Raidlist[self.raid]['fr_sets'])
            embed = discord.Embed(title=self.identifier, description=desc, color=0xfa3232)

        else:
            desc = Messages.get('created_vocal_dlc') % (Raidlist[self.raid]['fr_name'], Raidlist[self.raid]['DLC'], Raidlist[self.raid]['fr_sets'])
            embed = discord.Embed(title=self.identifier, description=desc, color=0xfa3232)

        embed.set_author(name=Messages.get('explain_date_definition'))
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/647916987950956554.png?size=64&v=1")

        for index, tank in enumerate(self.members.get('tank')):
            embed.add_field(name=f"Tank {index + 1} :", value=tank.user.mention, inline=True)

        for index, heal in enumerate(self.members.get('heal')):
            embed.add_field(name=f"Heal {index + 1} :", value=heal.user.mention, inline=True)

        for index, dd in enumerate(self.members.get('heal')):
            embed.add_field(name=f"DD {index + 1} :", value=dd.user.mention, inline=True)

        embed.set_footer(text=Messages.get('explain_role_pickup'))
        raid_description_message = await original_message.channel.send(embed=embed)
        self.discord_message_identifier = raid_description_message.id

        bot = ya_bot.Bot()
        for role in ["tank", "heal", "dd"]:
            installed_emoji = bot.get_emoji(role)
            await raid_description_message.add_reaction(discord_client.get_emoji(installed_emoji))
