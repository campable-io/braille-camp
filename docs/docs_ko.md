# Braille Camp 문서

**한국어** | [English](./docs_en.md)

## 소개

Math_to_Braille 패키지는 LaTeX 기반 수학식을 점자 형식으로 변환하는 도구로, BRF(Braille Ready Format)과 유니코드 점자 출력을 모두 지원합니다. 2024년 2월 개정을 포함한 한국 수학 점자 규정을 준수합니다.

### 1. 적용 범위 및 기능

- 2015 개정 한국 중·고등학교 교육과정에 포함된 수학 전 범위를 반영합니다.
- 분수, 루트, 로그, 삼각함수 등 다양한 수학 표현을 점역합니다.
- BRF 파일과 유니코드 점자 모두 규정에 맞게 출력하여 점자정보단말기 및 관련 보조공학 기기와 호환됩니다.

### 2. 구조

Math_to_Braille는 점역 과정의 각 단계를 담당하는 여러 모듈로 구성됩니다.

- LaTeX 기호를 BRF 코드로 매핑
- BRF 코드를 유니코드 점자로 변환
- LaTeX에서 BRF로 단계별 변환 수행

### 3. 문서 구성

이 문서는 다음과 같이 구성됩니다.

1. **소개** – 패키지 개요, 범위, 목적
2. **모듈 개요** – 각 모듈의 설명과 역할
3. **참고 사항** – 모듈 사용 시 알아두어야 할 세부 사항, 주의점, 특수 사례

## 모듈 개요

### 1. `brf_code`

- LaTeX 수식을 해당 BRF 코드로 매핑하는 code라는 변수명의 dictionary를 포함합니다.
- `Key`: LaTeX 수학식 (일부 key는 LaTeX와 BRF가 혼합될 수 있음)
- `Value`: `(latex_code: str, brf_code: str)` — 원본 `LaTeX` 코드와 해당 `BRF` 코드의 `tuple`

예시:

```
(key → value):
  "(" → ("(", "8")
  "\\times" → ("\\times", "\*")
  "\\left8" → ("\\left(", "8")
```

### 2. `brf_to_indeterminate_letter`

- BRF 코드를 해당 유니코드 점자로 매핑하는 indeterminate_code라는 이름의 dictionary를 포함합니다.
- `Key`: BRF 코드
- `Value`: `(brf_code: str, unicode_braille: str)` — BRF 코드와 해당 유니코드 점자 표현의 튜플

### 3. `MathBrailleTranscribe`

- LaTeX 기반 수학식을 BRF 형식으로 변환하는 함수들을 포함합니다.
- 함수들은 다음 네 가지 카테고리로 구성됩니다.

1. Basic Translation – brf_code.code 를 참조하여 LaTeX 기호를 1:1로 대응시켜 BRF로 변환
2. Translation Functions for Specific LaTeX Symbols – 특정 형식으로 작성된 LaTeX 수식을 변환 (분수, 선분, 로그 등 대부분의 수식 변환 포함)
3. Sophisticated Process – 변환된 BRF 결과물을 한국 수학 점자 규정(예: 제6항 2호, 제12항 1호)에 맞게 편집
4. Change Form – 점역 편의를 위해 LaTeX 표현의 구조나 형식을 변경 (예: 로그의 진수를 {}로 감싸기, 삼각함수 값을 {}로 감싸기)

### 4. 주요 함수

**`mathBrailleTranscribe`**

- LaTeX 문자열을 완전한 수학 점역 알고리즘을 사용하여 직접 BRF로 변환합니다.
- 코드를 수정하지 않고 개발된 점역 서비스를 그대로 사용하고자 할 때 이 함수를 사용하면 됩니다.
- 입력: latex_str (str) – LaTeX 수학식
- 출력: str – BRF 코드

<br/>

**`translate_to_math_braille`**

- Change Form 카테고리 일부 함수를 제외한 모든 카테고리의 함수를 점역 과정에 맞게 순서대로 실행합니다.
- 입력: latex_str (str) – LaTeX 수학식
- 출력: str – BRF 코드

## 3. 참고 사항

### 주요 함수: `translate_to_math_braille`

- 먼저 Basic Translation 단계를 거친 후, 결과물의 공백을 제거합니다.
- 점역 규정에 따라 띄어쓰기가 필요한 경우, 패키지에서 지정한 특수 문자열 WSP를 삽입하고 변환이 완료된 후 이를 일반 공백으로 교체합니다.
- 그리스 문자 _eta_, _theta_, *chi*는 점역의 일관성과 편의를 위해 임시로 .h, .j, .q로 변환한 뒤, 최종적으로 올바른 점형으로 변환합니다.

### 묶음괄호 처리 (한국 수학 점자 규정 제6항 2호)

- 묶음괄호 처리는 Sophisticated Process 카테고리의 brf_parentheses 함수가 담당합니다.
- 묶음괄호가 사용될 수 있는 모든 수식에 먼저 묶음괄호를 적용한 뒤, brf_parentheses 함수를 사용하여 유지 또는 제거를 판정합니다.
- 예시 – 분수 처리 과정:

- brf_parentheses에서 “괄호 불필요”로 정의되지 않은 경우에는 괄호가 유지되므로, 결과물에 불필요한 괄호가 남을 수 있습니다.

### 띄어쓰기 규정 준수

- 한국 수학 점자 규정 제11항을 포함한 띄어쓰기 관련 조항 준수는 완벽하지 않을 수 있습니다.
