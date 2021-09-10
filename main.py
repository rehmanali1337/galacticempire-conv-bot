from discord.ext import commands
import discord
import config
# from exts import store
from dislash import InteractionClient


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)
slash = InteractionClient(bot)


cogs_list = ['conversation']
# cogs_list = ["galactics"]


@bot.event
async def on_ready():
    # await setup_store()
    for cog in cogs_list:
        bot.load_extension(f'Cogs.{cog}')
    print('We have logged in as {0.user}'.format(bot))


if __name__ == '__main__':
    bot.run(config.BOT_TOKEN)
