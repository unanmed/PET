import os
import numpy as np
import scipy.io as io

def load_and_convert_mat(mat_path):
    # 加载 .mat 文件
    mat_data = io.loadmat(mat_path)
    
    # 获取 img 字段
    img_data = mat_data['img']
    
    # 确保 img 是 uint16 类型，如果是其他类型，可以先转换
    assert img_data.dtype == np.single, f"Expected uint16, but got {img_data.dtype}"

    # 将 uint16 数据转换为 float32，范围归一化到 [0, 1]
    img_normalized = img_data.astype(np.float32) / 65535.0
    
    return img_normalized

def process_mat_files_in_folder(folder_path, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历文件夹中的所有 .mat 文件
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mat'):
            mat_path = os.path.join(folder_path, file_name)
            
            # 执行转换
            converted_img = load_and_convert_mat(mat_path)
            
            # 保存转换后的数据（例如，保存为新的 .mat 文件）
            output_path = os.path.join(output_folder, file_name)
            io.savemat(output_path, {'img': converted_img})
            print(f"Processed {file_name} and saved to {output_path}")

# 设置输入文件夹和输出文件夹
input_folder = 'D:/PET/output/mat/CT_test_resize'  # 替换为你的输入文件夹路径
output_folder = 'D:/PET/output/mat/CT_test_resize'   # 替换为你想保存转换后的文件夹路径

# 批量处理文件夹中的所有 .mat 文件
process_mat_files_in_folder(input_folder, output_folder)