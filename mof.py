import bpy
import os
import subprocess
from bpy import context

bl_info = {
    "name": "Brender Mof Bridge",
    "blender": (2, 80, 0),
    "category": "UV",
}


class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    folder_path: bpy.props.StringProperty(
        name="folder_path",
        description="Ministy of Flatの存在するフォルダパスを入力してください",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "folder_path")


class AutoUV(bpy.types.Operator):
    """Ministy of Flatを使って自動でUV展開を行います"""  # ホバー時に表示される説明文

    bl_idname = "object.autouv"  # メニューのID、小文字でなければならない
    bl_label = "自動UV展開"  # UIにて表示される名前
    bl_options = {"REGISTER"}

    def execute(self, context):  # 実行時の処理
        # STEP3-1 選択オブジェクトのエクスポート
        obj = context.active_object
        fn = os.path.join(bpy.app.tempdir, obj.name + ".obj")  # ファイル名
        # 選択しているオブジェクトをエクスポート
        bpy.ops.wm.obj_export(
            filepath=fn,
            export_selected_objects=True,
            export_materials=False,
        )
        # STEP3-2 1のobjファイルを引数に与えMinistry of Flatをコマンドラインから実行する
        fn2 = os.path.join(bpy.app.tempdir, obj.name + "_unpacked.obj")  # 展開後のファイル名
        preferences = context.preferences.addons[__name__].preferences
        folder_path = (
            preferences.folder_path
        )  # Ministry of Flatがあるディレクトリを取得
        path = os.path.join(folder_path, "UnWrapConsole3.exe")
        subprocess.run([path, fn, fn2])  # 実行
        # STEP3-3 2で出力されたobjファイルをblenderにインポートする
        bpy.ops.wm.obj_import(filepath=fn2)
        # STEP3-4 1と2の一時ファイルを掃除する（消す）
        os.remove(fn)
        os.remove(fn2)

        return {"FINISHED"}  # 終了


def menu_func(self, context):
    self.layout.operator(AutoUV.bl_idname)  # メニューに追加


def register():
    bpy.utils.register_class(MyAddonPreferences)
    bpy.utils.register_class(AutoUV)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # オブジェクトメニューに項目追加


def unregister():
    bpy.utils.unregister_class(MyAddonPreferences)
    bpy.utils.unregister_class(AutoUV)
    bpy.types.VIEW3D_MT_object.remove(menu_func)  # オブジェクトメニューから削除


if __name__ == "__main__":
    register()
