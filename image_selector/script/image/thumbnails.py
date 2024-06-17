import os
import hashlib
import threading
from queue import PriorityQueue
from PIL import Image, ImageTk, ExifTags
from script.image.rotation import Rotation  # 画像回転用モジュール

class Thumbnails:
    cache_dir = os.path.join("dist", "thumbnail_cache")  # サムネイルキャッシュのディレクトリ
    lock = threading.Lock()  # スレッド間の排他制御のためのロック
    queue = PriorityQueue()  # サムネイル生成のための優先キュー
    generating = False  # generating属性を追加

    def __init__(self):
        pass

    @staticmethod
    def generate(selector):
        if not os.path.exists(Thumbnails.cache_dir):
            os.makedirs(Thumbnails.cache_dir)

        selector.thumbnails = []  # サムネイルパスのリストを初期化
        for image_path in selector.images:
            Thumbnails.queue.put((False, image_path))  # 通常優先度のサムネイル生成をキューに追加

        # サムネイル生成が行われていない場合は、新しいスレッドで生成処理を開始
        with Thumbnails.lock:
            if not Thumbnails.generating:
                Thumbnails.generating = True
                threading.Thread(target=Thumbnails.process_queue, args=(selector,)).start()

    @staticmethod
    def add_to_queue(image_path, priority=False):
        # 指定された優先度でサムネイル生成をキューに追加
        Thumbnails.queue.put((priority, image_path))

    @staticmethod
    def process_queue(selector):
        while not Thumbnails.queue.empty():
            priority, image_path = Thumbnails.queue.get()  # キューから画像パスを取得
            thumbnail_path = Thumbnails.get_thumbnail_path(image_path)  # キャッシュサムネイルのパスを取得
            if not os.path.exists(thumbnail_path):
                try:
                    # 画像を開いてサムネイルを生成
                    img = Image.open(image_path)
                    img = Rotation.rotate_image(img, image_path)  # 画像の向きを修正
                    img.thumbnail((150, 150))  # サムネイルサイズにリサイズ
                    img.save(thumbnail_path, "JPEG")  # サムネイルをJPEG形式で保存
                    print(f"サムネイルを生成しました: {thumbnail_path}")
                except Exception as e:
                    # サムネイル生成に失敗した場合のエラーメッセージ
                    print(f"サムネイルの生成に失敗しました {image_path}: {e}")
                    continue
            else:
                # キャッシュにサムネイルが存在する場合
                print(f"キャッシュからサムネイルを読み込みました: {thumbnail_path}")
            with Thumbnails.lock:
                # サムネイルパスをセレクタのリストに追加
                selector.thumbnails.append(thumbnail_path)
            selector.master.after(0, selector.update_status_label)  # ステータスラベルを更新

        with Thumbnails.lock:
            Thumbnails.generating = False  # サムネイル生成中フラグを下げる

        selector.master.after(0, selector.show_image)  # サムネイル生成後画像を表示

    @staticmethod
    def show(selector):
        # 現在の画像を表示する
        if selector.images:
            image_path = selector.images[selector.current_image_index]
            thumbnail_path = Thumbnails.get_thumbnail_path(image_path)
            if os.path.exists(thumbnail_path):
                img = Image.open(thumbnail_path)
            else:
                img = Image.open(image_path)
                img = Rotation.rotate_image(img, image_path)  # 画像の向きを修正
                img.thumbnail((600, 400))
            img_tk = ImageTk.PhotoImage(img)
            selector.image_label.config(image=img_tk)
            selector.image_label.image = img_tk

    @staticmethod
    def get_thumbnail_path(image_path):
        # 画像パスをMD5でハッシュ化してサムネイルのパスを生成
        hash_name = hashlib.md5(image_path.encode()).hexdigest() + ".jpg"
        return os.path.join(Thumbnails.cache_dir, hash_name)
