from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import subprocess
import requests
import asyncio
# import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
from db import fetch_data_from_db
import json

# # Set up logging
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     level=logging.INFO)
# logger = logging.getLogger(__name__)

# Initialize the Pyrogram client with the necessary parameters
app = Client("anime_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'OK')

def run_health_check_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    httpd.serve_forever()

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    """Send a welcome message on /start"""
    await message.reply("Welcome to the Anime Bot! Use the available commands to interact.")

async def run_script_and_send_output(script_name, message: Message):
    """Runs a script and sends each line of output as a message when it completes"""
    try:
        process = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Read stdout and send it line by line as it is generated
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line == b"" and process.poll() is not None:
                break
            if stdout_line:
                await message.reply(stdout_line.decode('utf-8').strip())
        
        # Check if there's any error in stderr
        stderr_line = process.stderr.read()
        if stderr_line:
            await message.reply(stderr_line.decode('utf-8').strip())
        
        # Wait for the process to finish
        process.wait()
        
    except Exception as e:
        await message.reply(f"Error running script: {str(e)}")

@app.on_message(filters.command("fast_update"))
async def fast_update(client, message: Message):
    """Trigger the check1.py script"""
    await message.reply("Running fast update...")
    try:
        await run_script_and_send_output('check1.py', message)
        await message.reply("Fast update completed successfully!")
    except Exception as e:
        await message.reply(f"Error during fast update: {str(e)}")

@app.on_message(filters.command("update_all"))
async def update_all(client, message: Message):
    """Trigger the update_all.py script"""
    await message.reply("Running full update...")
    try:
        await run_script_and_send_output('update_all.py', message)
        await message.reply("Full update completed successfully!")
    except Exception as e:
        await message.reply(f"Error during full update: {str(e)}")

@app.on_message(filters.command("check"))
async def check(client, message: Message):
    """Check the status of Git token, DB, Cloud URLs, and APIs"""
    try:
        status_report = "Checking platform and API statuses...\n\n"
        
        # Checking platform status
        for platform, url in PLATFORMS.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    status_report += f"✅ {platform}: Online\n"
                else:
                    status_report += f"❌ {platform}: Error - {response.status_code}\n"
            except Exception as e:
                status_report += f"❌ {platform}: Error - {str(e)}\n"
        
        # Checking Git Token (using GitHub API as an example)
        try:
            git_response = requests.get("https://api.github.com", headers={"Authorization": f"token {GIT_TOKEN}"})
            if git_response.status_code == 200:
                status_report += "✅ Git Token: Valid\n"
            else:
                status_report += f"❌ Git Token: Invalid - {git_response.status_code}\n"
        except Exception as e:
            status_report += f"❌ Git Token: Error - {str(e)}\n"
        
        # Checking Kitsu API
        try:
            kitsu_response = requests.get(API_URLS['Kitsu'])
            if kitsu_response.status_code == 200:
                status_report += "✅ Kitsu API: Online\n"
            else:
                status_report += f"❌ Kitsu API: Error - {kitsu_response.status_code}\n"
        except Exception as e:
            status_report += f"❌ Kitsu API: Error - {str(e)}\n"
        
        # Checking JikanV4 API
        try:
            jikan_response = requests.get(API_URLS['JikanV4'])
            if jikan_response.status_code == 200:
                status_report += "✅ Jikan API: Online\n"
            else:
                status_report += f"❌JikanV4 API: Error - {jikan_response.status_code}\n"
        except Exception as e:
            status_report += f"❌ JikanV4 API: Error - {str(e)}\n"
        
        # Send the status report
        await message.reply(status_report)

    except Exception as e:
        await message.reply(f"Error checking statuses: {str(e)}")


@app.on_message(filters.command("aniflix_api"))
async def aniflix_api(client, message: Message):
    """Fetch all AIDs and names from the database"""
    await message.reply("Fetching anime data...")
    try:
        # Fetch the raw data from the database (GitHub)
        data, _ = fetch_data_from_db()
        
        if data is None:
            await message.reply("Error fetching anime data.")
            return
        
        # Parse the fetched data (assuming it's a JSON formatted string)
        anime_data = json.loads(data)
        
        # Prepare a list of anime names and AIDs
        anime_list = [f"{anime['name']} - AID: {anime['aid']}" for anime in anime_data]
        
        if anime_list:
            await message.reply("\n".join(anime_list))
        else:
            await message.reply("No anime data found.")
        
    except Exception as e:
        await message.reply(f"Error fetching anime data: {str(e)}")

if __name__ == "__main__":
    # Start health check server in a separate thread
    health_check_thread = threading.Thread(target=run_health_check_server)
    health_check_thread.daemon = True
    health_check_thread.start()
    
    # Start the bot
    app.run()
