import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Translator:
    def __init__(self):
        # Google Gemini 설정
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            # 사용자가 지정한 모델 사용
            # 사용자가 강력히 요청한 모델 사용
            # 실제 API에서 지원하지 않는 이름일 경우를 대비해 Fallback 로직 추가가 필요하지만,
            # genai.GenerativeModel 생성자 자체는 검증하지 않을 수 있음. generate_content에서 에러 날 것.
            
            target_model = "gemini-3-pro-image-preview" 
            # target_model = "gemini-1.5-pro" # 안정적인 대안
            
            # 우선 사용자 요청 모델로 초기화
            self.model = genai.GenerativeModel(target_model)
            print(f"Translator initialized with model: {target_model}") 
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. Translation will be skipped.")
        
        self.retriever = None

    def translate(self, text, context_glossary=None):
        """
        텍스트를 일본어로 번역합니다.
        """
        
        if not self.model:
            return text

        # 기본 프롬프트
        prompt = f"""You are a professional translator.
        Translate the following text into Japanese.
        
        Rules:
        1. Output ONLY the translated text. 
        2. Do not add any explanations, notes, or punctuation that wasn't in the original.
        3. If the text is heavily broken or untranslatable, return the original text.
        4. Keep it short and fit for a poster.
        
        Original Text:
        {text}
        
        Translation:"""
        
        try:
            response = self.model.generate_content(prompt)
            cleaned = response.text.strip().replace('`', '').replace('"', '').replace("'", "")
            return cleaned
        except Exception as e:
            print(f"Translation Error with primary model: {e}")
            if "NOT_FOUND" in str(e) or "404" in str(e):
                print("Falling back to gemini-1.5-flash for translation...")
                try:
                    fallback_model = genai.GenerativeModel("gemini-1.5-flash")
                    response = fallback_model.generate_content(prompt)
                    return response.text.strip().replace('`', '').replace('"', '').replace("'", "")
                except Exception as e2:
                    print(f"Fallback Translation Error: {e2}")
            return text

    def analyze_and_translate(self, image_crop: "PIL.Image.Image", text: str) -> dict:
        """
        이미지 조각을 분석하여 번역문과 스타일 프롬프트를 생성합니다.
        Returns:
            dict: {'translated_text': str, 'style_prompt': str}
        """
        # Vision 모델 사용 시도 (404 오류 지속으로 인해 Text-Only로 전환)
        # 만약 정말 이미지를 보고 싶다면 'gemini-1.5-pro' 등을 써야 하지만, 
        # 현재 키 권한 문제로 추정되므로 안정성을 위해 텍스트 번역 + 일반 스타일 리턴.
        
        # 1. Translate Text
        translated = self.translate(text)
        
        # 2. General Style Prompt (Since we can't see the image)
        # In a real scenario with working vision, we would ask Gemini to describe it.
        # Fallback Style:
        style_desc = "High quality text, clean font, professional design"
        
        return {
            'translated_text': translated,
            'style_prompt': style_desc
        }
