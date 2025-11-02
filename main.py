import speech_recognition as sr
import pyttsx3
from google import genai
import os
import sys
import time
import re
import logging
import subprocess
import webbrowser
from typing import Optional
import string
import random
import time
import pyfiglet
from colorama import init, Fore, Style

# Initialize colorama
init()

# --- Greetings and Goodbyes ---
GREETINGS = [
    "Hello Sir! How may I assist you?",
    "Greetings Sir! What can I do for you today?",
    "Hi Sir! How can I help you?",
    "Welcome Sir! What's on your mind?"
]

GOODBYES = [
    "Goodbye Sir! Have a great day.",
    "Farewell Sir! Until next time.",
    "See you later Sir!",
    "Logging off. Take care Sir!"
]

# Optional runtime deps; degrade gracefully if unavailable
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    requests = None  # type: ignore
try:
    from pytube import YouTube  # type: ignore
except Exception:  # pragma: no cover
    YouTube = None # type: ignore
try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.common.keys import Keys  # type: ignore
except Exception:  # pragma: no cover
    webdriver = None # type: ignore


# Configure the Gemini client
api_key = "Enter the API Key Here"
if not api_key:
    raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")
client = genai.Client(api_key="Enter the API KEY HERE")

# Initialize the recognizer
r = sr.Recognizer()

# ------------------------------
# UI Functions
# ------------------------------

def display_logo():
    """Displays the Jarvis logo."""
    font = "doom"
    logo = pyfiglet.figlet_format("Jarvis", font=font)
    print(Fore.CYAN + logo + Style.RESET_ALL)

# ------------------------------
# Core Assistant Functions
# ------------------------------

def speak(text: str):
    """Converts text to speech with pauses between sentences."""
    print(Fore.CYAN + "Jarvis:" + Style.RESET_ALL, text)
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # Set speech rate to a slower value

        # Split text into sentences based on punctuation
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for i, sentence in enumerate(sentences):
            if not sentence.strip(): # Skip empty sentences
                continue

            # Remove punctuation from the current sentence for speaking
            text_to_speak_segment = sentence.translate(str.maketrans('', '', string.punctuation)).strip()

            if text_to_speak_segment: # Only speak if there's content
                engine.say(text_to_speak_segment)
                engine.runAndWait()

                # Add a short pause between sentences, but not after the last one
                if i < len(sentences) - 1:
                    time.sleep(0.5) # Adjust pause duration as needed

    except Exception as e:
        print(f"Error in speak function: {e}")


def listen() -> Optional[str]:
    """Listens for voice input and returns the transcribed text."""
    with sr.Microphone() as source:
        print(Fore.YELLOW + "Listening..." + Style.RESET_ALL)
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=8)
            text = r.recognize_google(audio)
            print(Fore.GREEN + "You said:" + Style.RESET_ALL, text)
            return text.lower()
        except sr.UnknownValueError:
            # This is not an error, just silence. Return None.
            return None
        except sr.RequestError as e:
            speak(f"Could not request results from Google Speech Recognition service; {e}")
            return None
        except sr.WaitTimeoutError:
            # This is not an error, just silence. Return None.
            return None


# ------------------------------
# Hardcoded Commands (from Friday.py)
# ------------------------------

def open_notepad() -> None:
    speak("Opening Notepad.")
    try:
        subprocess.Popen(["notepad.exe"])
    except Exception as e:
        speak("Sorry, I failed to open Notepad.")
        print(f"Error opening notepad: {e}")

def open_calculator() -> None:
    speak("Opening Calculator.")
    try:
        subprocess.Popen(["calc.exe"])
    except Exception as e:
        speak("Sorry, I failed to open the calculator.")
        print(f"Error opening calculator: {e}")

def open_browser() -> None:
    speak("Opening browser.")
    try:
        webbrowser.open("about:blank")
    except Exception as e:
        speak("Sorry, I failed to open the browser.")
        print(f"Error opening browser: {e}")

def confirm_and_shutdown() -> None:
    speak("Are you sure you want to shutdown? Say yes to confirm.")
    response = listen()
    if response and "yes" in response:
        speak("Shutting down.")
        try:
            subprocess.Popen(["shutdown", "/s", "/t", "0"])
        except Exception as e:
            speak("Sorry, I failed to initiate shutdown.")
            print(f"Error initiating shutdown: {e}")
    else:
        speak("Shutdown canceled.")

def open_youtube_search(query: str) -> None:
    search_query = query.replace("youtube", "").replace("search for", "").strip()
    speak(f"Searching for {search_query} on YouTube.")
    formatted_query = re.sub(r'\s+', '+', search_query)
    url = f"https://www.youtube.com/results?search_query={formatted_query}"
    webbrowser.open(url)

def download_youtube_video() -> None:
    if YouTube is None:
        speak("The pytube library is not installed. Please install it to download videos.")
        return
    speak("Please say the YouTube URL you want to download.")
    url = listen() # You might want a more robust way to get a URL
    if not url:
        speak("I didn't catch the URL. Please try again.")
        return
    try:
        speak("Starting download. This may take a moment.")
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download()
        speak("Download completed successfully.")
    except Exception as e:
        speak("Sorry, I could not download that video.")
        print(f"YouTube download error: {e}")


def fetch_weather_message() -> None:
    if requests is None:
        speak("The requests library is not installed. Cannot fetch weather.")
        return
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city_name = os.getenv("CITY_NAME", "Indore")
    if not api_key:
        speak("The OpenWeather API key is not configured.")
        return

    speak("Fetching the current weather.")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(base_url, params={"q": city_name, "appid": api_key, "units": "metric"}, timeout=10)
        response.raise_for_status()
        data = response.json()
        weather = data.get("weather", [{}])[0].get("description", "unknown")
        temp_c = data.get("main", {}).get("temp")
        message = f"The current weather in {city_name} is {weather}, with a temperature of {temp_c} degrees Celsius."
        speak(message)
    except Exception as e:
        speak("Sorry, I couldn't fetch the weather information.")
        print(f"Weather fetch failed: {e}")


def perform_login_via_selenium() -> None:
    if webdriver is None:
        speak("Selenium is not installed. Please install it to use this feature.")
        return

    url = os.getenv("LOGIN_URL")
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")

    if not (url and username and password):
        speak("Login is not configured. Please set the required environment variables.")
        return

    speak("Attempting to log in.")
    try:
        driver = webdriver.Edge()
        driver.get(url)
        time.sleep(2) # Wait for page to load

        username_field_id = os.getenv("LOGIN_USERNAME_FIELD_ID", "username")
        password_field_id = os.getenv("LOGIN_PASSWORD_FIELD_ID", "password")

        username_el = driver.find_element(By.ID, username_field_id)
        password_el = driver.find_element(By.ID, password_field_id)

        username_el.clear()
        username_el.send_keys(username)
        password_el.clear()
        password_el.send_keys(password)
        password_el.send_keys(Keys.ENTER)

        time.sleep(3) # Wait for login to process
        speak("Login attempted.")
        driver.quit()
    except Exception as e:
        speak("Sorry, the login process failed.")
        print(f"Selenium login error: {e}")


def execute_hardcoded_command(text: str) -> bool:
    """Checks for and executes a hardcoded command. Returns True if a command was executed."""
    if "notepad" in text:
        open_notepad()
        return True
    if "calculator" in text or "calc" in text:
        open_calculator()
        return True
    if "browser" in text:
        open_browser()
        return True
    if "shutdown" in text:
        confirm_and_shutdown()
        return True
    if "youtube" in text and "download" not in text:
        open_youtube_search(text)
        return True
    if "download" in text and "video" in text:
        download_youtube_video()
        return True
    if "weather" in text:
        fetch_weather_message()
        return True
    if "login" in text:
        perform_login_via_selenium()
        return True
    return False


# ------------------------------
# Main loop
# ------------------------------
if __name__ == "__main__":
    display_logo()
    speak(random.choice(GREETINGS))
    while True:
        user_input = listen()
        if user_input:
            # First, check for exit commands
            if "exit" in user_input or "quit" in user_input:
                speak(random.choice(GOODBYES))
                break

            # Next, try to execute a hardcoded command
            command_executed = execute_hardcoded_command(user_input)

            # If no hardcoded command was found, use the AI
            if not command_executed:
                try:
                    speak("Thinking...")
                    ai_query = f"in short and simple manner {user_input}"
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=ai_query,
                    )
                    if response.text:
                        speak(response.text)
                    else:
                        speak("Sorry, I couldn't generate a response for that.")
                except Exception as e:
                    speak("Sorry, there was an error with the AI service.")
                    print(f"Gemini API error: {e}")
