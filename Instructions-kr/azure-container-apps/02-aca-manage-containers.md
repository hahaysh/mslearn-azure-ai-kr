---
lab:
  topic: Azure Container Apps
  title: 실패한 배포 진단 및 수정
  description: 누락된 환경 변수, 잘못 구성된 수신, Log Analytics를 사용한 기록 로그 쿼리를 진단하여 Azure Container Apps 문제를 해결하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Container Apps
---

# 실패한 배포 진단 및 수정

이 실습에서는 실패한 컨테이너 앱의 문제를 해결하고 필요한 부분을 수정합니다. 리비전 상태, 로그, Azure CLI를 사용하여 배포 문제를 분리해 진단합니다. 모델과 종속성을 업데이트할 때 시작 동작이 자주 바뀌므로 AI 솔루션에서 흔히 사용하는 워크플로입니다.

이 실습에서 수행하는 작업:

- 모의 AI 문서 처리 API를 컨테이너 앱으로 배포합니다.
- 누락된 환경 변수 오류를 발생시키고 진단합니다.
- 수신 구성 문제를 발생시키고 진단합니다.
- 기록 문제 해결 데이터를 위해 Log Analytics를 쿼리합니다.

이 실습을 완료하는 데 약 **30**분이 걸립니다.

>**중요:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시 중지되어 있습니다. 이 실습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure Container Registry 및 Container Apps 환경을 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aca-manage-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일을 폴더에 압축 해제합니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder)...**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 상단의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 항목은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 메시지가 표시되면 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 Azure CLI에 **containerapp** 확장이 있는지 확인합니다.

    ```azurecli
    az extension add --name containerapp
    az extension add --name log-analytics
    ```

1. 다음 명령을 실행하여 구독에 실습에 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.App
    az provider register --namespace Microsoft.OperationalInsights
    az provider register --namespace Microsoft.ContainerRegistry
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 Azure 구독에 필요한 서비스를 배포합니다.

1. 프로젝트의 루트 디렉터리에 있는지 확인하고 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다. 배포 스크립트는 ACR을 배포하고 실습에 필요한 환경 변수 파일을 만듭니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **Azure Container Registry 만들기 및 컨테이너 이미지 빌드(Create Azure Container Registry and build container image)** 옵션을 시작합니다. 이 옵션은 ACR 서비스를 만들고 ACR Tasks를 사용하여 이미지를 빌드한 후 레지스트리에 푸시합니다.

1. 이전 작업이 완료되면 **2**를 입력하여 **Container Apps 환경 만들기(Create Container Apps environment)** 옵션을 시작합니다. 컨테이너를 배포하려면 먼저 환경을 만들어야 합니다.

1. 이전 작업이 완료되면 **3**을 입력하여 **컨테이너 앱 배포 및 비밀 구성(Deploy the container app and configure secrets)** 옵션을 시작합니다.

    >**참고:** 컨테이너 앱을 만든 후 환경 변수가 포함된 파일이 생성됩니다. 실습 전체에서 이 변수를 사용합니다.

1. 이전 작업이 완료되면 **5**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드하는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

1. 다음 명령을 실행하여 앱 FQDN을 가져와 변수에 저장합니다.

    **Bash**
    ```bash
    FQDN=$(az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --query properties.configuration.ingress.fqdn -o tsv)

    echo "$FQDN"
    ```

    **PowerShell**
    ```powershell
    $FQDN = az containerapp show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --query properties.configuration.ingress.fqdn -o tsv

    Write-Output $FQDN
    ```

1. 다음 명령을 실행하여 기본 엔드포인트를 호출하고 앱이 실행 중인지 확인합니다. 명령은 JSON을 반환해야 합니다. **model.name** 필드를 확인하면 **gpt-5.4-mini**로 설정되어 있어야 합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/"
    ```

## 누락된 환경 변수 진단

컨테이너 앱이 설정되지 않은 환경 변수에 의존하면 앱이 시작되지 않거나 예상과 다르게 동작할 수 있습니다. 이 섹션에서는 필수 환경 변수를 제거하고 증상을 확인합니다.

1. 다음 명령을 실행하여 컨테이너 앱에서 `MODEL_NAME` 환경 변수를 제거합니다.

    **Bash**
    ```bash
    az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --remove-env-vars MODEL_NAME
    ```

    **PowerShell**
    ```powershell
    az containerapp update -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --remove-env-vars MODEL_NAME
    ```

1. 다음 명령을 실행하여 리비전을 나열하고 새 리비전이 만들어졌는지 확인합니다. 접미사 번호가 더 큰 새 리비전(예: **ai-api--0000002**)과 모든 트래픽을 받음을 나타내는 **TrafficWeight** 값 **100**을 찾습니다.

    **Bash**
    ```bash
    az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
    ```

    **PowerShell**
    ```powershell
    az containerapp revision list -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP -o table
    ```

1. 다음 명령을 실행하여 루트 엔드포인트를 확인하고 API 소비자 관점에서 증상을 관찰합니다. 이제 **model.name** 필드에는 구성된 값 대신 기본값인 **not-configured**가 표시됩니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/" | jq .model
    ```

    **PowerShell**
<!-- 원문의 미종료 PowerShell 펜스를 동기화 검증용으로 보존합니다.
    ```powershell
    (Invoke-RestMethod -Uri "https://$FQDN/").model

1. Run the following command to diagnose the root cause by viewing the container app's configuration. Run the following command to confirm the **MODEL_NAME** environment variable is missing.

    **Bash**
    ```bash
    az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --query "properties.template.containers[0].env" -o table
    ```
-->
    ```powershell
    (Invoke-RestMethod -Uri "https://$FQDN/").model

1. 다음 명령을 실행하여 컨테이너 앱의 구성을 확인하고 근본 원인을 진단합니다. 다음 명령을 실행하여 **MODEL_NAME** 환경 변수가 없는지 확인합니다.

    **Bash**
    ```bash
    az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --query "properties.template.containers[0].env" -o table
    ```

    **PowerShell**
    ```powershell
    az containerapp show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --query "properties.template.containers[0].env" -o table
    ```

1. 다음 명령을 실행하여 `MODEL_NAME` 환경 변수를 다시 추가하고 문제를 해결합니다.

    **Bash**
    ```bash
    az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --set-env-vars MODEL_NAME=$MODEL_NAME
    ```

    **PowerShell**
    ```powershell
    az containerapp update -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --set-env-vars MODEL_NAME=$env:MODEL_NAME
    ```

1. 다음 명령을 실행하여 루트 엔드포인트를 다시 확인하고 수정 사항을 검증합니다. 이를 통해 API 소비자 관점에서 애플리케이션이 올바르게 동작하는지 확인합니다. 응답에 구성된 모델 이름이 표시되어야 합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/" | jq .model
    ```

    **PowerShell**
    ```powershell
    (Invoke-RestMethod -Uri "https://$FQDN/").model
    ```

누락된 환경 변수를 진단하고 수정했습니다. 다음으로 비밀 문제와 인그레스 구성 문제를 진단합니다.

## 인그레스 구성 문제 진단

Container Apps는 **target-port** 설정을 사용하여 컨테이너로 트래픽을 라우팅합니다. 포트가 애플리케이션이 수신 대기하는 포트와 일치하지 않으면 요청이 실패합니다. 이 섹션에서는 포트 불일치를 발생시킵니다.

1. 다음 명령을 실행하여 컨테이너 앱이 잘못된 대상 포트를 사용하도록 업데이트합니다.

    **Bash**
    ```bash
    az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --target-port 3000
    ```

    **PowerShell**
    ```powershell
    az containerapp ingress update -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --target-port 3000
    ```

1. 다음 명령을 실행하여 상태 엔드포인트에 액세스하고 API 소비자 관점에서 증상을 확인합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/health"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/health"
    ```

    Container Apps가 트래픽을 포트 3000으로 라우팅하지만 애플리케이션은 포트 8000에서 수신 대기하므로 요청이 실패하거나 시간 초과됩니다.

1. 다음 명령을 실행하여 현재 인그레스 구성을 확인하고 근본 원인을 진단합니다. **targetPort**가 3000으로 설정되어 있는지 확인합니다.

    **Bash**
    ```bash
    az containerapp show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --query "properties.configuration.ingress" -o yaml
    ```

    **PowerShell**
    ```powershell
    az containerapp show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --query "properties.configuration.ingress" -o yaml
    ```

1. 다음 명령을 실행하여 애플리케이션이 실행 중인지 컨테이너 로그를 확인합니다. 앱이 포트 8000에서 수신 중임을 나타내는 gunicorn 시작 메시지가 보여야 하며, 이로써 포트 불일치를 확인할 수 있습니다.

    **Bash**
    ```bash
    az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
    ```

    **PowerShell**
    ```powershell
    az containerapp logs show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP
    ```

1. 다음 명령을 실행하여 올바른 대상 포트로 설정하고 인그레스 구성을 수정합니다.

    **Bash**
    ```bash
    az containerapp ingress update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --target-port 8000
    ```

    **PowerShell**
    ```powershell
    az containerapp ingress update -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --target-port 8000
    ```

1. 다음 명령을 실행하여 상태 엔드포인트를 호출하고 수정 사항을 확인합니다. 이를 통해 API 소비자 관점에서 애플리케이션에 액세스할 수 있는지 확인합니다. **{"status":"healthy"}**가 표시되어야 합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/health"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/health"
    ```

인그레스 구성 문제를 진단하고 수정했습니다. 다음으로 기록 로그를 쿼리하는 방법을 알아봅니다.

## 기록 문제 해결을 위해 Log Analytics 쿼리

**az containerapp logs show**로 표시되는 콘솔 로그는 최근 항목만 보여 줍니다. 기록 문제 해결을 위해 로그는 Container Apps 환경과 연결된 Log Analytics 작업 영역에 유지됩니다.

1. 다음 명령을 실행하여 Container Apps 환경에서 Log Analytics 작업 영역 ID를 가져옵니다.

    **Bash**
    ```bash
    WORKSPACE_ID=$(az containerapp env show -n $ACA_ENVIRONMENT -g $RESOURCE_GROUP \
        --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv)

    echo "Workspace ID: $WORKSPACE_ID"
    ```

    **PowerShell**
    ```powershell
    $WORKSPACE_ID = az containerapp env show -n $env:ACA_ENVIRONMENT -g $env:RESOURCE_GROUP `
        --query properties.appLogsConfiguration.logAnalyticsConfiguration.customerId -o tsv

    Write-Output "Workspace ID: $WORKSPACE_ID"
    ```

1. 다음 명령을 실행하여 컨테이너 앱의 콘솔 로그를 쿼리합니다. 타임스탬프와 메시지를 보여 주는 최근 로그 항목 20개를 반환합니다.

    **Bash**
    ```bash
    az monitor log-analytics query -w $WORKSPACE_ID \
        --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' | project TimeGenerated, Log_s | order by TimeGenerated desc | take 20" \
        -o table
    ```

    **PowerShell**
    ```powershell
    az monitor log-analytics query -w $WORKSPACE_ID `
        --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$env:CONTAINER_APP_NAME' | project TimeGenerated, Log_s | order by TimeGenerated desc | take 20" `
        -o table
    ```

    > [!NOTE]
    > 이벤트가 발생한 후 Log Analytics 데이터가 표시되기까지 몇 분 정도 걸릴 수 있습니다. 최근 로그가 보이지 않으면 몇 분 기다렸다가 다시 시도합니다.

1. 다음 명령을 실행하여 오류 수준 로그만 쿼리합니다.

    **Bash**
    ```bash
    az monitor log-analytics query -w $WORKSPACE_ID \
        --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$CONTAINER_APP_NAME' and Log_s contains 'error' | order by TimeGenerated desc | take 20" \
        -o table
    ```

    **PowerShell**
    ```powershell
    az monitor log-analytics query -w $WORKSPACE_ID `
        --analytics-query "ContainerAppConsoleLogs_CL | where ContainerAppName_s == '$env:CONTAINER_APP_NAME' and Log_s contains 'error' | order by TimeGenerated desc | take 20" `
        -o table
    ```

이러한 쿼리를 사용하면 컨테이너가 다시 시작되거나 리비전이 변경된 후에도 과거에 발생한 문제를 조사할 수 있습니다.

## 리소스 정리

실습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 앞에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 포함된 모든 리소스가 삭제됩니다. 이 실습의 기존 리소스 그룹을 선택했다면 실습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

실습 중 문제가 발생하면 다음 단계를 시도합니다.

**컨테이너 앱이 응답하지 않음**
- **az containerapp revision list**를 사용하여 리비전이 활성 상태인지 확인합니다.
- **az containerapp show**를 사용하여 인그레스가 구성되었는지 확인합니다.

**로그가 보이지 않음**
- 콘솔 로그는 최근 항목만 표시합니다. 기록 데이터를 보려면 Log Analytics를 사용합니다.
- Log Analytics 데이터가 표시되는 데 2~5분 정도 걸릴 수 있습니다.

**환경 변수가 적용되지 않음**
- 환경 변수를 변경하면 Container Apps는 새 리비전을 만듭니다. 새 리비전이 활성 상태인지 확인합니다.
- 모든 환경 변수를 지정된 값으로 바꾸므로 **--replace-env-vars**를 주의해서 사용합니다.
