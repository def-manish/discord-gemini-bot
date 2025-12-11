
import discord
from discord.ext import commands
import google.generativeai as genai
import os
from threading import Thread
from flask import Flask

# Configure Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Configure Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Store conversation history for each user
conversation_history = {}

# Flask app to keep Replit alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} servers')

@bot.command(name='ask')
async def ask_gemini(ctx, *, question):
    """Ask Gemini AI a question. Usage: !ask your question here"""
    try:
        async with ctx.typing():
            user_id = str(ctx.author.id)
            if user_id not in conversation_history:
                conversation_history[user_id] = model.start_chat(history=[])
            
            chat = conversation_history[user_id]
            response = chat.send_message(question)
            
            reply = response.text
            if len(reply) > 2000:
                chunks = [reply[i:i+2000] for i in range(0, len(reply), 2000)]
                for chunk in chunks:
                    await ctx.reply(chunk)
            else:
                await ctx.reply(reply)
                
    except Exception as e:
        await ctx.reply(f"Sorry, an error occurred: {str(e)}")
        print(f"Error: {e}")

@bot.command(name='reset')
async def reset_conversation(ctx):
    """Reset your conversation history with Gemini"""
    user_id = str(ctx.author.id)
    if user_id in conversation_history:
        del conversation_history[user_id]
    await ctx.reply("Your conversation history has been reset!")

@bot.command(name='ping')
async def ping(ctx):
    """Check if bot is responsive"""
    await ctx.reply(f'Pong! Latency: {round(bot.latency * 1000)}ms')

@bot.command(name='help_bot')
async def help_command(ctx):
    """Show available commands"""
    help_text = """
**Available Commands:**
`!ask <question>` - Ask Gemini AI anything
`!reset` - Reset your conversation history
`!ping` - Check bot latency
`!help_bot` - Show this message

**Example:**
`!ask What is Python?`
`!ask Tell me a joke`
    """
    await ctx.reply(help_text)

# Keep Replit alive and run bot
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in secrets")
    else:
        bot.run(token)
