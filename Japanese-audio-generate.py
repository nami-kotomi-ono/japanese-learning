import os
import re
from google.cloud import texttospeech
from pydub import AudioSegment
from dotenv import load_dotenv

os.environ.pop('GOOGLE_APPLICATION_CREDENTIALS', None)
load_dotenv()

# 環境変数をチェック

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

audio_dir = os.getenv('AUDIO_DIR', "default/path/if/not/set")

os.makedirs(audio_dir, exist_ok=True)

# ファイル名をクリーンアップする関数
def clean_filename(text):
    """
    ファイル名に使用できない文字を取り除く。

    Args:
    - text (str): 対象の文字列

    Returns:
    - str: クリーンアップされた文字列
    """
    return re.sub(r'[\\/*?:"<>|]', "", text)

# 音声ファイルを生成する関数
def synthesize_text(text, language_code, voice_name, filename, gender):
    """
    Google Cloud Text-to-Speech APIを使用して音声ファイルを生成する。

    Args:
    - text (str): 変換するテキスト
    - language_code (str): 言語コード（例: 'ja-JP'）
    - voice_name (str): 使用する音声モデルの名前
    - filename (str): 出力音声ファイルのファイル名
    - gender (SsmlVoiceGender): 音声の性別（MALEまたはFEMALE）

    Returns:
    - str: 生成された音声ファイルのパス
    """
    try:
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

        # ファイルパスの生成
        full_filename = os.path.join(audio_dir, filename).replace("\\", "/")
        os.makedirs(os.path.dirname(full_filename), exist_ok=True)

        # 音声ファイルを書き込む
        with open(full_filename, "wb") as out:
            out.write(response.audio_content)
            print(f'音声ファイルが生成されました: "{full_filename}"')
        return full_filename

    except Exception as e:
        print(f"音声生成に失敗しました: {e}")
        return None

# 音声ファイルの長さを取得する関数
def get_audio_duration(file_path):
    """
    音声ファイルの再生時間を取得する。

    Args:
    - file_path (str): 音声ファイルのパス

    Returns:
    - float: 音声ファイルの長さ（秒）
    """
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000  # ミリ秒を秒に変換
    except Exception as e:
        print(f"音声ファイルの長さ取得に失敗しました: {e}")
        return 0

# ExtendScriptの内容を生成するための処理
def generate_extendscript(phrases):
    """
    ExtendScriptのコードを生成し、音声ファイルをPremiere Proにインポートするための内容を作成する。

    Args:
    - phrases (list): 処理するフレーズのリスト
    """
    current_time = 0  # 現在のタイムスタンプを追跡
    script_content = """
    var project = app.project;
    var sequence = project.sequences[0];
    """

    for i, phrase in enumerate(phrases):
        japanese_text = phrase["japanese"]
        english_text = phrase["english"]

        # 日本語音声ファイルを生成
        japanese_male_filename = f"{i+1:02d}[1J]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
        japanese_male_audio_file = synthesize_text(japanese_text, "ja-JP", "ja-JP-Neural2-D", japanese_male_filename, texttospeech.SsmlVoiceGender.MALE)
        
        if japanese_male_audio_file is None:
            continue

        japanese_male_duration = get_audio_duration(japanese_male_audio_file)
        japanese_audio_files = [japanese_male_audio_file]  # 元ファイルを格納

        # 日本語音声ファイルを複製（2J, 3Jバージョン）
        for j in range(2, 4):
            duplicated_filename = f"{i+1:02d}[{j}J]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
            duplicated_audio_file = os.path.join(audio_dir, duplicated_filename)
            AudioSegment.from_file(japanese_male_audio_file).export(duplicated_audio_file, format="mp3")
            print(f'複製された音声ファイル: "{duplicated_audio_file}"')
            japanese_audio_files.append(duplicated_audio_file)

        # 英語音声ファイルを生成
        english_filename = f"{i+1:02d}[1EN]{clean_filename(japanese_text)}{clean_filename(english_text)}.mp3"
        english_audio_file = synthesize_text(english_text, "en-US", "en-US-Wavenet-F", english_filename, texttospeech.SsmlVoiceGender.FEMALE)
        english_duration = get_audio_duration(english_audio_file)

        phrase["audio_files"] = japanese_audio_files + [english_audio_file]  # すべての音声ファイルを格納

        # ExtendScriptに音声ファイルを追加
        for idx, audio_file in enumerate(phrase["audio_files"]):
            audio_file_escaped = audio_file.replace("\\", "/")
            script_content += f"""
            var importResult = project.importFiles(["{audio_file_escaped}"], false, project.rootItem, false);
            if (importResult && importResult[0]) {{
                var audioClip = importResult[0];
                var audioTrack = sequence.audioTracks[{idx}];
                var timeOffset = new Time({current_time}, 0);
                audioTrack.insertClip(audioClip, timeOffset.ticks);
            }}
            """
            current_time += japanese_male_duration if idx < len(japanese_audio_files) else english_duration

    return script_content

# ExtendScriptファイルを保存する関数
def save_extendscript(script_content):
    """
    ExtendScriptのコードをファイルに保存する。

    Args:
    - script_content (str): 保存するスクリプトの内容
    """
    try:
        file_path = os.path.join(audio_dir, "import_audio_to_premiere.jsx")
        with open(file_path, "w", encoding="utf-8") as script_file:
            script_file.write(script_content)
        print(f"ExtendScriptが保存されました: {file_path}")
    except Exception as e:
        print(f"ExtendScriptファイルの保存に失敗しました: {e}")

# フレーズのリスト
phrases = [
    {"japanese": "お久しぶり", "english": "Long time no see"},
]

script_content = generate_extendscript(phrases)
save_extendscript(script_content)
