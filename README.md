# Sports2D GUI

Sports2D の主要機能をデスクトップGUIから操作するためのオープンなフロントエンドです。

## 方針

- 現行 Sports2D の設定体系をGUIへマッピング
- TOMLを一次設定として扱い、未知の将来パラメータをAdvanced editorから保持可能
- Sports2D本体は依存パッケージとして利用し、ソースを同梱しない
- 長時間処理は別プロセスで実行し、GUIを固めない
- ログ・終了コード・生成物をGUIから確認できる

## 対象環境

Python 3.11+。Windows / macOS / Linux を想定。

## インストール

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

GPUを使用する場合のOpenCV/ONNX Runtime等は、Sports2D公式ドキュメントに従って環境側へ導入してください。

## 起動

```bash
sports2d-gui
```

または

```bash
python run_gui.py
```

## 主要画面

- プロジェクト: 動画、webcam、時間範囲、結果ディレクトリ
- 人物・追跡: 人数、人物順序、見える側、Sports2D/DeepSORT、マッチング等
- Pose: モデル、mode、backend、device、検出間隔、閾値
- 座標変換: px→m、C3D、床角、原点、perspective、キャリブレーション
- Angle: 関節/セグメント角度、表示方法
- Post-processing: 補間、外れ値除去、フィルタと個別パラメータ
- Kinematics / OpenSim: marker augmentation、IK、mass、symmetry、scaling等
- Output: video/image/TRC/MOT/graph/realtime の出力制御
- Advanced TOML: 現行GUIがまだフォーム化していない項目や将来追加された項目も編集可能
- 実行ログ: 標準出力/標準エラー、終了コード、生成物ディレクトリ

## 重要

本アプリはSports2DのGUIフロントエンドです。解析アルゴリズムの妥当性や研究用途での精度を保証するものではありません。撮影条件・姿勢推定モデル・キャリブレーション・フィルタ設定は研究プロトコルに合わせて検証してください。

Sports2D公式: https://github.com/davidpagnon/Sports2D

## ライセンス

このGUI部分はMIT Licenseです。Sports2D本体は別プロジェクトで、同プロジェクトのライセンスに従います。
