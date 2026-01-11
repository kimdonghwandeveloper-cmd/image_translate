import cv2
import numpy as np

def get_dominant_color(image_cv2: np.ndarray) -> tuple:
    """
    이미지의 가장자리를 샘플링하여 배경색을 추정합니다.
    Returns: (r, g, b) tuple
    """
    if image_cv2 is None or image_cv2.size == 0:
        return (0, 0, 0)
        
    h, w = image_cv2.shape[:2]
    
    # 테두리 두께
    border = 5
    
    if h <= border * 2 or w <= border * 2:
        # 이미지가 너무 작으면 전체 평균
        avg_bgr = np.mean(image_cv2, axis=(0, 1))
    else:
        # 상하좌우 테두리 픽셀만 추출
        top = image_cv2[:border, :]
        bottom = image_cv2[h-border:, :]
        left = image_cv2[:, :border]
        right = image_cv2[:, w-border:]
        
        # 픽셀들을 1차원 배열로 펼침
        top_flat = top.reshape(-1, 3)
        bottom_flat = bottom.reshape(-1, 3)
        left_flat = left.reshape(-1, 3)
        right_flat = right.reshape(-1, 3)
        
        border_pixels = np.concatenate([top_flat, bottom_flat, left_flat, right_flat])
        avg_bgr = np.mean(border_pixels, axis=0)
        
    # BGR -> RGB 변환
    avg_rgb = avg_bgr.astype(int)[::-1]
    return tuple(avg_rgb)

def get_text_color(bg_color_rgb: tuple) -> tuple:
    """
    배경색(RGB)의 밝기(Luminance)를 계산하여,
    가독성이 좋은 텍스트 색상(검정/흰색)을 반환합니다.
    """
    r, g, b = bg_color_rgb
    
    # ITU-R BT.601 표준 루미넌스 공식
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    
    # 밝기가 128 이상이면 밝은 배경 -> 검은 글씨
    if luminance > 128:
        return (0, 0, 0)
    else:
        return (255, 255, 255)
