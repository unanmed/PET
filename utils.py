import numpy as np
import cv2

def save_img(img, img_path):
    img = np.clip(img*255,0,255)
    cv2.imwrite(img_path, img)