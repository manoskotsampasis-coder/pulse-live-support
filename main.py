import discord
import os
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Zerox is online!"

def run_web_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="clear", description="Delete messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Deleted {amount} messages", ephemeral=True)

@bot.tree.command(name="mute", description="Mute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10))
    await interaction.response.send_message(f"Muted {member.name}")

@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f"Unmuted {member.name}")

@bot.tree.command(name="warn", description="Warn a member")
@app_commands.checks.has_permissions(kick_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.send_message(f"Warned {member.name} for: {reason}")

@bot.tree.command(name="lock", description="Lock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("Channel locked")

@bot.tree.command(name="unlock", description="Unlock channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("Channel unlocked")

@bot.tree.command(name="serverinfo", description="Server info")
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.send_message(f"Server: {interaction.guild.name} | Members: {interaction.guild.member_count}")

@bot.tree.command(name="avatar", description="Show user avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(member.display_avatar.url)

@bot.tree.command(name="slowmode", description="Set slowmode")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"Slowmode set to {seconds}s")

@bot.tree.command(name="roleinfo", description="Get role info")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.send_message(f"Role: {role.name} | ID: {role.id} | Members: {len(role.members)}")

@bot.tree.command(name="botinfo", description="Bot status")
async def botinfo(interaction: discord.Interaction):
    await interaction.response.send_message("Zerox is running smoothly for the PlayStation community.")

@bot.tree.command(name="say", description="Make bot say something")
@app_commands.checks.has_permissions(manage_messages=True)
async def say(interaction: discord.Interaction, message: str):
    await interaction.channel.send(message)
    await interaction.response.send_message("Message sent", ephemeral=True)

@bot.tree.command(name="addrole", description="Add role to member")
@app_commands.checks.has_permissions(manage_roles=True)
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await interaction.response.send_message(f"Added {role.name} to {member.name}")

@bot.tree.command(name="removerole", description="Remove role from member")
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await interaction.response.send_message(f"Removed {role.name} from {member.name}")

@bot.tree.command(name="nuke", description="Delete and recreate channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    new_channel = await interaction.channel.clone()
    await interaction.channel.delete()
    await new_channel.send("Channel nuked")

if __name__ == "__main__":
    t = Thread(target=run_web_server)
    t.start()
    bot.run(os.environ.get("DISCORD_TOKEN"))
