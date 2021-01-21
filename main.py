import datetime
import locale

import discord
from discord.utils import get

from yvondir_ateldil.lists import Raidlist
from yvondir_ateldil.messages import Messages
from yvondir_ateldil.raid import Raid
from yvondir_ateldil.user import User
from yvondir_ateldil.utils import *
from yvondir_ateldil import bot as ya, config

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

        raid = Raid(raid=raid_identifier, global_identifier=f"{raid_identifier}_{len(raid_list) + 1}", date=None)
        channel_category = list(filter(lambda category: config.RAIDS == category.name, guild.categories))[0]

        await raid.setup(discord_client=bot, guild=guild, channel_category=channel_category, original_message=message)
        raid_list[raid.identifier] = raid


@bot.event
async def on_raw_reaction_add(payload):
    guild = discord.utils.get(bot.guilds, name=config.GUILD)
    chan = guild.get_channel(payload.channel_id)
    user = bot.get_user(payload.user_id)
    msg = await chan.fetch_message(payload.message_id)

    raid = find_raid_from_message(raid_list, payload.message_id)
    if raid is None:
        print(f"Failed to find raid {payload.message_id}")
        print(raid_list)
        return

    if user.id != bot.user.id:
        [succeed, role] = raid.add_member(payload.emoji, User(id=payload.user_id, user=user))

        if succeed:
            guild_role = get(guild.roles, name=role)
            await payload.member.add_roles(guild_role)

        else:
            await user.send(content=Messages.get('role_full'))

    await msg.edit(embed=await raid.render())


@bot.event
async def on_raw_reaction_remove(payload):
    guild = discord.utils.get(bot.guilds, name=config.GUILD)
    chan = guild.get_channel(payload.channel_id)
    user = bot.get_user(payload.user_id)
    msg = await chan.fetch_message(payload.message_id)

    raid = find_raid_from_message(raid_list, payload.message_id)
    if raid is None:
        print(f"Failed to find raid {payload.message_id}")
        print(raid_list)
        return

    if user.id != bot.user.id:
        [succeed, role] = raid.remove_member(payload.emoji, User(id=payload.user_id, user=user))

        if succeed:
            # Don't know why but payload.member here is None, so need to get mamber from the guild
            member = guild.get_member(user.id)
            guild_role = get(guild.roles, name=role)
            await member.remove_roles(guild_role)

        else:
            await user.send(content=Messages.get('internal_error'))

    await msg.edit(embed=await raid.render())


bot.run(config.TOKEN)
