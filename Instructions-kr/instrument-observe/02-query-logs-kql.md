---
lab:
  topic: 앱 계측 및 관찰
  title: KQL로 로그 쿼리
  description: Application Insights에서 KQL을 사용하여 요청, 예외 및 종속성을 쿼리하고 Azure CLI로 예약된 쿼리 경고 규칙을 만드는 방법을 알아봅니다.
  level: 300
  duration: 20
  islab: true
  primarytopics:
    - Azure
---

# KQL로 로그 쿼리

Kusto 쿼리 언어(KQL)는 Application Insights에서 로그 데이터를 분석하는 데 사용하는 쿼리 언어입니다. KQL 쿼리를 사용하면 요청, 종속성 및 예외와 같은 원격 분석 테이블을 필터링하고 집계하며 조인하여 애플리케이션 상태와 성능을 진단할 수 있습니다. Application Insights의 로그(Logs) 블레이드는 자동 완성, 시각적 결과 및 시간 범위 제어 기능을 갖춘 대화형 쿼리 편집기를 제공하므로 원격 분석 조사에 주로 사용됩니다. Azure CLI로 만드는 예약된 쿼리 경고 규칙과 KQL을 함께 사용하면 실패율이나 대기 시간이 허용 가능한 임계값을 초과할 때 팀에 알리는 사전 모니터링을 구현할 수 있습니다.

이 연습에서는 Application Insights 리소스를 배포하고 OpenTelemetry를 사용하여 샘플 요청, 종속성 및 예외 원격 분석을 생성하는 Python 스크립트를 실행한 다음 Azure portal의 로그 블레이드에서 KQL 쿼리를 작성하여 애플리케이션 상태를 조사합니다. requests 테이블을 쿼리하여 실패를 식별하고, 예외와 요청을 조인하여 오류를 연관시키며, 백분위수 계산으로 종속성 대기 시간을 분석하고, Azure CLI를 사용하여 작업 그룹과 로그 검색 경고 규칙을 만듭니다.

이 연습에서 수행하는 작업은 다음과 같습니다.

- 프로젝트 스타터 파일 다운로드
- Application Insights 리소스 만들기
- 원격 분석 생성기를 실행하여 샘플 데이터 만들기
- Azure portal에서 KQL로 원격 분석 쿼리
- Azure CLI로 작업 그룹 및 경고 규칙 만들기

이 연습을 완료하는 데 약 **20**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)

## 프로젝트 스타터 파일 다운로드 및 Application Insights 배포

이 섹션에서는 앱의 스타터 파일을 다운로드하고 스크립트를 사용하여 구독에 Application Insights 리소스를 배포합니다.

1. 브라우저를 열고 다음 URL을 입력하여 스타터 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/analyze-logs-python.zip
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

1. 다음 명령을 실행하여 이 연습에서 사용하는 Azure CLI 확장을 추가합니다. **application-insights** 확장은 배포 스크립트에서 Application Insights 리소스를 만들고 관리하는 데 사용하는 명령을 제공합니다. **scheduled-query** 확장은 뒤에서 로그 검색 경고 규칙을 만드는 데 사용하는 명령을 제공합니다.

    ```
    az extension add --name application-insights
    az extension add --name scheduled-query
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Application Insights** 옵션을 시작합니다.

    이 옵션은 리소스 그룹이 아직 없는 경우 만들고 Application Insights 리소스를 만듭니다.

1. **2**를 입력하여 **2. Assign role** 옵션을 실행합니다. 이 옵션은 앱에서 Microsoft Entra 인증을 사용하여 Application Insights에 원격 분석을 게시할 수 있도록 계정에 Monitoring Metrics Publisher 역할을 할당합니다.

1. **3**을 입력하여 **3. Check deployment status** 옵션을 실행합니다. 계속하기 전에 Application Insights 리소스가 **Succeeded**로 표시되고 역할이 할당되었는지 확인합니다. 리소스 프로비전이 아직 진행 중이면 잠시 기다렸다가 다시 확인합니다.

1. **4**를 입력하여 **4. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 Application Insights 연결 문자열, 리소스 그룹 이름, Application Insights 이름, 앱과 CLI 명령에 필요한 리소스 ID가 포함된 환경 변수 파일을 만듭니다.

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

## 원격 분석 데이터 생성

이 섹션에서는 Python 환경을 설정하고 미리 작성된 원격 분석 생성기를 실행하여 Application Insights에 샘플 요청, 종속성 및 예외 데이터를 만든 다음 쿼리하기 전에 데이터가 도착할 때까지 기다립니다. 생성기 스크립트는 OpenTelemetry를 사용하여 Application Insights의 **requests**, **dependencies** 및 **exceptions** 테이블에 매핑되는 스팬을 만듭니다.

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

1. 다음 명령을 실행하여 종속성을 설치합니다.

    ```
    pip install -r requirements.txt
    ```

1. 다음 명령을 실행하여 원격 분석 생성기를 시작합니다.

    ```
    python app.py
    ```

1. 스크립트가 요청 스팬 15개, 종속성 스팬 12개 및 예외 스팬 5개를 생성한 다음 요약을 출력합니다. 스크립트가 완료될 때까지 기다립니다.

1. 스크립트를 두 번 더 실행하여 원격 분석 데이터를 추가로 생성합니다.

    ```
    python app.py
    ```

1. 원격 분석이 Application Insights에 도착할 때까지 2~3분 기다립니다. 원격 분석은 일괄 처리되어 주기적으로 전송되므로 데이터가 표시되기까지 잠시 지연될 수 있습니다.

## Azure portal에서 원격 분석 쿼리

이 섹션에서는 Application Insights의 로그 블레이드를 사용하여 생성한 원격 분석에 대해 KQL 쿼리를 실행합니다. 로그 블레이드는 자동 완성 기능이 있는 대화형 편집기, 표 형식의 결과 및 차트 렌더링을 제공합니다.

1. [Azure portal](https://portal.azure.com)로 이동하여 앞에서 만든 리소스 그룹에서 Application Insights 리소스를 찾습니다.

1. Application Insights 리소스의 **모니터링(Monitoring)** 아래 왼쪽 탐색 메뉴에서 **로그(Logs)**를 선택합니다. 표시되는 쿼리 템플릿 대화 상자를 닫습니다. **참고:** 쿼리 표시줄의 드롭다운 선택기에서 **KQL 모드(KQL mode)**를 선택해야 합니다.

### 실패한 요청 쿼리

1. 다음 쿼리를 복사하여 쿼리 편집기에 붙여 넣고 **실행(Run)**을 선택합니다. 이 쿼리는 **where** 연산자를 사용하여 실패한 요청만 requests 테이블에서 필터링한 다음 **summarize**를 사용하여 서비스 이름과 HTTP 상태 코드별로 그룹화합니다. **count()** 집계는 각 조합의 실패 수를 계산하고, **order by**는 결과를 정렬하여 가장 자주 발생한 실패를 먼저 표시합니다.

    ```kusto
    requests
    | where success == false
    | summarize failedCount = count() by cloud_RoleName, resultCode
    | order by failedCount desc
    ```

1. 결과를 검토합니다. api-gateway, doc-processor 및 auth-service 서비스의 행과 500 및 429 상태 코드가 표시됩니다. **failedCount** 열에는 각 조합에서 발생한 실패 수가 표시됩니다.

### 요청량 및 성능 쿼리

1. 다음 쿼리를 복사하여 쿼리 편집기에 붙여 넣고 **실행(Run)**을 선택합니다. 이 쿼리는 **bin(timestamp, 1h)**를 사용하여 요청을 한 시간 간격으로 분류하고 서비스 이름별로 그룹화합니다. 각 간격에서 총 요청 수, **avg()**를 사용한 평균 지속 시간, **percentile()**을 사용한 95번째 백분위수 지속 시간을 계산합니다. 95번째 백분위수는 요청의 95%가 완료된 응답 시간을 보여 주므로 꼬리 지연을 감지하는 데 유용합니다.

    ```kusto
    requests
    | summarize requestCount = count(),
        avgDuration = avg(duration),
        p95Duration = percentile(duration, 95)
        by bin(timestamp, 1h), cloud_RoleName
    | order by timestamp desc
    ```

1. 결과를 검토합니다. **p95Duration** 열은 가장 느린 5%의 요청이 경험한 응답 시간을 보여 줍니다. 평균 지속 시간과 95번째 백분위수를 비교합니다. 차이가 크면 대부분의 요청은 빠르지만 일부 요청은 상당한 지연을 겪는 서비스가 있음을 나타냅니다.

### 예외와 요청 조인

1. 다음 쿼리를 복사하여 쿼리 편집기에 붙여 넣고 **실행(Run)**을 선택합니다. 이 쿼리는 exceptions 테이블에서 시작하여 **join kind=inner**를 사용해 공유 **operation_Id** 필드를 통해 각 예외와 이를 유발한 요청을 일치시킵니다. 하위 쿼리 안의 **project**는 조인 전에 **name**을 **requestName**으로 바꿔 두 테이블에 모두 있는 **name** 열의 충돌을 방지합니다. 조인한 후 **summarize**는 결과를 요청 이름, 예외 유형 및 서비스별로 그룹화하고 각 조합에서 발생한 예외 수를 셉니다. **take 15** 연산자는 상위 15개 행으로 출력을 제한합니다.

    ```kusto
    exceptions
    | join kind=inner (requests | project requestName = name, operation_Id, cloud_RoleName) on operation_Id
    | summarize exceptionCount = count()
        by requestName, exceptionType = type, cloud_RoleName
    | order by exceptionCount desc
    | take 15
    ```

1. 결과를 검토합니다. 각 행에는 요청 이름, 예외 유형 및 서비스의 조합이 표시됩니다. 이 뷰를 사용하면 어떤 작업에서 오류가 가장 많이 발생하는지와 관련 예외 유형을 식별할 수 있습니다.

### 종속성 대기 시간 분석

1. 다음 쿼리를 복사하여 쿼리 편집기에 붙여 넣고 **실행(Run)**을 선택합니다. 이 쿼리는 애플리케이션에서 데이터베이스, API 및 기타 서비스로 보내는 아웃바운드 호출을 기록하는 **dependencies** 테이블을 읽습니다. 종속성 엔드포인트인 **target**과 HTTP 또는 SQL 등의 **type**별로 그룹화한 다음 호출 수, 평균 지속 시간, 50번째·95번째·99번째 백분위수 대기 시간을 계산합니다. 여러 백분위수를 비교하면 느린 응답이 일부 이상치인지 아니면 더 광범위한 패턴인지 확인할 수 있습니다.

    ```kusto
    dependencies
    | summarize callCount = count(),
        avgDuration = avg(duration),
        p50 = percentile(duration, 50),
        p95 = percentile(duration, 95),
        p99 = percentile(duration, 99)
        by target, type
    | order by p95 desc
    ```

1. 결과를 검토합니다. p50과 p95 값의 차이가 크면 대부분의 호출은 빠르지만 상당한 비율의 호출은 훨씬 오래 걸리는 등 성능이 일정하지 않음을 나타냅니다.

## 작업 그룹 및 경고 규칙 만들기

이 섹션에서는 Azure CLI를 사용하여 실패율이 임계값을 초과할 때 이를 감지하는 작업 그룹과 로그 검색 경고 규칙을 만듭니다.

1. VS Code 터미널에서 다음 명령을 실행하여 이메일 알림이 포함된 작업 그룹을 만듭니다. **ALERT_EMAIL** 변수는 배포 스크립트의 **Retrieve connection info** 옵션을 실행할 때 Azure 계정에서 가져온 값으로 채워집니다.

    **Bash**
    ```bash
    ACTION_GROUP_ID=$(az monitor action-group create \
        --resource-group $RESOURCE_GROUP \
        --name pipeline-alerts-ag \
        --short-name PipeAlert \
        --action email oncall-email $ALERT_EMAIL \
        --query id \
        --output tsv)
    ```

    **PowerShell**
    ```powershell
    $ACTION_GROUP_ID = az monitor action-group create `
        --resource-group $env:RESOURCE_GROUP `
        --name pipeline-alerts-ag `
        --short-name PipeAlert `
        --action email oncall-email $env:ALERT_EMAIL `
        --query id `
        --output tsv
    ```

    이 명령은 **pipeline-alerts-ag**라는 작업 그룹을 만들고 트리거 시 이메일 알림을 보낸 다음 해당 리소스 ID를 **ACTION_GROUP_ID** 변수에 저장합니다.

1. 다음 명령을 실행하여 실패한 요청을 Application Insights 리소스에서 모니터링하는 로그 검색 경고 규칙을 만듭니다. 규칙은 5분 동안 쿼리를 평가하며 실패한 요청이 10개를 초과하면 경고를 발생시킵니다.

    **Bash**
    ```bash
    az monitor scheduled-query create \
        --resource-group $RESOURCE_GROUP \
        --name high-failure-rate-alert \
        --scopes $APPINSIGHTS_RESOURCE_ID \
        --action-groups $ACTION_GROUP_ID \
        --condition "count 'FailedRequests' > 10" \
        --condition-query FailedRequests="requests | where success == false" \
        --evaluation-frequency 5m \
        --window-size 5m \
        --severity 1 \
        --description "Alert when more than 10 requests fail in a 5-minute window"
    ```

    **PowerShell**
    ```powershell
    az monitor scheduled-query create `
        --resource-group $env:RESOURCE_GROUP `
        --name high-failure-rate-alert `
        --scopes $env:APPINSIGHTS_RESOURCE_ID `
        --action-groups $ACTION_GROUP_ID `
        --condition "count 'FailedRequests' > 10" `
        --condition-query FailedRequests="requests | where success == false" `
        --evaluation-frequency 5m `
        --window-size 5m `
        --severity 1 `
        --description "Alert when more than 10 requests fail in a 5-minute window"
    ```

    심각도는 1(Error)로 설정하여 중대한 문제이지만 서비스 중단 수준은 아님을 나타냅니다. 경고가 발생하면 작업 그룹이 트리거되어 이메일을 보냅니다.

1. 다음 명령을 실행하여 경고 규칙이 만들어져 있고 사용하도록 설정되었는지 확인합니다.

    **Bash**
    ```bash
    az monitor scheduled-query show \
        --resource-group $RESOURCE_GROUP \
        --name high-failure-rate-alert \
        --query "{Name:name, Severity:severity, Enabled:enabled, Window:windowSize, Frequency:evaluationFrequency, Threshold:condition.failingPeriods}" \
        --output table
    ```

    **PowerShell**
    ```powershell
    az monitor scheduled-query show `
        --resource-group $env:RESOURCE_GROUP `
        --name high-failure-rate-alert `
        --query "{Name:name, Severity:severity, Enabled:enabled, Window:windowSize, Frequency:evaluationFrequency, Threshold:condition.failingPeriods}" `
        --output table
    ```

    **Enabled** 열에 **True**가 표시되고 심각도, 기간 및 빈도 값이 이전 단계에서 지정한 값과 일치하는지 확인합니다.

1. 다음 명령을 실행하여 리소스 그룹의 예약된 쿼리 경고 규칙을 모두 나열합니다.

    **Bash**
    ```bash
    az monitor scheduled-query list \
        --resource-group $RESOURCE_GROUP \
        --output table
    ```

    **PowerShell**
    ```powershell
    az monitor scheduled-query list `
        --resource-group $env:RESOURCE_GROUP `
        --output table
    ```

    **high-failure-rate-alert**라는 규칙 하나가 표시되어야 합니다. 실패한 요청을 포함한 원격 분석을 이미 생성했으므로 규칙은 5분 주기로 즉시 평가를 시작합니다. 기간 내 실패한 요청 수가 임계값을 초과하면 Azure Monitor가 경고를 발생시키고 작업 그룹이 지정한 이메일 주소로 알림을 보냅니다.

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
**연결 문자열 확인**
- 배포 스크립트의 **Check deployment status** 옵션을 실행하여 리소스가 성공적으로 만들어졌는지 확인합니다.
- *.env* 및 *.env.ps1* 파일 모두에 **APPLICATIONINSIGHTS_CONNECTION_STRING** 값이 포함되어 있는지 확인합니다.
- 연결 문자열이 없으면 **Retrieve connection info** 옵션을 다시 실행합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **APPLICATIONINSIGHTS_CONNECTION_STRING**, **RESOURCE_GROUP**, **APPINSIGHTS_NAME**, **APPINSIGHTS_RESOURCE_ID** 및 **ALERT_EMAIL** 값이 포함되어 있는지 확인합니다.
- Bash에서 **source .env**를 실행하거나 PowerShell에서 **. .\.env.ps1**를 실행하여 환경 변수를 터미널 세션에 로드합니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- Azure portal에서 역할 할당을 확인하거나 배포 스크립트의 역할 할당 옵션을 다시 실행하여 Monitoring Metrics Publisher 역할이 계정에 할당되었는지 확인합니다.

**Python 환경 및 종속성 확인**
- 스크립트를 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
- **azure-monitor-opentelemetry**가 설치되지 않았다면 **pip install -r requirements.txt**를 다시 실행합니다.

**쿼리 결과에 원격 분석이 표시되지 않음**
- 스크립트에서 원격 분석을 보낸 후 표시되기까지 2~5분 정도 걸릴 수 있습니다. 기다렸다가 로그 블레이드에서 **실행(Run)**을 다시 선택합니다.
- Application Insights 리소스의 **개요(Overview)** 페이지에서 보이는 값과 연결 문자열이 올바른지 비교하여 확인합니다.
- VS Code 터미널 출력에서 원격 분석 내보내기와 관련된 오류를 확인합니다.
- 쿼리 결과가 비어 있으면 로그 블레이드의 시간 선택기를 사용하여 시간 범위를 늘립니다(예: **지난 1시간(Last 1 hour)**에서 **지난 4시간(Last 4 hours)**으로 변경).

**경고 규칙 만들기 실패**
- **az extension add --name scheduled-query**를 실행하여 **scheduled-query** 확장이 설치되었는지 확인합니다.
- **echo $APPINSIGHTS_RESOURCE_ID**를 실행하여 **APPINSIGHTS_RESOURCE_ID** 환경 변수에 유효한 리소스 ID가 있는지 확인합니다.
- 명령에 미리 보기 확장이 필요한 경우 먼저 **az config set extension.dynamic_install_allow_preview=true**를 실행합니다.
