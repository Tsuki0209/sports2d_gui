# Sports2D Studio GUI 🚀

Sports2D（2次元Markerless動作解析ライブラリ）を、モダンで洗練されたデスクトップGUIから直感的に操作するためのオープンソース・フロントエンドです。

---

## ✨ 特長・主な変更点

- 🎨 **モダンな UI/UX デザイン**: フラット・ダークテーマ調のカードレイアウトとサイドバーナビゲーションを採用。
- 📂 **Drag & Drop 対応**: 動画ファイルやパラメータファイルを画面上に直接ドラッグ＆ドロップして即座に登録。
- 🎛️ **フィルタ設定のインタラクティブ化**: Butterworth, Kalman, 1-Euro, GCV Spline 等の各フィルタ設定をリアルタイム入力可能。
- 📊 **解析結果・生成物ビューア機能**: 処理後の動画再生案内、各種グラフ画像・データのプレビュー表示、OSのファイルマネージャーでダイレクトオープン。
- ⚡ **プリセット設定機能**: 「標準」「高精度・詳細」「高速スクリーニング」「OpenSim連携」を一発切り替え。
- 💻 **Cross-Platform & 簡単 Windows EXE 化**: PyInstaller 構成および GitHub Actions を標準搭載。Macで開発して push するだけで Windows 用 standalone `.exe` を自動ビルド可能です。

---

## 💻 起動方法 (Mac / Windows / Linux)

### 環境構築

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

python -m pip install -U pip
python -m pip install -e .
```

### 起動

```bash
sports2d-gui
```

または

```bash
python run_gui.py
```

---

## 📦 Windows EXE にパッケージ化する

Mac上で開発していても、以下の方法で簡単に Windows 用の `.exe` を生成・取得できます。

### 方法 A: GitHub Actions (おすすめ・Macから完全自動)
1. リポジトリを GitHub に push します。
2. GitHub の Actions タブから **Build Windows EXE** ワークフローが自動実行されます。
3. 完了後、Artifacts から ZIP（`Sports2D_GUI.exe` 梱包）をダウンロードできます！

### 方法 B: Windows実機でワンクリックビルド
Windows 上で `build_windows.bat` をダブルクリックするだけで `dist/Sports2D_GUI/Sports2D_GUI.exe` が作成されます。

詳細な手順は [BUILD.md](file:///Users/yy/Downloads/sports2d_gui/BUILD.md) を参照してください。

---

## 🎯 画面構成

1. **🎬 プロジェクト & 動画**: 動画ファイル入力 (D&D対応)、webcam、時間範囲、解像度、結果出力ディレクトリ
2. **👤 Pose & トラッキング**: Poseモデル (body_with_feet/whole_body等)、モード (performance/balanced/lightweight)、検出周波数、トラッキング、閾値
3. **📐 座標変換 & 校正**: 実寸法(m)変換、Perspective補正、C3Dバイナリ出力、校正TOML
4. **🦴 角度計算**: 関節角度・セグメント角度のマルチ選択、表示オーバーレイ、床角補正
5. **🧹 Post-processing**: 欠損補間、外れ値自動検出、各平滑化フィルタ (Butterworth, Kalman, 1-Euro等) の動的パラメータフォーム
6. **🏃 Kinematics & OpenSim**: Inverse Kinematics (IK), Keypoint Augmentation, 身体パラメータ, OpenSim連動
7. **📊 出力設定**: 動画/画像/TRC/MOT/グラフ出力制御、スローモーション倍率
8. **📝 Advanced TOML**: リアルタイム構文チェック・フォーム相互バインディング付き TOML エディタ
9. **📁 結果ビューア**: 解析結果（動画・画像・数値データ）の内部プレビュー & OSフォルダオープン
10. **⚙️ 環境 & プリセット**: Python/Sports2D検出状態確認とクイックプリセットの適用

---

## 📜 ライセンス

このGUI部分は MIT License です。Sports2D 本体は別プロジェクトであり、同プロジェクトのライセンス（BSD 3-Clause）に従います。

Sports2D 公式: https://github.com/davidpagnon/Sports2D
