import json
from cloud import fetch_all_cloud_folders  # Function to fetch cloud data
from db import fetch_data_from_db  # Function to fetch data from DB
from addon import fetch_complete_data  # Function to fetch full anime data
import subprocess  # To call the update.py script
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_new_aid(existing_db_data):
    """Generate the next available AID based on the highest existing AID in the DB."""
    # Check if the database is empty or has no aid values
    if not existing_db_data:
        logging.info("Database is empty. Starting with AID 1.")
        return 1  # If the database is empty, start with AID 1

    # Extract AIDs and find the highest AID
    aids = [anime.get('aid', 0) for anime in existing_db_data]
    
    # Ensure that the aids are unique and get the maximum one
    max_aid = max(set(aids))  # Convert to set to eliminate duplicates and find max
    
    # Log the maximum AID found in the database
    logging.info(f"Maximum AID found in database: {max_aid}. Using {max_aid + 1} for the next anime entry.")
    
    # Return the next available AID
    return max_aid + 1


def perform_check():
    # Fetch cloud and DB data
    cloud_data = fetch_all_cloud_folders()
    db_data, _ = fetch_data_from_db()

    if not cloud_data or not db_data:
        print("Error: Unable to fetch data from cloud or database.")
        return

    if db_data.strip() == "":
        print("Error: The database data is empty.")
        return

    try:
        db_data_parsed = json.loads(db_data)
    except json.JSONDecodeError:
        print("Error: Failed to decode the database data.")
        return

    # Extract anime names from cloud and DB
    cloud_anime_names = {anime.get('name') for anime in cloud_data if anime.get('name')}
    db_anime_dict = {anime.get('name'): anime for anime in db_data_parsed if anime.get('name')}
    db_anime_names = set(db_anime_dict.keys())

    # Determine new, unchanged, and deleted anime
    new_anime_names = cloud_anime_names - db_anime_names
    unchanged_anime_names = cloud_anime_names & db_anime_names
    deleted_anime_names = db_anime_names - cloud_anime_names

    updated_db_data = db_data_parsed.copy()

    # Handle new anime names
    if new_anime_names:
        print("\nNew Anime Names:")
        for name in new_anime_names:
            print(f" - {name}")
            # Fetch the full data for the new anime
            new_anime_data = fetch_complete_data([anime for anime in cloud_data if anime.get('name') == name])
            if new_anime_data:
                new_aid = generate_new_aid(updated_db_data)
                for anime in new_anime_data:
                    anime['aid'] = new_aid
                    updated_db_data.append(anime)
            else:
                print(f"Failed to fetch data for {name}")

    # Handle deleted anime names
    if deleted_anime_names:
        print("\nDeleted Anime Names:")
        for name in deleted_anime_names:
            print(f" - {name}")
            # Remove the anime entry from the database
            updated_db_data = [anime for anime in updated_db_data if anime.get('name') != name]
            print(f" - {name} has been removed from the database.")

    # Handle unchanged anime names and ensure their data remains unchanged
    if unchanged_anime_names:
        print("\nUnchanged Anime Names:")
        for name in unchanged_anime_names:
            print(f" - {name} data is unchanged in the database.")
            # Ensure unchanged anime data remains the same
            for anime in updated_db_data:
                if anime.get('name') == name:
                    # Ensure 'aid' stays the same for unchanged anime
                    continue  # No change needed

    # Check if any changes occurred
    if updated_db_data == db_data_parsed:
        print("\nNOTHING NEW TO SEE BRO")
        try:
            # Send the current DB data directly to check2.py
            print("\nNo changes detected, sending data to check2.py...")
            subprocess.run(['python', 'check2.py'], input=json.dumps(updated_db_data), text=True, check=True)
        except Exception as e:
            print(f"Failed to send data to check2.py: {e}")
        return

    # Call update.py to process and update the database
    try:
        # Pass the updated data to the update.py script using subprocess
        subprocess.run(['python', 'update.py'], input=json.dumps(updated_db_data), text=True, check=True)
        print("\nDatabase updated successfully!")
    except Exception as e:
        print(f"Failed to update the database: {e}")


if __name__ == "__main__":
    perform_check()
