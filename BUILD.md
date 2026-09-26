# Windows EXE ビルドガイド

Macで開発している場合でも、簡単に Windows 用 `.exe` をビルド・取得できるように3つの方法を用意しています。

---

## 方法 1: GitHub Actions を使う方法（おすすめ・Macから完全自動化）

Mac上での開発時に最も簡単な方法です。Windows実機がなくてもGitHub上で自動ビルドされます。

1. 本リポジトリを GitHub に Push します。
2. GitHub の **Actions** タブを開きます。
3. **Build Windows EXE** ワークフローが自動実行されます（手動実行したい場合は `Run workflow` を押すことも可能です）。
4. ビルド完了後、**Artifacts** から `Sports2D_GUI_Windows_x64` (ZIPファイル) をダウンロードします。
5. 解凍すると、Windows 上でそのまま実行できる `Sports2D_GUI.exe` が入手できます！

---

## 方法 2: Windows 実機でワンクリックビルドする

Windows マシンで直接 `.exe` を作成する場合の手順です。

1. Windows 上で Python 3.11+ をインストールします。
2. 本リポジトリをダウンロード / clone します。
3. リポジトリ内の `build_windows.bat` をダブルクリックして実行します。
4. 処理が終わると `dist\Sports2D_GUI\` フォルダの中に `Sports2D_GUI.exe` が生成されます。

---

## 方法 3: コマンドラインからビルドする

```bash
# 依存関係のインストール
pip install -e .
pip install pyinstaller

# ビルド実行
python build_exe.py
```

生成物: `dist/Sports2D_GUI/Sports2D_GUI.exe`
