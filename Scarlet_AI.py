import speech_recognition as sr
import webbrowser
import requests
import wikipediaapi
from gtts import gTTS
import pygame
import os
import time

recognizer = sr.Recognizer()

newsapi_key = "News api key here"  # get one free from newsapi.org

ASSISTANT_NAME = "scarlet"
WAKE_WORD = "scarlet"

pygame.mixer.init()  # only do this once, not every time speak() runs

wiki = wikipediaapi.Wikipedia(user_agent='Scarlet/1.0 (personal voice assistant project)', language='en')


def speak(text):
    print(f"{ASSISTANT_NAME}: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        tts.save('temp.mp3')

        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.music.unload()
        try:
            os.remove('temp.mp3')
        except PermissionError:
            pass
    except Exception as e:
        print(f"[TTS ERROR] {e}")


def search_wikipedia(query):
    # strip the trigger phrase so we're left with just the actual topic
    try:
        for phrase in ["who is", "what is", "tell me about", "search wikipedia for", "wikipedia"]:
            query = query.lower().replace(phrase, "")
        query = query.strip()

        if not query:
            speak("Sir, please tell me what to search for.")
            return

        page = wiki.page(query)

        if page.exists():
            sentences = page.summary.split('. ')
            short_summary = '. '.join(sentences[:2]).strip()
            if not short_summary.endswith('.'):
                short_summary += '.'
            speak(short_summary)
        else:
            speak("Sir, I couldn't find anything on that topic.")

    except Exception as e:
        print(f"[WIKIPEDIA ERROR] {e}")
        speak("Sir, I had trouble reaching Wikipedia.")


def process_command(command):
    command = command.lower()

    if "open google" in command:
        speak("Opening Google, Sir.")
        webbrowser.open("https://google.com")

    elif "open youtube" in command:
        speak("Opening YouTube, Sir.")
        webbrowser.open("https://youtube.com")

    elif "designed" in command:
        speak("I was designed by 4 U M T students for Miss Maryam, namely Zain, Muhammad, Gujjar, and Adeel.")

    elif "news" in command:
        speak("Fetching headlines.")
        try:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi_key}",
                timeout=5
            )
            if r.status_code == 200:
                articles = r.json().get("articles", [])[:5]
                for i, art in enumerate(articles, 1):
                    speak(f"Headline {i}: {art['title']}")
            else:
                print(f"[NEWS ERROR] status {r.status_code}: {r.text}")
                speak("Unable to reach news networks.")
        except Exception as e:
            print(f"[NEWS ERROR] {e}")
            speak("Unable to reach news networks.")

    elif "who is" in command or "what is" in command or "tell me about" in command or "wikipedia" in command:
        search_wikipedia(command)

    else:
        speak("Sir, I don't have a brain connected for that yet. Try asking me to open something, fetch news, or search Wikipedia.")


def listen_for_wake_word():
    with sr.Microphone() as source:
        print(f"\n[Listening for wake word '{WAKE_WORD}'...]")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=3)
        except sr.WaitTimeoutError:
            return None

    try:
        word = recognizer.recognize_google(audio, language='en-in')
        print(f"[HEARD] '{word}'")
        return word.lower()
    except sr.UnknownValueError:
        print("[INFO] Didn't catch any clear speech.")
        return None
    except sr.RequestError as e:
        print(f"[STT ERROR] {e}")
        return None


def listen_for_command():
    with sr.Microphone() as source:
        print("[Listening for your command...]")
        try:
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            print("[INFO] No command heard in time.")
            return None

    try:
        command = recognizer.recognize_google(audio, language='en-in')
        print(f"[COMMAND] '{command}'")
        return command
    except sr.UnknownValueError:
        print("[INFO] Didn't catch the command clearly.")
        return None
    except sr.RequestError as e:
        print(f"[STT ERROR] {e}")
        return None


def shutdown():
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    print("\n[INFO] Scarlet shut down cleanly.")


if __name__ == "__main__":
    speak(f"Initializing {ASSISTANT_NAME}.")

    try:
        while True:
            heard_word = listen_for_wake_word()

            if heard_word is not None and WAKE_WORD in heard_word:
                speak("Yes, Sir?")
                user_command = listen_for_command()

                if user_command is None:
                    speak("I didn't catch that, Sir.")
                    continue

                if "exit" in user_command.lower() or "stop" in user_command.lower():
                    speak("Powering down, goodbye Sir.")
                    break

                process_command(user_command)
    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C detected. Shutting down...")
    finally:
        shutdown()