import os
import numpy as np
from PIL import Image
import scipy.io as io

def mat_to_png(mat_path, output_path):
    # 加载 .mat 文件
    mat_data = io.loadmat(mat_path)
    
    # 获取 data 字段
    data = mat_data['img']
    
    # 确保 data 是浮动在 0 到 1 之间
    assert data.min() >= 0 and data.max() <= 1, f"Data in {mat_path} is not in the [0, 1] range."
    
    # 将 [0, 1] 范围的数据转换为 [0, 255] 范围的 uint8 类型
    data = (data * 255).astype(np.uint8)
    
    # 如果是灰度图，直接保存；如果是 RGB 图，确保它有 3 个通道
    if len(data.shape) == 2:  # 灰度图
        img = Image.fromarray(data)
    elif len(data.shape) == 3 and data.shape[2] == 3:  # RGB 图
        img = Image.fromarray(data)
    else:
        raise ValueError(f"Unexpected data shape {data.shape}. Only 2D or 3D RGB images are supported.")
    
    # 保存为 PNG
    img.save(output_path)
    print(f"Saved {mat_path} as {output_path}")

def process_mat_files_in_folder(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历文件夹中的所有 .mat 文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.mat'):
            mat_path = os.path.join(input_folder, file_name)
            
            # 生成输出路径
            output_path = os.path.join(output_folder, file_name.replace('.mat', '.png'))
            
            # 执行转换
            mat_to_png(mat_path, output_path)

# 设置输入文件夹和输出文件夹
input_folder = 'D:/PET/output/mat/AC_gen_output/test/0049.pth/pred_mat'  # 替换为你的 .mat 文件夹路径
output_folder = 'D:/PET/output/mat/AC_gen_output/test/0049.pth/pred'   # 替换为你想保存 PNG 文件的文件夹路径

# 批量处理文件夹中的所有 .mat 文件并保存为 PNG
process_mat_files_in_folder(input_folder, output_folder)
