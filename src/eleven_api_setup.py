import os
from elevenlabs import set_api_key
from dotenv import load_dotenv
load_dotenv()
eleven_api_key = os.getenv('ELEVEN_API_KEY')
if eleven_api_key:
    set_api_key(eleven_api_key)
else:
    print("you need to set eleven labs api key in .env")
    exit(1)
