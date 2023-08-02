# Overview

voice clone via [eleven-labs](https://elevenlabs.io/) using existing youtube videos

# Features
- script `src/main.py` 

- gunicorn server `export PYTHONPATH=$PYTHONPATH:`pwd` && gunicorn -w 1 -b 0.0.0.0:8889 -c src/gunicorn_config.py src/server:app --timeout 30`
    - queue requests
    - handle request sequentially

# Setup

- create `.env` template from `.example.env` with `cp .example.env .env`
- Fill eleven labs API key in `.env`
`You can view your xi-api-key using the 'Profile' tab on https://elevenlabs.io. Our API is experimental so all endpoints are subject to change.`
- create a virtual env `python -m venv venv`
- source venv
- install requirements `pip install -r requirements` tested using `python 3.10.10`

### Script
- Usage `python src/main.py`
- modify values in the `__name__ == "__main__"`
    - `video_urls` 
        - list of youtube videos to get audio from
    - `voice_name`
        - name of voice for eleven labs
    - `filename`
        - name of file and folder clips will be saved to

### Server
- Usage: `export PYTHONPATH=$PYTHONPATH:`pwd` && gunicorn -w 1 -b 0.0.0.0:8889 -c src/gunicorn_config.py src/server:app --timeout 30`
- Routes
    - `GET /q`
        - returns queue length
    - `POST /base`
        - take in request
        - example requests in `examples/`

### TODOs
[] Package structure
[] Testing

