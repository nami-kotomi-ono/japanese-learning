import re
import MeCab
from dotenv import load_dotenv
import os

load_dotenv()

input_srt_file_path = os.getenv('INPUT_SRT_FILE_PATH')
output_srt_file_path = os.getenv('OUTPUT_SRT_FILE_PATH')

def load_srt_file(file_path):
    """SRTファイルを読み込み、タイムスタンプとテキストをパースする"""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\n|\Z)", re.DOTALL)
    matches = pattern.findall(content)

    subtitles = []
    for match in matches: 
        index = int(match[0])
        start_time = match[1]
        end_time = match[2]
        text = match[3].strip()
        subtitles.append({'index': index, 'start': start_time, 'end': end_time, 'text': text})

    return subtitles

def convert_kanji_to_hiragana(text):
    """漢字をひらがなに変換"""
    tagger = MeCab.Tagger("-Oyomi")
    parsed = tagger.parse(text)
    hiragana_text = ''
    for line in parsed.splitlines():
        if line == 'EOS':
            break
        hiragana_text += line.strip()
    return hiragana_text

def hiragana_to_katakana(hiragana_text):
    """ひらがなをカタカナに変換"""
    return hiragana_text.translate(str.maketrans(
        "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょっーゔ",
        "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポャュョッーヴ"
    ))

def hepburn_romaji(katakana_text):
    katakana_to_romaji = {
        'ア': 'a', 'イ': 'i', 'ウ': 'u', 'エ': 'e', 'オ': 'o',
        'カ': 'ka', 'キ': 'ki', 'ク': 'ku', 'ケ': 'ke', 'コ': 'ko',
        'サ': 'sa', 'シ': 'shi', 'ス': 'su', 'セ': 'se', 'ソ': 'so',
        'タ': 'ta', 'チ': 'chi', 'ツ': 'tsu', 'テ': 'te', 'ト': 'to',
        'ナ': 'na', 'ニ': 'ni', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no',
        'ハ': 'ha', 'ヒ': 'hi', 'フ': 'fu', 'ヘ': 'he', 'ホ': 'ho',
        'マ': 'ma', 'ミ': 'mi', 'ム': 'mu', 'メ': 'me', 'モ': 'mo',
        'ヤ': 'ya', 'ユ': 'yu', 'ヨ': 'yo',
        'ラ': 'ra', 'リ': 'ri', 'ル': 'ru', 'レ': 're', 'ロ': 'ro',
        'ワ': 'wa', 'ヲ': 'wo', 'ン': 'n',
        'ガ': 'ga', 'ギ': 'gi', 'グ': 'gu', 'ゲ': 'ge', 'ゴ': 'go',
        'ザ': 'za', 'ジ': 'ji', 'ズ': 'zu', 'ゼ': 'ze', 'ゾ': 'zo',
        'ダ': 'da', 'ヂ': 'ji', 'ヅ': 'zu', 'デ': 'de', 'ド': 'do',
        'バ': 'ba', 'ビ': 'bi', 'ブ': 'bu', 'ベ': 'be', 'ボ': 'bo',
        'パ': 'pa', 'ピ': 'pi', 'プ': 'pu', 'ペ': 'pe', 'ポ': 'po',
        'ャ': 'ya', 'ュ': 'yu', 'ョ': 'yo',
        'ッ': '', 
        'ー': '-',
        'ヴ': 'vu'
    }
    romaji_text = ""
    for char in katakana_text:
        romaji_text += katakana_to_romaji.get(char, char)
    return romaji_text

def katakana_to_hiragana(katakana_text):
    """カタカナをひらがなに変換"""
    return katakana_text.translate(str.maketrans("アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポャュョッーヴ",
                                                "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゃゅょっーゔ"))

def find_phrases_in_srt(subtitles, phrases):
    """SRTのエントリからphrasesリストに基づいてタイムスタンプを抽出する"""
    new_subtitles = []
    i = 0
    while i < len(subtitles) - 1:
        current = subtitles[i]

        for phrase in phrases:
            # テキストの末尾のピリオドを削除して比較
            current_text = current['text'].rstrip('.')
            if current_text.upper() == phrase['english'].upper():
                # 次のエントリ（話者2）が存在する場合のタイムスタンプ調整
                next_entry = subtitles[i + 1]

                # 話者1のエントリ
                english_text = phrase['english']
                if not english_text.endswith('?'):
                    english_text += '.'

                speaker1_entry = {
                    'index': len(new_subtitles) + 1,
                    'start': current['start'],
                    'end': next_entry['start'],
                    'text': english_text
                }
                new_subtitles.append(speaker1_entry)

                # 漢字の日本語フレーズを取得
                japanese_text = phrase['japanese']
                # 漢字をひらがなに変換
                hiragana_text = convert_kanji_to_hiragana(japanese_text)
                # ひらがなをカタカナに変換
                ja_katakana = hiragana_to_katakana(hiragana_text)
                # カタカナをヘボン式ローマ字に変換
                ja_romaji = hepburn_romaji(ja_katakana)
                # カタカナをひらがなに変換
                ja_katakana_to_hiragana = katakana_to_hiragana(ja_katakana)


                # 結合されたテキスト
                combined_text = f"{ja_romaji}\n{ja_katakana_to_hiragana}"

                # 話者2のエントリ
                if i + 2 < len(subtitles):
                    next_speaker1_entry = subtitles[i + 2]
                    speaker2_end_time = next_speaker1_entry['start']
                else:
                    speaker2_end_time = next_entry['end']  # 次の話者1がない場合は元のエンド時間

                speaker2_entry = {
                    'index': len(new_subtitles) + 1,
                    'start': next_entry['start'],
                    'end': speaker2_end_time,
                    'text': combined_text
                }
                new_subtitles.append(speaker2_entry)

                i += 2
                break
        else:
            i += 1

    return new_subtitles

def adjust_end_times(subtitles):
    """すべてのエントリのエンド時間を次のエントリのスタート時間に変更する"""
    for i in range(len(subtitles) - 1):
        subtitles[i]['end'] = subtitles[i + 1]['start']
    return subtitles

def save_srt_file(subtitles, output_path):
    """SRT形式でファイルを保存する"""
    with open(output_path, 'w', encoding='utf-8') as file:
        for sub in subtitles:
            file.write(f"{sub['index']}\n{sub['start']} --> {sub['end']}\n{sub['text']}\n\n")

# SRTファイルを読み込み
subtitles = load_srt_file(input_srt_file_path)

# フレーズに基づいてタイムスタンプを調整
new_subtitles = find_phrases_in_srt(subtitles, phrases)

# エンド時間を次のエントリのスタート時間に調整
adjusted_subtitles = adjust_end_times(new_subtitles)

# 新しいSRTファイルを保存
save_srt_file(adjusted_subtitles, output_srt_file_path)

print(f"新しいSRTファイルが作成されました。: {output_srt_file_path}")
