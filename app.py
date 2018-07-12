#import traceback
#import sys
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import sqlite3
import os


description = 'Verwaltet Koordinaten.'
command_prefix='.'
case_insensitive=True
bot = commands.Bot(
    command_prefix=command_prefix,
    description=description,
    case_insensitive=case_insensitive)


@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)
    print('          id: ' + str(bot.user.id))
    print('- - - - - - -')
    await bot.change_presence(activity=discord.Game(name='.help | by SerWampe'))


@bot.command(ignore_extra=False, aliases=['show'])
async def coords(ctx, username:str):
    '''Zeigt die Koordinaten von <username>'''
    cursor.execute('''SELECT corp, username, pwr, x, y, ts_str FROM gamer WHERE username=? COLLATE NOCASE ORDER by id desc LIMIT 1''', (username,))
    row = cursor.fetchone()
    if row is None:
        await ctx.send('Kein Eintrag für \"{}\" gefunden!'.format(username))
    else:
        await ctx.send('[{}] {}, {} mio, ({} : {}) | {}'.format(row[0], row[1], row[2], row[3], row[4], row[5]))


@coords.error
async def coords_error(ctx, exception):
    await ctx.send(exception)
    if type(exception) is commands.MissingRequiredArgument:
        await ctx.send('Es muss ein Argument <username> eingegeben werden! \"User Name\" wenn ein Leerzeichen im Namen ist.')
    if type(exception) is commands.TooManyArguments:
        await ctx.send('Es darf nur ein Argument <username> eingegeben werden! \"User Name\" wenn ein Leerzeichen im Namen ist.')


#@tag.command(pass_context=True, aliases=['delete'])
@bot.command(ignore_extra=False)
async def range(ctx, pwr:int):
    '''Zeigt Einträge in Range von <pwr>'''
    rmin = pwr/5
    rmax = pwr*5
    cursor.execute('''SELECT corp, username, pwr, x, y, ts_str FROM gamer WHERE pwr BETWEEN ? AND ? ORDER by pwr asc''', (rmin, rmax,))
    all_rows = cursor.fetchall()
    if len(all_rows) == 0:
        await ctx.send('Kein passender Eintrag gefunden!')
    else:
        for row in all_rows:
            await ctx.send('[{}] {}, {} mio, ({} : {}) | {}'.format(row[0], row[1], row[2], row[3], row[4], row[5]))


@range.error
async def range_error(ctx, exception):
    await ctx.send(exception)
    if type(exception) is commands.BadArgument:
        await ctx.send('Das Argument <pwr> muss eine Zahl sein!')
    if type(exception) is commands.MissingRequiredArgument:
        await ctx.send('Es muss ein Argument <pwr> eingegeben werden!')
    if type(exception) is commands.TooManyArguments:
        await ctx.send('Es darf nur ein Argument <pwr> eingegeben werden!')
        


@bot.command(ignore_extra=False)
async def range2(ctx, rmin:int, rmax:int):
    '''Zeigt Einträge mit Kraft zwischen <rmin> und <rmax>'''
    cursor.execute('''SELECT corp, username, pwr, x, y, ts_str FROM gamer WHERE pwr BETWEEN ? AND ? ORDER by pwr asc''', (rmin, rmax,))
    all_rows = cursor.fetchall()
    if len(all_rows) == 0:
        await ctx.send('Kein passender Eintrag gefunden!')
    else:
        for row in all_rows:
            await ctx.send('[{}] {}, {} mio, ({} : {}) | {}'.format(row[0], row[1], row[2], row[3], row[4], row[5]))


@range2.error
async def range2_error(ctx, exception):
    await ctx.send(exception)
    if type(exception) is commands.BadArgument:
        await ctx.send('Die Argumente <rmin> und <rmax> müssen Zahlen sein!')
    if type(exception) is commands.MissingRequiredArgument:
        await ctx.send('Es müssen zwei Argumente <rmin> und <rmax> eingegeben werden!')
    if type(exception) is commands.TooManyArguments:
        await ctx.send('Es dürfen nur zwei Argumente eingegeben werden!')


@bot.command()
async def add(ctx, corp:str, username:str, pwr:int, x:int, y:int):
    '''Fügt die Koordinaten zur Datenbank hinzu'''

    ts_str = datetime.now().isoformat(sep=' ', timespec='seconds')
    author = str(ctx.author)
    guild = str(ctx.guild)
        
    cursor.execute('''INSERT INTO gamer(corp, username, pwr, x, y, ts_str, author, guild)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', (corp, username, pwr, x, y, ts_str, author, guild))
    db.commit()


@add.error
async def add_error(ctx, exception):
    await ctx.send(exception)
    if type(exception) is commands.BadArgument:
        await ctx.send('Die Argumente <pwr>, <x> und <y> müss Zahlen sein!')
    if type(exception) is commands.MissingRequiredArgument:
        await ctx.send('Es müssen fünf Argumente eingegeben werden! Benutze \".help add\"')


#@bot.command()
#async def foo(ctx):
#    await ctx.send('Hallo {0.author} {0.guild} {0.channel}'.format(ctx))


# Creates or opens a file called usercoords with a SQLite3 DB
db = sqlite3.connect('usercoords2.db')
# Get a cursor object
cursor = db.cursor()
# Check if table users does not exist and create it
cursor.execute('''CREATE TABLE IF NOT EXISTS gamer(
    id INTEGER PRIMARY KEY,
    corp TEXT,
    username TEXT,
    pwr INTEGER,
    x INTEGER,
    y INTEGER,
    ts_str TEXT,
    author TEXT,
    guild TEXT)''')
# Commit the change
db.commit()


bot.run(os.getenv('TOKEN'))


db.close()