import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os
import datetime

app = Flask(__name__)
@app.route('/')
def home(): return "Pulse Pro Suite is Online!"
Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Database placeholders
stats = {"total_tickets": 0, "staff_actions": {}, "category_counts": {}}
ticket_timers = {}

class TicketControlView(discord.ui.View):
    def __init__(self, ticket_author, category):
        super().__init__(timeout=None)
        self.ticket_author = ticket_author
        self.category = category
        self.start_time = datetime.datetime.now()

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, custom_id="claim")
    async def claim(self, interaction: discord.Interaction, button):
        duration = datetime.datetime.now() - self.start_time
        stats["staff_actions"][interaction.user.name] = stats["staff_actions"].get(interaction.user.name, 0) + 1
        embed = discord.Embed(title="✅ Claimed", description=f"Αναλήφθηκε από {interaction.user.name}\nΧρόνος απόκρισης: {duration.seconds}s", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Close & Log", style=discord.ButtonStyle.danger, custom_id="close")
    async def close(self, interaction: discord.Interaction, button):
        log_channel = interaction.guild.get_channel(123456789012345678) # Βάλε το ID του log channel
        await interaction.response.send_message("Αποθήκευση logs και κλείσιμο...")
        # Εδώ θα έμπαινε η λογική για export του chat σε .txt
        await interaction.channel.delete()

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", emoji="ℹ️"),
            discord.SelectOption(label="Ban Appeal", emoji="🚫")
        ]
        super().__init__(placeholder="Επίλεξε κατηγορία...", options=options)

    async def callback(self, interaction: discord.Interaction):
        stats["total_tickets"] += 1
        stats["category_counts"][self.values[0]] = stats["category_counts"].get(self.values[0], 0) + 1
        
        # VIP Priority check
        is_vip = any(role.name.lower() in ["premium", "donor"] for role in interaction.user.roles)
        ping = "@here" if not is_vip else "@admin"
        
        channel = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}")
        embed = discord.Embed(title="🎫 Ticket Created", color=discord.Color.blue())
        
        if self.values[0] == "Ban Appeal":
            embed.description = "Παρακαλώ απάντησε: 1. Γιατί unban; 2. Discord ID; 3. Ανέβασε screenshot."
            
        await channel.send(f"{ping}", embed=embed, view=TicketControlView(interaction.user, self.values[0]))
        await interaction.response.send_message(f"Ticket: {channel.mention}", ephemeral=True)

@bot.command()
async def bots(ctx):
    embed = discord.Embed(title="🤖 Pulse Status", color=discord.Color.teal())
    embed.add_field(name="Latency", value=f"{round(bot.latency*1000)}ms")
    embed.add_field(name="Uptime", value="24/7 Active")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def stats(ctx):
    embed = discord.Embed(title="📊 Pulse Analytics", color=discord.Color.dark_blue())
    embed.add_field(name="Συνολικά Tickets", value=stats["total_tickets"])
    cat_text = "\n".join([f"{k}: {v}" for k, v in stats["category_counts"].items()])
    embed.add_field(name="Δημοφιλή", value=cat_text)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    view = discord.ui.View(timeout=None)
    view.add_item(TicketSelect())
    await ctx.send("Επίλεξε κατηγορία:", view=view)

bot.run(os.environ.get("DISCORD_TOKEN")