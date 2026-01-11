import cv2
import numpy as np
from PIL import Image
from src.detector import TextDetector
from src.inpainter import Inpainter, OpenCVInpainter, StabilityAIInpainter
from src.translator import Translator
from src.renderer import TextRenderer
from src.color_utils import get_dominant_color, get_text_color


class VisualTranslatorPipeline:
    def __init__(self, detector, inpainter, translator, renderer):
        self.detector = detector
        self.inpainter = inpainter
        self.translator = translator
        self.renderer = renderer

    def run(self, input_path, output_path):
        """
        v5 Pipeline (Hybrid):
        1. Detect Text
        2. Inpaint (Erase) ALL text regions using Stability AI (High Quality Background)
        3. Translate & Render (Type) new text using Pillow (High Legibility)
        """
        print(f"[Pipeline] Start processing (v5 Hybrid Mode): {input_path}")
        
        # 1. Text Search
        detection_results = self.detector.detect(input_path)
        print(f"[Pipeline] Detected {len(detection_results)} text regions.")
        
        original_cv2 = cv2.imread(input_path)
        if original_cv2 is None:
            raise ValueError(f"Could not load image: {input_path}")
            
        # Inpainting을 위해 작업할 복사본
        inpainted_cv2 = original_cv2.copy()
        
        # Inpainting Mask 생성 (전체 텍스트 영역)
        full_mask = np.zeros(original_cv2.shape[:2], dtype=np.uint8)
        
        # [Phase 4] Debugging Setup
        import os
        debug_dir = "debug_crops"
        os.makedirs(debug_dir, exist_ok=True)
        debug_vis_image = original_cv2.copy()
        
        detected_texts = []
        for idx, item in enumerate(detection_results):
            box = item['box']
            detected_texts.append(item)
            
            # [Phase 4] Visualize Bounding Box
            cv2.polylines(debug_vis_image, [box], True, (0, 255, 0), 2)
            cv2.putText(debug_vis_image, str(idx+1), (box[0][0], box[0][1]-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # [Phase 4] Save Crop Image
            # Get bounding rect for cropping
            x_min = int(np.min(box[:, 0]))
            x_max = int(np.max(box[:, 0]))
            y_min = int(np.min(box[:, 1]))
            y_max = int(np.max(box[:, 1]))
            
            # Padding slightly
            pad = 5
            h, w, _ = original_cv2.shape
            x_min = max(0, x_min - pad)
            y_min = max(0, y_min - pad)
            x_max = min(w, x_max + pad)
            y_max = min(h, y_max + pad)
            
            cropped_cv2 = original_cv2[y_min:y_max, x_min:x_max]
            if cropped_cv2.size > 0:
                crop_path = os.path.join(debug_dir, f"crop_{idx+1}.png")
                cv2.imwrite(crop_path, cropped_cv2)

            # [Phase 4] Smart Color Extraction
            # 원본 배색에 어울리는 글자색 결정
            bg_color = get_dominant_color(cropped_cv2)
            item['text_color'] = get_text_color(bg_color)

            # 마스크에 영역 추가 (cv2.fillPoly expects a list of points)
            cv2.fillPoly(full_mask, [box], 255)

        # [Phase 4] Save Visualization Image
        cv2.imwrite("debug_detection.png", debug_vis_image)
        print(f"[Phase 4] Debug outputs saved: 'debug_detection.png' and '{debug_dir}/'")
            
        # 2. Inpainting (Background Restoration)
        # 텍스트 영역을 지운 배경 이미지 생성
        
        # Mask dilation to cover edges better
        kernel = np.ones((5, 5), np.uint8) # v5에서는 넉넉하게 지움
        dilated_mask = cv2.dilate(full_mask, kernel, iterations=2)
        
        print(f"[Pipeline] Restoring background (Erase text)...")
        # 여기서 Stability AI가 사용됨 (API Key가 있으면)
        background_restored = self.inpainter.inpaint(inpainted_cv2, dilated_mask)
        
        # OpenCV -> PIL 변환 (렌더링은 PIL이 한글 폰트 처리에 유리)
        background_restored_rgb = cv2.cvtColor(background_restored, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(background_restored_rgb)
        
        # 3. Translation & Rendering
        for idx, item in enumerate(detected_texts):
            original_text = item['text']
            box = item['box'] # numpy array
            
            print(f"[Pipeline] Processing region {idx+1}/{len(detected_texts)}: '{original_text}'")
            
            # Translate (Simple translation)
            # v5 uses basic translate, not analyze_and_translate
            translated_text = self.translator.translate(original_text)
            print(f"    -> Translated: '{translated_text}'")
            
            # 텍스트 회전 각도 계산
            vec = box[1] - box[0]
            angle_rad = np.arctan2(vec[1], vec[0])
            angle_deg = np.degrees(angle_rad)
            render_angle = -angle_deg 
            
            # Render (Pillow) - 깔끔한 폰트로 그리기
            # [Phase 4] Use Smart Color
            text_color = item.get('text_color', (0, 0, 0))
            self.renderer.render(pil_image, translated_text, box, render_angle, text_color=text_color)
            
        # 4. Save
        pil_image.save(output_path)
        print(f"[Pipeline] Saved result to {output_path}")
