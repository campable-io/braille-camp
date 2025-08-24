# 시각장애인을 위한 수학 점자 변환 서비스 / Korean Math Braille Transcription Service

**Convert LaTeX mathematical notation to Korean Math Braille with accessibility in mind.**

## 🏕 About CampAble

### 프로젝트 개요

Campable(구 해바라기팀)은 2023년 SK 행복나눔재단과 공과대학교가 협력한 캡스톤 디자인 프로젝트로 시작된 팀입니다. 시각장애인의 교육 불평등 문제를 해결하기 위해 단순한 구상과 기획에 그치지 않고, 실질적인 도움이 되는 작동 가능한 프로덕트를 만들겠다는 목표 아래 약 3년간 팀원 모두가 꾸준히 협력해왔습니다. Braille Camp는 Campable 팀이 개발한 교육용 웹 기반 점역 소프트웨어로, 일반 텍스트는 물론 수학 수식까지 점역이 가능한 수학 특화 점역 프로그램입니다. Campable 팀은 사용자들이 쉽고 빠르게 원하는 교육 자료를 점역할 수 있도록 돕고, 더 많은 교육 자료에 대한 접근성을 높이기 위해 지속적으로 노력하고 있습니다.

Campable 팀은 언제나 실질적인 문제 해결, 그리고 누군가 실제로 사용할 수 있는 가치 있는 기술을 최우선에 두고 활동해왔습니다. 수많은 절차와 제약이 뒤따르는 시각장애인의 수학 교재 제작 과정을 생각할 때, 저희가 모든 문제를 단독으로 해결하는 데는 분명 한계가 있습니다. 하지만 오픈소스로 알고리즘을 공개한다면, 더 많은 개인과 조직이 이를 활용해 자신만의 방식으로 시각장애인을 위한 다양한 솔루션을 만들어낼 수 있습니다.

이는 단순히 교육 접근성을 높이는 차원을 넘어, 시각장애인이 겪는 문제에 진심으로 공감하고 해결하고자 하는 사람들의 진입 장벽을 낮추고, 문제 해결 활동의 접근성 자체를 확장하는 일이라고 생각합니다. 더 많은 사람들이 해당 문제에 대해 공감하고 자유롭게 혁신적이고 창의적인 솔루션을 만들어가셨으면 합니다.

### Overview

Campable (formerly the Team Haebaragi) began in 2023 as a capstone design project in collaboration between the SK Happiness Foundation and a university of engineering. Aiming to address the issue of educational inequality faced by visually impaired individuals, the team has spent about three years working steadily together—not stopping at mere concepts and plans, but striving to create a functional product that can provide real help.

**Braille Camp** is an educational, web-based braille transcription software developed by the Campable team. It is a math-specialized transcription program capable of converting not only plain text but also mathematical expressions into braille. The Campable team is committed to helping users quickly and easily transcribe the educational materials they need, and continues to work toward improving accessibility to a wider range of educational resources.

The Campable team has always prioritized solving real-world problems and developing valuable technologies that people can actually use. We recognize that, given the many procedures and constraints involved in producing math textbooks for the visually impaired, there are clear limitations to solving all issues on our own. However, by releasing our algorithm as open source, more individuals and organizations will be able to utilize it to create diverse solutions for the visually impaired in their own ways.

This is not merely about improving access to education—it is about lowering the barriers for those who genuinely empathize with the challenges faced by visually impaired individuals and wish to address them, thereby expanding the accessibility of problem-solving efforts themselves. We hope more people will empathize with this issue and freely create innovative and creative solutions.

### Links

**Team CampAble** - https://www.campable.io <br/>
**Braille Camp** - https://braille.campable.io

## Key Features

### 주요 기능

_Braille Camp 알고리즘은 LaTeX 수학 표기(입력)를 한국어 수학 점자(출력)로 변환합니다. 본 알고리즘은 2024년 개정 수학점자규정을 반영하였습니다._

**1. 한국 점자 규정을 준수한 latex -> brf 수식 점역**

- 2015 개정 한국 중·고등학교 교육과정의 수식을 점역합니다.
- 2024년 2월 개정된 한국 수학 점자 규정을 준수합니다.
- LaTeX로 작성된 수식을 BRF(Braille Ready Format)으로 변환하며, 유니코드 점자 출력도 지원합니다.

**2. 커뮤니티 발전을 위한 오픈소스**

- Apache 2.0 라이선스로 배포되어 자유로운 사용, 수정, 상업적 배포가 가능합니다.
- 교육자, 개발자, 접근성 전문가의 커뮤니티 기여를 환영하며, 이를 통해 점자 매핑을 개선·확장합니다.

**3. 결과물 활용**

- 교육용 소프트웨어, 점자 정보단말기, 점자 디스플레이, 타 점역 프로그램으로 결과물을 활용할 수 잇습니다.

### Core Features

_Braille Camp converts LaTeX mathematical notation (Input) to Korean Math Braille (Output). This algorithm reflects the 2024 revised Korean Math Braille regulations._

**1. Accurate LaTeX-to-Korean Math Braille Transcription**

- Transcribes all math expressions from the Korean middle and high school curriculum (2015 revision).
- Complies with the February 2024 update to the Korean Braille regulations.
- Converts LaTeX-based math equations into BRF (Braille Ready Format), with support for Unicode Braille output.

**2. Open-source for Community Improvement**

- Distributed under the Apache 2.0 license, allowing free use, modification, and commercial distribution.
- Welcomes community contributions from educators, developers, and accessibility experts to enhance and expand Braille mappings.

**3. Use of Output**

- The output can be utilized in educational software, Braille notetakers, Braille displays, and other transcription programs.

## Open Source License

This opensource project is based on the [Apache 2.0](./LICENSE) license.

## Quick Start

### Installation

Clone this repository:

```
git clone https://github.com/campable-io/braille-camp.git
cd braille-camp
```

Import the `convert_latex_to_braille` function. This takes a `LaTeX` input which transcribes to braille notation:

```
from .algorithm import convert_latex_to_braille

problem = """다음 극한값을 구하여라.
(1) \( \lim _{n \rightarrow \infty} \frac{(n+2)(3n-5)}{(2n+1)(n-2)} \)
(2) \( \lim _{n \rightarrow \infty} \frac{3n-1}{n^{2}-2n+2} \)
(3) \( \lim _{n \rightarrow \infty} \frac{2n^{3}+5 n}{n^{2}+1} \)
(4) \( \lim _{n \rightarrow \infty}\{\log (2n+1)-\log (3n+2)\} \)"""

braille_output = convert_latex_to_braille(problem)
print(braille_output)
```

Output is braille notation which can be read with braille notetakers:

```
다음 극한값을 구하여라.
(1) ^123,24,134,56,1345^ ^25,135^ ^123456^ ^12356,236,3456,12,1345,26,3456,1,356,236,1345,35,3456,12,356,23456,34,12356,236,1345,26,3456,12,356,236,3456,14,1345,35,3456,15,356,23456^
(2) ^123,24,134,56,1345^ ^25,135^ ^123456^ ^12356,1345,45,3456,12,35,3456,12,1345,26,3456,12,23456,34,12356,3456,14,1345,35,3456,1,23456^
(3) ^123,24,134,56,1345^ ^25,135^ ^123456^ ^12356,1345,45,3456,12,26,3456,1,23456,34,12356,3456,12,1345,45,3456,14,26,3456,15,1345,23456^
(4) ^123,24,134,56,1345^ ^25,135^ ^123456^ ^2356,456,236,3456,12,1345,26,3456,1,356,35,456,236,3456,14,1345,26,3456,12,356,2356^
```

## Documentation

For more detailed guides, examples, and implementation notes, see the documentation below:

- 🇰🇷 [Documenation - Korean](./docs/docs_ko.md)
- 🇺🇸 [Documenation - English](./docs/docs_en.md)

## Contribute

### Bug Reports

재현 단계와 함께 최소 LaTeX 입력, 실제 출력(BRF/유니코드)과 기대 출력(가능하면 관련 규정 조항 예: 제6-2)을 적어 Issues에 등록해 주세요. 사용 환경(OS, Python/패키지 버전, 점자 디스플레이/리더)과 스크린샷·오류 로그를 첨부해 주시면 원인 파악이 훨씬 빨라집니다.

Please open an issue with reproduction steps, a minimal LaTeX input, the actual output (BRF/Unicode), and the expected output (ideally citing the relevant rule, e.g., Section 6-2). Include your environment (OS, Python/package versions, Braille device/reader) and attach screenshots or error logs to speed up triage.

### Feature Requests & Questions

해결하려는 문제와 제안 기능(또는 대안), 예상 사용 시나리오(예: 교육용 소프트웨어/점자정보단말기)를 간단히 설명해 주세요. 관련 문서 링크(예: docs_ko.md/규정 조항)나 기존 이슈/PR을 함께 남기면 논의가 더 수월합니다.

Briefly describe the problem, the proposed feature (or alternatives), and your intended use case (e.g., educational software, Braille notetaker). Linking relevant docs (e.g., docs_en.md/rule sections) and any related issues/PRs makes review and discussion easier.

## Acknowledgements / Sponsors

본 프로젝트는 초기 구상 단계부터 완성된 제품 개발에 이르기까지 다음의 주체 및 회사의 아낌없는 지원과 도움으로 가능했습니다:

- [SK 행복나눔재단](https://skhappiness.org)
- [법무법인 DLG](https://dlglaw.co.kr)
- [브라이언 임팩트 재단](https://brianimpact.org)
- [연세대학교 메이커스페이스](https://www.makerspacei7.com)
- [푸르매 재단](https://purme.org)

프로젝트 전 과정에서 소중한 의견과 피드백을 나누어 주신 점역사, 시각장애인 학생 및 교육자 여러분께 깊은 감사를 드립니다. 여러분의 참여가 진정한 사용자 중심 솔루션을 만드는 데 큰 힘이 되었습니다.

This project was made possible through the generous support of the following organizations:

- [SK Happiness Foundation](https://skhappiness.org)
- [DLG Law Firm](https://dlglaw.co.kr)
- [Brian Impact](https://brianimpact.org)
- [Yonsei-Makerspace](https://www.makerspacei7.com)
- [Purme Foundation](https://purme.org)

Special thanks to our mentors, collaborators, and all the visually impaired students and educators who shared their insights and feedback throughout the process. Your contributions have been invaluable in shaping a truly user-centered solution.
