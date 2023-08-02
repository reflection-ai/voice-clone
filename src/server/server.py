from flask import Flask, request
from queue import Queue
from threading import Lock, Thread
from src.main import main
import threading
import os
import logging

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(level=getattr(logging, log_level),
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()

app = Flask(__name__, static_folder='demo')
app.config['SECRET_KEY'] = 'secret!'

# Create the request queue and image queue
request_queue = Queue()
queue_lock = Lock()

def parse_body(body):

    required_keys = ["name", "description", "youtube_links"]
    
    if not all(key in body for key in required_keys):
        raise ValueError("Missing required keys in body")
    
    if not body["youtube_links"] or not isinstance(body["youtube_links"], list):
        raise ValueError("'youtube_links' should be a list with at least 1 video")
    
    return body


def voice_generator(queue):
    logger.info(f"voice generator started")
    while True:
        if not queue.empty():
            logger.info(f"queue not empty")
            with queue_lock:
                request_body = queue.get()
            if request_body is not None:
                try:
                    name = request_body['name']
                    description = request_body['description']
                    youtube_links = request_body['youtube_links']

                    # validate inputs here and return response if valid
                    # start main() in a new thread

                    logger.info(f"thread created for name: {name}, description: {description}")
                    main(youtube_links, name, name, description)
                except Exception as e:
                    print(f"Error in processing request: {str(e)}")

@app.route("/q", methods=["GET"])
def queues():
    request_length = request_queue.qsize()
    return str(request_length)

@app.route("/base", methods=["POST"])
def create_voice_handler():
    json = request.get_json(force=True)
    with queue_lock:
        try:
            logger.info("recieved request")
            r = parse_body(json)
            # NOTE: this allownace for num_images is broken
            # in the context of konjure's backend
            # as it simply rewrites to the same imageId in the DB instead of a new one
            request_queue.put(r)
            logger.info("request placed in queue")
        except Exception as e:
            return {"error": str(e)}, 400
    return '', 200


if __name__ == "__main__":
    # Start the voice_generator in a new thread
    # Thread(target=voice_generator, args=(request_queue,)).start()

    # Run the Flask app in the main thread
    app.run()
