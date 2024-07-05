import os  # OS操作ユーティリティ
import shutil  # ファイルおよびディレクトリ操作ユーティリティ
from tkinter import Label, Button, Frame, Toplevel, Listbox, StringVar, Canvas, Scrollbar, PhotoImage  # GUIコンポーネント
from tkinter import ttk, filedialog  # 追加のGUIコンポーネントとファイルダイアログ
import tkinter as tk
from PIL import Image, ImageTk
from script.ai.judge import AIJudge  # AI判定用モジュール
from script.image.images import Images  # 画像操作用モジュール
from script.image.thumbnails import Thumbnails  # サムネイル生成用モジュール
from script.image.rotation import Rotation  # 画像回転用モジュール
from script.image.file_manager import FileManager  # ファイル管理用モジュール

class Selector:
    def __init__(self, master):
        self.master = master
        self.master.title("画像選択")

        button_height = Button(master, text="サンプル").winfo_reqheight()
        window_height = 600 + button_height + 150
        self.master.geometry(f"600x{window_height}")

        self.image_label = Label(self.master)
        self.image_label.pack(fill="both", expand=True)

        self.status_frame = Frame(self.master)
        self.status_frame.pack(fill="x", side="top")

        self.status_label = Label(self.status_frame, text="")
        self.status_label.pack(side="left")

        self.button_frame = Frame(self.master)
        self.button_frame.pack(fill="x", side="bottom")

        self.back_button = Button(self.button_frame, text="戻る", command=self.back_image)
        self.back_button.pack(side="left")

        self.next_button = Button(self.button_frame, text="次へ", command=self.next_image)
        self.next_button.pack(side="right")

        self.keep_button = Button(self.button_frame, text="保持", command=self.keep_image)
        self.keep_button.pack(side="right")

        self.discard_button = Button(self.button_frame, text="破棄", command=self.discard_image)
        self.discard_button.pack(side="right")

        self.execute_button = Button(self.button_frame, text="実行", command=self.execute_changes)
        self.execute_button.pack(side="right")

        self.view_discarded_button = Button(self.button_frame, text="破棄した画像を確認", command=self.view_discarded_images)
        self.view_discarded_button.pack(side="right")

        self.view_keeped_button = Button(self.button_frame, text="保持した画像を確認", command=self.view_keeped_images)
        self.view_keeped_button.pack(side="right")

        self.ai_judge_button = Button(self.button_frame, text="AI判定", command=self.ai_judge)
        self.ai_judge_button.pack(side="right")

        self.progress_var = StringVar()
        self.progress_label = Label(self.master, textvariable=self.progress_var)
        self.progress_label.pack()

        self.progressbar = ttk.Progressbar(self.master, orient='horizontal', mode='determinate', length=400)
        self.progressbar.pack()

        self.finish_button = Button(self.master, text="厳選完了", command=self.finish_selection)
        self.finish_button.pack(side="bottom")
        self.finish_button.pack_forget()  # 初期状態で非表示

        # 各種データの初期化
        self.images = []
        self.thumbnails = []
        self.current_image_index = 0
        self.deleted_images_file = "deleted_images.json"
        self.keep_images_file = "keep_images.json"
        self.deleted_images = FileManager.load_deleted_images(self.deleted_images_file)
        self.keep_images = FileManager.load_keep_images(self.keep_images_file)
        self.discarded_images_tk = []  # 廃棄された画像のサムネイルを保持するリスト
        self.keeped_images_tk = []     # 保持された画像のサムネイルを保持するリスト

        self.thumbnail = Thumbnails()

        self.load_images()

    def load_images(self):
        # 画像を読み込み、プログレスバーを設定
        Images.load(self)
        self.progressbar["maximum"] = len(self.images)
        # self.update_progress()
        self.generate_thumbnails()

    def generate_thumbnails(self):
        # サムネイルを生成
        self.thumbnail.generate(self)

    def show_image(self):
        # 画像を表示
        if self.images:
            image_path = self.images[self.current_image_index]
            self.thumbnail.add_to_queue(image_path, priority=True)
            Images.show(self)
            self.update_status_label()

    def update_status_label(self):
        # ステータスラベルを更新
        if self.images:
            self.status_label.config(text=f"{self.current_image_index + 1} / {len(self.images)}")

    def update_progress(self):
        # プログレスバーを更新
        self.progressbar["value"] = len(self.thumbnails)
        self.progress_var.set(f"{len(self.thumbnails)}/{len(self.images)}")
        if len(self.thumbnails) == len(self.images):
            self.progressbar.pack_forget()
            self.progress_label.pack_forget()

    def rotate_image(self, img):
        # 画像を回転
        return Rotation.rotate_image(img)

    def back_image(self):
        # 前の画像を表示
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image()

    def next_image(self):
        # 次の画像を表示
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image()

    def keep_image(self):
        # 画像を保持リストに追加
        if self.images:
            keep_image_path = self.images[self.current_image_index]
            self.keep_images.append(keep_image_path)
            del self.images[self.current_image_index]
            if self.thumbnails:
                del self.thumbnails[self.current_image_index]
            if self.images:
                self.current_image_index = self.current_image_index % len(self.images)
                self.show_image()
            else:
                self.image_label.config(text="これ以上画像がありません")
                self.finish_button.pack(side="bottom")
            FileManager.save_keep_images(self.keep_images, self.keep_images_file)
            self.update_status_label()

    def discard_image(self):
        # 画像を破棄リストに追加
        if self.images:
            discarded_image_path = self.images[self.current_image_index]
            self.deleted_images.append(discarded_image_path)
            if discarded_image_path in self.keep_images:
                self.keep_images.remove(discarded_image_path)
                FileManager.save_keep_images(self.keep_images, self.keep_images_file)  # 削除後に保存
            del self.images[self.current_image_index]
            if self.thumbnails:
                del self.thumbnails[self.current_image_index]
            if self.images:
                self.current_image_index = self.current_image_index % len(self.images)
                self.show_image()
            else:
                self.image_label.config(text="これ以上画像がありません")
                self.finish_button.pack(side="bottom")
            FileManager.save_deleted_images(self.deleted_images, self.deleted_images_file)
            self.update_status_label()

    def execute_changes(self):
        # 破棄リストの画像を削除
        for image_path in self.deleted_images:
            try:
                os.remove(image_path)
                print(f"画像を削除しました: {image_path}")
            except Exception as e:
                print(f"画像の削除に失敗しました: {image_path}, エラー: {e}")
        self.deleted_images.clear()
        FileManager.save_deleted_images(self.deleted_images, self.deleted_images_file)
        print("変更を実行しました")

    def restore_image(self, image_list, image_tk_list, file_path, scrollable_frame, window):
        if image_list:
            restored_image = image_list.pop()
            FileManager.save_deleted_images(image_list, file_path)
            self.images.append(restored_image)
            self.generate_thumbnails()

            # ウィジェットの更新
            for widget in scrollable_frame.winfo_children():
                widget.destroy()

            # サムネイル画像を表示し直す
            thumbnails = [Thumbnails.get_thumbnail_path(img) for img in reversed(image_list)]
            image_tk_list.clear()  # ImageTkオブジェクトのリストを空にする

            for idx, image_path in enumerate(thumbnails):
                img = Image.open(image_path)
                img.thumbnail((150, 150))
                img_tk = ImageTk.PhotoImage(img)
                image_tk_list.append(img_tk)
                label = Label(scrollable_frame, image=img_tk)
                label.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
                label.bind("<Button-1>", lambda e, i=idx: self.on_image_click(e, i, 'discarded'))

            # ウィンドウの再描画を要求する
            window.update()


    def view_discarded_images(self):
        # 破棄された画像を確認するためのウィンドウを表示
        discarded_window = Toplevel(self.master)
        discarded_window.title("破棄された画像")

        canvas = Canvas(discarded_window)
        scrollbar = Scrollbar(discarded_window, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # サムネイル画像を表示
        thumbnails = [Thumbnails.get_thumbnail_path(img) for img in reversed(self.deleted_images)]
        self.discarded_images_tk = []

        for idx, image_path in enumerate(thumbnails):
            img = Image.open(image_path)
            img.thumbnail((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            self.discarded_images_tk.append(img_tk)
            label = Label(scrollable_frame, image=img_tk)
            label.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
            label.bind("<Button-1>", lambda e, i=idx: self.on_image_click(e, i, 'discarded'))

        def restore_image_wrapper():
            # 破棄された画像を復元
            self.restore_image(self.deleted_images, self.discarded_images_tk, self.deleted_images_file, scrollable_frame, discarded_window)

        restore_button = Button(discarded_window, text="破棄から復元", command=restore_image_wrapper)
        restore_button.pack()


    def view_keeped_images(self):
        # 保持された画像を確認するためのウィンドウを表示
        keeped_window = Toplevel(self.master)
        keeped_window.title("保持された画像")

        canvas = Canvas(keeped_window)
        scrollbar = Scrollbar(keeped_window, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # サムネイル画像を表示
        thumbnails = [Thumbnails.get_thumbnail_path(img) for img in reversed(self.keep_images)]
        self.keeped_images_tk = []

        for idx, image_path in enumerate(thumbnails):
            img = Image.open(image_path)
            img.thumbnail((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            self.keeped_images_tk.append(img_tk)
            label = Label(scrollable_frame, image=img_tk)
            label.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)
            label.bind("<Button-1>", lambda e, i=idx: self.on_image_click(e, i, 'keeped'))

        def restore_image():
            # 保持された画像を復元
            self.restore_image(self.keep_images, self.keeped_images_tk, self.keep_images_file, scrollable_frame, keeped_window)

        discard_button = Button(keeped_window, text="保持から復元", command=restore_image)
        discard_button.pack()

    def on_image_click(self, event, index, mode):
        # 画像がクリックされた時の処理
        if mode == 'discarded':
            selected_image = self.deleted_images[-(index + 1)]
        elif mode == 'keeped':
            selected_image = self.keep_images[-(index + 1)]
        else:
            selected_image = None

        if selected_image:
            # 画像を表示する新しいウィンドウを作成
            image_window = Toplevel(self.master)
            image_window.title("選択された画像")

            img = Image.open(selected_image)
            img = Rotation.rotate_image(img)  # 画像の向きを修正
            img.thumbnail((800, 800))  # 画像サイズを制限
            img_tk = ImageTk.PhotoImage(img)
            label = Label(image_window, image=img_tk)
            label.image = img_tk  # 参照を保持するために必要
            label.pack()

        else:
            print("Invalid mode or index out of range.")

    def ai_judge(self):
        # AIによる画像判定を実行
        AIJudge.judge(self)

    def finish_selection(self):
        self.execute_changes()
        # 画像選択の処理を完了
        self.keep_images.clear()
        FileManager.save_keep_images(self.keep_images, self.keep_images_file)
        if os.path.exists(Thumbnails.cache_dir):
            shutil.rmtree(Thumbnails.cache_dir)
            print(f"キャッシュディレクトリ {Thumbnails.cache_dir} をクリアしました")
        self.images.clear()
        self.current_image_index = 0
        self.finish_button.pack_forget()
        self.load_images()
