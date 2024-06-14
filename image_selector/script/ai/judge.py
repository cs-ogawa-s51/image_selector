# script/ai/judge.py

class AIJudge:
    @staticmethod
    def judge(selector):
        # TODO: AI判定の実装
        pass

    @staticmethod
    def _judge(image_select):
        pass
        # TODO: 開発途中
        # if not image_select.images:
        #     print("画像がありません")
        #     return

        # total_images = len(image_select.images)
        # for index, image_path in enumerate(image_select.images):
        #     try:
        #         img = Image.open(image_path)
        #         img = img.resize((224, 224))  # モデルに合わせてリサイズ
        #         # TODO: 以下のコメントアウトしている処理が正しい処理なのか確認
        #         result = ai_judge(image_select.model, img)
        #         if result == 0:  # 例えば、AIが「削除」と判断した場合
        #             image_select.deleted_images.append(image_path)
        #             image_select.save_deleted_images()
        #             print(f"画像を破棄: {image_path}")
        #         else:
        #             image_select.keep_images.append(image_path)
        #             image_select.save_keep_images()
        #             print(f"画像を保持: {image_path}")
        #     except Exception as e:
        #         print(f"AI判定に失敗しました {image_path}: {e}")
        #     image_select.progress_var.set(f"AI判定中: {index + 1}/{total_images}")
        #     image_select.progressbar['value'] = (index + 1) / total_images * 100
        #     image_select.master.update_idletasks()

        # # 最後に削除する画像を削除リストから画像リストから削除
        # for discarded_image in image_select.deleted_images:
        #     if discarded_image in image_select.images:
        #         image_select.images.remove(discarded_image)
        #         image_select.generate_thumbnails()

        # print("AI判定が完了しました")
