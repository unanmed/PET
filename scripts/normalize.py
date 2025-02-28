import os
import numpy as np
import scipy.io as io

# 设置输入和输出文件夹
input_folder = "D:/PET/output/mat/CT_test_resize"  # 替换为你的.mat文件夹路径
output_folder = "D:/PET/output/mat/CT_test_resize"  # 归一化后的.mat存放路径

os.makedirs(output_folder, exist_ok=True)  # 确保输出文件夹存在

def normalize_image(img):
    """ 归一化 img 到 [0,1] """
    img = img.astype(np.float32)  # 转换为 float32 避免数据丢失
    img_min = img.min()
    img_max = img.max()
    if img_max > img_min:  # 避免除零错误
        img = (img - img_min) / (img_max - img_min)
    else:
        img = np.zeros_like(img)  # 如果最大值和最小值相等，则输出全零
    return img

# 遍历文件夹内所有 .mat 文件
for filename in os.listdir(input_folder):
    if filename.endswith(".mat"):
        file_path = os.path.join(input_folder, filename)
        data = io.loadmat(file_path)  # 读取 .mat 文件

        if "img" in data:  # 确保字段存在
            img = data["img"]
            normalized_img = normalize_image(img)  # 归一化处理

            # 保存归一化后的数据
            data["img"] = normalized_img  # 替换原 img 数据
            output_path = os.path.join(output_folder, filename)
            io.savemat(output_path, data)
            print(f"Processed: {filename}")

print("All files processed!")