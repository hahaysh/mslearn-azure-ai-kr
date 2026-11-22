# Microsoft Azure AI 한국어 실습

[한국어 실습 사이트](https://koreamtt.github.io/mslearn-azure-ai-kr/) · [Microsoft Learning 영문 원본](https://microsoftlearning.github.io/mslearn-azure-ai/)

이 저장소는 Microsoft Learning의 Azure 개발자 실습과 한국어 번역본을 제공합니다. 기존 Microsoft Learning Jekyll 테마와 GitHub Pages 배포 구성을 사용합니다.

## 프로젝트 구성

| 경로 | 역할 |
| --- | --- |
| [Instructions](./Instructions/) | 영문 실습 27개와 원본 자산 |
| [Instructions-kr](./Instructions-kr/) | 동일한 경로의 한국어 실습 27개와 미러 자산 |
| [한국어 번역 유지관리 지침](./Instructions-kr/README.md) | 번역 원칙, 동기화 기준 및 검증 기록 |
| [index.md](./index.md) | 한국어 실습을 주제별로 표시하는 홈페이지 |
| [lab-requirements.md](./lab-requirements.md) | 전체 실습의 공통 준비 사항 |
| [finished](./finished/) | 실습 완성 예제 |
| [downloads/python](./downloads/python/) | 학습자용 다운로드 ZIP |

## GitHub Pages

- 게시 주소: https://koreamtt.github.io/mslearn-azure-ai-kr/
- 사이트 설정: [_config.yml](./_config.yml)의 조직 주소, 프로젝트 경로 및 저장소 이름을 사용합니다.
- 기존 [Pages 워크플로](./.github/workflows/pages.yml)가 **main** 브랜치에 푸시할 때 Jekyll로 빌드하고 배포합니다. GitHub Actions에서 수동 실행할 수도 있습니다.
- 저장소의 **Settings > Pages > Build and deployment > Source**는 **GitHub Actions**를 사용합니다.
- 홈페이지는 한국어 실습만 표시합니다. 실습 본문의 원본 다운로드 URL과 영문 자료는 유지합니다.
- [_build.yml](./_build.yml)은 기존 Azure Pipelines 문서 패키징 설정이며, GitHub Pages 배포에는 사용하지 않습니다.

## About the original exercises

This repo contains exercises and supporting files for Microsoft skilling content.

The exercises may be used in both self-paced skilling experiences on [Microsoft Learn](https://learn.microsoft.com) and in Microsoft authorized instructor-led training.

Students and lab providers can review the [lab requirements](./lab-requirements.md) for the combined accounts and software needed to support all exercises in this repository.

## Information for MCTs

**Are you an MCT?** - Have a look at our [GitHub User Guide for MCTs](https://microsoftlearning.github.io/MCT-User-Guide/)

Any MCT (Microsoft Certified Trainer) can submit a pull request to the code or content in the GitHub repro. Microsoft and the course author will then triage and include content and lab code changes as needed. You can submit bugs, changes, improvement, and ideas. Find a new Azure or Microsoft 365 feature before we have? Submit a new demo!
