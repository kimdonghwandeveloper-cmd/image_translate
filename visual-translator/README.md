# 🍓 AI Visual Translator (시각적 번역기)

> **"외국어 메뉴판, 만화, 포스터를 원본 느낌 그대로 번역해 드립니다."**

이 프로젝트는 단순히 글자만 번역하는 것이 아닙니다.  
이미지 속의 **글자를 감쪽같이 지우고**, 그 자리에 **번역된 글자를 자연스럽게 합성**해주는 AI 도구입니다.

![Before & After Example](result_phase4_final.png)
*(위 이미지는 예시입니다. 실제로 이렇게 바뀝니다!)*

---

## ✨ 무엇이 특별한가요?

보통 번역기(파파고, 구글 렌즈)는 글자 위에 색깔 상자를 덧씌워서 번역하죠?  
**Visual Translator**는 다릅니다.

1.  **AI 지우개 (Inpainting)**: 글자가 있던 자리를 주변 배경과 똑같이 복원해서 지웁니다. (마치 처음부터 글자가 없었던 것처럼!)
2.  **스마트 디자인**: 배경색이 어두운지 밝은지 스스로 판단해서, 가장 잘 보이는 글자색을 골라줍니다.
3.  **정밀한 위치 선정**: 원래 글자가 있던 각도와 크기를 그대로 따라가서, 디자인을 해치지 않습니다.

## 🛠️ 사용된 기술 (어떻게 작동하나요?)

전문가가 아니어도 이해할 수 있는 4단계 과정입니다:

1.  **눈 (PaddleOCR)**: "여기 글자가 있네?" 하고 위치를 찾아냅니다.
2.  **지우개 (Stability AI)**: "글자만 싹 지워줘." 하고 배경을 깨끗하게 만듭니다.
3.  **뇌 (Google Gemini)**: "이거 한국어로 무슨 뜻이야?" 하고 문맥에 맞게 번역합니다.
4.  **손 (Python Pillow)**: "이제 예쁜 폰트로 다시 적자." 하고 깨끗해진 배경 위에 번역문을 씁니다.

---

## 🚀 시작하기 (설치 방법)

### 1. 준비물
*   Python (파이썬)이 설치되어 있어야 합니다.
*   **API 키**: 두 가지 열쇠가 필요합니다.
    *   `GOOGLE_API_KEY`: 번역을 위한 구글(Gemini) 키
    *   `STABILITY_API_KEY`: 배경 지우기를 위한 Stability AI 키

### 2. 설치
터미널(명령 프롬프트)에서 다음 명령어를 입력하세요.

```bash
# 필요한 프로그램들을 설치합니다
pip install -r requirements.txt
```
*(또는 `uv`를 사용하신다면 `uv pip install -e .`)*

### 3. 열쇠 설정 (.env)
폴더 안에 `.env` 라는 파일을 만들고, 준비한 키를 적어주세요.

```ini
GOOGLE_API_KEY=여러분의_구글_키_입력
STABILITY_API_KEY=여러분의_스태빌리티_키_입력
```

---

## 💻 사용 방법

아주 간단합니다. 번역하고 싶은 이미지 파일이 있다면 실행해 보세요!

```bash
# 기본 실행
python main.py menu.jpg --output menu_translated.png

# (NEW) 텍스트 회전 기능 끄기 (OCR 각도가 이상할 때 사용)
python main.py menu.jpg --no-rotate
```
잠시 기다리면 `menu_translated.png` 파일이 짠! 하고 나타납니다.

---

## 📁 폴더 구조 (개발자를 위한 정보)

*   `main.py`: 이 프로그램을 실행하는 메인 파일입니다.
*   `src/`: 핵심 부품들이 들어있는 상자입니다.
    *   `detector.py`: 글자 위치 탐지기
    *   `inpainter.py`: 배경 지우개
    *   `translator.py`: 번역기
    *   `renderer.py`: 글자 쓰기 도구
    *   `color_utils.py`: 색상 골라주는 도구

---
*Created by Karl3 & Antigravity (Google DeepMind)*
