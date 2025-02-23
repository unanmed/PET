import os

input_folder = " D:\PET\PET_AC_sCT"  # DICOM 文件夹路径
output_folder = "converted_images"

os.makedirs(output_folder, exist_ok=True)  # 创建输出文件夹

for file in os.listdir(input_folder):
    if file.endswith(".dcm"):
        dicom_path = os.path.join(input_folder, file)
        output_path = os.path.join(output_folder, file.replace(".dcm", ".png"))

        ds = pydicom.dcmread(dicom_path)
        image_array = ds.pixel_array.astype(np.float32)
        image_array = (image_array - image_array.min()) / (image_array.max() - image_array.min()) * 255
        image_array = image_array.astype(np.uint8)

        image = Image.fromarray(image_array)
        image.save(output_path)
        print(f"已转换：{dicom_path} → {output_path}")

print("批量转换完成！")
