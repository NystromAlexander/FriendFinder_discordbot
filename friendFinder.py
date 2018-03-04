import discord
import asyncio
import re
import json
from discord.ext import commands

nicknames = {}

description = '''My purpose is to find which server your friends are Connected to.
Only requirement is that I'm present on that server.'''
bot = commands.Bot(command_prefix='!', description=description)

master = 'replace with id of owner'

async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    read_nicknames()

bot.add_listener(on_ready)

@bot.command(pass_context=True, description='Give me the name of your friend and I\'ll try to find them.')
async def find(ctx, name : str):
    user = ctx.message.author.id
    if user in nicknames :
        nicks = nicknames[user]
        name = nicks[name] if name in nicks else name
        print("Using nickname")

    use_desc = 1 if re.search("#[0-9]{4}$", name) != None else 0
    name = name.casefold()
    connection = find_connection(name, use_desc)

    if connection == None :
        await bot.reply("{} is Not connected to a known server".format(name))
    else :
        await bot.reply("Your friend {}\n Is connected to Server: {}\n in Channel: {}".format(name,connection[0], connection[1]))




@bot.command(pass_context=True, description='Adds a nickname for your friend.\n The name has to have their discriminator i.e #xxxx')
async def addNick(ctx, name : str, nickname : str) :
    # print(name)
    user = ctx.message.author.id
    # print(user)
    if re.search("#[0-9]{4}$", name) == None :
        await bot.reply("You have to include their discriminator ({}#xxxx)".format(name))
        return
    if user not in nicknames:
        nicknames[user] = {}

    nicknames[user][nickname] = name.casefold()
    backup_nicknames()
    print(nicknames)
    await bot.reply("You have given {} the nickname {}".format(name, nickname))



@bot.command(pass_context=True, description='Lists your nicknames.')
async def listNicks(ctx) :
    user = ctx.message.author.id
    print(nicknames)
    if user not in nicknames :
        await bot.reply("You do not have any nicknames rigistred.")
        return
    nicks = nicknames[user]

    await bot.reply("You have the following nicknames registred.")
    for name in nicks.keys() :
        print("nick:  {} name: {}".format(name, nicks[name]))
        await bot.reply("Name: {} Nickname: {}".format(nicks[name], name))



@bot.command(pass_context=True, description="Finds all friends with a registred nickname.")
async def findAll(ctx) :
    user = ctx.message.author.id
    if user not in nicknames :
        await bot.reply("You do not have any nicknames rigistred.")
        return
    nicks = nicknames[user]

    for name in nicks.keys() :
        connection  = find_connection(nicks[name], True)
        if connection != None :
            await bot.reply("Friend: {} \n Server: {} \n Channel: {}".format(nicks[name], connection[0], connection[1]))


@bot.command(pass_context=True, description="Removes a nickname rigistred to a friend.")
async def rmNick(ctx, nickname : str) :
    user = ctx.message.author.id
    if user not in nicknames :
        await bot.reply("You do not have any nicknames rigistred.")
        return
    nicks = nicknames[user]

    if nickname not in nicks :
        await bot.reply("You don't not have the nickname \"{}\" registred.".format(nickname))
        return

    tmp_name = nicks[nickname]
    del nicks[nickname]
    backup_nicknames()
    if nickname in nicks :
        print("Could not remove {} from the dictionary {}".format(nickname, nicks))
    else :
        await bot.reply("You removed the nickname {} for {}".format(nickname, tmp_name))



@bot.command(pass_context=True, description="Feeling lonely? look if any of your closest friends are online.")
async def lonely(ctx) :
        user = ctx.message.author.id
        found = False
        if user not in nicknames :
            await bot.reply("You do not have any nicknames rigistred.")
            return
        nicks = nicknames[user]

        for name in nicks.keys() :
            connection  = find_connection(nicks[name], True)
            if connection != None :
                if found is False :
                    await bot.reply("I found you some friends that are online!")
                    found = True
                await bot.reply("Friend: {} \n Server: {} \n Channel: {}".format(nicks[name], connection[0], connection[1]))
        if found is False :
            await bot.reply("I'm sorry I could not find any friends online! :frowning2:")



@bot.command(pass_context=True)
async def backup(ctx) :
    user = ctx.message.author.id
    if user != master :
        await bot.reply("You do not have permission")
        return
    backup_nicknames()



def find_connection(name, desc):
    servers = bot.servers
    connection = []
    for server in servers:
        # print("Server: {}".format(server.name))
        member = server.members
        for user in member:
            if (desc):
                full_name = (user.name + "#" + user.discriminator).casefold()
            else :
                full_name = user.name.casefold()
            # print("member: {}".format(str(full_name)))

            if full_name == name :
                if user.voice.voice_channel is not None:
                    # print("  Connected to channel {}".format(user.voice.voice_channel.name))
                    connection = [server.name, user.voice.voice_channel.name]

    if len(connection) == 0 :
        return None
    else :
        return connection

def backup_nicknames() :
    nick_json = json.dumps(nicknames)
    nick_file = open("nicknames.json","w")
    nick_file.write(nick_json)
    nick_file.close()

def read_nicknames() :
    global nicknames
    nick_file = open("nicknames.json", "r")
    nicknames = json.load(nick_file)
    print(nicknames)
    nick_file.close()

bot.run('token')
