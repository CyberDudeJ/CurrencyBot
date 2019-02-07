# CurrencyBot

This bot is designed to be a simple to use Discord currency bot.
------
## Features:

This bot has some neat features: It comes with permissions that are based on user IDs and role IDs so you can give certain people access to certain things, and the 'pl' command can query permission levels aswell as set them.

Setting someone's permission level to -1 will block them from using commands completely, effectively blacklisting them from using the bot.

Among all the basic bot commands, including help (which is automatically managed, just add your commands to the lists at the bottom along with the help line) This bot is focused around being a currency bot. The main way to gain currency with this bot is to react to someone's message with a certain emoji (Can be a custom emoji too). You can customize the name of your currency, the symbol, and easily modify someone's balance using the 'modifybalance' command, which accept both absolute values (`modbal @user 10`, which sets @user's balance to 10) and relative values (`modbal @user +10/-10`, which adds or subtracts 10 from @user's balance). This is a bare-bones currency bot, so add whatever features you'd like!
