import discord
import time as t

token = ""
with open('token', 'r') as file:
    token = file.read().replace('\n', '')

client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as: {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        if message.content.startswith("!"):
            command = message.content.strip('!')
            if command == "stop":
                try:
                    await client.close()
                    print("Disconnected, quitting...")
                except:
                    print("Could not disconnect.")

@client.event
async def on_member_update(before, after):
    print("[{0}] {1} {2}: ".format(t.asctime(t.time), before.name, before.discriminator))

def writeToLog(before, after):
    line = "[{0}] {1} {2}: ".format(t.asctime(t.time), before.name, before.discriminator)

    # check what changed
    if (before.status != after.status):
        line += "{0} -> {1}".format(before.status, after.status)
    elif (before.activity != after.activity):
        line += "{0} -> {1}".format(before.activity, after.activity)
    elif (before.nick != after.nick):
        line += "{0} -> {1}".format(before.nick, after.nick)
    elif (before.roles != after.roles):
        line += "{0} -> {1}".format(before.roles, after.roles)

client.run(token)
