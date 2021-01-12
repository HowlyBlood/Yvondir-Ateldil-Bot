# bot.py
from lists import Raidlist,Dungeonlist
import os
import datetime
from time import sleep
import locale

import discord
from discord.ext.commands import Bot
from discord.utils import get
from dotenv import load_dotenv
locale.setlocale(locale.LC_ALL, 'fr_FR')
#embed management
Mbrs=['Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre','Place libre']
ttl=''
desc=''
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
RAIDS = os.getenv('RAIDS_VOCAL_CATEGORY')
TANK = int(os.getenv('TANK_ID'))
DD = int(os.getenv('DD_ID'))
HEAL = int(os.getenv('HEAL_ID'))
TIMER = int(os.getenv('TIME_ID'))
print (Raidlist['nSS']['fr_name'])
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
raidID = 0
donjID = 0
dictIDs = {}

@bot.event
async def on_ready():
    guild = discord.utils.get(bot.guilds, name=GUILD)
    members = '\n - '.join([member.name for member in guild.members])
    cat = guild.categories
    print(f'Bot connected as {bot.user}')
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    print(f'Guild Members:\n - {members}\n')

@bot.event
async def on_message(message):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    cat = guild.categories
    Raids=-1
    global raidID

    for category in cat:
        if RAIDS in str(category):
            Raids=cat.index(category)

    if message.content.startswith('/h') or message.content.startswith('/help'):
        MSG = await message.channel.send(f"\n \n\
**RAIDS :**\nPour proposer un raid, la syntaxe est l'une des suivantes : \n\
/r [Abréviation du donjon]\n\
/raid [Abréviation du donjon]\n\
*Par exemple :* \n\
/r nSS\n\
Notez que pour simplifier la syntaxe, il faut ensuite faire un '/set_date' (expliqué ci-dessous)\
\n\n\
**SET_DATE :**\nPour modifier la date d'un raid, la syntaxe est la suivante : \n\
/set_date [ID du raid] [Date et heure au format AAAA-MM-JJ hh:mm]\n\
/sd [ID du raid] [Date et heure au format AAAA-MM-JJ hh:mm]\n\
*Par exemple :* \n\
/sd nSS_1 2021-01-17 14:30\
\n\n\
**END**\n\
Pour mettre fin à un raid, il vousfaudra les permissions de gestion des channels et des roles\n\
La syntaxe est l'une des suivantes :\n\
/end [ID du raid]\n\
[ID du raid] représente le 'code' affiché sur le haut du message correspondant a celui-ci.\n\n\
*Par exemple :* \n\
/end nSS_1\n")
        await message.delete()

    if message.content.startswith('/end'):
        if message.author.guild_permissions.manage_roles==True and message.author.guild_permissions.manage_channels==True:
            print(dictIDs)
            msg = message.content.replace('/end ', '')
            vocal = get(guild.voice_channels,name=msg)
            T_role = get(guild.roles, name=f"Tank_{msg}")
            H_role = get(guild.roles, name=f"Heal_{msg}")
            D_role = get(guild.roles, name=f"DD_{msg}")
            await vocal.delete()
            await D_role.delete()
            await T_role.delete()
            await H_role.delete()
            await message.delete()
            MSG = await message.channel.fetch_message(dictIDs[msg])
            await MSG.delete()
            dictIDs.pop(msg)
            print(dictIDs)

    if message.content.startswith('/set_date') or message.content.startswith('/sd '):
        print(dictIDs)
        if message.content.startswith('/set_date '):
            msg=message.content.replace('/set_date ', '')
        if message.content.startswith('/sd '):
            msg=message.content.replace('/sd ', '')

        msg,date,hour = msg.split(' ')
        date=date+' '+hour
        print (msg,dictIDs[msg], date)
        MSG = await message.channel.fetch_message(dictIDs[msg])
        embed=MSG.embeds[0]

        date = datetime.datetime.fromisoformat(date)
        date = date.strftime("Le %A %d %B %Y à %H:%M")
        print (date)
        embed.set_author(name=date)
        await MSG.edit(embed=embed)
        await message.delete()

    if message.content.startswith('/raid') or message.content.startswith('/r '):

        raidID += 1
        if message.content.startswith('/raid '):
            msg=message.content.replace('/raid ', '')
        if message.content.startswith('/r '):
            msg=message.content.replace('/r ', '')
        raid=msg
        await message.delete()
        #tank_c,heal_c,dd_c=1,2,9
        dd_role   = await guild.create_role(name=f"DD_{raid}_{str(raidID)}",colour=discord.Colour(0x2ecc71))
        heal_role = await guild.create_role(name=f"Heal_{raid}_{str(raidID)}",colour=discord.Colour(0x3498db))
        tank_role = await guild.create_role(name=f"Tank_{raid}_{str(raidID)}", colour=discord.Colour(0xe74c3c))
        permissions={tank_role,heal_role,dd_role}
        vocal = await guild.create_voice_channel(f'{raid}_{str(raidID)}',user_limit=12,category=cat[Raids])
        await vocal.set_permissions(tank_role, connect=True)
        await vocal.set_permissions(heal_role, connect=True)
        await vocal.set_permissions(dd_role, connect=True)
        Mbrs = ['Place libre', 'Place libre', 'Place libre', 'Place libre', 'Place libre', 'Place libre', 'Place libre',
                'Place libre', 'Place libre', 'Place libre', 'Place libre', 'Place libre']
        #MSG = await message.channel.send(f'Un Channel vocal a été créée pour ce Sollance en mode normal. Il vous faudra {tank_c} {bot.get_emoji(TANK)}, {heal_c}{bot.get_emoji(HEAL)} et {dd_c}{bot.get_emoji(DD)}. Réagissez ci-dessous pourvous inscrire au raid en fonction de votre Rôle')
        ttl = f"{raid}_{str(raidID)}"
        if Raidlist[raid]['DLC']=='Vanilla':

            desc=f"Le salon vocal a été crée pour l'épreuve : {Raidlist[raid]['fr_name']}. \nPas besoin de DLC particulier. \n\nLes sets de cette épreuve sont les suivants : \n{Raidlist[raid]['fr_sets']}.\n\nVoici la liste des participants au raid :"
            embed = discord.Embed(title=ttl,
                              description=desc,
                              color=0xfa3232)
        else:
            desc=f"Le salon vocal a été crée pour l'épreuve : {Raidlist[raid]['fr_name']}. \nIl vous faudra le DLC : {Raidlist[raid]['DLC']}.\n\nLes sets de cette épreuve sont les suivants : \n{Raidlist[raid]['fr_sets']}\n\nVoici la liste des participants au raid :"
            embed = discord.Embed(title=ttl,
                                  description=desc,
                                  color=0xfa3232)
        embed.set_author(name="Définissez une date avec /set_date [ID] [AAAA-MM-JJ HH:MM]")
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/647916987950956554.png?size=64&v=1")
        embed.add_field(name="Tank :", value=Mbrs[0], inline=True)
        embed.add_field(name="Heal 1 :", value=Mbrs[1], inline=True)
        embed.add_field(name="Heal 2 :", value=Mbrs[2], inline=True)
        embed.add_field(name="DD 1 :", value=Mbrs[3], inline=True)
        embed.add_field(name="DD 2 :", value=Mbrs[4], inline=True)
        embed.add_field(name="DD 3 :", value=Mbrs[5], inline=True)
        embed.add_field(name="DD 4 :", value=Mbrs[6], inline=True)
        embed.add_field(name="DD 5 :", value=Mbrs[7], inline=True)
        embed.add_field(name="DD 6 :", value=Mbrs[8], inline=True)
        embed.add_field(name="DD 7 :", value=Mbrs[9], inline=True)
        embed.add_field(name="DD 8 :", value=Mbrs[10], inline=True)
        embed.add_field(name="DD 9 :", value=Mbrs[11], inline=True)
        embed.set_footer(
            text="Veillez réagir en fonction du rôle que vous voulez jouer. Merci de ne mettre qu'une seule réaction par personne. Vous pouvez toujours vous désinscrire en enlevant votre réaction")
        MSG = await message.channel.send(embed=embed)
        dictIDs[f'{raid}_{str(raidID)}']=MSG.id
        tank_react = await MSG.add_reaction(bot.get_emoji(TANK))
        heal_react = await MSG.add_reaction(bot.get_emoji(HEAL))
        dd_react   = await MSG.add_reaction(bot.get_emoji(DD))
        #timer_react = await MSG.add_reaction(bot.get_emoji(TIMER))

        #await vocal.delete()
        #await dd_role.delete()
        #await tank_role.delete()
        #await heal_role.delete()

@bot.event
async def on_raw_reaction_add(payload):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    chan= guild.get_channel(payload.channel_id)
    msg=await chan.fetch_message(payload.message_id)
    user=bot.get_user(payload.user_id)
    reaction = get(msg.reactions, emoji=payload.emoji)
    embed=msg.embeds[0]

    T_role = get(guild.roles, name=f"Tank_{embed.title}")
    H_role = get(guild.roles, name=f"Heal_{embed.title}")
    D_role = get(guild.roles, name=f"DD_{embed.title}")

    if user.name!='Yvondir Ateldil':
        if reaction.emoji==bot.get_emoji(TANK):
            if reaction.count==2:
                Mbrs[0] = user.mention
                embed.set_field_at(index = 0,name ='Tank :',value=Mbrs[0],inline=True)
                await payload.member.add_roles(T_role)
            else:
                await user.send(content='Plus de place pour ce rôle')
        elif reaction.emoji==bot.get_emoji(HEAL):
            if reaction.count == 2:
                Mbrs[1] = user.mention
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                await payload.member.add_roles(H_role)
            elif reaction.count == 3 :
                Mbrs[2] = user.mention
                embed.set_field_at(index=2, name='Heal 2 :', value=Mbrs[2], inline=True)
                await payload.member.add_roles(f"Heal_{role_list[role_list.index(embed.author)]}")
            else:
                await user.send(content="Désolé, il n'y a plus de place pour ce rôle, reste à l'affut en cas de désistement")
        elif reaction.emoji == bot.get_emoji(DD):
            if reaction.count == 2:
                Mbrs[3] = user.mention
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                await payload.member.add_roles(H_role)
            elif reaction.count == 3 :
                Mbrs[4] = user.mention
                embed.set_field_at(index=4, name='DD 2 :', value=Mbrs[4], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 4 :
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
            elif reaction.count == 7 :
                Mbrs[8] = user.mention
                embed.set_field_at(index=8, name='DD 6 :', value=Mbrs[8], inline=True)
                await payload.member.add_roles(D_role)
            elif reaction.count == 8 :
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
                dm_channel= await user.create_dm()
                dm_channel.send('Plus de place pour ce role')
    await msg.edit(embed=embed)

@bot.event
async def on_raw_reaction_remove(payload):
    guild = discord.utils.get(bot.guilds, name=GUILD)
    chan= guild.get_channel(payload.channel_id)
    msg=await chan.fetch_message(payload.message_id)
    user=bot.get_user(payload.user_id)
    member = get(guild.members, id=payload.user_id)
    reaction = get(msg.reactions, emoji=payload.emoji)
    embed=msg.embeds[0]

    T_role = get(guild.roles, name=f"Tank_{embed.title}")
    H_role = get(guild.roles, name=f"Heal_{embed.title}")
    D_role = get(guild.roles, name=f"DD_{embed.title}")

    if user.name!='Yvondir Ateldil':
        if payload.emoji==bot.get_emoji(TANK):
            if reaction.count==1:
                Mbrs[0] = 'Place libre'
                embed.set_field_at(index = 0,name ='Tank :',value=Mbrs[0],inline=True)
                await member.remove_roles(T_role)

        elif reaction.emoji==bot.get_emoji(HEAL):
            if reaction.count == 1:
                Mbrs[1]=Mbrs[2]
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                await member.remove_roles(H_role)
            elif reaction.count == 2 :

                if Mbrs[1]==user.mention:
                    Mbrs[1]=Mbrs[2]
                    Mbrs[2]='Place libre'
                else:
                    Mbrs[2] = 'Place libre'
                embed.set_field_at(index=1, name='Heal 1 :', value=Mbrs[1], inline=True)
                embed.set_field_at(index=2, name='Heal 2 :', value=Mbrs[2], inline=True)
                await member.remove_roles(H_role)

        elif reaction.emoji == bot.get_emoji(DD):
            if reaction.count == 1:
                Mbrs[3]="Place Libre"
                embed.set_field_at(index=3, name='DD 1 :', value=Mbrs[3], inline=True)
                await member.remove_roles(D_role)
            elif reaction.count == 2 :
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
            elif reaction.count == 3 :
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
            elif reaction.count == 6 :
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
            elif reaction.count == 7 :
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

bot.run(TOKEN)