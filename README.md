# Speech-to-Text Transcription App

This project is a speech-to-text transcription app built using the Vosk speech recognition library and Gradio for the user interface. It allows users to upload or record audio files, transcribe speech into text, and display additional stats like the word and character count of the transcription. The app supports transcription in multiple languages, including English, French, and Spanish, making it more versatile for a wider audience.

## Features
- Upload or record audio for transcription.
- Real-time transcription of speech to text using the Vosk speech recognition library.
- Supports multiple languages including English, French, and Spanish.
- Displays word and character count of the transcription.
- User-friendly web interface powered by Gradio.
- Optimized for use with the Vosk models (`vosk-model-small-en-us-0.15`, `vosk-model-small-fr-fr-0.15`, `vosk-model-small-es-es-0.15` or similar).
- Simple and clean design to facilitate quick and easy transcription.

## Requirements
- Python 3.7+
- Vosk library for speech recognition
- Gradio library for building the web interface
- Vosk models for English, French, and Spanish speech recognition:
  - `vosk-model-small-en-us-0.15` (English)
  - `vosk-model-small-fr-fr-0.15` (French)
  - `vosk-model-small-es-es-0.15` (Spanish)
