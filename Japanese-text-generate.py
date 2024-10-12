import re
import MeCab  # MeCabを使用して漢字をひらがなに変換

# フレーズリスト（英語と日本語のペア）
phrases = [
    {"japanese": "お久しぶり", "english": "Long time no see"},  # "It's been a while"
    {"japanese": "最近どう？", "english": "How have you been?"},  # "What's new?"
    {"japanese": "調子はどう？", "english": "How's it going?"},  # "How's everything?"
    {"japanese": "やっぱり", "english": "As expected"},  # "I knew it"
    {"japanese": "なんとなく", "english": "Just because"},  # "No specific reason"
    {"japanese": "気にしないで", "english": "Don't worry about it"},  # "No worries"
    {"japanese": "めっちゃ嬉しい", "english": "I'm so happy"},  # "Super glad"
    {"japanese": "信じられない", "english": "I can't believe it"},  # "Unbelievable"
    {"japanese": "その通り", "english": "Exactly"},  # "That's right"
    {"japanese": "たぶんね", "english": "Maybe"},  # "Probably"
    {"japanese": "どうしても", "english": "No matter what"},  # "By all means"
    {"japanese": "大変だね", "english": "That's tough"},  # "Must be hard"
    {"japanese": "何て言うか", "english": "How should I say this?"},  # "It's like..."
    {"japanese": "そんなことないよ", "english": "Not really"},  # "I don't think so"
    {"japanese": "ありえる", "english": "That's possible"},  # "Could happen"
    {"japanese": "どうしようかな", "english": "What should I do?"},  # "I'm not sure"
    {"japanese": "楽しみにしてる", "english": "I'm looking forward to it"},  # "Can't wait"
    {"japanese": "ちょっと無理かも", "english": "It might be a bit difficult"},  # "Not sure if I can"
    {"japanese": "そう言えば", "english": "By the way"},  # "Speaking of which"
    {"japanese": "やっと終わった", "english": "Finally finished"},  # "It's done at last"
    {"japanese": "たしかに", "english": "Indeed"},  # "That's true"
    {"japanese": "楽しそう", "english": "Looks fun"},  # "Seems enjoyable"
    {"japanese": "本当に助かった", "english": "You really helped me"},  # "I appreciate it"
    {"japanese": "それな", "english": "Exactly"},  # "I know, right?"
    {"japanese": "悪くないね", "english": "Not bad"},  # "Pretty decent"
    {"japanese": "なんとかなる", "english": "It'll work out somehow"},  # "It'll be fine"
    {"japanese": "全然大丈夫", "english": "Totally fine"},  # "No problem at all"
    {"japanese": "やってみる", "english": "I'll give it a try"},  # "I'll try it out"
    {"japanese": "すごく助かった", "english": "That really helped"},  # "It was a big help"
    {"japanese": "気をつけないと", "english": "Gotta be careful"},  # "I need to be cautious"
    {"japanese": "おかげさまで", "english": "Thanks to you"},  # "Because of you, it's better"
    {"japanese": "お先に", "english": "I'll go ahead"},  # "Going first"
    {"japanese": "よくあることだよ", "english": "It happens"},  # "Common thing"
    {"japanese": "まぁまぁ", "english": "Not too bad"},  # "Not too bad"
    {"japanese": "なんだかんだで", "english": "One way or another"},  # "Somehow or another"
    {"japanese": "考えとく", "english": "I'll think about it"},  # "Let me consider it"
    {"japanese": "ついでに", "english": "By the way"},  # "While you're at it"
    {"japanese": "どうにかなる", "english": "It'll work out"},  # "It'll be okay"
    {"japanese": "いろいろありがとう", "english": "Thanks for everything"},  # "Appreciate all the help"
    {"japanese": "また今度", "english": "Maybe next time"},  # "Let's do it some other time"
    {"japanese": "微妙だね", "english": "It's iffy"},  # "Not so sure"
    {"japanese": "やっぱりそうか", "english": "I thought so"},  # "As expected"
    {"japanese": "もう少しで", "english": "Almost there"},  # "Just a bit more"
    {"japanese": "急にごめんね", "english": "Sorry for the sudden request"},  # "Didn't mean to surprise you"
    {"japanese": "この間", "english": "The other day"},  # "Recently"
    {"japanese": "お疲れ様でした", "english": "Good work"},  # "Thanks for your hard work"
    {"japanese": "確かにそうだね", "english": "You're right"},  # "That's true"
    {"japanese": "なんか変だね", "english": "Something feels off"},  # "Seems weird"
    {"japanese": "できれば", "english": "If possible"},  # "Preferably"
    {"japanese": "たまにはいいね", "english": "It's nice once in a while"},  # "Not bad for a change"
    {"japanese": "助かる", "english": "That helps"},  # "Appreciate it"
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


# 入力と出力のSRTファイルパス
input_srt_file_path = "C:/Users/user/Documents/AudioFiles/JapanesePhrase/テキストに変換する音声ファイル/シーケンス 01.srt"
output_srt_file_path = "C:/Users/user/Documents/AudioFiles/JapanesePhrase/テキストに変換する音声ファイル/英語学習2-1.srt"

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
    tagger = MeCab.Tagger("-Oyomi")  # -Oyomi オプションで読み仮名を取得
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
        'ッ': '',  # 'ッ' needs further handling for correct conversion
        'ー': '-',  # Prolonged sound mark
        'ヴ': 'vu'  # 'ヴ' sound
    }
    romaji_text = ""
    for char in katakana_text:
        romaji_text += katakana_to_romaji.get(char, char)
    return romaji_text

def katakana_to_hiragana(katakana_text):
    """Convert Katakana to Hiragana"""
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
                    'end': next_entry['start'],  # エンド時間は後で調整するので、今は次のエントリの開始時間を使用
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
                    'end': speaker2_end_time,  # エンド時間は後で調整するので、今は次のエントリの開始時間を使用
                    'text': combined_text
                }
                new_subtitles.append(speaker2_entry)

                # インデックスを次の話者1のエントリに進める
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

print(f"新しいSRTファイルが作成されました: {output_srt_file_path}")
