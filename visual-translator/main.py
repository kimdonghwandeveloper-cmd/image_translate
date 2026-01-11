import os
import argparse
from dotenv import load_dotenv
print("Starting main.py...")
print("Importing pipeline...")
from src.pipeline import VisualTranslatorPipeline
print("Importing detector...")
from src.detector import TextDetector
print("Importing inpainter...")
from src.inpainter import StabilityAIInpainter, OpenCVInpainter
print("Importing translator...")
from src.translator import Translator
print("Importing renderer...")
from src.renderer import TextRenderer
import traceback

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Visual Translator CLI")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("--output", default="output.png", help="Path to save the translated image")
    args = parser.parse_args()

    # Verify API Keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        print("Warning: No API Key found (OPENAI_API_KEY or GOOGLE_API_KEY). Translation might be skipped.")

    print(f"Processing {args.image_path}...")

    # Initialize Components
    print("Initializing components...")
    
    # Detector (PaddleOCR)
    detector = TextDetector()
    
    # Inpainter (Stability AI) - 핵심: 배경을 깨끗하게 지움
    inpainter = StabilityAIInpainter()
    
    # Translator (Gemini)
    translator = Translator()
    
    # Renderer (Pillow) - 핵심: 폰트로 깔끔하게 찍음
    renderer = TextRenderer()
    
    # Pipeline
    print("Initializing pipeline...")
    pipeline = VisualTranslatorPipeline(detector, inpainter, translator, renderer)
    
    try:
        pipeline.run(args.image_path, args.output)
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()

    print(f"Done! Saved to {args.output}")

if __name__ == "__main__":
    main()
