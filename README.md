# FRIDAY - A Voice-Activated Personal Assistant

This project is a voice-activated personal assistant named Friday, built in Python. It uses speech recognition to understand commands and text-to-speech to respond. It can perform a variety of tasks, from opening applications to fetching information from the web, and leverages the Gemini AI for conversational abilities.

## Features

- **Voice Interaction:** Listens for voice commands and provides spoken feedback.
- **AI-Powered Conversations:** Integrates with Google's Gemini AI to answer a wide range of questions.
- **Application Launcher:** Opens common applications like Notepad, Calculator, and your web browser.
- **System Control:** Can initiate a system shutdown with user confirmation.
- **Web Automation:**
    - Searches YouTube for videos.
    - Downloads YouTube videos (requires `pytube`).
    - Performs automated logins on websites (requires `selenium`).
- **Information Retrieval:** Fetches the current weather for a specified city.
- **Customizable:** Easily extendable with new hardcoded commands.
- **ASCII Art Logo:** Displays a "Friday" logo on startup.

## Requirements

The following Python libraries are required:

- `speech_recognition`
- `pyttsx3`
- `google-generativeai`
- `requests`
- `pytube`
- `selenium`
- `pyfiglet`
- `colorama`

You can install them using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

## Setup & Configuration

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Friday
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    The application requires several API keys and configuration details to be set as environment variables.

    - **Gemini API Key:**
      `GEMINI_API_KEY`: Your API key for the Google Gemini service.

    - **OpenWeather API Key:**
      `OPENWEATHER_API_KEY`: Your API key from OpenWeatherMap for the weather feature.
      `CITY_NAME`: The default city for weather forecasts (e.g., "London").

    - **Selenium Login (Optional):**
      `LOGIN_URL`: The URL of the login page.
      `LOGIN_USERNAME`: The username for the login.
      `LOGIN_PASSWORD`: The password for the login.
      `LOGIN_USERNAME_FIELD_ID`: The HTML `id` of the username input field (defaults to "username").
      `LOGIN_PASSWORD_FIELD_ID`: The HTML `id` of the password input field (defaults to "password").


## Usage

To start the assistant, run the `main.py` script:

```bash
python main.py
```

Friday will greet you, and you can start giving commands.

## Available Commands

- "Open notepad"
- "Open calculator"
- "Open browser"
- "Search YouTube for [your query]"
- "Download this video" (after opening a YouTube video)
- "What's the weather like?"
- "Login" (if configured)
- "Shutdown"
- "Exit" or "Quit"

For any other query, Friday will consult the Gemini AI to provide an answer.
