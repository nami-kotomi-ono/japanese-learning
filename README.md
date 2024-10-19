# 日本語学習動画自動生成システム

このプロジェクトは、日本語学習者向けの教育動画を自動で作成するためのシステムです。

Google Cloud Text-to-Speech (TTS) API を利用して対応する音声ファイルを生成し、それらをAdobe Premiere Proにインポートして、動画を作成します。
字幕は、ローマ字表記、ひらがな表記を生成しています。

作成した動画はこちらにアップしています
https://www.youtube.com/@japaneselearningjourneylife


## 目次

- [特徴](#特徴)
- [前提条件](#前提条件)

## 特徴

- Google Cloud Text-to-Speech APIを使って、日本語と英語の音声ファイルを自動生成します。
- 生成された音声ファイルのExtendScriptを生成し、Adobe Premiere Proに自動的にインポートします。
- `.srt`形式の字幕ファイルを取り込み、英語と日本語のフレーズを処理します。
- 漢字をひらがな、ローマ字に変換し、英語の字幕と組み合わせて両言語の字幕を作成、それもとにを新しい`.srt`形式の字幕ファイルを作成します。


## 前提条件

プロジェクトを実行する前に、以下のソフトウェアやツールが必要です：

- Python 3.x
- `Google Cloud Text-to-Speech` APIを有効にする
- [MeCab](https://taku910.github.io/mecab/)（日本語形態素解析器）と`mecab-python3`ライブラリ
- 音声ファイルを処理するための[Pydub](https://github.com/jiaaro/pydub)→今後は使わない方法に移行
- Adobe Premiere Pro（動画編集用）
- [FFmpeg](https://ffmpeg.org/download.html)（Pydubで音声処理を行うために必要）
