from config import *
import discord
from discord.ext import commands
from datetime import datetime

bot = commands.Bot(command_prefix=prefix)

@bot.event #print the username and id to the console
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True, brief="prints the ping time of the bot")
async def ping(ctx):#prints the ping and the time the bot needed to process this command
    now = datetime.utcnow()#get the current time
    delta = round((now.microsecond - ctx.message.created_at.microsecond) /1000)#substract the time the message was created from the current time 8in microsecconds), convert this to millisecconds and round
    embed = discord.Embed(title=":ping_pong: | Pong!", description="```prolog\nLatency :: " + str(round(bot.latency * 1000)) + "ms\nResponse :: " + str(delta) + "ms```")#make the response, we format it as code and select prolog as language for nice cloloring

    await ctx.message.channel.send(embed=embed)#send the prepared message

bot.run(token)#start the bot with the token in config.py