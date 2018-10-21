# Imports
import sys
import discord
import asyncio
import json

client = discord.Client()

@client.event
async def on_ready():
    print('Started bot as %s (%s)' % (client.user.name, client.user.id))
@client.event
async def on_message(message):
    if message.content.startswith(prefix):
        # message is valid command
        command = message.content.split(" ")[0][1:]
        arguments = message.content.split(" ")[1:]
        print("[%s/%s](%s): %s" % (message.server, message.channel, message.author.name+"#"+message.author.discriminator, message.content))
        if command in commandAliases: command = commandAliases[command]
        checkUser(message.author.id)
        upl = getPermissionLevel(message.author)
        if upl==0:
            # user is blacklisted
            return
        elif command in commands:
            if upl >= permissionLevels[command]:
                # Command exists and user can execute it.
                await commands[command](message, arguments)
            else:
                # User isn't allowed to execute that command
                await client.send_message(message.channel, "Permission error, this command requires permission level %s, you have %s." % (permissionLevels[command], upl))
        else:
            # Command doesn't exist.
            await client.send_message(message.channel, "Unknown command '%s'" % command)
@client.event
async def on_reaction_add(reaction, user):
    emoji = ""
    if type(reaction.emoji)==discord.Emoji: emoji = reaction.emoji.name
    else: emoji = reaction.emoji
    if emoji in reactionModifiers and user != reaction.message.author:
        config["users"][reaction.message.author.id]["balance"] += reactionModifiers[emoji]
        config["users"][reaction.message.author.id]["awards"] += reactionModifiers[emoji]
        saveConfig()
@client.event
async def on_reaction_remove(reaction, user):
        emoji = ""
        if type(reaction.emoji)==discord.Emoji: emoji = reaction.emoji.name
        else: emoji = reaction.emoji
        if emoji in reactionModifiers and user != reaction.message.author:
            config["users"][reaction.message.author.id]["balance"] -= reactionModifiers[emoji]
            config["users"][reaction.message.author.id]["awards"] -= reactionModifiers[emoji]
            saveConfig()
def checkUser(uid):
    if not uid in config["users"]:
        config["users"][uid] = {"balance":0, "permissionLevel":1, "awards":0}
        saveConfig()
def checkRole(rid):
    if not rid in config["roles"]:
        config["roles"][rid] = {"permissionLevel":1}
def saveConfig():
    with open("bot.json", "w") as f:
        f.write(json.dumps(config, sort_keys=True, indent=2))
def loadConfig():
    global config
    try:
        with open("bot.json") as f:
            config = json.loads(f.read())
    except Exception as e:
        print("Could not load config file\n", e)
        sys.exit(1)
def formatCurrency(amount):
    return currencyFormat.replace("{AMOUNT}", str(amount)).replace("{SYMBOL}", currencySymbol)
def getPermissionLevel(user):
    uid = user.id
    highestpl = config["users"][uid]["permissionLevel"]
    if highestpl==0: return 0
    for role in user.roles:
        if role.id in config["roles"]:
            if config["roles"][role.id]["permissionLevel"]==0:
                return 0
            elif config["roles"][role.id]["permissionLevel"] > highestpl:
                highestpl = config["roles"][role.id]["permissionLevel"]
    return highestpl
async def balance(msg, args):
    uid = msg.author.id
    checkUser(uid)
    ubal = config["users"][uid]["balance"]
    await client.send_message(msg.channel, "You have %s" % formatCurrency(ubal))
async def modifybalance(msg, args):
    target = msg.author
    if(len(args)<1 or len(args) > 2):
        await client.send_message(msg.channel, "Command syntax: `%sbalmod [input] [user (optional)]`. input can be relative (eg. +20, -5) or absolute (eg. 10)" % prefix)
        return
    elif(len(args)==2):
        # Target was specified
        if len(msg.mentions) < 1:
            await client.send_message(msg.channel, "Syntax error, second argument must be a user mention or nothing (got '%s')" % args[1])
        target = msg.mentions[0]
    amount = 0
    try:
        amount = int(args[0])
    except:
        await client.send_message(msg.channel, "Syntax error, first argument must be an integer preceeded by a +, -, or nothing (got '%s')" % args[0])
        return
    uid = target.id
    checkUser(uid)
    oldbal = config["users"][uid]["balance"]
    if(args[0].startswith('+') or args[0].startswith('-')):
        # The input was relative
        config["users"][uid]["balance"] += amount
    else:
        # The input was absolute
        config["users"][uid]["balance"] = amount
    saveConfig()
    await client.send_message(msg.channel, "Updated %s's balance to %s. (was %s)" % (target.name, formatCurrency(config["users"][uid]["balance"]), formatCurrency(oldbal)))
async def permissionlevel(msg, args):
    if len(args)==0:
        uid = msg.author.id
        checkUser(uid)
        newmsg = "Your highest permission level is %s, gained from:\n" % getPermissionLevel(msg.author)
        newmsg += "User level: %s" % config["users"][uid]["permissionLevel"]
        for role in msg.author.roles:
            if role.id in config['roles']:
                newmsg += "\n[ROLE] %s: %s" % (role.name, config["roles"][role.id]["permissionLevel"])
        await client.send_message(msg.channel, newmsg)
    elif len(args)==1:
        if(len(msg.mentions)==0):
            # the mention was not a user mention
            userole = ""
            if len(msg.role_mentions)==0:
                # the mention was not a role mention
                matches = 0
                for role in msg.server.roles:
                    if role.name==args[0]:
                        matches += 1
                        userole = role
                if matches==0:
                    await client.send_message(msg.channel, "Syntax error, first argument should be a user or role mention (got %s)" % args[0])
                    return
                elif matches > 1:
                    await client.send_message(msg.channel, "There's multiple roles with that name, try pinging the roles in your command or renaming one of them temporairly.")
                    return
            else:
                userole = msg.role_mentions[0]
            if userole.id in config['roles']:
                await client.send_message(msg.channel, "Role '%s' has permission level %s" % (userole.name, config["roles"][userole.id]["permissionLevel"]))
            else:
                await client.send_message(msg.channel, "Role '%s' doesn't have a permission level set" % userole.name)
        else:
            uid = msg.mentions[0].id
            checkUser(uid)
            newmsg = "%s's highest permission level is %s, gained from:\n" % (msg.mentions[0].name, getPermissionLevel(msg.mentions[0]))
            newmsg += "User level: %s" % config["users"][uid]["permissionLevel"]
            for role in msg.mentions[0].roles:
                if role.id in config['roles']:
                    newmsg += "\n[ROLE] %s: %s" % (role.name, config["roles"][role.id]["permissionLevel"])
            await client.send_message(msg.channel, newmsg)
    else:
        # this is to set a level
        value = args[1]
        if len(msg.mentions)>0:
            # modify a user permission level
            target = msg.mentions[0]
            checkUser(target.id)
            try:
                config["users"][target.id]["permissionLevel"] = int(value)
                saveConfig()
            except:
                await client.send_message(msg.channel, "Syntax error, second argument must be an integet (got %s)" % value)
                return
            await client.send_message(msg.channel, "Updated %s's permission level to %s." % (target.name, value))
        elif len(msg.role_mentions)>0:
            target = msg.role_mentions[0]
            checkRole(target.id)
            try:
                config["roles"][target.id]["permissionLevel"] = int(value)
                saveConfig()
            except:
                await client.send_message(msg.channel, "Syntax error, second argument must be an integet (got %s)" % value)
                return
            await client.send_message(msg.channel, "Updated %s's permission level to %s." % (target.name, value))
async def reloadConfig(msg, args):
    loadConfig()
    await client.send_message(msg.channel, "Reloaded config!")
async def help(msg, args):
    if len(args)==0:
        newmsg = "Command list:"
        for key,value in commands.items():
            newmsg += "\n  %s%s" % (prefix,key)
        await client.send_message(msg.channel, newmsg)
    else:
        topic = args[0]
        if topic not in commands:
            if topic in commandAliases:
                topic = commandAliases[topic]
            else:
                await client.send_message(msg.channel, "No help entry found for '%s'" % topic)
                return
        aliases = ""
        firstAlias = True
        for key,value in commandAliases.items():
            if value == topic:
                if firstAlias:
                    aliases += key
                    firstAlias = False
                else:
                    aliases += ", %s" % key

        help_message = helpEntries[topic]
        help_message = help_message.replace("{PREFIX}", prefix).replace("{PERMISSIONLEVEL}", str(permissionLevels[topic])).replace("{ALIASES}", aliases).replace("{CURRENCYSINGULAR}", currencyNameSingular)
        await client.send_message(msg.channel,"__**%s**__\n%s" % (topic, help_message))
async def awards(msg, args):
    target = msg.author
    if len(msg.mentions)>0: target = msg.mentions[0]
    checkUser(target.id)
    uawards = config["users"][target.id]["awards"]
    if target!=msg.author: await client.send_message(msg.channel, "%s has received %s lifetime award%s" % (target.name, uawards, "" if uawards == 1 else "s"))
    else: await client.send_message(msg.channel, "You have received %s lifetime award%s" % (uawards, "" if uawards == 1 else "s"))

config = {}
loadConfig()
prefix = "*"
currencyNameSingular = "Flapjack"
currencyNamePleurl = "Flapjacks"
currencySymbol = "ƒ"
currencyFormat = "{SYMBOL}{AMOUNT}"
commands = {
    "balance":balance,
    "modifybalance":modifybalance,
    "permissionlevel":permissionlevel,
    "reloadconfig":reloadConfig,
    "help":help,
    "awards":awards}
commandAliases = {
    "bal":"balance",
    "pl":"permissionlevel",
    "rlcfg":"reloadconfig",
    "h":"help"
    "modbal":"modifybalance"}
helpEntries = {
    "help":"Shows a detailed description of a command, or a command list if none is provided.\nSyntax: `{PREFIX}help [command (optional)]`\nPermission level {PERMISSIONLEVEL}\nAliases: {ALIASES}",
    "balance":"Show the balance for the specified user (or yourself if none is given).\nSyntax: `{PREFIX}balance [target (optional)]`\ntarget: User to show the balance of\nPermission level {PERMISSIONLEVEL}\nAliases: {ALIASES}",
    "modifybalance":"Modifies the balance of the specified user (or yourself if none is given) by the specified value.\nSyntax: `{PREFIX}balmod [value] [target (optional)]`\nvalue: the value to modify the balance by. Can be relative (eg +20, -10) or absolute (eg 5)\ntarget: User to modify the balance of.\nPermission level {PERMISSIONLEVEL}\nAliases: {ALIASES}",
    "permissionlevel":"Gets or sets the permission level for the specified user (or yourself if none is given)\nSyntax: `{PREFIX}permissionlevel [target (optional)] [value (optional)]`\ntarget: the user who's permission level to get or set\nvalue: if given, set this as the target's permission level.\nPermission level {PERMISSIONLEVEL}\n\nAliases: {ALIASES}",
    "reloadconfig":"Reloads the bot's config.\nSyntax: `{PREFIX}reloadconfig`\nPermission level {PERMISSIONLEVEL}\nAliases: {ALIASES}",
    "awards":"Shows the specified user's lifetime {CURRENCYSINGULAR} reward count (or yours if none is given)\nSyntax: `{PREFIX}awards [target (optional)]`\ntarget: the user to display the awards of\nPermission level {PERMISSIONLEVEL}\nAliases: {ALIASES}"}
permissionLevels = {
    "balance":1, # Anyone can use this command
    "modifybalance":3, # Only moderators can use this
    "permissionlevel":3,
    "reloadconfig":3,
    "help":1,
    "awards":1}
reactionModifiers = {
    "logo":-1,
    "🍆":1
}
client.run(config["token"])
