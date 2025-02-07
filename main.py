import os
from datetime import datetime
import pandas as pd
from data_processing.character_parser import parse_character_info
from data_processing.story_parser import parse_story_overview
from data_processing.scene_parser import parse_scene_design
from data_processing.shot_parser import parse_shot_script
from utilities.excel_writer import set_wrap_text
from utilities.dependency_manager import install_dependencies
from utilities.virtual_env import create_and_activate_venv
from utilities.branding import print_banner

create_and_activate_venv()
install_dependencies()


def main_process():
    while True:
        base_dir = os.getcwd()
        data_dir = os.path.join(base_dir, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print("提示：data 文件夹不存在，已自动创建，请将 TXT 文件放置在 data 文件夹中。")
        
        subfolders = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        if not subfolders:
            print("提示：data 文件夹内没有子文件夹，请在 data 文件夹中创建子文件夹后输入 'r' 刷新。")
        else:
            print("请选择要处理的文件夹：")
            for idx, folder in enumerate(subfolders, 1):
                print(f"{idx}. {folder}")

        user_input = input("请输入数字选择，或输入 'r' 刷新列表：").strip().lower()
        if user_input == 'r':
            continue

        try:
            choice = int(user_input)
            selected_folder = subfolders[choice - 1]
            break
        except (ValueError, IndexError):
            print("输入错误，请重新选择。")

    folder_path = os.path.join(data_dir, selected_folder)
    print(f"已选择文件夹：{selected_folder}")

    file_map = {fname.split('_')[0]: os.path.join(folder_path, fname) for fname in os.listdir(folder_path) if fname.endswith(".txt")}
    try:
        df_overview = parse_story_overview(file_map["1"])
        df_character = parse_character_info(file_map["2"])
        df_scene = parse_scene_design(file_map["3"])
        df_shot = parse_shot_script(file_map["4"])
    except Exception as e:
        print(f"处理文件时出错：{e}")
        return

    current_time_str = datetime.now().strftime("%y%m%d_%H%M")
    excel_filename = f"{selected_folder}_{current_time_str}.xlsx"
    excel_path = os.path.join(folder_path, excel_filename)

    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df_overview.to_excel(writer, sheet_name="故事概要", index=False)
            df_character.to_excel(writer, sheet_name="角色设定", index=False)
            df_scene.to_excel(writer, sheet_name="场景剧情设计", index=False)
            df_shot.to_excel(writer, sheet_name="分镜脚本", index=False)
            set_wrap_text(writer)
        print(f"转换成功！生成的 Excel 文件位于：{excel_path}")
        print(f"--------------------------------------------------")
    except Exception as e:
        print(f"写入 Excel 文件时出错：{e}")

if __name__ == "__main__":
    print_banner()
    while True:
        main_process()
