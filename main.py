import datetime
import locale
import logging

import discord
from discord.utils import get

import config
from lists import Raidlist
from messages import Messages
from raid import Raid
from utils import *
from yvondir_ateldil import bot as ya

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

print(Raidlist['nSS']['fr_name'])
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
ya_bot = ya.Bot()

# Contains all running Raid /!\ do not survive bot restart
raid_list = {}


@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=config.GUILD)
    members = '\n - '.join([member.name for member in guild.members])
    await ya_bot.setup(guild)

    print(f'Bot connected as {bot.user}')
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    print(f'Guild Members:\n - {members}\n')


@bot.event
async def on_message(message):
    guild = discord.utils.get(bot.guilds, name=config.GUILD)

    # Match either "/h" or "/help"
    if re.match('^/(h|help)$', message.content):
        await message.channel.send(Messages.get('help'))
        await message.delete()

    # Match "/end <arg>"
    if re.match(r'^/(end)\s', message.content):
        if message.author.guild_permissions.manage_roles and message.author.guild_permissions.manage_channels:
            raid_identifier, *others = extract_command_args(message.content)
            raid = raid_list.get(raid_identifier)

            if raid is None:
                await message.reply(content=Messages.get('raid_not_found') % raid_identifier)
                return

            await raid.end(guild=guild, original_message=message)
            raid_list.pop(raid_identifier)

    if re.match(r'^/(sd|set_date)\s?', message.content):
        raid_identifier, date, hour, *others = extract_command_args(message.content)
        raid = raid_list[raid_identifier]
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

        raid = Raid(raid=raid_identifier, global_identifier=f"{raid_identifier}_{len(raid_list) + 1}", date=None)
        channel_category = list(filter(lambda category: config.RAIDS == category.name, guild.categories))[0]

        await raid.setup(discord_client=bot, guild=guild, channel_category=channel_category, original_message=message)
        raid_list[raid.identifier] = raid


@bot.event
async def on_raw_reaction_add(payload):
    guild = discord.utils.get(bot.guilds, name=config.GUILD)
    chan = guild.get_channel(payload.channel_id)
    msg = await chan.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    reaction = get(msg.reactions, emoji=payload.emoji)
    embed = msg.embeds[0]

    T_role = get(guild.roles, name=f"Tank_{embed.title}")
    H_role = get(guild.roles, name=f"Heal_{embed.title}")
    D_role = get(guild.roles, name=f"DD_{embed.title}")

    if user.name != 'Yvondir Ateldil':
        if reaction.emoji == bot.get_emoji(config.TANK):
            if reaction.count == 2:
                Mbrs[0] = user.mention
                embed.set_field_at(index=0, name='Tank :', value=Mbrs[0], inline=True)
                await payload.member.add_roles(T_role)
            else:
                await user.send(content='Plus de place pour ce rôle')
        elif reaction.emoji == bot.get_emoji(config.HEAL):
            if reaction.count == 2:
                Mbrs[1] = user.mention
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                await payload.member.add_roles(H_role)
            elif reaction.count == 3:
                Mbrs[2] = user.mention
                embed.set_field_at(index=2, name='Heal 2 :', value=Mbrs[2], inline=True)
                await payload.member.add_roles(f"Heal_{role_list[role_list.index(embed.author)]}")
            else:
                await user.send(
                    content="Désolé, il n'y a plus de place pour ce rôle, reste à l'affut en cas de désistement")
        elif reaction.emoji == bot.get_emoji(config.DD):
            if reaction.count == 2:
                Mbrs[3] = user.mention
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                await payload.member.add_roles(H_role)
            elif reaction.count == 3:
                Mbrs[4] = user.mention
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 4:
                Mbrs[5] = user.mention
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 5:
                Mbrs[6] = user.mention
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 6:
                Mbrs[7] = user.mention
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 7:
                Mbrs[8] = user.mention
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 8:
                Mbrs[9] = user.mention
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 9:
                Mbrs[10] = user.mention
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 10:
                Mbrs[11] = user.mention
                embed.set_field_at(index=11, name='DD 9 :', value=Mbrs[11], inline=True)
                await payload.member.add_roles(D_role)
            else:
                dm_channel = await user.create_dm()
                dm_channel.send('Plus de place pour ce role')
    await msg.edit(embed=embed)


@bot.event
async def on_raw_reaction_remove(payload):
    guild = discord.utils.get(bot.guilds, name=config.GUILD)
    chan = guild.get_channel(payload.channel_id)
    msg = await chan.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    member = get(guild.members, id=payload.user_id)
    reaction = get(msg.reactions, emoji=payload.emoji)
    embed = msg.embeds[0]

    T_role = get(guild.roles, name=f"Tank_{embed.title}")
    H_role = get(guild.roles, name=f"Heal_{embed.title}")
    D_role = get(guild.roles, name=f"DD_{embed.title}")

    if user.name != 'Yvondir Ateldil':
        if payload.emoji == bot.get_emoji(config.TANK):
            if reaction.count == 1:
                Mbrs[0] = 'Place libre'
                embed.set_field_at(index=0, name='Tank :', value=Mbrs[0], inline=True)
                await member.remove_roles(T_role)

        elif reaction.emoji == bot.get_emoji(config.HEAL):
            if reaction.count == 1:
                Mbrs[1] = Mbrs[2]
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                await member.remove_roles(H_role)
            elif reaction.count == 2:

                if Mbrs[1] == user.mention:
                    Mbrs[1] = Mbrs[2]
                    Mbrs[2] = 'Place libre'
                else:
                    Mbrs[2] = 'Place libre'
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                embed.set_field_at(index=2, name='Heal 2 :', value=Mbrs[2], inline=True)
                await member.remove_roles(H_role)

        elif reaction.emoji == bot.get_emoji(config.DD):
            if reaction.count == 1:
                Mbrs[3] = "Place Libre"
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 2:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 3:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 4:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 5:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 6:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 7:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 8:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 9:
                Mbrs.remove(user.mention)
                Mbrs.append('Place libre')
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                embed.set_field_at(index=5, name='DD 3 :', value=Mbrs[5], inline=True)
                embed.set_field_at(index=6, name='DD 4 :', value=Mbrs[6], inline=True)
                embed.set_field_at(index=7, name='DD 5 :', value=Mbrs[7], inline=True)
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                embed.set_field_at(index=9, name='DD 7 :', value=Mbrs[9], inline=True)
                embed.set_field_at(index=10, name='DD 8 :', value=Mbrs[10], inline=True)
                embed.set_field_at(index=11, name="DD 9 :", value=Mbrs[11], inline=True)
                await member.remove_roles(D_role)

    await msg.edit(embed=embed)


bot.run(config.TOKEN)
