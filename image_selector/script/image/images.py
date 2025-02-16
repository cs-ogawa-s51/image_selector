import os
import threading
import io  # ioモジュールのインポート
from tkinter import filedialog  # ファイル選択ダイアログのためのモジュール
from PIL import Image, ImageTk, ExifTags  # 画像操作とEXIFデータの処理のためのモジュール
import rawpy  # RAW画像の処理のためのモジュール
from datetime import datetime  # 日付と時間の処理のためのモジュール

class Images:
    cache = {}  # キャッシュ用の辞書

    @staticmethod
    def load(selector):
        # フォルダ選択ダイアログを開いて選択されたフォルダを取得
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            print("フォルダが選択されていません")
            return
        # 新しいスレッドで画像を読み込む処理を開始
        threading.Thread(target=Images._load_thread, args=(selector, folder_selected)).start()

    @staticmethod
    def _load_thread(selector, folder_selected):
        print(f"選択されたフォルダ: {folder_selected}")
        files = os.listdir(folder_selected)  # フォルダ内のファイル一覧を取得
        total_files = len(files)  # ファイルの総数を取得

        # 破棄リストと保持リストをセットに変換
        deleted_images_set = set(selector.deleted_images)
        keep_images_set = set(selector.keep_images)

        image_paths = []  # 画像ファイルのパスを格納するリスト

        for index, file in enumerate(files):
            # 対応する画像形式をチェック
            if file.lower().endswith(("jpg", "jpeg", "png", "cr2", "cr3")):
                image_path = os.path.join(folder_selected, file)
                if os.path.isfile(image_path):
                    # 破棄リストと保持リストに含まれていない場合のみリストに追加
                    if image_path not in deleted_images_set and image_path not in keep_images_set:
                        image_paths.append(image_path)

            # 読み込み進捗を更新
            selector.progress_var.set(f"読み込み中: {index + 1}/{total_files}")
            selector.progressbar['value'] = (index + 1) / total_files * 100
            selector.master.update_idletasks()

        # 撮影日が古い順にソート
        sorted_image_paths = sorted(image_paths, key=Images.get_image_date)

        # ソートされた画像パスをセレクタに追加
        selector.images.extend(sorted_image_paths)

        if not selector.images:
            print("選択したフォルダ内に画像が見つかりませんでした")
        else:
            print(f"合計画像数: {len(selector.images)}")
            # サムネイル生成を新しいスレッドで開始
            threading.Thread(target=selector.generate_thumbnails).start()

    @staticmethod
    def get_image_date(image_path):
        try:
            img = Image.open(image_path)  # 画像を開く
            exif_data = img._getexif()  # EXIFデータを取得
            if exif_data is not None:
                # EXIFデータを辞書に変換
                exif = {ExifTags.TAGS[k]: v for k, v in exif_data.items() if k in ExifTags.TAGS}
                date_str = exif.get('DateTimeOriginal', None)
                if date_str:
                    # 撮影日を取得
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            print(f"EXIFデータの取得に失敗しました {image_path}: {e}")
        return datetime.min  # データが取得できない場合、最小の日時を返す

    @staticmethod
    def show(selector):
        if selector.images:
            image_path = selector.images[selector.current_image_index]
            print(f"画像を表示中: {image_path}")

            # キャッシュの確認
            if image_path in Images.cache:
                print(f"キャッシュを使用: {image_path}")
                photo = Images.cache[image_path]
                selector.image_label.config(image=photo)
                selector.image_label.image = photo
                return

            try:
                if image_path.lower().endswith(("cr2", "cr3")):
                    # RAWファイルの場合
                    # 非同期でRAW画像を読み込む
                    threading.Thread(target=Images._load_raw_image, args=(selector, image_path)).start()
                else:
                    img = Image.open(image_path)
                    # 画像の向きを修正
                    img = selector.rotate_image(img)
                    img.thumbnail((840, 840))  # サムネイルサイズにリサイズ
                    photo = ImageTk.PhotoImage(img)
                    # キャッシュに追加
                    Images.cache[image_path] = photo
                    # 画像ラベルに表示
                    selector.image_label.config(image=photo)
                    selector.image_label.image = photo
            except Exception as e:
                # 画像の読み込みに失敗した場合のエラーメッセージ
                print(f"画像の読み込みに失敗しました {image_path}: {e}")
                selector.image_label.config(text=f"画像の読み込みに失敗しました: {image_path}")

    @staticmethod
    def _load_raw_image(selector, image_path):
        try:
            with rawpy.imread(image_path) as raw:
                # サムネイルの抽出
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    img = Image.open(io.BytesIO(thumb.data))
                elif thumb.format == rawpy.ThumbFormat.BITMAP:
                    img = Image.fromarray(thumb.data)
                else:
                    # サムネイルがない場合はフルサイズの画像を処理
                    rgb = raw.postprocess()
                    img = Image.fromarray(rgb)

                # 画像の向きを修正
                img = selector.rotate_image(img)
                img.thumbnail((840, 840))  # サムネイルサイズにリサイズ
                photo = ImageTk.PhotoImage(img)
                # キャッシュに追加
                Images.cache[image_path] = photo
                # 画像ラベルに表示
                selector.image_label.config(image=photo)
                selector.image_label.image = photo
        except Exception as e:
            print(f"RAW画像の読み込みに失敗しました {image_path}: {e}")
            selector.image_label.config(text=f"RAW画像の読み込みに失敗しました: {image_path}")
