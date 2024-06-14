import shutil  # ファイル操作ユーティリティ
import os  # OS操作ユーティリティ

# サムネイルキャッシュディレクトリのパスを設定
cache_dir = os.path.join("dist", "thumbnail_cache")

# キャッシュディレクトリが存在するか確認
if os.path.exists(cache_dir):
    # ディレクトリとその中身を再帰的に削除
    shutil.rmtree(cache_dir)
    print(f"キャッシュディレクトリ {cache_dir} をクリアしました")
else:
    # ディレクトリが存在しない場合のメッセージ
    print(f"キャッシュディレクトリ {cache_dir} は存在しません")
