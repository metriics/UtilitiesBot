import discord
import time as t
from datetime import date
import os
import json


jsonLog = {}
jsonLog['records'] = []
logChannel = None
episode = ""
act = ""
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

    status = GetLastEpisodeAct()
    if status == -1:
        print("No log file found")
    elif status == 0:
        print("No logs in log file")
    elif status == 1:
        print("Got {0}, {1} from log file".format(episode, act))

@client.event
async def on_message(message):
    global logChannel, episode, act

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
                    await message.delete()

                    jsonLog['records'].append({
                        'date': today,
                        'episode': episode,
                        'act': act,
                        'wins': wins,
                        'losses': losses
                    })
                    AppendJsonData()

            elif command.startswith("ratio"):
                args = command.split(" ")

                # figure out what we are looking for. Total, episode x or episode x act y.
                lookingFor = []
                print(args)
                if len(args) > 2: # episode x act y ratio
                    lookingFor[0] = "Episode {}".format(args[1])
                    lookingFor[1] = "Act {}".format(args[2])
                elif len(args) > 1: # episode x ratio
                    lookingFor[0] = "Episode {}".format(args[1])

                if GetJsonData() == 1:
                    if len(lookingFor) == 0: # total ratio
                        wins = 0
                        losses = 0
                        for record in jsonLog['records']:
                            wins += int(record['wins'])
                            losses += int(record['losses'])
                        if losses == 0:
                            losses = 1 # dont divide by zero
                        ratio = wins/losses
                        await message.channel.send("**Total W/L ratio:** {}".format(ratio))
                    elif len(lookingFor) == 1: # episode x ratio
                        matchingGames = 0
                        wins = 0
                        losses = 0
                        for record in jsonLog['records']:
                            if record['episode'] == lookingFor[0]:
                                wins += int(record['wins'])
                                losses += int(record['losses'])
                                matchingGames += 1

                        if matchingGames > 0:
                            if losses == 0:
                                losses = 1 # dont divide by zero
                            ratio = wins/losses
                            await message.channel.send("**{0} W/L ratio:** {1}".format(lookingFor[0], ratio))
                        else:
                            await message.channel.send("**No games found in:** {0}".format(lookingFor[0]))
                    elif len(lookingFor) == 2: # episode x act y ratio
                        matchingGames = 0
                        wins = 0
                        losses = 0
                        for record in jsonLog['records']:
                            if record['episode'] == lookingFor[0]:
                                if record['act'] == lookingFor[1]:
                                    wins += int(record['wins'])
                                    losses += int(record['losses'])
                                    matchingGames += 1

                        if matchingGames > 0:
                            if losses == 0:
                                losses = 1 # dont divide by zero
                            ratio = wins/losses
                            await message.channel.send("**{0} {1} W/L ratio:** {2}".format(lookingFor[0], lookingFor[1], ratio))
                        else:
                            await message.channel.send("**No games found in:** {0} {1}".format(lookingFor[0], lookingFor[1]))

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

            elif command.startswith('setEpisode'):
                args = command.split(' ')
                if len(args) > 1:
                    episode = "Episode " + args[1]
                    await message.channel.send("**Set to:** {}".format(episode))
                else:
                    await message.channel.send("**Incorrect amount of arguments**")
            
            elif command.startswith('setAct'):
                args = command.split(' ')
                if len(args) > 1:
                    act = "Act " + args[1]
                    await message.channel.send("**Set to:** {}".format(act))
                else:
                    await message.channel.send("**Incorrect amount of arguments**")



def GetLogChannel():
    global logChannel, workingDir

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

def GetLastEpisodeAct():
    global jsonLog, episode, act

    try:
        with open(workingDir + "/log.txt") as json_file:
            jsonLog = json.load(json_file)
            if len(jsonLog['records']) > 0:
                episode = jsonLog['records'][len(jsonLog['records'])-1]['episode']
                act = jsonLog['records'][len(jsonLog['records'])-1]['act']
                return 1
            else:
                return 0
    except FileNotFoundError:
        print("File not found")
        return -1


client.run(token)
