import os
import shutil
import re

# 定义输入和输出目录
png_input_dir = "png/brain"
mat_input_dir = "mat/brain"
png_output_dir = "output"
mat_output_dir = "output_mat"

def flat_folder():
    # 确保输出目录存在
    for folder in ["CT", "PET_NAC", "CTAC"]:
        os.makedirs(os.path.join(png_output_dir, folder), exist_ok=True)
        os.makedirs(os.path.join(mat_output_dir, folder), exist_ok=True)

    # 处理所有患者文件夹
    for patient in os.listdir(png_input_dir):
        patient_png_path = os.path.join(png_input_dir, patient)
        patient_mat_path = os.path.join(mat_input_dir, patient)
        
        if not os.path.isdir(patient_png_path):
            continue  # 跳过非文件夹项

        # 定义 PNG 和 MAT 子文件夹路径
        ct_png_path = os.path.join(patient_png_path, "CT")
        pet_nac_png_path = os.path.join(patient_png_path, "PET")
        pet_ctac_png_path = os.path.join(patient_png_path, "PET_1")

        ct_mat_path = os.path.join(patient_mat_path, "CT")
        pet_nac_mat_path = os.path.join(patient_mat_path, "PET")
        pet_ctac_mat_path = os.path.join(patient_mat_path, "PET_1")

        # 确保 PNG 目录存在
        if not (os.path.exists(ct_png_path) and os.path.exists(pet_nac_png_path) and os.path.exists(pet_ctac_png_path)):
            print(f"⚠️ PNG 跳过 {patient}，因为缺少 CT/PET/PET_1 目录")
            continue

        # 确保 MAT 目录存在
        if not (os.path.exists(ct_mat_path) and os.path.exists(pet_nac_mat_path) and os.path.exists(pet_ctac_mat_path)):
            print(f"⚠️ MAT 跳过 {patient}，因为缺少 CT/PET/PET_1 目录")
            continue

        # 获取文件列表并按数值顺序排序
        def sorted_file_list(directory, ext):
            return sorted(
                (f for f in os.listdir(directory) if f.endswith(ext)),
                key=lambda x: int(re.findall(r"\d+", x)[0])  # 提取数字部分进行排序
            )

        # 获取 PNG 和 MAT 文件列表
        ct_png_files = sorted_file_list(ct_png_path, ".png")
        pet_nac_png_files = sorted_file_list(pet_nac_png_path, ".png")
        pet_ctac_png_files = sorted_file_list(pet_ctac_png_path, ".png")

        ct_mat_files = sorted_file_list(ct_mat_path, ".mat")
        pet_nac_mat_files = sorted_file_list(pet_nac_mat_path, ".mat")
        pet_ctac_mat_files = sorted_file_list(pet_ctac_mat_path, ".mat")

        # 去除 CT 目录中的最后一张 PNG 和 MAT
        if ct_png_files:
            last_ct_png = ct_png_files.pop()
            print(f"🗑️ 跳过 {os.path.join(ct_png_path, last_ct_png)}（不复制）")

        if ct_mat_files:
            last_ct_mat = ct_mat_files.pop()
            print(f"🗑️ 跳过 {os.path.join(ct_mat_path, last_ct_mat)}（不复制）")

        # 确保三类文件数量一致（PNG 和 MAT）
        min_png_count = min(len(ct_png_files), len(pet_nac_png_files), len(pet_ctac_png_files))
        min_mat_count = min(len(ct_mat_files), len(pet_nac_mat_files), len(pet_ctac_mat_files))
        min_count = min(min_png_count, min_mat_count)

        # 遍历并复制 PNG 和 MAT
        for i in range(min_count):
            shutil.copy2(os.path.join(ct_png_path, ct_png_files[i]), os.path.join(png_output_dir, "CT", f"{patient}_{ct_png_files[i]}"))
            shutil.copy2(os.path.join(pet_nac_png_path, pet_nac_png_files[i]), os.path.join(png_output_dir, "PET_NAC", f"{patient}_{pet_nac_png_files[i]}"))
            shutil.copy2(os.path.join(pet_ctac_png_path, pet_ctac_png_files[i]), os.path.join(png_output_dir, "CTAC", f"{patient}_{pet_ctac_png_files[i]}"))

            shutil.copy2(os.path.join(ct_mat_path, ct_mat_files[i]), os.path.join(mat_output_dir, "CT", f"{patient}_{ct_mat_files[i]}"))
            shutil.copy2(os.path.join(pet_nac_mat_path, pet_nac_mat_files[i]), os.path.join(mat_output_dir, "PET_NAC", f"{patient}_{pet_nac_mat_files[i]}"))
            shutil.copy2(os.path.join(pet_ctac_mat_path, pet_ctac_mat_files[i]), os.path.join(mat_output_dir, "CTAC", f"{patient}_{pet_ctac_mat_files[i]}"))

        print(f"✅ 处理完成: {patient}（{min_count} 张 PNG & MAT 匹配）")

    print("🎉 所有患者的 PNG & MAT 处理完成！")

if __name__ == "__main__":
    flat_folder()