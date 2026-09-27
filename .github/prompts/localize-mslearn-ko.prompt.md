---
description: Microsoft Learn 영문 실습을 한국어로 현지화하고 검증합니다.
---

mslearn-korean-localization Skill을 사용해서 현재 저장소의 Microsoft Learn 실습을 한국어로 현지화해줘.

먼저 저장소 구조를 분석하고 `Instructions`가 영문 실습 원본인지 확인해. 구조가 호환되면 다음 작업을 수행해줘.

- `Instructions` 원본은 수정하지 않는다.
- `Instructions-kr`을 만들고 모든 영문 실습을 같은 폴더 및 파일명으로 번역한다.
- `Instructions-kr/README.md`에 번역 규칙, 원본 기준 커밋, 파일별 상태와 동기화 절차를 기록한다.
- 자연스러운 한국어를 사용하고 영어 UI 이름은 필요한 경우 병기한다.
- 영문과 한국어 프롬프트를 각각 복사 가능한 `prompt` 코드 블록으로 제공한다.
- 사람 친화적인 영문 입력값은 실제 입력값을 유지하고 괄호 안에 한국어 설명을 병기한다.
- 스키마명, 변수명, URL, Power Fx, Power Automate 식, OData 필터 및 종속 데이터는 변경하지 않는다.
- 이미지와 링크 경로를 유지한다.
- 번역 완료 후 Skill의 `validate_translation.py`를 가상 환경을 만들지 않고 실행하고 오류를 수정한다.
