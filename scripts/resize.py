import os
import cv2
import numpy as np
import scipy.io as sio
from tqdm import tqdm

# 📂 输入 MAT 文件夹 和 预处理后的输出文件夹
input_folder = "D:/PET/output/mat/CT_test"  # 原始 .mat 文件夹
output_folder = "D:/PET/output/mat/CT_test_resize"  # 预处理后 256x256 的 .mat

# 创建输出文件夹
os.makedirs(output_folder, exist_ok=True)

# 处理所有 .mat 文件
for filename in tqdm(os.listdir(input_folder), desc="Processing CT MAT Files"):
    if filename.endswith(".mat"):
        mat_path = os.path.join(input_folder, filename)
        mat_data = sio.loadmat(mat_path)  # 加载 .mat 文件
        
        if 'img' not in mat_data:
            print(f"⚠ 警告: {filename} 没有 'img' 字段，跳过")
            continue
        
        img = mat_data['img']  # 提取图像数据
        
        # ✅ 统一大小 512x512 -> 256x256
        img_resized = cv2.resize(img, (128, 128), interpolation=cv2.INTER_AREA)
        
        # ✅ 归一化并转换为 float32
        img_resized = img_resized.astype(np.float32)

        # ✅ 保存为新的 .mat 文件
        output_path = os.path.join(output_folder, filename)
        sio.savemat(output_path, {'img': img_resized})

print(f"✅ 预处理完成，所有 CT MAT 数据已保存至 {output_folder}")