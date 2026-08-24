# ComfyUI-PillowImageSaver

ComfyUI用の、Pillowを用いた画像保存ノード群じゃ。

最初のノード **Pillow Image JPEG Save** は、出力専用のJPEG保存ノードじゃぞ。ComfyUIの `IMAGE` テンソルを Pillow で直接JPEG保存し、プレビュー画像は返さない設計になっておる。

このプロジェクトは [ComfyUI-GMImageSaver](https://github.com/ruminar/ComfyUI-GMImageSaver) の Pillow版兄弟ノードじゃ。ユーザー向け仕様はできるだけ揃えつつ、GraphicsMagickを使う部分だけPillowに置き換えておる。

## ノード

### Pillow Image JPEG Save

「ただひたすらにJPEGを保存する」ことに特化した、意図的に機能を絞り込んだノードじゃ。

汎用的な画像保存ノードを目指したものではないぞ。

- JPEG専用
- PNG出力なし
- プレビュー出力なし
- `IMAGE` のパススルーなし
- 外部コマンド実行なし
- HandpickerSuite への直接依存なし
- 入力ピン経由でのみ、任意のJPEGコメントを追加可能
- `label` 入力ピンを用いた、ファイル・ディレクトリの柔軟な命名
- 画像が保存されるごとに、ComfyUIのプログレスバーを更新

<img width="431" height="364" alt="image" src="https://github.com/user-attachments/assets/c784580e-965d-4340-a9d0-fdf7441dacba" />


PNGで保存したい時は、ComfyUI標準の Save Image ノードを使うのじゃ。

## 動作要件

Pillow が必要じゃ。

多くの ComfyUI 環境ではすでに Pillow が入っているはずじゃが、このリポジトリには `requirements.txt` も用意しておる。

## 入力

必須ピン:

- `images`: ComfyUIの `IMAGE` テンソルじゃ。
- `filename_prefix`: ファイル名の接頭辞。デフォルトは `image` じゃ。
- `directory_pattern`: ディレクトリの構成パターン。デフォルトは `prefix/date` じゃ。
- `filename_date_format`: ファイル名に付与する日付の書式。デフォルトは `none` じゃ。
- `quality`: JPEGの品質（1〜100）。デフォルトは `80` じゃ。
- `subsampling`: JPEGのクロマサブサンプリング。デフォルトは `4:2:2` じゃ。
- `progressive`: プログレッシブJPEGにするか否か。デフォルトは `False` じゃ。

オプションピン:

- `output_dir`: 出力先のベースディレクトリじゃ。文字列ノードから繋ぐのじゃ。
- `label`: 追加の命名用ラベルじゃ。ここに `ckpt_name_safe` などの文字列を繋ぐと良いぞ。
- `comment`: JPEGに埋め込むコメント文じゃ。文字列ノードから繋ぐのじゃ。

`output_dir` が未接続、または空欄の場合は、ComfyUI標準の output ディレクトリが使われるぞ。

相対パスを指定した場合は標準outputディレクトリの配下に、絶対パスを指定した場合はその場所に直接保存される仕様じゃ。

Windowsのドライブ相対パス（`C:foo` など）は拒否されるぞ。代わりに `C:\foo` のような絶対パスを指定するのじゃ。

## ディレクトリパターン

`directory_pattern` は、`output_dir` の下に作られるフォルダ構造を決定するぞ。`date` 部分は常に `yyyyMMdd` 形式じゃ。

選択可能なパターン:

```text
none
date
prefix
prefix_date
prefix/date
label
label_date
label/date
prefix_label
prefix/label
prefix_label_date
prefix/label/date
prefix_date_label
prefix/date/label
```

出力例:

```text
output_dir: D:\ComfyJPEG
filename_prefix: image
label: meinamix_v11
date: 20260601
```

```text
none                -> D:\ComfyJPEG
date                -> D:\ComfyJPEG\20260601
prefix              -> D:\ComfyJPEG\image
prefix_date         -> D:\ComfyJPEG\image_20260601
prefix/date         -> D:\ComfyJPEG\image\20260601
label               -> D:\ComfyJPEG\meinamix_v11
label_date          -> D:\ComfyJPEG\meinamix_v11_20260601
label/date          -> D:\ComfyJPEG\meinamix_v11\20260601
prefix_label        -> D:\ComfyJPEG\image_meinamix_v11
prefix/label        -> D:\ComfyJPEG\image\meinamix_v11
prefix_label_date   -> D:\ComfyJPEG\image_meinamix_v11_20260601
prefix/label/date   -> D:\ComfyJPEG\image\meinamix_v11\20260601
prefix_date_label   -> D:\ComfyJPEG\image_20260601_meinamix_v11
prefix/date/label   -> D:\ComfyJPEG\image\20260601\meinamix_v11
```

`label` を含むパターンを選んだ場合は、必ず `label` ピンに何かを接続するのじゃぞ。

## ファイル名の日付フォーマット

`filename_date_format` は、ファイル名そのものに刻まれる日付を制御するぞ。ディレクトリとは別じゃ。

選択可能な値:

```text
none
yyyyMMdd
yyyyMMdd_HHmm
```

連番は常に4桁じゃ。

```text
image_0001.jpg
image_20260601_0001.jpg
image_20260601_1423_0001.jpg
image_meinamix_v11_0001.jpg
image_meinamix_v11_20260601_1423_0001.jpg
```

`label` ピンが接続されている場合は、このように自動的にファイル名にも組み込まれるのじゃ。

タイムスタンプはノード実行時に1回だけ固定されるため、同じバッチ内で生成された画像はすべて同じ時刻のファイル名になるぞ。

## おすすめ運用

大量生成やCheckpoint棚卸し用途では、初期値は軽めの設定にしておる。

```text
quality: 80
subsampling: 4:2:2
```

棚卸しが終わり、お気に入りCheckpointや画像を絞り込んだ後は、必要に応じて次のように画質を上げて保存するとよいぞ。

```text
quality: 95
subsampling: 4:4:4
```

## HandpickerSuiteとの連携

このノードは HandpickerSuite に依存しない。

ただし、[ComfyUI-CheckpointHandpickerSuite](https://github.com/ruminar/ComfyUI-CheckpointHandpickerSuite) のようなCheckpoint棚卸しワークフローとは相性がよいぞ。

たとえばこう繋ぐだけじゃ。

```text
ckpt_name_safe -> label
```

これにより、Checkpoint名を含むファイル名やディレクトリ構造で、画像を整理しながら保存できる。

## 進捗表示

画像が1枚保存されるごとに、ComfyUIの進捗バーを更新するぞ。

## プレビューポリシー

このノードは意図的にプレビュー画像を返さない仕様じゃ。

プレビューを見たい場合は、このノードの直前で `IMAGE` テンソルを分岐させ、お好みのプレビュー専用ノードへ繋ぐのじゃ。

```text
VAE Decode / IMAGE
  ├─ Preview node
  └─ Pillow Image JPEG Save
```

## ライセンス

GPL-3.0

## 宣伝画像

<img width="1055" height="1491" alt="PillowImageSaver宣伝画像" src="https://github.com/user-attachments/assets/cc44d6c2-5dc1-4a1b-93fd-15def20e50e8" />

