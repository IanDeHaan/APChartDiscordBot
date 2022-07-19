import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import datetime
import discord
import asyncio

HYPIXEL_API_KEY = "<api key here>" 
DISCORD_BOT_TOKEN = "<bot token here>"

years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

def get_ap_data(user):
    print("https://api.hypixel.net/player?key=" + HYPIXEL_API_KEY + "&name=" + user)
    data = requests.get("https://api.hypixel.net/player?key=" + HYPIXEL_API_KEY + "&name=" + user).json()
    #print(data)
    if not data["player"]:
        return None
    if "achievementRewardsNew" not in data["player"]:
        return None
    values = []
    for item in data["player"]["achievementRewardsNew"]:
        values.append((int(item[11:]), data["player"]["achievementRewardsNew"][item]))
    values.sort()
    # Normalize values
    for i in range(len(values)-1):
        if values[i+1][1] < values[i][1]:
            values[i+1] = (values[i+1][0], values[i][1])
    out = ([], [])
    for item in values:
        out[0].append(datetime.datetime.fromtimestamp(item[1]//1000))
        out[1].append(item[0])
    return out

def get_ap_chart(users):
    fig, ax = plt.subplots()
    plotted = 0
    for user in users:
        user_data = get_ap_data(user)
        if not user_data:
            continue
        plotted += 1
        #print("plotting")
        ax.plot(user_data[0], user_data[1], label=user)
    ax.legend()
    ax.grid()
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)
    fig.savefig("plot.png")
    if plotted == 0:
        return -1
    else:
        return 0




client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.lower().startswith("s!chart"):
        inp = message.content.split()[1:]
        if len(inp) <= 0:
            await message.channel.send("Ya gotta put the names you want to chart.")
            return
        if get_ap_chart(inp) == -1:
            await message.channel.send("There were no valid users to chart. Make sure you're spelling them right.")
            return
        with open("plot.png", "rb") as f:
            await message.channel.send(file=discord.File(f, "plot.png"))

client.run(DISCORD_BOT_TOKEN)