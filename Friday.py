import os
import sys
import time
import re
import logging
import subprocess
import webbrowser
from typing import Optional

# Optional runtime deps; degrade gracefully if unavailable
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    requests = None  # type: ignore

try:
    import pyttsx3  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    pyttsx3 = None  # type: ignore


# ------------------------------
# Logging
# ------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("friday")


# ------------------------------
# Text-to-Speech
# ------------------------------
_tts_engine = None


def init_tts_engine() -> None:
    global _tts_engine
    if _tts_engine is not None:
        return
    if pyttsx3 is None:
        logger.warning("pyttsx3 not installed; voice output disabled.")
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", int(os.getenv("FRIDAY_TTS_RATE", "140")))
        engine.setProperty("volume", float(os.getenv("FRIDAY_TTS_VOLUME", "1.0")))
        _tts_engine = engine
    except Exception as error:
        logger.warning("Failed to initialize TTS engine: %s", error)


def speak(message: str) -> None:
    init_tts_engine()
    print(message)
    if _tts_engine is None:
        return
    try:
        _tts_engine.say(message)
        _tts_engine.runAndWait()
    except Exception as error:
        logger.warning("TTS error: %s", error)


# ------------------------------
# Speech recognition (with fallback to text input)
# ------------------------------
def listen_for_command(prompt: Optional[str] = None, timeout_seconds: int = 6, phrase_limit_seconds: int = 8) -> str:
    if prompt:
        print(prompt)
        speak(prompt)

    # Lazy import to avoid hard dependency when running without mic/PyAudio
    try:
        import speech_recognition as sr  # type: ignore
    except Exception as error:  # pragma: no cover
        logger.info("Speech recognition unavailable (%s). Falling back to keyboard.", error)
        return input("Command> ").strip().lower()

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:  # type: ignore
            print("Listening…")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout_seconds, phrase_time_limit=phrase_limit_seconds)
        text = recognizer.recognize_google(audio)
        print("Heard:", text)
        return text.strip().lower()
    except Exception as error:
        logger.info("Voice capture failed (%s). Falling back to keyboard.", error)
        return input("Command> ").strip().lower()


# ------------------------------
# Weather
# ------------------------------
def fetch_weather_message() -> Optional[str]:
    if requests is None:
        return None
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city_name = os.getenv("CITY_NAME", "Indore")
    if not api_key:
        logger.info("OPENWEATHER_API_KEY not set; skipping weather fetch.")
        return None
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(base_url, params={"q": city_name, "appid": api_key, "units": "metric"}, timeout=10)  # type: ignore
        response.raise_for_status()
        data = response.json()
        weather = data.get("weather", [{}])[0].get("description", "unknown")
        temp_c = data.get("main", {}).get("temp")
        humidity = data.get("main", {}).get("humidity")
        wind_speed = data.get("wind", {}).get("speed")
        return f"Current weather in {city_name} is {weather}. Temperature {temp_c}°C. Humidity {humidity}%. Wind {wind_speed} m/s."
    except Exception as error:
        logger.warning("Weather fetch failed: %s", error)
        return None


# ------------------------------
# Apps and utilities
# ------------------------------
def open_notepad() -> None:
    try:
        subprocess.Popen(["notepad.exe"])  # nosec - Windows builtin
    except Exception as error:
        logger.error("Failed to open Notepad: %s", error)


def open_calculator() -> None:
    try:
        subprocess.Popen(["calc.exe"])  # nosec - Windows builtin
    except Exception as error:
        logger.error("Failed to open Calculator: %s", error)


def open_browser() -> None:
    try:
        # Prefer default browser; Edge fallback
        opened = webbrowser.open("about:blank")
        if not opened:
            subprocess.Popen(["cmd", "/c", "start", "msedge"], shell=False)  # nosec
    except Exception as error:
        logger.error("Failed to open browser: %s", error)


def confirm_and_shutdown() -> None:
    speak("Are you sure you want to shutdown? Say yes to confirm.")
    response = listen_for_command()
    if "yes" in response:
        try:
            subprocess.Popen(["shutdown", "/s", "/t", "0"])  # nosec
        except Exception as error:
            logger.error("Shutdown failed: %s", error)
    else:
        speak("Shutdown canceled.")


def open_youtube_search(query: str) -> None:
    url = f"https://www.youtube.com/results?search_query={re.sub(r'/s+', '+', query.strip())}"
    webbrowser.open(url)


def download_youtube_video(url: str) -> None:
    try:
        from pytube import YouTube  # type: ignore
    except Exception as error:  # pragma: no cover
        speak("YouTube download requires pytube. Please install it first.")
        logger.info("pytube unavailable: %s", error)
        return
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download()
        speak("Download completed.")
    except Exception as error:
        logger.error("YouTube download failed: %s", error)
        speak("Sorry, I could not download that video.")


# ------------------------------
# Optional: Selenium login (env-configured)
# ------------------------------
def perform_login_via_selenium() -> None:
    url = os.getenv("LOGIN_URL")
    username = os.getenv("LOGIN_USERNAME")
    password = os.getenv("LOGIN_PASSWORD")
    username_field_id = os.getenv("LOGIN_USERNAME_FIELD_ID", "username")
    password_field_id = os.getenv("LOGIN_PASSWORD_FIELD_ID", "password")
    browser_choice = os.getenv("LOGIN_BROWSER", "edge").lower()

    if not (url and username and password):
        speak("Login is not configured. Set LOGIN_URL, LOGIN_USERNAME, and LOGIN_PASSWORD.")
        return

    try:
        from selenium import webdriver  # type: ignore
        from selenium.webdriver.common.by import By  # type: ignore
        from selenium.webdriver.common.keys import Keys  # type: ignore
    except Exception as error:  # pragma: no cover
        speak("Selenium is not installed. Please install it to use login.")
        logger.info("selenium unavailable: %s", error)
        return

    try:
        if browser_choice == "chrome":
            driver = webdriver.Chrome()
        else:
            driver = webdriver.Edge()
    except Exception as error:
        logger.error("WebDriver failed to start: %s", error)
        speak("Could not start the browser for login.")
        return

    try:
        driver.get(url)
        username_el = driver.find_element(By.ID, username_field_id)
        password_el = driver.find_element(By.ID, password_field_id)
        username_el.clear()
        username_el.send_keys(username)
        password_el.clear()
        password_el.send_keys(password)
        password_el.send_keys(Keys.ENTER)
        time.sleep(2)
        speak("Login attempted.")
    except Exception as error:
        logger.error("Login flow failed: %s", error)
        speak("Login failed.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


# ------------------------------
# Command routing
# ------------------------------
def execute_command(command_text: str) -> None:
    text = command_text.strip().lower()
    if not text:
        return

    if "notepad" in text:
        open_notepad()
        return

    if "calculator" in text or "calc" in text:
        open_calculator()
        return

    if "browser" in text or "edge" in text or "chrome" in text:
        open_browser()
        return

    if "shutdown" in text:
        confirm_and_shutdown()
        return

    if any(word in text for word in ["exit", "quit", "close"]):
        speak("Goodbye.")
        sys.exit(0)

    if "login" in text:
        perform_login_via_selenium()
        return

    if "download" in text and "video" in text:
        speak("Please provide the YouTube URL.")
        url = input("YouTube URL> ").strip()
        download_youtube_video(url)
        return

    if "youtube" in text and "download" not in text:
        speak("What do you want to watch?")
        query = listen_for_command()
        if query:
            speak(f"Searching for {query} on YouTube.")
            open_youtube_search(query)
        return

    if "weather" in text:
        speak("Fetching the current weather…")
        message = fetch_weather_message()
        if message:
            speak(message)
        else:
            speak("Sorry, I couldn't fetch the weather information.")
        return

    speak("Sorry, I didn't understand that.")


# ------------------------------
# Main loop
# ------------------------------
def main() -> None:
    banner = "Friday Assistant [Improved]"
    print(banner)
    speak("Welcome! Say a command like notepad, calculator, browser, weather, YouTube, download video, login, shutdown, or say exit to quit.")

    while True:
        try:
            command = listen_for_command("Awaiting your command…")
            if command:
                execute_command(command)
        except KeyboardInterrupt:
            print()
            speak("Goodbye.")
            break
        except Exception as error:
            logger.error("Unexpected error: %s", error)
            speak("An unexpected error occurred.")


if __name__ == "__main__":
    main()


