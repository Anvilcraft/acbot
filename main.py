from config import *
import discord
from discord.ext import commands
from datetime import datetime
import pymysql
from requests import get
from json import loads

bot = commands.Bot(command_prefix=prefix)

@bot.event #print the username and id to the console
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_member_update(before, after):
    roles = []
    for role in after.roles: #get the name of all roles except @everyone
        if(role.name != "@everyone"):
            roles.append(role.name)

    for role in ignoreRoles: #check if the user has one of the ignore roles, if yes stop here
        if role in roles:
            return
    
    rolesString = ""
    for role in roles:#try to find the name for the role in the role map and convert it. After that add it to roleString
        try:
            rolesString = rolesString + roleMap[role] + ","
        except:
            pass
    rolesString = rolesString[:-1] #remove the "," at the end
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE discord=%s", (after.id))
    if(len(cursor.fetchall()) == 0):
        cursor.execute("INSERT INTO users (discord, roles) VALUES (%s, %s)", (after.id, rolesString))
    else:
        cursor.execute("UPDATE users SET roles=%s WHERE discord=%s", (rolesString, after.id))
    db.commit()
    db.close() 
    print("updated profile for " + after.name)

@bot.event
async def on_member_join(member):
    r = get("https://data.tilera.xyz/api/acapi/discord.php?id=" + str(member.id))
    response = loads(r.text)
    try:
        ytchannel = response["ytchannel"]
    except:
        pass
    try:
        twchannel = response["twchannel"]
    except:
        pass

    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (discord, ytchannel, twchannel) VALUES (%s, %s, %s)", (member.id, ytchannel, twchannel))
    db.commit()
    db.close() 
    print(member.name + " joined the Server")

@bot.event
async def on_member_remove(member):
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE discord=%s", (member.id))
    db.commit()
    db.close()  
    print(member.name + " left the server")

@bot.command(pass_context=True, brief="set your minecraft username")
async def mc(ctx, minecraftUsername : str):
    r = get("https://data.tilera.xyz/api/acapi/mcuuid.php?id=" + minecraftUsername)
    respone = loads(r.text)
    if(respone["status"] == "404"):
        await ctx.send("Can't find your minecraft username, please check your spelling and try again.")
        return
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE discord=%s", (ctx.author.id))
    if(len(cursor.fetchall()) == 0):
        cursor.execute("INSERT INTO users (discord, mcuuid) VALUES (%s, %s)", (ctx.author, respone["uuid"]))
    else:
        cursor.execute("UPDATE users SET mcuuid=%s WHERE discord=%s", (respone["uuid"], ctx.author.id))
    db.commit()
    db.close() 
    await ctx.send("successfully updated your minecraft username")
    print(ctx.author.name + " updated his Minecraft username")    

@bot.command(pass_context=True, brief="set your YouTube channel URL")
async def yt(ctx, youTubeChannelURL):
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE discord=%s", (ctx.author.id))
    if(len(cursor.fetchall()) == 0):
        cursor.execute("INSERT INTO users (discord, ytchannel) VALUES (%s, %s)", (ctx.author, youTubeChannelURL))
    else:
        cursor.execute("UPDATE users SET ytchannel=%s WHERE discord=%s", (youTubeChannelURL, ctx.author.id))
    db.commit()
    db.close() 
    await ctx.send("successfully updated your YouTube channel URL")
    print(ctx.author.name + " updated his youtube channel URL")     

@bot.command(pass_context=True, brief="set your Twitch channel URL")
async def twitch(ctx, twitchChannelURL):
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE discord=%s", (ctx.author.id))
    if(len(cursor.fetchall()) == 0):
        cursor.execute("INSERT INTO users (discord, twchannel) VALUES (%s, %s)", (ctx.author, twitchChannelURL))
    else:
        cursor.execute("UPDATE users SET twchannel=%s WHERE discord=%s", (twitchChannelURL, ctx.author.id))
    db.commit()
    db.close() 
    await ctx.send("successfully updated your Twitch channel URL")
    print(ctx.author.name + " updated his twitch channel URL")     

@bot.command(pass_context=True, brief="updates the roles in the database of a user")
async def update(ctx, user : discord.Member = None):
    if (user == None): #check if the message author submitted a different user to check, if not use the message author
        user = ctx.message.author

    roles = []
    for role in user.roles: #get the name of all roles except @everyone
        if(role.name != "@everyone"):
            roles.append(role.name)

    for role in ignoreRoles: #check if the user has one of the ignore roles, if yes stop here
        if role in roles:
            return
    
    rolesString = ""
    for role in roles:#try to find the name for the role in the role map and convert it. After that add it to roleString
        try:
            rolesString = rolesString + roleMap[role] + ","
        except:
            pass
    rolesString = rolesString[:-1] #remove the "," at the end
    db = pymysql.connect(sqlServer,sqlUser,sqlPassword,sqlDatabase )
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE discord=%s", (user.id))
    if(len(cursor.fetchall()) == 0):
        cursor.execute("INSERT INTO users (discord, roles) VALUES (%s, %s)", (user.id, rolesString))
    else:
        cursor.execute("UPDATE users SET roles=%s WHERE discord=%s", (rolesString, user.id))
    db.commit()
    db.close() 
    await ctx.send("profile for user " + user.name + " updated")
    print("updated profile for " + user.name)

@bot.command(pass_context=True, brief="prints the ping time of the bot")
async def ping(ctx):#prints the ping and the time the bot needed to process this command
    now = datetime.utcnow()#get the current time
    delta = round((now.microsecond - ctx.message.created_at.microsecond) /1000)#substract the time the message was created from the current time 8in microsecconds), convert this to millisecconds and round
    embed = discord.Embed(title=":ping_pong: | Pong!", description="```prolog\nLatency :: " + str(round(bot.latency * 1000)) + "ms\nResponse :: " + str(delta) + "ms```")#make the response, we format it as code and select prolog as language for nice cloloring

    await ctx.message.channel.send(embed=embed)#send the prepared message

bot.run(token)#start the bot with the token in config.py