# Overview

voice clone via [eleven-labs](https://elevenlabs.io/) using existing youtube videos

# Features
- script `main.py` 
- gunicorn server `gunicorn -w 1 -b 0.0.0.0:8889 -c gunicorn_config.py server:app --timeout 30`
    - queue requests
    - handle request sequentially

# Setup
- Fill eleven labs API key in `audio_helper`
`You can view your xi-api-key using the 'Profile' tab on https://elevenlabs.io. Our API is experimental so all endpoints are subject to change.`
- create a virtual env `python -m venv venv`
- source env
- install requirements `pip install -r requirements` tested using `python 3.10.10`

### Script
- Usage `python main.py`
- modify values in the `__name__ == "__main__"`
    - `video_urls` 
        - list of youtube videos to get audio from
    - `voice_name`
        - name of voice for eleven labs
    - `filename`
        - name of file and folder clips will be saved to

### Server
- Usage: `gunicorn -w 1 -b 0.0.0.0:8889 -c gunicorn_config.py server:app --timeout 30`
- Routes
    - `GET /q`
        - returns queue length
    - `POST /base`
        - take in request
        - example requests in `pre-2023-hormozi-example.json` and `2023-hormozi-example.json`
