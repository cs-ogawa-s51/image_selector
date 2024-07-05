from PIL import ExifTags

class Rotation:
    @staticmethod
    def rotate_image(img):
        try:
            # 画像のEXIFデータからOrientationタグを取得する
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            # 画像のEXIFデータを辞書形式で取得する
            exif = dict(img._getexif().items())

            # Orientationタグに基づいて画像を回転させる
            if exif[orientation] == 3:
                # 180度回転
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                # 270度回転（時計回りに90度回転）
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                # 90度回転（反時計回りに90度回転）
                img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # EXIFデータがない場合やOrientationタグがない場合は何もしない
            pass

        return img
