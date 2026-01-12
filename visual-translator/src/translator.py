import os
import openai
from dotenv import load_dotenv

load_dotenv()

class Translator:
    def __init__(self):
        # OpenAI 설정
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            # OpenAI 모델 설정 (GPT-4o 사용 권장)
            self.model_name = "gpt-4o" 
            print(f"Translator initialized with model: {self.model_name}") 
        else:
            self.client = None
            print("Warning: OPENAI_API_KEY not found. Translation will be skipped.")
        
        self.retriever = None

    def translate(self, text, context_glossary=None):
        """
        텍스트를 일본어로 번역합니다.
        """
        
        if not self.client:
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
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful translator."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            cleaned = response.choices[0].message.content.strip().replace('`', '').replace('"', '').replace("'", "")
            return cleaned
        except Exception as e:
            print(f"Translation Error with OpenAI: {e}")
            return text

    def analyze_and_translate(self, image_crop, text):
        """
        이미지 조각을 분석하여 번역문과 스타일 프롬프트를 생성합니다.
        (OpenAI 마이그레이션: 현재는 텍스트 번역만 수행하고 기본 스타일을 반환합니다)
        """
        # 1. Translate Text
        translated = self.translate(text)
        
        # 2. Default Style
        style_desc = "High quality text, clean font, professional design"
        
        return {
            'translated_text': translated,
            'style_prompt': style_desc
        }
