from elevenlabs import generate, play, clone
from elevenlabs import set_api_key
set_api_key("aadc31374f6d0280caa4e89926c5f222")

def clone_and_play_voice(voice_name, files):
    voice = clone(
        name=voice_name,
        description="A cloned voice from the file: " + ', '.join(files),
        files=files,
    )

    audio = generate(text="Hi! I'm a cloned voice!", voice=voice)

    play(audio)
