import math
import os
import platform
import re
import json
from phonemizer import phonemize
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Requires local installation of espeak in src folder. Only used if hosting locally
if platform.system() == 'Windows':
    os.environ["PHONEMIZER_ESPEAK_LIBRARY"]= str(BASE_DIR / "libespeak-ng.dll")

vowels = {
    "ʊɹ"  : 0b0000000011101,
    "ɪɹ"  : 0b0000000001101,
    "ɛɹ"  : 0b0000000000101,
    "ɑːɹ" : 0b0000000011011,
    "oʊ"  : 0b0000000011111,
    "aʊ"  : 0b0000000000001,
    "ɔɪ"  : 0b0000000000010,
    "eɪ"  : 0b0000000001000,
    "aɪ"  : 0b0000000010000,
    "uː"  : 0b0000000011110,
    "ɑː"  : 0b0000000001100,
    "iː"  : 0b0000000001111,
    "ɜː"  : 0b0000000010111,
    "æ"   : 0b0000000011100,
    "ə"   : 0b0000000011000,
    "ɛ"   : 0b0000000000111,
    "ʊ"   : 0b0000000000110,
    "ɪ"   : 0b0000000000011,
    "_"   : 0b0000000000000
}

consonants = {
    "tʃ"  : 0b0100101000000,
    "dʒ"  : 0b0101010000000,
    "ŋ"   : 0b0111111100000,
    "ʒ"   : 0b0111110100000,
    "θ"   : 0b0111101000000,
    "ʃ"   : 0b0110111100000,
    "t"   : 0b0110101000000,
    "w"   : 0b0010100000000,
    "s"   : 0b0111011000000,
    "ɹ"   : 0b0111001000000,
    "k"   : 0b0111000100000,
    "p"   : 0b0110001000000,
    "f"   : 0b0110011000000,
    "ɡ"   : 0b0110001100000,
    "d"   : 0b0101010100000,
    "n"   : 0b0000110100000,
    "m"   : 0b0000010100000,
    "z"   : 0b0101101100000,
    "j"   : 0b0101101000000,
    "v"   : 0b0101100100000,
    "h"   : 0b0101001100000,
    "ð"   : 0b0101011100000,
    "l"   : 0b0101001000000,
    "b"   : 0b0101000100000,
    "_"   : 0b0000000000000
}

def normalize_ipa(raw_ipa_text:str)->str:
    ipa = raw_ipa_text

    # Deliaisons
    ipa = ipa.replace('wʌzɐ', 'wʌz ɐ')
    ipa = ipa.replace('fɚɹə', 'fɚɹ ə')
    ipa = re.sub('əvə ', 'əv ə ', ipa)
    ipa = re.sub(r'(?:(?<=^)|(?<=[\s\,\.\!\?]))aɪɐm($|[\s\,\.\!\?])', r'aɪ æm\1', ipa)
    ipa = re.sub(r'(?<=\S)ðə([\s\,\.\!\?])', r' ðə\1', ipa)

    # Dippthong replacements
    ipa = ipa.replace('ɾ','t')
    ipa = ipa.replace('ɚɹ','ʊɹ')
    ipa = ipa.replace('ɜːɹ','ɜː')
    ipa = ipa.replace('ɔɹ','ʊɹ')
    ipa = ipa.replace('ɔːɹ','ʊɹ')
    ipa = ipa.replace('ɔː','ɑː')
    ipa = ipa.replace('ɹɹ','ɹ')
    
    # Monothong replacements
    ipa = ipa.replace('ʌ','ə')
    ipa = ipa.replace('ɐ','ə')
    ipa = ipa.replace('ᵻ','ə')
    ipa = re.sub(r'ɔ(?!ɪ)', r'ɑː', ipa)
    ipa = re.sub(r'i(?!ː)', r'iː', ipa)
    ipa = re.sub(r'ɚ(?!ɹ)', r'ɜː', ipa)

    # Punctuation spacing
    ipa = re.sub(r'(\s)([\.\,\!\%\)])',r'\2\1', ipa)

    return ipa

def extract_next_phoneme(string:str, start:int)->str:
    if start >= len(string):
        return ''
    
    for phoneme in consonants.keys():
        if string[start:].startswith(phoneme):
            return phoneme
    for phoneme in vowels.keys():
        if string[start:].startswith(phoneme):
            return phoneme
    return string[start]

def convert_to_normalized_ipa(text: str) -> str:
    # Preprocessing
    text = text.replace(' – ',',,')
    text = text.replace(' - ',',,')

    ipa = phonemize(
        text,
        language="en-us",
        backend="espeak",
        preserve_punctuation=True,
    )
    print(f"raw: {ipa}")
    ipa = normalize_ipa(ipa)
    ipa = ipa.replace(',,', ' - ')
    print(f"normalized: {ipa}")

    return ipa

def english_to_trunic(text:str) -> list:
    """
    Takes English text and converts it into a list of unicode characters (or punctuation)
    to be rendered in HTML with one of the Trunic fonts. The phonemes used to create the 
    Trunic glyphs are based on American English pronunciation.
    """

    ipa = convert_to_normalized_ipa(text)
    
    syllables = []
    syllable_names = []
    cur = 0

    with open(BASE_DIR / "Data" / "unicode_mapping.json","r") as f:
        unicode_mapping = json.loads(f.read())

    while cur < len(ipa):
        phoneme_1 = extract_next_phoneme(ipa, cur)
        phoneme_2 = extract_next_phoneme(ipa, cur + len(phoneme_1))
        syllable_name = f"{phoneme_1}{phoneme_2}"

        # Full syllable identified
        if syllable_unicode := unicode_mapping.get(syllable_name):
            cur += len(syllable_name)
            syllables.append(syllable_unicode)
            syllable_names.append(syllable_name)
        # Only next phoneme has a mapping
        elif syllable_unicode := unicode_mapping.get(phoneme_1):
            cur += len(phoneme_1)
            syllables.append(syllable_unicode)
            syllable_names.append(phoneme_1)
        # Next phoneme is not a mappable object, render it literally
        else:
            cur += len(phoneme_1)
            syllables.append(phoneme_1)
            syllable_names.append(phoneme_1)

    return syllables