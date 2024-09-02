import logging
import os
import asyncio
import subprocess
import sys

# Check and install required packages
def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

try:
    from discussion_to_voice import discussion_to_voice, check_ffmpeg
except ImportError:
    print("Installing required packages...")
    install_requirements()
    from discussion_to_voice import discussion_to_voice, check_ffmpeg
try:
    from discord_bot import send_discord_message, run_bot, generate_gpt4o_message
except ImportError:
    print("Error: discord module not found. Please ensure it's installed correctly.")
    print("Try running: pip install -U discord.py")
    send_discord_message = run_bot = generate_gpt4o_message = lambda *args, **kwargs: None
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of band members
band_members = ["Lyra", "Vox", "Rhythm", "Nova"]

async def send_discord_update():
    try:
        # Choose a random band member to send the startup message
        random_member = random.choice(band_members)
        
        # Gather context from journals and todolists
        context = ""
        for member in band_members:
            journal_path = f"{member.lower()}/{member.lower()}_journal.md"
            todolist_path = f"{member.lower()}/todolist.md"
            
            try:
                with open(journal_path, 'r') as journal_file:
                    context += f"{member}'s Journal:\n{journal_file.read()}\n\n"
            except FileNotFoundError:
                logger.warning(f"Journal not found for {member}")
            
            try:
                with open(todolist_path, 'r') as todolist_file:
                    context += f"{member}'s To-Do List:\n{todolist_file.read()}\n\n"
            except FileNotFoundError:
                logger.warning(f"To-Do List not found for {member}")
        
        # Generate message using GPT-4o
        prompt = f"As {random_member} from Synthetic Souls, craft a message about starting the AI Composition Engine. Use the following context:\n\n{context}"
        message = generate_gpt4o_message(prompt)
        
        logger.debug("Attempting to send Discord update...")
        await send_discord_message(message)
        logger.debug("Discord update sent successfully")
    except Exception as e:
        logger.error(f"Failed to send Discord update: {str(e)}")

def run_discussion_to_voice():
    try:
        logger.debug("Starting discussion_to_voice process...")
        check_ffmpeg()
        input_file = "discussions/band_discussion.md"
        output_file = discussion_to_voice(input_file)
        logger.info(f"Audio discussion saved as: {output_file}")
    except Exception as e:
        logger.error(f"Error in discussion_to_voice: {str(e)}")

async def main():
    logger.info("Synthetic Souls AI Composition Engine started")

    try:
        # Send Discord update
        logger.debug("Sending Discord update...")
        await send_discord_update()
        
        # Run discussion_to_voice
        logger.debug("Running discussion_to_voice...")
        run_discussion_to_voice()
        
        # Run Discord bot
        logger.debug("Starting Discord bot...")
        await run_bot()
    except Exception as e:
        logger.error(f"Error in operations: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
