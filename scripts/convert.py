import os
import pydicom
from scipy.io import savemat
from PIL import Image
import numpy as np

# 需要保留的图像相关字段
IMAGE_METADATA_KEYS = [
    'Rows', 'Columns', 'BitsAllocated', 'PhotometricInterpretation',
    'PixelSpacing', 'ImagePositionPatient', 'ImageOrientationPatient',
    'RescaleIntercept', 'RescaleSlope', 'WindowCenter', 'WindowWidth',
    'InstanceNumber', 'SliceThickness'
]

def truncate_keys(d, max_length=31):
    """截断字典中的键名到指定长度"""
    return {k[:max_length]: v for k, v in d.items()}


def dicom_to_png(dicom_array, output_path):
    """保存 DICOM 图像为 PNG"""
    # 归一化到 0-255
    scaled_img = (dicom_array - np.min(dicom_array)) / (np.max(dicom_array) - np.min(dicom_array))
    scaled_img = (scaled_img * 255).astype(np.uint8)
    
    # 保存为 PNG
    img = Image.fromarray(scaled_img)
    img.save(output_path)

def process_dicom_file(dicom_path, png_output_dir, mat_output_dir):
    """处理单个 DICOM 文件：转换为 PNG 和 MAT"""
    try:
        # 读取 DICOM 文件
        dicom_file = pydicom.dcmread(dicom_path)
        
        # 确认 PixelData 存在
        if 'PixelData' not in dicom_file:
            print(f"⚠️ No PixelData in {dicom_path}. Skipping.")
            return
        
        dicom_array = dicom_file.pixel_array
        
        # 检查是否为空
        if dicom_array is None:
            print(f"⚠️ Empty pixel_array in {dicom_path}. Skipping.")
            return

        # 获取基本信息
        dicom_filename = os.path.basename(dicom_path)
        base_name = os.path.splitext(dicom_filename)[0]

        # 生成输出路径
        png_path = os.path.join(png_output_dir, base_name + '.png')
        mat_path = os.path.join(mat_output_dir, base_name + '.mat')

        # 确保输出目录存在
        os.makedirs(png_output_dir, exist_ok=True)
        os.makedirs(mat_output_dir, exist_ok=True)

        # 保存为 PNG
        dicom_to_png(dicom_array, png_path)
        print(f"✅ PNG saved: {png_path}")

        # 提取元数据
        metadata = {
            key: getattr(dicom_file, key, None)
            for key in IMAGE_METADATA_KEYS
            if hasattr(dicom_file, key)
        }
        
        # 保存为 MAT
        savemat(mat_path, {'img': dicom_array, 'metadata': metadata})
        print(f"✅ MAT saved: {mat_path}")

    except Exception as e:
        print(f"❌ Failed to process {dicom_path}: {e}")

def traverse_and_convert(input_dir, png_output_dir, mat_output_dir):
    """递归遍历目录，转换所有 DICOM 文件"""
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().startswith('i'):  # 根据文件名 (I10, I20) 过滤
                dicom_path = os.path.join(root, file)

                # 生成与输入目录对应的输出路径
                rel_path = os.path.relpath(root, input_dir)
                png_dir = os.path.join(png_output_dir, rel_path)
                mat_dir = os.path.join(mat_output_dir, rel_path)

                process_dicom_file(dicom_path, png_dir, mat_dir)

if __name__ == "__main__":
    # 输入 DICOM 文件夹路径
    input_directory = "F:\download\AC data"  # 替换为实际路径
    # 输出路径
    png_output_directory = "F:\download\AC_Output\png"
    mat_output_directory = "F:\download\AC_Output\mat"

    traverse_and_convert(input_directory, png_output_directory, mat_output_directory)
    print("🎉 All DICOM files converted to PNG and MAT!")
