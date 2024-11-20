import pyttsx3
import speech_recognition as sr
import webbrowser
from music import music_library
import vlc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from openai import OpenAI

engine = pyttsx3.init()
r = sr.Recognizer()

# Initialize the VLC player globally
player = None
client = OpenAI(
    api_key="#api_here"
)

def speak(text):
    engine.say(text)
    engine.runAndWait()
    
def speak_ai(text):
    # Start the streaming process with OpenAI's TTS
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",  # or any other supported voice
        input=text,
    )
    
    # Create a VLC player instance to play the audio
    tts_player = vlc.MediaPlayer()

    # Start streaming and writing the audio to a file simultaneously
    response.stream_to_file("output.mp3", callback=lambda chunk: play_audio_chunk(chunk, tts_player))

def play_audio_chunk(chunk, tts_player):
    # Use VLC to play the audio chunk as it is received
    media = vlc.Media("output.mp3")
    tts_player.set_media(media)
    
    # If not already playing, start playback
    if not tts_player.is_playing():
        tts_player.play()

def listen():
    with sr.Microphone() as source:
        print("Listening ...")
        audio = r.listen(source)
        
        try:
            print("Recognizing ...")
            return r.recognize_google(audio)
        except Exception as e:
            return ""

def set_volume(volume_level):
    # volume_level should be an integer between 1 and 100
    if volume_level < 1 or volume_level > 100:
        raise ValueError("Volume level must be between 1 and 100")
    
    # Convert volume_level from 1-100 range to 0.0-1.0 range
    normalized_volume = volume_level / 100.0

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    
    # Set the master volume
    volume.SetMasterVolumeLevelScalar(normalized_volume, None)

def find_song_in_library(song_name):
    # Find a song in the music_library that contains the song_name as a substring
    for key in music_library.keys():
        if song_name in key.lower():
            return music_library[key]
    return None

def startCommandEngine(command):
    global player
    if "open google" in command.lower():
        speak("Opening Google")
        webbrowser.open("https://www.google.com")
    elif "open youtube" in command.lower():
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif "open youtube music" in command.lower():
        speak("Opening YouTube Music")
        webbrowser.open("https://music.youtube.com")
    elif command.lower().startswith("play"):
        try:
            music_name = command.replace("play ", "").lower()
            song_file = find_song_in_library(music_name)

            if song_file:
                # Stop the previous player if it's active
                if player is not None:
                    player.stop()

                # Create a new player instance for the new song
                player = vlc.MediaPlayer(f"file:///music/{song_file}")
                speak("Ok Sir")
                player.play()
            else:
                speak(f"Music, {music_name}, not found")
                print(f"Music {music_name} not found")
                
        except Exception as e:
            speak("An error occurred while trying to play the music")
            print(f"Error: {e}")
            
    elif "stop music" in command.lower() or "top music" in command.lower():
        try:
            if player is not None:
                player.stop()
                speak("Music Stopped")
            else:
                speak("No music is playing")
        except Exception as e:
            speak("No Music is playing")
            print("No music is playing")
            
    elif command.lower().startswith("music volume"):
        volume = int(command.replace("music volume ", "").lower())
        if player is not None:
            player.audio_set_volume(volume)
            speak(f"Setting Music Volume To {volume}")
        else:
            speak("No music is playing to set the volume")
        
    elif command.lower().startswith("volume"):
        volume = int(command.replace("volume ", "").lower())
        set_volume(volume)
        speak(f"Setting Master Volume To {volume}")

if __name__ == "__main__":
    speak("Jarvis Is Activated")
    while True:
        result = listen()
        if result != "":
            print(result)
            startCommandEngine(result)