---
lab:
    topic: 앱 계측 및 관찰
    title: 'OpenTelemetry SDK로 앱 계측'
    description: 'OpenTelemetry로 애플리케이션을 계측하고, 사용자 지정 스팬과 특성을 만들며, Application Insights로 원격 분석을 내보내고, 트랜잭션 검색과 로그 쿼리를 사용하여 성능 문제를 진단하는 방법을 알아봅니다.'
    level: 300
    duration: 25
    islab: true
---

# OpenTelemetry로 앱 계측

OpenTelemetry는 애플리케이션에서 추적, 메트릭 및 로그를 수집하는 표준화된 방법을 제공하는 오픈 소스 관찰 가능성 프레임워크입니다. Azure Monitor OpenTelemetry Distro는 OpenTelemetry SDK를 Azure Monitor 내보내기 도구와 함께 패키징하므로 Python 애플리케이션에서 최소한의 구성으로 Application Insights에 원격 분석을 보낼 수 있습니다. 사용자 지정 스팬을 사용하면 애플리케이션별 작업을 추적하고 비즈니스 컨텍스트로 추적 데이터를 보강하는 특성을 추가할 수 있습니다.

이 연습에서는 Application Insights 리소스를 배포하고 문서 처리 파이프라인에 OpenTelemetry 계측을 보여 주는 Python Flask 웹 애플리케이션을 빌드합니다. Azure Monitor OpenTelemetry Distro를 구성하고, 각 파이프라인 단계에 사용자 지정 부모 및 자식 스팬을 만들고, 문서 메타데이터를 캡처하도록 스팬 특성을 추가합니다. 그런 다음 Azure portal에서 트랜잭션 검색(Transaction search)과 로그 쿼리를 사용하여 원격 분석을 확인하고 시뮬레이션된 지연 병목 현상을 진단합니다.

이 연습에서 수행하는 작업은 다음과 같습니다.

- 프로젝트 스타터 파일 다운로드
- Application Insights 리소스 만들기
- 앱을 완성하기 위해 스타터 파일에 코드 추가
- 앱을 실행하고 Application Insights에서 성능 문제 진단

이 연습을 완료하는 데 약 **25**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 스타터 파일 다운로드 및 Application Insights 배포

이 섹션에서는 앱의 스타터 파일을 다운로드하고 스크립트를 사용하여 구독에 Application Insights 리소스를 배포합니다.

1. 브라우저를 열고 다음 URL을 입력하여 스타터 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/instrument-app-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder)...**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위에 있는 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 부분은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 연습에 필요한 리소스 공급자가 등록되었는지 확인합니다.

    ```
    az provider register --namespace Microsoft.Insights
    az provider register --namespace Microsoft.OperationalInsights
    ```

1. 다음 명령을 실행하여 Application Insights CLI 확장을 추가합니다. 이 확장은 배포 스크립트에서 Application Insights 리소스를 만들고 관리하는 데 사용하는 명령을 제공합니다.

    ```
    az extension add --name application-insights
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Application Insights** 옵션을 시작합니다.

    이 옵션은 리소스 그룹이 아직 없는 경우 만들고 Application Insights 리소스를 만듭니다.

1. **2**를 입력하여 **2. Assign role** 옵션을 실행합니다. 이 옵션은 앱에서 Microsoft Entra 인증을 사용하여 Application Insights에 원격 분석을 게시할 수 있도록 계정에 Monitoring Metrics Publisher 역할을 할당합니다.

1. **3**을 입력하여 **3. Check deployment status** 옵션을 실행합니다. 계속하기 전에 Application Insights 리소스가 **Succeeded**로 표시되고 역할이 할당되었는지 확인합니다. 리소스 프로비전이 아직 진행 중이면 잠시 기다렸다가 다시 확인합니다.

1. **4**를 입력하여 **4. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 앱에 필요한 Application Insights 연결 문자열과 **OTEL_SERVICE_NAME** 변수가 포함된 환경 변수 파일을 만듭니다.

1. **5**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드하는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 로드하기 위해 이 명령을 다시 실행해야 합니다.

## 앱 완성

이 섹션에서는 *telemetry_functions.py* 파일에 코드를 추가하여 OpenTelemetry 계측 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수를 호출하고 결과를 브라우저에 표시합니다. 연습 후반부에 앱을 실행합니다.

1. 코드를 추가하려면 *client/telemetry_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 같은 위치에 맞춰야 합니다.

### 원격 분석 구성 코드 추가

이 섹션에서는 애플리케이션이 Application Insights로 추적을 내보내도록 Azure Monitor OpenTelemetry Distro를 구성하는 코드를 추가합니다. 함수는 환경 변수에서 연결 문자열을 읽고, Microsoft Entra 인증을 위해 **DefaultAzureCredential**을 만들며, Azure Monitor 내보내기 도구를 구성합니다. 앱은 로컬에서 실행되므로 자격 증명에서 관리 ID 공급자를 제외합니다. 이 설정이 없으면 자격 증명 체인이 원격 분석을 내보낼 때마다 Azure Instance Metadata Service에 연결을 시도하고, 실패한 HTTP 호출이 Application Map에 불필요하게 표시됩니다.

이 함수는 Azure Monitor OpenTelemetry Distro 패키지의 **configure_azure_monitor()**를 호출합니다. 이 단일 호출은 Azure Monitor 추적 내보내기 도구로 OpenTelemetry SDK를 구성하고 Flask 요청의 자동 계측을 설정합니다. **credential** 매개 변수는 Entra 기반 인증을 사용하도록 하여 앱이 계측 키 대신 Monitoring Metrics Publisher 역할로 원격 분석을 게시하도록 합니다. 배포 스크립트가 *.env* 파일에 설정하는 **OTEL_SERVICE_NAME** 환경 변수는 Application Map에 표시되는 **cloud.role.name**을 제어합니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 같은 들여쓰기 수준에 코드를 붙여 넣습니다. 블록의 위치가 맞지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN CONFIGURE TELEMETRY FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def configure_telemetry():
        """Configure the Azure Monitor OpenTelemetry Distro."""
        connection_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")

        if not connection_string:
            raise ValueError(
                "APPLICATIONINSIGHTS_CONNECTION_STRING environment variable must be set"
            )

        from azure.monitor.opentelemetry import configure_azure_monitor

        credential = DefaultAzureCredential(
            exclude_managed_identity_credential=True
        )

        configure_azure_monitor(
            connection_string=connection_string,
            credential=credential,
        )
    ```

1. 잠시 시간을 내어 코드를 검토합니다.

### 문서 처리 코드 추가

이 섹션에서는 일괄 문서 처리 작업을 위한 부모 스팬을 만드는 코드를 추가합니다. 함수는 구성 가능한 문서 수만큼 반복하면서 각 문서에 대해 유효성 검사, 보강 및 저장의 세 가지 자식 스팬 함수를 호출합니다.

이 함수는 **start_as_current_span()**을 사용하여 전체 일괄 처리를 감싸는 "process-documents"라는 부모 스팬을 만듭니다. 각 자식 함수는 자체 스팬을 만들며, 이 스팬은 현재 스팬의 자식이 되어 계층적 추적 트리를 구성합니다. 스팬 특성에는 일괄 처리 크기와 성공적으로 처리된 문서 수가 기록됩니다.

1. **# BEGIN PROCESS DOCUMENTS FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def process_documents(doc_count):
        """Process a batch of documents through the pipeline with tracing."""
        tracer = get_tracer()
        results = []

        with tracer.start_as_current_span("process-documents") as parent_span:
            parent_span.set_attribute("document.count", doc_count)
            parent_span.set_attribute("pipeline.name", "document-processing")

            for i in range(1, doc_count + 1):
                doc_id = f"DOC-{i:04d}"

                validate_result = validate_document(doc_id)
                enrich_result = enrich_document(doc_id)
                store_result = store_document(doc_id)

                results.append({
                    "doc_id": doc_id,
                    "validate": validate_result,
                    "enrich": enrich_result,
                    "store": store_result
                })

            parent_span.set_attribute("document.processed", len(results))

        return results
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 파이프라인 단계 추적 코드 추가

이 섹션에서는 각각 문서 파이프라인의 한 단계인 유효성 검사, 보강 및 저장을 위한 자식 스팬을 만드는 세 함수를 추가합니다. 세 함수는 모두 같은 패턴을 따릅니다. **start_as_current_span()**을 호출하여 활성 부모의 자식이 되는 스팬을 만든 다음, **set_attribute()**를 호출하여 검색 가능한 메타데이터를 연결하고 **set_status()**를 호출하여 결과를 표시합니다.

**enrich_document** 함수에는 의도적으로 지연 문제가 포함되어 있습니다. **DOC-0003** 및 **DOC-0005** 문서는 1.5~3초 지연을 겪어 외부 서비스 병목 현상을 시뮬레이션합니다. **enrichment.slow** 특성은 영향을 받은 스팬을 표시하므로 Application Insights에서 해당 스팬을 필터링할 수 있습니다. 뒤에서 종단 간 트랜잭션 뷰를 살펴볼 때 이 스팬이 파이프라인 지연의 원인으로 두드러지게 표시됩니다.

1. **# BEGIN PIPELINE STAGE FUNCTIONS** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def validate_document(doc_id):
        """Validate a document and record a traced span."""
        tracer = get_tracer()

        with tracer.start_as_current_span("validate-document") as span:
            span.set_attribute("document.id", doc_id)
            span.set_attribute("document.stage", "validate")

            # Simulate validation work
            time.sleep(random.uniform(0.05, 0.15))
            is_valid = True

            span.set_attribute("document.valid", is_valid)
            span.set_status(StatusCode.OK)

        return {"status": "valid", "duration_ms": round(random.uniform(50, 150))}


    def enrich_document(doc_id):
        """Enrich a document with metadata and record a traced span."""
        tracer = get_tracer()

        with tracer.start_as_current_span("enrich-document") as span:
            span.set_attribute("document.id", doc_id)
            span.set_attribute("document.stage", "enrich")

            # Simulated latency issue: documents DOC-0003 and DOC-0005
            # experience high latency during enrichment, representing
            # a bottleneck for the student to diagnose in Application Insights
            if doc_id in ("DOC-0003", "DOC-0005"):
                delay = random.uniform(1.5, 3.0)
                span.set_attribute("enrichment.slow", True)
            else:
                delay = random.uniform(0.05, 0.2)
                span.set_attribute("enrichment.slow", False)

            time.sleep(delay)
            span.set_attribute("enrichment.duration_s", round(delay, 3))
            span.set_status(StatusCode.OK)

        return {
            "status": "enriched",
            "duration_ms": round(delay * 1000),
            "slow": doc_id in ("DOC-0003", "DOC-0005")
        }


    def store_document(doc_id):
        """Store a document and record a traced span."""
        tracer = get_tracer()

        with tracer.start_as_current_span("store-document") as span:
            span.set_attribute("document.id", doc_id)
            span.set_attribute("document.stage", "store")
            span.set_attribute("storage.type", "blob")

            # Simulate storage write
            time.sleep(random.uniform(0.05, 0.2))

            span.set_status(StatusCode.OK)

        return {"status": "stored", "duration_ms": round(random.uniform(50, 200))}
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

## Python 환경 구성

이 섹션에서는 클라이언트 앱 디렉터리로 이동하고 Python 환경을 만든 다음 종속성을 설치합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 Python 환경을 만듭니다.

    ```
    python -m venv .venv
    ```

1. 다음 명령을 실행하여 Python 환경을 활성화합니다. **참고:** Linux/macOS에서는 Bash 명령을 사용합니다. Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

1. VS Code 터미널에서 다음 명령을 실행하여 종속성을 설치합니다.

    ```
    pip install -r requirements.txt
    ```

## 앱 실행

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 원격 분석을 생성한 다음 Azure portal의 트랜잭션 검색과 로그 쿼리를 사용하여 스팬을 확인하고 시뮬레이션된 성능 병목 현상을 진단합니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 앞서 설명한 환경 활성화 명령을 참조합니다. *client* 디렉터리에서 다른 위치로 이동했다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 창에서 **원격 분석 상태 확인(Check Telemetry Status)**을 선택합니다. 원격 분석 상태가 **active**로 표시되고 리소스 특성에 **service.name** 값인 **document-pipeline-app**이 포함되어 있는지 확인합니다. 이는 Azure Monitor OpenTelemetry Distro가 구성되어 원격 분석을 내보내고 있음을 확인합니다.

1. 왼쪽 창에서 **문서 처리(Process Documents)**를 선택합니다. 파이프라인을 통해 문서 5개를 처리하고 결과를 표에 표시합니다. **DOC-0003** 및 **DOC-0005** 문서는 보강 시간이 훨씬 길고 **SLOW** 태그가 표시되는 반면, 다른 문서는 빠르게 완료되는 점에 주목합니다.

1. **문서 처리(Process Documents)**를 두 번 더 선택하여 원격 분석 데이터를 추가로 생성합니다. 각 실행은 부모 및 자식 스팬이 포함된 새 추적을 만듭니다.

1. 원격 분석이 Application Insights에 도착할 때까지 2~3분 기다립니다. 원격 분석은 일괄 처리되어 주기적으로 전송되므로 portal에 데이터가 표시되기까지 잠시 지연될 수 있습니다.

1. [Azure portal](https://portal.azure.com)로 이동하여 앞에서 만든 리소스 그룹에서 Application Insights 리소스를 찾습니다.

### 종단 간 트랜잭션 보기

1. Application Insights 리소스의 **조사(Investigate)** 아래 왼쪽 탐색 메뉴에서 **검색(Search)**을 선택합니다. 이 뷰에는 들어오는 모든 요청과 관련 원격 분석이 나열됩니다.

1. 결과 목록에서 **POST /process-documents** 항목 중 하나를 찾아 선택합니다. 종단 간 트랜잭션 뷰가 열리고 루트 HTTP 요청 스팬, "process-documents" 부모 스팬, 각 파이프라인 단계(validate, enrich, store)의 자식 스팬 등 전체 스팬 계층이 표시됩니다.

1. 트랜잭션 타임라인에서 지속 시간이 1.5초 이상인 "enrich-document" 스팬을 찾습니다. 이 스팬은 시뮬레이션된 지연이 발생하는 **DOC-0003** 및 **DOC-0005** 문서에 해당합니다. 이 스팬 중 하나를 선택하여 **document.id**, **document.stage**, **enrichment.slow = True** 등의 특성을 확인합니다.

### KQL로 원격 분석 쿼리

1. Application Insights 리소스의 **모니터링(Monitoring)** 아래 왼쪽 탐색 메뉴에서 **로그(Logs)**를 선택합니다. 표시되는 쿼리 템플릿 대화 상자를 닫습니다. **참고:** 쿼리 표시줄의 드롭다운 선택기에서 **KQL 모드(KQL mode)**를 선택해야 합니다.

1. 다음 쿼리를 복사하여 쿼리 편집기에 붙여 넣고 **실행(Run)**을 선택합니다. 이 쿼리는 코드에서 만든 사용자 지정 스팬과 설정한 스팬 특성을 검색합니다.

    ```kusto
    dependencies
    | where timestamp > ago(1h)
    | project timestamp, name, duration,
        documentId = customDimensions["document.id"],
        stage = customDimensions["document.stage"],
        slow = customDimensions["enrichment.slow"]
    | order by timestamp desc
    ```

1. 결과를 검토합니다. 코드에서 추가한 **documentId** 및 **stage** 특성과 함께 각 파이프라인 단계인 validate-document, enrich-document, store-document의 행이 표시됩니다. **slow** 열은 DOC-0003 및 DOC-0005 행에서 **True**를 표시합니다.

1. 다음 쿼리를 복사하여 붙여 넣고 느린 보강 스팬과 빠른 보강 스팬의 평균 지속 시간을 비교합니다.

    ```kusto
    dependencies
    | where timestamp > ago(1h) and name == "enrich-document"
    | extend slow = tostring(customDimensions["enrichment.slow"])
    | summarize avgDuration = round(avg(duration), 0) by slow
    ```

1. 결과를 검토합니다. **True** 행의 평균 지속 시간은 1,500밀리초 이상이고 **False** 행은 200밀리초 미만입니다. 이를 통해 보강 단계가 병목 현상이며 스팬 특성으로 영향을 받는 문서를 명확히 식별할 수 있음을 확인합니다.

## 리소스 정리

연습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 연습 앞부분에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그 안에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택한 경우 이 연습 범위를 벗어나는 기존 리소스도 삭제됩니다.

## 문제 해결

이 연습을 완료하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Application Insights 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Application Insights 리소스의 **프로비전 상태(Provisioning State)**가 **Succeeded**인지 확인합니다.

**연결 문자열 확인**
- 배포 스크립트의 **Check deployment status** 옵션을 실행하여 리소스가 성공적으로 만들어졌는지 확인합니다.
- *.env* 및 *.env.ps1* 파일 모두에 **APPLICATIONINSIGHTS_CONNECTION_STRING** 값이 포함되어 있는지 확인합니다.
- 연결 문자열이 없으면 **Retrieve connection info** 옵션을 다시 실행합니다.

**코드 완성도 및 들여쓰기 확인**
- *telemetry_functions.py*의 각 코드 블록이 적절한 BEGIN/END 주석 표시 사이의 올바른 섹션에 추가되었는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 그리고 모든 코드의 위치가 올바른지 확인합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **APPLICATIONINSIGHTS_CONNECTION_STRING** 값이 포함되어 있는지 확인합니다.
- Bash에서 **source .env**를 실행하거나 PowerShell에서 **. .\.env.ps1**를 실행하여 환경 변수를 터미널 세션에 로드합니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- Azure portal에서 역할 할당을 확인하거나 배포 스크립트의 역할 할당 옵션을 다시 실행하여 Monitoring Metrics Publisher 역할이 계정에 할당되었는지 확인합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
- **azure-monitor-opentelemetry**가 설치되지 않았다면 **pip install -r requirements.txt**를 다시 실행합니다.
