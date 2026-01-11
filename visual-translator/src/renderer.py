from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math

class TextRenderer:
    def __init__(self, font_path="C:/Windows/Fonts/msgothic.ttc"): # 윈도우 시스템 폰트 절대 경로 사용
        self.font_path = font_path

    def render(self, image: Image.Image, text: str, box: np.ndarray, angle: float = 0, text_color: tuple = (0, 0, 0)):
        """
        이미지에 번역된 텍스트를 그립니다.
        Args:
            image: PIL Image 객체 (수정될 이미지)
            text: 그릴 텍스트
            box: 4개의 점 좌표
            angle: 텍스트 회전 각도
            text_color: 텍스트 색상 (R, G, B) - 기본값 검정
        """
        # Box 좌표에서 너비와 높이 계산
        width = int(np.linalg.norm(box[1] - box[0]))
        height = int(np.linalg.norm(box[3] - box[0]))
        
        if width == 0 or height == 0:
            return

        # 텍스트를 그릴 투명 레이어 생성
        print(f"[Renderer] Rendering text: '{text}' into box {width}x{height} with color {text_color}")
        text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # 폰트 크기 자동 조절
        font_size = height # 초기값
        font = self._load_font(font_size)
        
        # 텍스트가 박스 안에 들어갈 때까지 폰트 줄이기
        while font_size > 5:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            if text_w <= width and text_h <= height:
                break
            font_size -= 1
            font = self._load_font(font_size)
            
        # 텍스트 중앙 정렬 좌표 계산
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (width - text_w) // 2
        y = (height - text_h) // 2
        
        # 외곽선 색상 자동 계산 (보색/반전)
        outline_color = (255 - text_color[0], 255 - text_color[1], 255 - text_color[2])
        
        # 텍스트 그리기
        stroke_width = max(1, font_size // 15)
        
        # 가독성을 위해 외곽선(Stroke)을 그리고, 그 위에 글자(Fill)를 그림
        draw.text((x, y), text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=outline_color)

        # 회전 (Pillow는 시계 반대 방향이 양수)
        # PaddleOCR의 각도 처리는 상황에 따라 다를 수 있으므로 테스트 필요
        # 여기서는 입력받은 angle만큼 회전
        rotated_layer = text_layer.rotate(angle, expand=True, resample=Image.BICUBIC)
        
        # 원본 이미지에 붙여넣기 위한 좌표 계산
        # 회전 중심은 box의 중심
        center_x = int(np.mean(box[:, 0]))
        center_y = int(np.mean(box[:, 1]))
        
        # 회전된 레이어의 크기
        rw, rh = rotated_layer.size
        paste_x = center_x - rw // 2
        paste_y = center_y - rh // 2
        
        image.paste(rotated_layer, (paste_x, paste_y), rotated_layer)

        image.paste(rotated_layer, (paste_x, paste_y), rotated_layer)

    def _load_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception as e:
            print(f"[Renderer] ERROR: Could not load {self.font_path} at size {size}. Error: {e}")
            return ImageFont.load_default()
