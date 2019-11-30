import os, discord, json, random, asyncio, requests

with open(os.path.dirname(__file__) + "/config.json") as f:
    config = json.load(f)
    f.close()

def getRank(summoner):
    with open(os.path.dirname(__file__) + "/config.json") as f:
        data = json.load(f)
    apiKey = data["riotKey"]
    try:
        summoner = json.loads(requests.get("https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/%s?api_key=%s" % (summoner, apiKey)).content)
        data = json.loads(requests.get("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/%s?api_key=%s" % (summoner['id'], apiKey)).content)

        for i in data:
            if i["queueType"] == "RANKED_SOLO_5x5":
                rank = {
                    "name": summoner["name"],
                    "profile": summoner["profileIconId"],
                    "tier": i["tier"][0] + i["tier"][1:].lower(),
                    "rank": i["rank"],
                    "lp": i["leaguePoints"],
                    "winrate": round(i["wins"] / (i["wins"] + i["losses"]) * 100, 1),
                    "games": i["wins"] + i["losses"]
                }
        return rank
    except:
        return None

def generateEmbed(data):
    colors = {
        "Iron": 0x8e898b,
        "Bronze": 0x7d553e,
        "Silver": 0x646a64,
        "Gold": 0xe3c44b,
        "Platinum": 0x275752,
        "Diamond": 0x5587c3,
        "Master": 0xce56fe,
        "Grandmaster": 0xc31f2d,
        "Challenger": 0x1f6da5
    }
    embed=discord.Embed(title=data["name"], color=colors[data["tier"]])
    embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/9.23.1/img/profileicon/" + str(data["profile"]) + ".png")
    embed.add_field(name="Games", value=data["games"], inline=False)
    embed.add_field(name="Rank", value="%s %s" % (data["tier"], data["rank"]), inline=False)
    embed.add_field(name="LP", value=data["lp"], inline=False)
    embed.add_field(name="Winrate", value=str(data["winrate"]) + "%", inline=False)
    return embed

class botClient(discord.Client):
    async def update(self):
        while True:
            with open(os.path.dirname(__file__) + "/stalkList.json") as f:
                slist = json.load(f)
                for i in slist["stalkList"]:
                    try:
                        data = getRank(i["summoner"])
                        if data is None:
                            await self.get_channel(i["id"]).send("%s not found..." % i["summoner"])
                        else:
                            await self.get_channel(i["id"]).send(embed=generateEmbed(data))
                            if data["winrate"] < 49:
                                await message.channel.send(random.choice(config["shame"]["poor"]))
                            elif data["winrate"] < 51:
                                await message.channel.send(random.choice(config["shame"]["average"]))
                            else:
                                await message.channel.send(random.choice(config["shame"]["good"]))
                    except:
                        print("Error.")
                f.close()
            await asyncio.sleep(86400)
            

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.update()

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith(config["prefix"]):
            cmd = message.content.split(" ")[0][len(config["prefix"]):]
            args = message.content.split(" ")[1:]

            if cmd == "shame":
                if len(args) == 0:
                    await message.channel.send("Please enter a summoner name to shame")
                else:
                    summoner = " ".join(args)
                    
                    data = getRank(summoner)
                    if data is None:
                        await message.channel.send("%s not found..." % (summoner))
                    else:
                        await message.channel.send(embed=generateEmbed(data))
                        if data["winrate"] < 49:
                            await message.channel.send(random.choice(config["shame"]["poor"]))
                        elif data["winrate"] < 51:
                            await message.channel.send(random.choice(config["shame"]["average"]))
                        else:
                            await message.channel.send(random.choice(config["shame"]["good"]))

            if cmd == "stalk":
                if not message.author.permissions_in(message.channel).administrator: 
                    await message.channel.send("You must be an administrator to stalk people. Don't ask why.")
                else:
                    summoner = " ".join(args)
                    data = getRank(summoner)
                    if(data):
                        
                        with open(os.path.dirname(__file__) + "/stalkList.json", "r") as f:
                            slist = json.load(f)
                            stalking = False
                            for i in slist["stalkList"]:
                                if message.channel.id == i["id"] and data["name"] == i["summoner"]:
                                    await message.channel.send("Already stalking %s in channel %s" % (i["summoner"], message.channel))
                                    stalking = True
                            if not stalking:
                                await message.channel.send("Now stalking %s in %s" % (data["name"], message.channel.name))
                                entry = {
                                    "id": message.channel.id,
                                    "summoner": data["name"]
                                }
                                slist["stalkList"].append(entry)
                                f.close()
                            with open(os.path.dirname(__file__) + "/stalkList.json", "w") as f:
                                json.dump(slist, f)
                                f.close()
                    else:
                        await message.channel.send("%s not found..." % (summoner))
    
            if cmd == "stop":
                if len(args) == 0:
                    await message.channel.send("Removing all targets from channel %s" % (message.channel))
                    with open(os.path.dirname(__file__) + "/stalkList.json", "r") as f:
                            slist = json.load(f)
                            slist["stalkList"] = [x for x in slist["stalkList"] if not x["id"] == message.channel.id]
                            f.close()
                    with open(os.path.dirname(__file__) + "/stalkList.json", "w") as f:
                        json.dump(slist, f)
                        f.close()
                else:
                    summoner = " ".join(args)
                    await message.channel.send("Removing %s from channel %s" % (summoner, message.channel))
                    with open(os.path.dirname(__file__) + "/stalkList.json", "r") as f:
                            slist = json.load(f)
                            slist["stalkList"] = [x for x in slist["stalkList"] if not (x["id"] == message.channel.id and x["summoner"].lower() == summoner.lower())]
                            f.close()
                    with open(os.path.dirname(__file__) + "/stalkList.json", "w") as f:
                        json.dump(slist, f)
                        f.close()
                
client = botClient()
client.run(config["botKey"])