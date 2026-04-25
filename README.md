# Trunic Glyph Generator

A Streamlit web app that converts English text into Trunic, a writing system from the game _TUNIC_, using phonetic transcription.

<a href="https://trunic-glyph-generator.streamlit.app/" target="_blank">Link to Web App</a>
![Web app screenshot](docs/web_app_screenshot.png)

## About

This simple web app takes English text, converts it into phonetic form, and maps the sounds to Trunic - a writing system from the game _TUNIC_. The phonetics are all derived from American English pronunciation, similar to the text found in the in-game manual.

The following diagram explains the system in detail.
![Diagram explaining the Trunic writing system](docs/trunic_guide.png)
_credit: https://tunic.wiki/books/secrets/page/trunic_

This repository exists mainly for transparency, issue reporting, and source availability. Most users should use the live web app.

You may also run the jupyter notebook locally if you wish to modify or extend any of the code.

## Bug Reports / Feedback

If you encounter a bug or incorrect transcription, please open an issue on this repository.

Helpful information to include:

- The text you entered
- What you expected to happen
- What actually happened
- Screenshot (if relevant)
- Browser / device

## Local Development

You may wish to clone and run the web app locally:

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

Please note that the project has a dependency on the open-source `espeak-ng` software, the installation of which will vary depending on your platform.

## Credits

Uses Streamlit, phonemizer, fontParts, ufo2ft, and eSpeak NG.

Inspired by the writing system in TUNIC by Isometricorp Games.
Unofficial fan project.

## License

MIT License © 2026 Ricardo Cortes-Monroy
