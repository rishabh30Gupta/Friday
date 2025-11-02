import pyttsx3

def test_speak():
    """Initializes pyttsx3 and speaks a test sentence."""
    try:
        engine = pyttsx3.init('sapi5')
        print("pyttsx3 engine initialized.")

        voices = engine.getProperty('voices')
        print("Available voices:")
        for voice in voices:
            print(f"  - {voice.name} ({voice.id})")
        rate = engine.getProperty('rate')
        print(f"Current speech rate: {rate}")
        engine.setProperty('rate', 150)
        print("Set speech rate to 150.")

        volume = engine.getProperty('volume')
        print(f"Current volume: {volume}")

        print("\nAttempting to speak...")
        engine.say("Hello, this is a test of the text to speech engine.")
        engine.runAndWait()
        print("'runAndWait' has completed.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_speak()
