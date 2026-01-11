import sys
import os
import numpy as np
from paddleocr import PaddleOCR
from dotenv import load_dotenv

load_dotenv()

class TextDetector:
    def __init__(self):
        # OCR 언어 설정 (기본값: korean)
        lang = os.getenv("OCR_LANG", "korean")
        
        # PaddleOCR issue: It parses sys.argv and conflicts with main argparse
        # Workaround: Clear sys.argv temporarily
        original_argv = sys.argv
        sys.argv = ['']
        try:
            # use_angle_cls=True: 텍스트 방향(각도) 분류 활성화
            self.ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        finally:
            sys.argv = original_argv

    def detect(self, image_path):
        """
        이미지에서 텍스트를 감지합니다.
        Returns:
            list[dict]: 감지된 텍스트 정보 리스트
            [
                {
                    'box': np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]]),
                    'text': 'Detected Text',
                    'confidence': 0.98
                },
                ...
            ]
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # PaddleOCR 실행
        # cls=True: 방향 분류 실행 (에러 발생으로 제거)
        result = self.ocr.ocr(image_path)
        print(f"DEBUG: OCR result type: {type(result)}")
        print(f"DEBUG: OCR result: {result}")
        if result:
             print(f"DEBUG: result[0] type: {type(result[0])}")
        
        parsed_results = []
        
        if not result:
            return parsed_results

        # PaddleX result format (dict-like object)
        # result[0] is typically a dict with 'rec_texts', 'rec_polys', 'rec_scores'
        first_res = result[0]
        
        # PaddleX result format (dict-like object)
        first_res = result[0]
        
        # Check for PaddleX dict format
        if hasattr(first_res, 'keys') and 'rec_texts' in first_res:
             rec_texts = first_res['rec_texts']
             rec_polys = first_res['rec_polys']
             rec_scores = first_res['rec_scores']
             
             for poly, text, score in zip(rec_polys, rec_texts, rec_scores):
                 # Filter low confidence text (Garbage filtering)
                 if score < 0.85: # Threshold set high to avoid handwriting noise
                     continue
                     
                 parsed_results.append({
                     'box': np.array(poly).astype(np.int32),
                     'text': text,
                     'confidence': score
                 })
        # Legacy list-of-lists format
        elif isinstance(first_res, list):
            for line in first_res:
                box_points = line[0] 
                text_info = line[1]
                score = text_info[1]
                
                if score < 0.85:
                    continue

                parsed_results.append({
                    'box': np.array(box_points).astype(np.int32),
                    'text': text_info[0],
                    'confidence': score
                })
        else:
            print(f"Warning: Unknown PaddleOCR result format: {type(first_res)}")
            
        return parsed_results
