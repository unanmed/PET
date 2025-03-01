import os
import shutil

# 源数据集文件夹和目标文件夹
source_folder = "../mat/NAC_resize_normalized"  # 修改为你的数据集文件夹
destination_folder = "../mat/NAC_train"  # 修改为目标文件夹

# 需要匹配的多个前缀
prefixes = ["S80"]  # 修改为你的前缀列表

# 确保目标文件夹存在
os.makedirs(destination_folder, exist_ok=True)

# 遍历源文件夹中的所有文件
for filename in os.listdir(source_folder):
    if any(filename.startswith(prefix) for prefix in prefixes):
        source_path = os.path.join(source_folder, filename)
        destination_path = os.path.join(destination_folder, filename)
        
        # 移动文件
        shutil.copy2(source_path, destination_path)
        print(f"Copied: {filename} -> {destination_folder}")

print("✅ 所有符合条件的文件已移动完成！")
