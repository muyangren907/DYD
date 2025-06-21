import os
import re
import shutil


def move_files(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                move_files(s, d)
            else:
                shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)


def batch_rename(root_dir):
    for name in os.listdir(root_dir):
        old_path = os.path.join(root_dir, name)
        if os.path.isdir(old_path):
            match = re.match(r'UID(\d+)_(.*)_发布作品', name)
            if match:
                new_name = match.group(2)
                new_path = os.path.join(root_dir, new_name)
                if os.path.exists(new_path):
                    print(f"合并文件夹内容: {old_path} -> {new_path}")
                    move_files(old_path, new_path)
                    shutil.rmtree(old_path)
                else:
                    print(f"重命名文件夹: {old_path} -> {new_path}")
                    os.rename(old_path, new_path)


if __name__ == '__main__':
    root_dir = 'D:\Program Files\TikTokDownloader_V5.6_Windows_X64\_internal'
    batch_rename(root_dir)