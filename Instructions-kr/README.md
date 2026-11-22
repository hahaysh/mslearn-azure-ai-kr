# Azure 개발자 실습 한국어 번역 및 유지관리 지침

## 목적

이 디렉터리는 `Instructions`에 있는 영문 Microsoft Learn 실습의 디렉터리 구조를 그대로 반영한 한국어 번역본을 관리합니다. 원본 디렉터리는 `Instructions`, 번역 디렉터리는 `Instructions-kr`이며, GitHub Pages에서는 경로의 대소문자를 구분합니다.

- 영문 원본에 번역용 편집을 하지 않습니다. 최신화할 때는 MicrosoftLearning upstream의 파일을 내용 변경 없이 그대로 동기화합니다.
- 한국어 파일은 영문 원본과 동일한 상대 경로, 파일명 및 문서 구조를 유지합니다.
- 자연스러운 한국어를 사용하고 필요한 영어 UI 이름을 함께 표기합니다.
- 영문 원본이 변경되면 이 문서의 동기화 절차에 따라 번역본을 갱신합니다.

## 번역 경로

| 구분 | 경로 |
| --- | --- |
| 영문 원본 | `Instructions` |
| upstream 영문 경로 | `MicrosoftLearning/mslearn-azure-ai`의 `instructions` |
| 한국어 번역 | `Instructions-kr` |
| 영문 미디어 | `Instructions/**/media` |
| 한국어 미디어 | `Instructions-kr/**/media` |

upstream은 소문자 `instructions`, 이 fork는 대문자 `Instructions`를 사용합니다. 동기화 시 루트 디렉터리 이름만 매핑하고 그 아래의 상대 경로와 파일명은 그대로 유지합니다. 최신 upstream에서 확인된 영문 실습은 29개이며 모두 YAML front matter를 포함합니다.

## 번역 원칙

- 수행 단계는 `~합니다` 형식으로 작성합니다.
- 실습 안내에는 `실습`, `시작 파일`, `프로비저닝`을 일관되게 사용합니다. 코드와 복사 가능한 프롬프트 안의 표현은 변경하지 않습니다.
- Microsoft 제품명과 공식 서비스 이름은 원문을 유지합니다.
- 영어 UI를 사용하는 경우 처음 의미 있게 등장하는 주요 항목을 `한국어(English)` 형식으로 표기합니다.
- YAML front matter의 키, `level`, `duration` 같은 구조 값은 유지하고 제목과 설명은 번역합니다.
- 제목 수준, 번호 매기기, 목록, 표, 콜아웃 및 실행 단계의 순서는 유지합니다.
- 같은 단계에 나란히 제시된 완전한 셸 예제와 셸별 목록은 사용자 요청에 따라 `PowerShell`, `Bash` 순서로 제공합니다. 명령 내용은 원문 그대로 유지하며, 이 순서 변경만 번역 계약의 예외로 허용합니다.
- 번역본에만 추가된 Git Bash 전체 예제로 본문의 명령을 중복하지 않습니다. 검증된 호환성 보완은 해당 단계의 짧은 참고와 문제 해결 안내로 분리하고, 원문에 없는 보완임을 명시합니다.
- 원문에 없는 절차를 추측하여 추가하지 않습니다.
- 원문의 오류는 임의로 수정하지 않고 알려진 원문 문제에 기록합니다.

## 프롬프트

영문과 한국어 프롬프트를 각각 복사 가능한 `prompt` 코드 블록으로 제공합니다. 영문 프롬프트는 정확히 보존하고, 바로 다음에 자연스럽게 번역한 한국어 프롬프트를 추가합니다.

````markdown
```prompt
You are an agent that analyzes tasks.
```

```prompt
작업을 분석하는 에이전트입니다.
```
````

- `한국어 의미:`와 같은 레이블을 사용하지 않습니다.
- 한국어 프롬프트 안에 입력값이 아닌 Markdown 장식을 추가하지 않습니다.
- URL, 자리표시자, 슬래시 참조 및 필수 식별자를 보존합니다.

## 사람 친화적인 입력값

이름, 제목, 설명처럼 사람이 읽는 영문 입력값은 실제 입력값을 그대로 유지하고 한국어 설명을 코드 범위 밖에 표기합니다.

```markdown
**`US Benefits Assistant`(미국 복리후생 지원 담당자)**
```

학습자는 영문 값만 입력합니다. 이후 단계에서도 작업에 사용되는 영문 이름을 변경하지 않습니다.

다음 값에는 이 방식을 적용하지 않으며 원문을 그대로 보존합니다.

- 스키마명, 변수명, GUID 및 URL
- 파일 경로, API 및 커넥터 식별자
- Power Fx 및 Power Automate 식
- OData 필터와 식에 종속되는 데이터
- Excel 헤더와 필터 또는 식에서 사용하는 선택 값

## 이미지와 링크

- 원본에서 참조하는 이미지와 기타 필수 자산을 동일한 상대 경로로 복사합니다.
- 바이너리 자산은 별도 요청이 없으면 변경하지 않습니다.
- 이미지 대체 텍스트와 링크 텍스트는 번역하되 대상 경로는 유지합니다.
- 한국어 문서의 모든 로컬 링크와 이미지 경로가 실제 대상으로 확인되어야 합니다.

## 동기화 절차

1. MicrosoftLearning 원본의 `main`을 가져오고 정확한 upstream 커밋을 즉시 기록합니다. `FETCH_HEAD`는 다음 fetch에서 바뀔 수 있으므로 이후 비교에는 기록한 커밋을 사용합니다.
2. 마지막 동기화 upstream 커밋과 새 커밋의 `instructions` 트리를 비교하여 추가, 삭제, 이름 변경 및 내용 변경을 분류합니다. 로컬 `Instructions`와 upstream `instructions`의 대소문자 차이를 삭제로 해석하지 않습니다.
3. 작업 트리를 확인하고 사용자 변경을 보존합니다. upstream의 영문 파일만 `Instructions`로 원문 그대로 동기화하고 파일별 Git blob 해시를 비교하여 내용이 같은지 확인합니다. 영문 실습을 번역하거나 임의로 고치지 않습니다.
4. 영문 변경 사항을 의미 단위로 한국어 문서에 반영합니다. 기존 한국어 파일을 영문 파일로 덮어쓰지 않습니다.
5. 변경된 이미지와 필수 자산을 동일한 상대 경로로 복사하고 SHA-256을 비교합니다.
6. 전체 문맥, 프롬프트 쌍, 입력값, 코드, 상대 경로 및 링크를 검토하고 번들 검증기를 실행합니다. 검증을 위해 새 가상 환경을 만들 필요는 없습니다.
7. 모든 변경을 반영하고 검증한 후에만 기준 커밋, 검토일 및 파일별 상태를 갱신합니다. 커밋, 푸시 및 게시 작업은 별도 요청이 있을 때만 수행합니다.

```powershell
$previousCommit = "4bb868b5f05e233df0d0e2294dc75438038e1b6f"
git fetch https://github.com/MicrosoftLearning/mslearn-azure-ai.git main
$sourceCommit = git rev-parse FETCH_HEAD
git diff "$($previousCommit):instructions" "$($sourceCommit):instructions"
python .github\skills\mslearn-korean-localization\scripts\validate_translation.py --repo . --source Instructions --target Instructions-kr --readme Instructions-kr\README.md --powershell-first
git diff --check
git status --short
```

이 저장소의 한국어판 검증에는 `--powershell-first`를 사용합니다. 이 옵션은 같은 단계의 인접한 셸 예제를 PowerShell 우선 순서로 비교하며, 명령 수정이나 다른 단계로의 이동을 허용하지 않습니다. 옵션을 생략하면 기존의 엄격한 원문 순서 검증이 유지되므로 현재 한국어판의 의도적인 셸 순서 변경이 오류로 보고됩니다.

## 동기화 상태

| 항목 | 값 |
| --- | --- |
| 저장소 | `koreamtt/mslearn-azure-ai-kr` |
| 영문 원본 저장소 | `https://github.com/MicrosoftLearning/mslearn-azure-ai` |
| 원본 브랜치 | `main` |
| 기준 upstream 커밋 | `4bb868b5f05e233df0d0e2294dc75438038e1b6f` |
| 이전 번역 기준 커밋 | `af79d9a3fd8c972b1de35467d638344241a99420` |
| 마지막 검토일 | `2026-11-22` |
| 전체 상태 | 한국어 실습 29개 문장·용어 교정, PowerShell 우선 재배치 및 검증 완료 |
| upstream 동기화 변경 | 기존 한국어 실습 21개 갱신, 6개 변경 없이 검토, 신규 실습 2개 번역 |
| 한국어 교정 | 한국어 실습 29개 의미·문법·용어·문체·UI 병기 개선, 영문 원본 변경 없음 |
| 영문 최신화 | 기존 영문 18개 갱신 및 신규 2개 추가, 모든 파일이 upstream 원문과 바이트 단위로 일치 |

## 동기화 시 파일별 상태

아래 표는 upstream 동기화 당시의 변경 내역입니다. 이후 적용한 한국어 교정 내역은 다음 섹션에 별도로 기록합니다.

| 영문 원본 기준 상대 경로 | 상태 |
| --- | --- |
| `app-sec-config/01-aks-retrieve-secrets.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `app-sec-config/02-exercise-retrieve-settings.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-container-apps/01-aca-deploy-containers.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `azure-container-apps/02-aca-manage-containers.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `azure-container-apps/03-aca-scale-containers.md` | Load Run 설명 추가·원문 활성화 명령 복원 및 검증 완료 |
| `azure-container-apps/04-aca-dynamic-sessions.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-database-postgresql/01-build-agent-tool-backend.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-database-postgresql/02-implement-vector-search.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-database-postgresql/03-optimize-vector-search.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `azure-kubernetes-service/01-aks-deploy-container.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-kubernetes-service/02-aks-configure-container.md` | 원문 활성화 명령 복원 및 검증 완료 |
| `azure-kubernetes-service/03-aks-troubleshoot-container.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `azure-managed-redis/01-amr-data-operations.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-managed-redis/02-amr-pub-sub.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `azure-managed-redis/03-amr-vector-storage.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `container-hosting/01-acr-tasks.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `container-hosting/02-app-svc-container.md` | 전체 검토 및 검증 완료, 변경 없음 |
| `container-hosting/03-app-svc-sidecar.md` | 단계 번호 검토·원문 활성화 명령 복원 및 검증 완료 |
| `cosmosdb/01-build-rag-document-store.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `cosmosdb/02-build-semantic-search.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `cosmosdb/03-optimize-query-performance.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `cosmosdb/04-persisent-agent-memory.md` | 신규 전체 번역 및 검증 완료 |
| `instrument-observe/01-instrument-app-opentelemetry.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `instrument-observe/02-query-logs-kql.md` | 원문 활성화 명령 복원 및 검증 완료 |
| `integrate-services/01-svcbus-process-messages.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `integrate-services/02-eventgrid-publish-receive-events.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `integrate-services/03-azure-functions-mcp-server.md` | 프롬프트 범주 보존·원문 활성화 명령 복원 및 검증 완료 |
| `integrate-services/04-durable-functions-ai.md` | 안내 동기화·원문 활성화 명령 복원 및 검증 완료 |
| `integrate-services/05-azure-web-pubsub.md` | 신규 전체 번역 및 검증 완료 |

## 한국어 교정 이력

2026-11-22 번역 품질 검토에서 제안한 개선 사항을 한국어 실습 29개에 반영했습니다. 기준 upstream 커밋은 변경하지 않았으며, 영문 원본과 실습 코드는 수정하지 않았습니다.

- 동적 세션: 인증과 권한 부여를 구분하고, 세션 삭제 시 임시 데이터를 제거한다는 의미를 명확히 했습니다. REST 요청 완료와 코드 실행 성공의 차이도 자연스럽게 설명했습니다.
- Key Vault 및 App Configuration: 반복 가능한 객체와 비밀 속성·설정 개체의 관계를 명확히 했습니다. 레이블 우선순위 적용과 참조가 가리키는 실제 비밀 값 조회를 구체적으로 설명했습니다.
- Container Apps, PostgreSQL, Cosmos DB 및 Functions: 로그 진단 설명, 라우트 처리 함수, 택배 예시, 사전 요구 사항의 불완전한 문장을 교정했습니다.
- 공통 표현: `실습`, `시작 파일`, `프로비저닝`과 `~합니다`체를 통일했습니다. 일반 콜아웃 제목은 `중요`, `참고`, `팁`, `주의`로 맞췄습니다.
- UI: 기존 영한 병기는 한국어 우선 순서로 정리하고, 한국어 이름에 맞게 조사를 교정했습니다. 실제 영어 UI 이름과 선택값은 보존했습니다.
- 보존 검증: 교정 전 HEAD와 비교하여 모든 코드 블록, 영문·한국어 프롬프트, 인라인 입력값 및 링크·이미지 대상이 동일함을 확인했습니다. 변경은 `Instructions-kr` 안에만 있습니다.
- 번들 검증기: 29개 Markdown 파일 통과. 구조 검증은 문장의 자연스러움이나 의미 정확성을 자동으로 보장하지 않으므로 별도의 문맥 검토와 함께 사용합니다.
- 기존 Markdown lint 경고는 유지했습니다. 커밋, 푸시 및 게시 작업은 수행하지 않았습니다.

## 셸 안내 정리 이력

2026-11-22 사용자 요청에 따라 한국어 실습 29개의 완전한 인접 셸 예제와 셸별 문제 해결 목록을 PowerShell 우선으로 재배치했습니다. 20개 실습의 가상 환경 활성화 설명도 Windows·PowerShell을 먼저 언급하도록 정리했습니다.

- ACR Tasks와 App Service 컨테이너 실습에 추가돼 있던 Git Bash 전체 예제 2개를 제거했습니다. 원문 Bash·PowerShell 명령은 유지하고, 경로 자동 변환 우회 방법은 문제 해결 안내로 옮겼습니다.
- 번들 검증기에 선택형 `--powershell-first` 옵션을 추가했습니다. 기본 엄격 검증은 유지하며, 완전한 인접 셸 쌍 외의 이동이나 코드 내용 변경은 허용하지 않습니다.
- 원문의 손상된 코드 블록, 코드 블록 내부의 셸 레이블 및 주석은 재배치하지 않습니다. Container Apps 관리 실습에서 닫히지 않은 PowerShell 블록이 다음 Bash 예제까지 포함하는 구간도 그대로 보존했습니다.
- 검증: PowerShell 우선 옵션으로 실습 29개 통과. 셸 순서·줄바꿈·주석·중첩 코드·반복 적용 검사와 명령 변조·단계 이동 거부 검사를 통과했습니다.
- 영문 원본, 클라이언트 코드, 배포 스크립트 및 환경 파일은 수정하지 않았습니다. 커밋, 푸시 및 게시 작업은 수행하지 않았습니다.

## 동기화 당시 검증 결과

2026-11-22 최신 upstream 동기화 및 검증 결과입니다. 이전 Pages 점검에서 보고된 21개 코드 블록 오류는 한국어판의 Bash 활성화 명령이 원문과 달랐기 때문입니다. 원문의 `source .venv/bin/activate`를 복원하고 Windows Git Bash용 설명은 유지했습니다.

- 번들 검증기: 29개 Markdown 파일 통과. 새 가상 환경을 만들지 않고 실행했습니다.
- 구조: 파일명, 상대 경로, 제목 수준, 번호 단계 및 YAML front matter 대응 확인.
- 코드 및 입력값: 원문 코드 블록과 인라인 입력값의 순서 및 내용 보존 확인.
- 이미지 및 링크: 원문 대상 경로 보존, 로컬 대상 및 미러 자산 존재 확인.
- 미러 자산: 이미지 3개와 리소스 공급자 목록 1개의 SHA-256이 원본과 일치.
- 프롬프트: 영문과 한국어 `prompt` 블록 4쌍 유지, 한국어 분류 프롬프트의 `invoice`, `contract`, `memo` 범주 보존.
- 영문 원본: `Instructions`의 모든 파일이 기준 upstream의 `instructions` Git blob과 바이트 단위로 일치.
- 신규 실습: upstream `finished` 클라이언트가 `os.environ`을 직접 읽는 것을 확인하여 환경 변수 로드 안내를 유지했습니다. 다운로드 ZIP 2개도 기준 upstream에 존재합니다.
- CLI: 신규 실습의 로그인, 공급자 등록, 확장 설치 및 그룹 삭제 구문을 Azure CLI 도구로 확인했습니다. 로그인하거나 클라우드 리소스를 생성하지 않았습니다.
- 에디터 진단: 기존 App Configuration·Key Vault 문서 등에 Markdown lint 경고가 남아 있습니다. 언어 없는 공통 명령 펜스, 셸 레이블 바로 아래의 펜스, 굵은 문제 해결 소제목 등 원문 및 저장소 문서 규칙과 충돌하는 일반 규칙은 이번 현지화에서 임의로 바꾸지 않았습니다.
- 게시: 이번 동기화에서는 커밋, 푸시 또는 Pages 게시를 수행하지 않았습니다.

## 검증 체크리스트

- [x] 영문과 한국어 Markdown 상대 경로가 모두 대응하는가?
- [x] YAML과 제목 구조가 유지되었는가?
- [x] 번호가 지정된 단계 구조가 유지되었는가?
- [x] 이미지와 링크 대상 경로가 유지되었는가?
- [x] 참조되는 이미지와 필수 자산이 한국어 디렉터리에 존재하는가?
- [x] 원문의 코드 내용과 실행 단계가 보존되고, 승인된 인접 셸 쌍만 PowerShell 우선으로 배치되었는가?
- [x] 영문과 한국어 프롬프트를 각각 복사할 수 있는가?
- [x] 기술 식별자, 식 및 종속 데이터가 변경되지 않았는가?
- [x] 기존 영문 원본과 관련 없는 파일이 변경되지 않았는가?

## GitHub Pages

| 항목 | 값 |
| --- | --- |
| 사이트 URL | `https://hahaysh.github.io/mslearn-azure-ai-kr/` |
| 게시 방식 | GitHub Actions의 `pages.yml` 워크플로 |
| 게시 소스 | `main` 브랜치의 저장소 루트(`/`) |
| 검증 커밋 | `554c8f32665bf722cd787e91c2780c8c3da09df2` |
| 워크플로 실행 | `36310706415` |
| 검증일 | `2026-09-27` |
| 검증 결과 | 빌드 및 배포 성공, 루트·한국어 실습 27개·자산 4개 모두 HTTP 200 |

## 알려진 원문 문제

- 공통 터미널 안내 일부는 환경 변수를 다시 로드하는 절차를 변수를 다시 만드는 명령으로 표현합니다. 원문의 표현에서 비롯된 문제이므로 이번 한국어 교정에서 절차를 임의로 변경하지 않았습니다.
- `cosmosdb/04-persisent-agent-memory.md`: 실습 파일명의 `persisent`와 다운로드 ZIP 이름의 `persistant`는 원문 철자를 그대로 유지합니다. 링크 및 파일 대응을 위해 임의로 고치지 않습니다.
- `app-sec-config/01-aks-retrieve-secrets.md`: 파일명은 AKS를 나타내지만 실습 내용은 Azure Key Vault 비밀 관리입니다.
- `azure-container-apps/02-aca-manage-containers.md`: PowerShell 코드 펜스 하나가 닫히지 않아 뒤의 설명과 Bash 블록을 포함합니다. 번역본은 보이는 한국어 콘텐츠와 별도로 원본 블록을 Jekyll Liquid 주석 안에 보존합니다.
- `azure-database-postgresql/02-implement-vector-search.md`: 설명에서는 임베딩 차원을 384로 안내하지만 테이블 정의는 `vector(330)`을 사용합니다.
- `azure-kubernetes-service/02-aks-configure-container.md`: 설명과 주석은 Secret 값을 base64로 인코딩한다고 안내하지만 매니페스트는 평문을 받는 `stringData`를 사용합니다.
- `cosmosdb/01-build-rag-document-store.md`: 가상 환경은 `.venv`로 만들지만 문제 해결의 PowerShell 활성화 경로는 `.\venv\Scripts\Activate.ps1`입니다.
- `integrate-services/02-eventgrid-publish-receive-events.md`: `all_events` 결과의 `event_type`에 이벤트 유형 대신 `modelName`을 할당합니다.
- `integrate-services/03-azure-functions-mcp-server.md`: Microsoft Learn 문서 링크 하나가 루트 상대 경로 `/azure/azure-functions/functions-bindings-mcp`를 사용합니다. 원문 경로를 보존했으며 GitHub Pages에서는 호스트 루트 링크로 해석됩니다.
