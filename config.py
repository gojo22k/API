# config.py
import os
# Telegram API credentials
API_ID = 25198711
API_HASH = '2a99a1375e26295626c04b4606f72752'
BOT_TOKEN = '7096468759:AAFt7RTlnBwNHRJA1fQC0a4TayXKaEubVGs'
ADMINS = 1740287480, 5192808332, 7428552084, 5626835282, 1190642269
# File paths and messages
OWNER = 'OtakuFlix'
REPO = 'ADATA'
PATH = 'anime_data.txt'
MESSAGE = 'Update anime_data.txt'
GIT_TOKEN = os.getenv('GIT_TOKEN', '')

# API keys for different platforms
MIXDROP_API_KEY = 'gAR2UJ0JE2RKlhJJCqE'
FILEMOON_API_KEY = '42605q5ytvlhmu9eris67'
VIDHIDE_API_KEY = '27261mmymf1etcdwfdvr3'
STREAMWISH_API_KEY = '10801lny3tlwanfupzu4m'
DOODSTREAM_API_KEY = '355892lri7tbejk8bpq7vt'
HYDRAX_API_KEY = 'fb4feb8eea990f7ff7d922111cfc25d8'

# URLs for fetching data
PLATFORMS = {
    'Filemoon': f'https://filemoon-api.vercel.app/api/filemoon?key={FILEMOON_API_KEY}&fld_id=0',
    'MixDrop': f'https://api.mixdrop.ag/folderlist?email=mohapatraankit22@gmail.com&key={MIXDROP_API_KEY}&id=0',
    'VidHide': f'https://vidhideapi.com/api/folder/list?key={VIDHIDE_API_KEY}&fld_id=0',
    'StreamWish': f'https://api.streamwish.com/api/folder/list?key={STREAMWISH_API_KEY}&fld_id=0',
    'DoodStream': f'https://doodapi.com/api/folder/list?key={DOODSTREAM_API_KEY}'
}

API_URLS = {
    'Kitsu': 'https://kitsu.io/api/edge/genres',  # Example Kitsu API endpoint
    'JikanV4': 'https://api.jikan.moe/v4/anime/1',  # Example JikanV4 API endpoint
}
