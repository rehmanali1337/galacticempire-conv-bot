from discord.channel import CategoryChannel
from dislash import SelectMenu, SelectOption
from discord.ext import commands
import config
import discord
from exts.cache import ListCache


class Hire(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self._close_ticket_messages = ListCache("close_ticket_messages")
        self._open_ticker_users = ListCache("open_ticket_users")

    async def create_ticket(self, reaction):
        async for message in self.bot.get_channel(reaction.channel_id).history():
            if message.id == config.TICKET_MESSAGE_ID:
                await message.remove_reaction(reaction.emoji, reaction.member)
        category = discord.utils.get(
            reaction.member.guild.categories, id=config.TICKET_CHANNELS_CATEGORY_ID)
        if self._open_ticker_users.item_exists(reaction.member.id):
            channel = self.bot.get_channel(reaction.channel_id)
            for channel in category.text_channels:
                if reaction.member in channel.overwrites.keys():
                    permissions = channel.overwrites[reaction.member]
                    if permissions.send_messages:
                        await channel.send(f'{reaction.member.mention} you already have this ticket open! Close this ticket to open a new one.')
                        return
        if len(category.text_channels) == 0:
            new_ticket_number = '10001'
        else:
            new_ticket_number = int(category.text_channels[-1].name.replace(
                'ticket-', '').strip()) + 1
        overwrites = {
            reaction.member.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            reaction.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            self.bot.user: discord.PermissionOverwrite(
                read_messages=True, send_messages=True)
        }
        ticket_channel = await category.create_text_channel(f'ticket-{new_ticket_number}', overwrites=overwrites)
        sent = await ticket_channel.send(f'{reaction.member.mention} Add reaction to this message to close this ticket!')
        await sent.add_reaction("⏹️")
        self._close_ticket_messages.add_item(sent.id)
        self._open_ticker_users.add_item(reaction.member.id)
        await self.galactics_hire(ticket_channel, reaction.member)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        if reaction.message_id == config.TICKET_MESSAGE_ID:
            await self.create_ticket(reaction)
        if self._close_ticket_messages.item_exists(reaction.message_id):
            if reaction.member.id != self.bot.user.id:
                await self.close_ticket(reaction)

    async def close_ticket(self, reaction):
        channel = self.bot.get_channel(reaction.channel_id)
        new_overwrites = discord.PermissionOverwrite()
        new_overwrites.view_channel = False
        new_overwrites.send_messages = False
        await channel.set_permissions(reaction.member, overwrite=new_overwrites)
        self._open_ticker_users.remove_item(reaction.member.id)

    @staticmethod
    def create_menu(*, labels: list = [], placeholder="Choose and option!", selections=1):
        options = list()
        for label in labels:
            opt = SelectOption(label, label)
            options.append(opt)
        return SelectMenu(
            custom_id="My Menu",
            placeholder=placeholder,
            max_values=selections,
            options=options,
        )

    @staticmethod
    def is_text(author, channel):
        def wrapper(message):
            if message.author != author:
                return False
            if message.channel != channel:
                return False
            return True
        return wrapper

    @staticmethod
    def has_image(author, channel):
        def wrapper(message):
            if message.author != author:
                return False
            if message.channel != channel:
                return False
            if len(message.attachments) == 0:
                return False
            return True
        return wrapper

    # @commands.command()
    async def galactics_hire(self, channel: discord.TextChannel, member: discord.Member):
        await channel.send("Thank you for applying for the Spaceflight…just a few questions.")
        options_labels = ["Yes", "No"]
        menu = self.create_menu(labels=options_labels)
        sent = await channel.send("Are you a galactics holder?", components=[menu])
        inter = await sent.wait_for_dropdown()
        selected = inter.select_menu.selected_options[0]
        await sent.delete()
        is_holder = selected.value
        await channel.send(f"Holder of GalacticEmpire : {is_holder}")
        if is_holder.lower() == "no":
            return
        menu = self.create_menu(labels=["Yes", "No"])
        sent = await channel.send("Have you invited 3 friends to the server?", components=[menu])
        inter = await sent.wait_for_dropdown()
        selected = inter.select_menu.selected_options[0]
        invited_3 = selected.value
        await sent.delete()
        if invited_3.lower() == "no":
            await channel.send("Please close the ticket and apply again after getting 3 invites!")
            return
        await channel.send(f"Have invited 3 friends : {invited_3}")
        sent = await channel.send("Please send !invites command to list your invites from invites bot!")
        res = await self.bot.wait_for('message', check=self.is_text(member, channel))
        q = await channel.send("Enter the discord username of 1 of your invited friends that is holding GalacticEmpire?")
        res = await self.bot.wait_for('message', check=self.is_text(member, channel))
        friend_name = res.content
        await q.delete()
        await res.delete()
        await channel.send(f'GalacticEmpire holder friend name : {friend_name}')
        options_labels = list(range(1, 11))
        options_labels.append("10+")
        menu = self.create_menu(labels=options_labels)
        sent = await channel.send("how much you are holding?", components=[menu])
        inter = await sent.wait_for_dropdown()
        selected = inter.select_menu.selected_options[0]
        await sent.delete()
        holding_value = selected.value
        await channel.send(f'Holding the value : {holding_value}')
        sent1 = await channel.send("Please send your opensea link, and a picture of your collection?")
        sent2 = await channel.send("Send link first!")
        res = await self.bot.wait_for('message', check=self.is_text(member, channel))
        opensea_link = res.content
        await sent1.delete()
        await sent2.delete()
        await res.delete()
        await channel.send(f"Opensea link : {opensea_link}")
        await channel.send("Now waiting for picture of your collection!")
        res = await self.bot.wait_for('message', check=self.has_image(member, channel))
        attachment = res.attachments[0]
        await channel.send("Thank you, a clan member will be with you soon to add you to the Spaceflight")


def setup(bot: commands.Bot):
    bot.add_cog(Hire(bot))
    print('Conversation extension loaded!')
