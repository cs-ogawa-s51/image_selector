import os  # OS操作ユーティリティ
import json  # JSON操作ユーティリティ

class FileManager:
    # 破棄リストの読み込み
    @staticmethod
    def load_deleted_images(deleted_images_file):
        # 破棄リストファイルが存在するか確認
        if os.path.exists(deleted_images_file):
            # ファイルが存在する場合、読み込んでリストとして返す
            with open(deleted_images_file, "r") as file:
                return json.load(file)
        # ファイルが存在しない場合は空のリストを返す
        return []

    # 破棄リストの書き込み
    @staticmethod
    def save_deleted_images(deleted_images, deleted_images_file):
        # 破棄リストをファイルに書き込む
        with open(deleted_images_file, "w") as file:
            json.dump(deleted_images, file)

    # 保持リストの読み込み
    @staticmethod
    def load_keep_images(keep_images_file):
        # 保持リストファイルが存在するか確認
        if os.path.exists(keep_images_file):
            # ファイルが存在する場合、読み込んでリストとして返す
            with open(keep_images_file, "r") as file:
                return json.load(file)
        # ファイルが存在しない場合は空のリストを返す
        return []

    # 保持リストの書き込み
    @staticmethod
    def save_keep_images(keep_images, keep_images_file):
        # 保持リストをファイルに書き込む
        with open(keep_images_file, "w") as file:
            json.dump(keep_images, file)
