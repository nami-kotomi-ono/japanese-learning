import os
import re
from google.cloud import texttospeech
from pydub import AudioSegment

# Set the environment variable (replace with your actual path)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\\Users\\user\\GOOGLE_APPLICATION_CREDENTIALS\\carbide-eye-435714-a6-0fc9ffff53f4.json'

# Specify the directory for audio files
audio_dir = "c:/Users/user/Documents/AudioFiles/JapanesePhrase/2"

# Create the directory if it does not exist
os.makedirs(audio_dir, exist_ok=True)

# Function to clean up filenames
def clean_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "", text)

# Function for Google Cloud Text-to-Speech
def synthesize_text(text, language_code, voice_name, filename, gender):
    """
    Generate audio file using Google Cloud Text-to-Speech API.

    Args:
    - text (str): The text to be converted into speech.
    - language_code (str): The language code (e.g., 'ja-JP' for Japanese).
    - voice_name (str): The name of the voice model.
    - filename (str): The filename for the output audio file.
    - gender (SsmlVoiceGender): The gender of the voice (MALE or FEMALE).

    Returns:
    - str: The path to the generated audio file.
    """
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=gender
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    # Ensure the directory exists
    full_filename = os.path.join(audio_dir, filename).replace("\\", "/")
    os.makedirs(os.path.dirname(full_filename), exist_ok=True)

    with open(full_filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{full_filename}"')
    return full_filename

# Function to get the duration of the audio file
def get_audio_duration(file_path):
    """
    Calculate the duration of the audio file.

    Args:
    - file_path (str): The path to the audio file.

    Returns:
    - float: The duration of the audio file in seconds.
    """
    audio = AudioSegment.from_file(file_path)
    return len(audio) / 1000  # Convert milliseconds to seconds

# Create a list of phrases and audio files
phrases = [
    {"japanese": "そうかもね", "english": "Maybe so"},  # "Could be"
    {"japanese": "気に入った", "english": "I like it"},  # "I'm into it"
    {"japanese": "そんなに", "english": "Not that much"},  # "Not really"
    {"japanese": "おそらく", "english": "Probably"},  # "Most likely"
    {"japanese": "どういうこと？", "english": "What do you mean?"},  # "How so?"
    {"japanese": "正直言うと", "english": "To be honest"},  # "Honestly"
    {"japanese": "思ったより", "english": "More than I expected"},  # "Surprisingly"
    {"japanese": "うまくいった", "english": "It went well"},  # "Succeeded"
    {"japanese": "ちょうどいい", "english": "Just right"},  # "Perfect timing"
    {"japanese": "気になる", "english": "I'm curious"},  # "Interested in"
    {"japanese": "すっかり忘れてた", "english": "I completely forgot"},  # "Slipped my mind"
    {"japanese": "なるべく早く", "english": "As soon as possible"},  # "As quickly as possible"
    {"japanese": "冗談でしょ？", "english": "You're kidding, right?"},  # "No way!"
]


# Main processing
current_time = 0  # Track the current time

# Initialize ExtendScript content
script_content = """
var project = app.project;
var sequence = project.sequences[0];
"""

print("Start generating ExtendScript content...")

# Process each phrase
for i, phrase in enumerate(phrases):
    japanese_text = phrase["japanese"]
    english_text = phrase["english"]

    # Generate one Japanese male voice audio file using Google Cloud Text-to-Speech API
    japanese_male_filename = f"{i+1:02d}[1J]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
    japanese_male_audio_file = synthesize_text(japanese_text, "ja-JP", "ja-JP-Neural2-D", japanese_male_filename, texttospeech.SsmlVoiceGender.MALE)
    japanese_male_duration = get_audio_duration(japanese_male_audio_file)

    # Duplicate the generated Japanese audio file to create two additional versions with different filenames
    japanese_audio_files = [japanese_male_audio_file]  # Store the original file path
    for j in range(2, 4):  # Start from 2 to create [2J] and [3J]
        # File names are prefixed with [2J], [3J] respectively
        duplicated_filename = f"{i+1:02d}[{j}J]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
        duplicated_audio_file = os.path.join(audio_dir, duplicated_filename)
        # Copy the content of the original file to the new file
        AudioSegment.from_file(japanese_male_audio_file).export(duplicated_audio_file, format="mp3")
        print(f'Duplicated audio content to file "{duplicated_audio_file}"')
        japanese_audio_files.append(duplicated_audio_file)  # Store duplicated file path

    # Generate English audio file (female voice)
    english_filename = f"{i+1:02d}[1EN]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
    english_audio_file = synthesize_text(english_text, "en-US", "en-US-Wavenet-F", english_filename, texttospeech.SsmlVoiceGender.FEMALE)
    english_duration = get_audio_duration(english_audio_file)

    # Add audio file paths to the phrase
    phrase["audio_files"] = japanese_audio_files + [english_audio_file]  # Include all Japanese and English files

    # Add all generated audio files to ExtendScript content
    for idx, audio_file in enumerate(phrase["audio_files"]):
        audio_file_escaped = audio_file.replace("\\", "/")  # Use forward slashes
        script_content += f"""
var importResult = project.importFiles(["{audio_file_escaped}"], false, project.rootItem, false);
if (importResult && importResult[0]) {{
    var audioClip = importResult[0];
    var audioTrack = sequence.audioTracks[{idx}];
    var timeOffset = new Time({current_time}, 0);
    audioTrack.insertClip(audioClip, timeOffset.ticks);
}}
"""
        # Update playback time
        if idx < len(japanese_audio_files):  # For Japanese audio files
            current_time += japanese_male_duration
        else:  # For English audio files
            current_time += english_duration

print("ExtendScript content generated.")

# Save ExtendScript file
try:
    file_path = os.path.join(audio_dir, "import_audio_to_premiere.jsx")
    print(f"Attempting to write to {file_path}...")
    with open(file_path, "w", encoding="utf-8") as script_file:
        script_file.write(script_content)
    print(f"ExtendScript code has been generated and saved to {file_path}")
except Exception as e:
    print(f"Failed to write ExtendScript file: {e}")
