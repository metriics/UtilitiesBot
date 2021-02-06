import discord
import time as t
from datetime import date
import os
import json

jsonLog = {}
jsonLog['records'] = []
logChannel = None
workingDir = "/home/pi/Utilities"
token = ""
with open(workingDir+"/token", 'r') as file:
    token = file.read().replace('\n', '')

client = discord.Client()

@client.event
async def on_ready():
    global logChannel

    print('Logged in as: {0.user}'.format(client))
    if isinstance(GetLogChannel(), str):
        logChannel = GetLogChannel()
    else:
        print("No log channel set")

@client.event
async def on_message(message):
    global logChannel

    if message.author == client.user:
        return
    else:
        if message.content.startswith("!"):
            command = message.content.strip('!')
            
            if command == "stop":
                await client.close()
            
            elif command == "setLogChannel":
                SetLogChannel(str(message.channel.name))
                print("Log channel set to: {}".format(logChannel))
                await message.channel.send("**Log channel set to:** {}".format(message.channel.mention))
           
            elif command.startswith("log"):
                if logChannel == None:
                    await message.channel.send("**No log channel set**")
                else:
                    if isinstance(logChannel, str):
                        logChannel = discord.utils.get(message.guild.channels, name=logChannel)
                    
                    numbersToLog = command.split(' ')
                    wins = numbersToLog[1]
                    losses = numbersToLog[2]
                    ratio = int(numbersToLog[1])/int(numbersToLog[2])
                    wlText = "Wins: {0} | Losses: {1}\nRatio: {2}".format(wins, losses, ratio)
                    today = date.today().strftime("%B %d, %Y")
                    await logChannel.send("```{0}\n{1}```".format(today, wlText))

                    jsonLog['records'].append({
                        'date': today,
                        'wins': wins,
                        'losses': losses
                    })
                    AppendJsonData()

            elif command == "ratio":
                if GetJsonData() == 1:
                    print(jsonLog)
                    wins = 0
                    losses = 0
                    for record in jsonLog['records']:
                        wins += int(record['wins'])
                        losses += int(record['losses'])
                    ratio = wins/losses
                    await message.channel.send("**Total W/L ratio:** {}".format(ratio))

                else:
                    await message.channel.send("**No logs exist**")

            
            elif command == "clearSetLogChannel":
                if ClearLogChannel():
                    await message.channel.send("**Cleared set log channel**")
                
                else:
                    await message.channel.send("**Failed to clear set log channel**")

            elif command.startswith('clearLogFile'):
                args = command.split(' ')
                if len(args) > 1:
                    if args[1] == "true":
                        ClearJsonData(True)
                        await message.channel.send("**Cleared log file and data in memory**")

                    else:
                        ClearJsonData(False)
                        await message.channel.send("**Cleared log file**")


def GetLogChannel():
    global logChannel
    global workingDir

    try:
        with open(workingDir + "/logChannel", 'r') as file:
            logChannel = file.read().replace('\n', '')
            return logChannel
    except FileNotFoundError:
        return None
    
def SetLogChannel(channel):
    global logChannel

    try:
        with open(workingDir + "/logChannel", 'x') as file:
            file.write(channel)

        logChannel = channel
    except FileExistsError:
        return -1

def ClearLogChannel():
    global logChannel

    if os.path.exists(workingDir + "/logChannel"):
        os.remove(workingDir + "/logChannel")
        logChannel = None
        return True
    else:
        return False

def GetJsonData():
    global jsonLog

    try:
        with open(workingDir + "/log.txt") as json_file:
            jsonLog = json.load(json_file)
            return 1
    except FileNotFoundError:
        print("File not found")
        return -1

def AppendJsonData():
    global jsonLog

    try:
        with open(workingDir + "/log.txt", 'x') as json_file:
            json.dump(jsonLog, json_file)

        jsonLog = {}
        jsonLog['records'] = []
        return 1
    except FileExistsError:
        newData = jsonLog
        GetJsonData()
        for record in newData['records']:
            jsonLog['records'].append(record)
        
        with open(workingDir + "/log.txt", 'w') as json_file:
            json.dump(jsonLog, json_file)

        jsonLog = {}
        jsonLog['records'] = []

        return 0

def ClearJsonData(includeCurrent):
    if includeCurrent:
        global jsonLog
        jsonLog = {}
        jsonLog['records'] = []
        if os.path.exists(workingDir + "/log.txt"):
            os.remove(workingDir + "/log.txt")
            return True
        else:
            return False
    else:
        if os.path.exists(workingDir + "/log.txt"):
            os.remove(workingDir + "/log.txt")
            return True
        else:
            return False

client.run(token)
