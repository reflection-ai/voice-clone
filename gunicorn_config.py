def post_fork(server, worker):
    from server import voice_generator, request_queue
    import threading

    threading.Thread(target=voice_generator, args=(request_queue,)).start()

