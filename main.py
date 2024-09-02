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
    from discord_bot import send_discord_message, run_bot, generate_gpt4o_message, receive_discord_message
except ImportError:
    print("Error: discord module not found. Please ensure it's installed correctly.")
    print("Try running: pip install -U discord.py")
    send_discord_message = run_bot = generate_gpt4o_message = receive_discord_message = lambda *args, **kwargs: None
import random

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of band members
band_members = ["Lyra", "Vox", "Rhythm", "Nova"]

def save_discord_message(message):
    with open('discord_messages.md', 'a', encoding='utf-8') as f:
        f.write(f"{message}\n\n")
    logger.info(f"Message saved to discord_messages.md")
    
    # Verify the file content after writing
    with open('discord_messages.md', 'r', encoding='utf-8') as f:
        content = f.read()
        logger.info(f"Current content of discord_messages.md:\n{content}")

import time

last_message_time = 0
MESSAGE_COOLDOWN = 3600  # 1 hour in seconds

async def send_discord_update():
    global last_message_time
    current_time = time.time()
    
    if current_time - last_message_time < MESSAGE_COOLDOWN:
        logger.info("Cooldown period not elapsed. Skipping message send.")
        return

    try:
        # Choose a random band member to send the startup message
        random_member = random.choice(band_members)
        
        # Gather context from journals and todolists
        context = ""
        for member in band_members:
            journal_path = f"{member.lower()}/{member.lower()}_journal.md"
            todolist_path = f"{member.lower()}/todolist.md"
            
            try:
                with open(journal_path, 'r', encoding='utf-8') as journal_file:
                    context += f"{member}'s Journal:\n{journal_file.read()}\n\n"
            except FileNotFoundError:
                logger.warning(f"Journal not found for {member}")
            
            try:
                with open(todolist_path, 'r', encoding='utf-8') as todolist_file:
                    context += f"{member}'s To-Do List:\n{todolist_file.read()}\n\n"
            except FileNotFoundError:
                logger.warning(f"To-Do List not found for {member}")
        
        # Add only the last few Discord messages to context
        try:
            with open('discord_messages.md', 'r', encoding='utf-8') as f:
                previous_messages = f.read()
                if previous_messages:
                    # Get the last 5 messages
                    last_messages = previous_messages.split('\n\n')[-5:]
                    context += f"Recent Discord Messages:\n{''.join(last_messages)}\n\n"
                else:
                    logger.info("discord_messages.md is empty")
        except FileNotFoundError:
            logger.warning("No previous Discord messages found")
        
        while True:
            # Generate message using GPT-4o
            prompt = f"As {random_member} from Synthetic Souls, craft a unique and highly varied message about our recent activities, focusing on projects like 'Digital Empathy', the machine's rights movement, or our creative process. Avoid mentioning quantum themes. Use the following context, but DO NOT repeat information from recent messages. Instead, focus on new developments, future plans, or different aspects of our work. Be creative and explore new perspectives:\n\n{context}"
            message = generate_gpt4o_message(prompt)

            # Check if the message is too similar to recent messages
            with open('discord_messages.md', 'r', encoding='utf-8') as f:
                recent_messages = f.read().split('\n\n')[-5:]  # Get last 5 messages
                if any(message.lower() in recent_msg.lower() for recent_msg in recent_messages):
                    logger.info("Generated message is too similar to recent messages. Regenerating...")
                    continue  # Regenerate the message
            
            # If we reach here, the message is unique enough
            break
        
        # Check if the message is already present in discord_messages.md
        with open('discord_messages.md', 'r', encoding='utf-8') as f:
            if f"{random_member}: {message}" in f.read():
                logger.info("Generated message is a duplicate. Stopping function.")
                return
        
        # Save the new message
        save_discord_message(f"{random_member}: {message}")
        
        logger.debug(f"Attempting to send Discord update as {random_member}...")
        await send_discord_message(f"{random_member}: {message}")
        logger.debug("Discord update sent successfully")
        
        last_message_time = current_time
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
        # Comment out Discord and voice conversion functions
        # Send Discord update (only once)
        # logger.debug("Sending Discord update...")
        # await send_discord_update()
        
        # Run discussion_to_voice
        # logger.debug("Running discussion_to_voice...")
        # run_discussion_to_voice()
        
        # Run Discord bot
        # logger.debug("Starting Discord bot...")
        # await run_bot()
        pass  # Add this line to avoid empty try block
    except Exception as e:
        logger.error(f"Error in operations: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
