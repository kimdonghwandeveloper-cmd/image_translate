from abc import ABC, abstractmethod
import cv2
import numpy as np
import requests
import os
import io

class Inpainter(ABC):
    @abstractmethod
    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        pass

class OpenCVInpainter(Inpainter):
    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        OpenCV의 inpaint 함수를 사용하여 텍스트 영역을 복원합니다.
        """
        restored_image = cv2.inpaint(image, mask, 3, cv2.INPAINT_NS)
        return restored_image

class StabilityAIInpainter(Inpainter):
    def __init__(self):
        self.api_key = os.getenv("STABILITY_API_KEY")
        if not self.api_key:
            print("Warning: STABILITY_API_KEY not found. Fallback to OpenCV.")
            
    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Stability AI의 Erase API를 사용하여 텍스트 영역을 복원(지우기)합니다.
        """
        if not self.api_key:
            print("[Inpainter] Stability Key missing, fallback to OpenCV.")
            return OpenCVInpainter().inpaint(image, mask)

        print("Sending request to Stability AI for inpainting...")
        
        # 1. Encode image and mask to bytes
        _, img_encoded = cv2.imencode('.png', image)
        _, mask_encoded = cv2.imencode('.png', mask)
        
        try:
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/edit/erase",
                headers={
                    "authorization": f"Bearer {self.api_key}",
                    "accept": "image/*"
                },
                files={
                    "image": img_encoded.tobytes(),
                    "mask": mask_encoded.tobytes(),
                },
                data={
                    "output_format": "png"
                },
            )

            if response.status_code == 200:
                print("Stability AI Inpainting Success!")
                # Convert bytes response back to numpy array
                nparr = np.frombuffer(response.content, np.uint8)
                restored_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return restored_image
            else:
                print(f"Stability AI Error ({response.status_code}): {response.json()}")
                print("Falling back to OpenCV inpainting...")
                return OpenCVInpainter().inpaint(image, mask)
                
        except Exception as e:
            print(f"Stability AI Request Failed: {e}")
            print("Falling back to OpenCV inpainting...")
            return OpenCVInpainter().inpaint(image, mask)
