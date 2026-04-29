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

numbers = {
    "0": 0b1000000000000,
    "1": 0b0001000000000,
    "2": 0b0010100000000,
    "3": 0b0011100000000,
    "4": 0b0010110100000,
    "5": 0b0011110100000,
    "6": 0b0010110111000,
    "7": 0b0011110111000,
    "8": 0b0010110111011,
    "9": 0b0011110111011
}


with open(BASE_DIR / "Data" / "word_substitutions.json","r", encoding="utf-8") as f:
        word_substitutions = json.loads(f.read())

# re_sep = "\n\s\,\.\!\?\[\]\{\}\(\)\""
re_sep = r"[\W\n\s]"
def word_replace(text:str, target:str, repl:str) -> str:
    return re.sub(rf'(?:(?<=^)|(?<={re_sep})){target}($|{re_sep})', rf'{repl}\1', text)

def normalize_ipa(raw_ipa_text:str)->str:
    ipa = raw_ipa_text

    # Substring replacements
    ipa = re.sub(rf'ifəl(?={re_sep})', r'ɪfəl', ipa) # e.g. beautiful

    # Dippthong/syllable replacements
    ipa = ipa.replace('ʔn̩','ən')
    ipa = ipa.replace('ɜːɹ','ɜː')
    ipa = ipa.replace('ɔɹ','ʊɹ')
    ipa = ipa.replace('ɔːɹ','ʊɹ')
    ipa = ipa.replace('ɔː','ɑː')
    
    # Monothong replacements
    ipa = ipa.replace('ɾ','t')
    ipa = ipa.replace('ɹɹ','ɹ')
    ipa = ipa.replace('ʌ','ə')
    ipa = ipa.replace('ɐ','ə')
    ipa = ipa.replace('ᵻ','ə')
    ipa = ipa.replace('ɚɹ','ɜː') # e.g. numerous
    ipa = ipa.replace('ɚ','ɜː') # e.g. general
    ipa = re.sub(r'ɔ(?!ɪ)', r'ɑː', ipa)
    ipa = re.sub(r'i(?!ː)', r'iː', ipa)

    ## Post-normalized word replacements and de-liaisons
    for target, substitution in word_substitutions.items():
        ipa = word_replace(ipa, target, substitution)
    ipa = re.sub(rf'(?:(?<=^)|(?<=[\s\,\.\!\?]))nɑːtɜː ɹ', 'nɑːt ə ɹ', ipa) # e.g. not a rare
    ipa = re.sub(rf'(?<=\w)wəz({re_sep})', r' wəz\1', ipa)
    ipa = re.sub(rf'(?<=\w)ðə({re_sep})', r' ðə\1', ipa)

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
    for phoneme in numbers.keys():
        if string[start:].startswith(phoneme):
            return phoneme
    return string[start]

def convert_to_normalized_ipa(text: str) -> str:

    dont_phonemize = "1234567890,.–-(){}[]<>/\\%!?*^:;`¬|\n!\"°#~+£$&"

    ipa = phonemize(
        text,
        language="en-us",
        backend="espeak",
        preserve_punctuation=True,
        punctuation_marks=dont_phonemize
    )
    print(f"raw: {ipa}")
    ipa = normalize_ipa(ipa)
    print(f"normalized: {ipa}")

    return ipa

def english_to_trunic(
        text:str,
        minimise_inversions:bool=False,
        convert_numbers:bool=True
    ) -> list:
    """
    Takes English text and converts it into a list of unicode characters (or punctuation)
    to be rendered in HTML with one of the Trunic fonts. The phonemes used to create the 
    Trunic glyphs are based on American English pronunciation.

    Setting `deinvert` to True will attempt to minimise inverted glyph chains to make words
    easier to read. This works by ensuring any instance of VCV is rendered as V-CV instead of VC-V.
    For example, "anemones" may be easier to read if it starts with the "a" glyph by itself
    """

    ipa = convert_to_normalized_ipa(text)
    
    syllables = []
    cur = 0

    with open(BASE_DIR / "Data" / "unicode_mapping.json","r", encoding="utf-8") as f:
        unicode_mapping = json.loads(f.read())

    while cur < len(ipa):
        phoneme_1 = extract_next_phoneme(ipa, cur)

        if phoneme_1 == ' ':
            syllables.append(' ')
            cur += 1
            continue
        elif phoneme_1 in numbers:
            if convert_numbers:
                syllable = unicode_mapping[phoneme_1]
            else:
                syllable = phoneme_1
            syllables.append(syllable)
            cur += 1
            continue

        phoneme_2 = extract_next_phoneme(ipa, cur + len(phoneme_1))
        phoneme_3 = extract_next_phoneme(ipa, cur + len(phoneme_1)+ len(phoneme_2))
        syllable_name = f"{phoneme_1}{phoneme_2}"

        # Start with a vowel-only glyph if the word starts with <vowel><cons><vowel>
        # This helps prevent chains of inversions which make words harder to read
        vowel_only = minimise_inversions \
            and phoneme_1 in vowels \
            and phoneme_2 in consonants \
            and phoneme_3 in vowels

        # Full syllable identified
        if not vowel_only and syllable_name in unicode_mapping:
            cur += len(syllable_name)
            
            syllable_unicode = unicode_mapping.get(syllable_name)
            syllables.append(syllable_unicode)

        # Only next phoneme has a mapping
        elif phoneme_1 in unicode_mapping:
            cur += len(phoneme_1)

            syllable_unicode = unicode_mapping.get(phoneme_1)
            syllables.append(syllable_unicode)

        # Next phoneme is not a mappable object, render it literally
        else:
            cur += len(phoneme_1)

            if phoneme_1 == '\n':
                phoneme_1 = '<br>'

            syllables.append(phoneme_1)

    return syllables