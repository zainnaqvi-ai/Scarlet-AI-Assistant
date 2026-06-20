# Scarlet AI Voice Assistant

Scarlet is a Python-based voice assistant that listens for a wake word and responds to spoken commands. It can open websites, fetch live news headlines, search Wikipedia for factual queries, and reply through natural-sounding text-to-speech. The project includes two versions: a lightweight console version and a full graphical version with a custom holographic HUD interface inspired by sci-fi designs (Iron Man / J.A.R.V.I.S. style).(Author submitted the project in his university UMT as well, therefore, in a condition he mentioned 3 designer names as well. They were part of his group.)

## Project Files

This repository contains two separate runnable versions of the assistant:

- **`Scarlet_AI.py`** — Console version. Runs entirely in the terminal with no graphical interface. Lightweight and faster to start; best for testing core voice logic without any visual overhead.

- **`Scarlet_Interface.py`** — Graphical version. Includes a full custom-built fullscreen GUI using CustomTkinter, featuring an animated holographic HUD with radiating light rings and a pulsing core display showing Scarlet's live status (listening, processing, speaking). Same voice assistant logic as `Scarlet_AI.py`, with a visual interface layered on top.

Both versions share the same feature set described below — the only difference is the presence of the graphical interface.

## Features

- **Wake word detection** — Scarlet listens passively and activates when she hears her name
- **Voice commands** — open Google, open YouTube, fetch news headlines, who designed you?
- **Wikipedia search** — ask "who is" or "what is" any topic and get a spoken summary, no AI API required
- **Text-to-speech replies** — natural voice responses via gTTS
- **Custom GUI** (Scarlet_Interface.py only) — animated holographic HUD interface, fullscreen sci-fi design

## Tech Stack

- Python 3.13
- `speech_recognition` — voice input / speech-to-text
- `gTTS` + `pygame` — text-to-speech output
- `wikipedia-api` — factual Q&A without needing an AI API
- `requests` — NewsAPI integration for headlines
- `customtkinter` — modern GUI framework for the HUD interface (Scarlet_Interface.py)

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Scarlet-AI-Assistant.git
   cd Scarlet-AI-Assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add your NewsAPI key inside whichever file you plan to run (get a free key at newsapi.org).

5. Run the version you want:
   ```bash
   python Scarlet_AI.py
   ```
   or
   ```bash
   python Scarlet_Interface.py
   ```

## Author

Built by Syed Ali Zain Naqvi — AI student at UMT, PIAIC AI Architect trainee.