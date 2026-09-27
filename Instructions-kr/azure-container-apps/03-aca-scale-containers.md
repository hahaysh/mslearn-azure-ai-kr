---
lab:
  topic: Azure Container Apps
  title: KEDA를 사용하여 API 자동 크기 조정 구성
  description: HTTP 동시성 트리거를 사용하여 Azure Container Apps에서 KEDA 기반 자동 크기 조정을 구성하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Container Apps
---

# KEDA 트리거를 사용하여 자동 크기 조정 구성

AI 애플리케이션은 추론 요청 급증, 일괄 작업 또는 에이전트 기반 워크플로의 갑작스러운 트래픽 증가처럼 예측하기 어려운 워크로드를 자주 경험합니다. Azure Container Apps의 KEDA 기반 자동 크기 조정을 사용하면 워크로드가 유휴 상태일 때 인스턴스를 0개까지 축소하여 비용을 절감하고, 수요가 증가하면 빠르게 확장할 수 있습니다.

이 연습에서는 간단한 모의 에이전트 API를 배포하고 **HTTP 동시 요청**을 기준으로 자동 크기 조정을 구성합니다. 그런 다음 동시 부하를 생성하고 앱의 확장 및 구성 변경 적용 시 새 리비전이 생성되는 것을 관찰합니다.

이 연습에서 수행하는 작업:

- Azure Container Registry 및 Container Apps 리소스 만들기
- 모의 에이전트 API 컨테이너 앱 배포
- KEDA를 사용하여 HTTP 동시성 크기 조정 규칙 구성
- 동시 요청을 생성하여 확장을 트리거하고 복제본 수 변경을 실시간으로 모니터링
- YAML을 사용하여 크기 조정 규칙 구성

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**Important:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시 중지되어 있습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비저닝할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상
- **선택 사항:** YAML 언어 지원, 유효성 검사 및 서식을 제공하는 [Visual Studio Code용 YAML 확장](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure Container Registry와 Container Apps 환경을 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aca-scale-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 Azure CLI에 **containerapp** 확장이 있는지 확인합니다.

    ```azurecli
    az extension add --name containerapp
    az extension add --name log-analytics
    ```

1. 다음 명령을 실행하여 구독에 연습에 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.App
    az provider register --namespace Microsoft.OperationalInsights
    az provider register --namespace Microsoft.ContainerRegistry
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 Azure 구독에 필요한 서비스를 배포합니다.

1. 프로젝트의 루트 디렉터리에 있는지 확인하고 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다. 스크립트는 ACR, Container Apps 환경 및 수신이 활성화된 Container App을 배포합니다. 또한 연습 전반에서 사용할 환경 변수 파일도 만듭니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행 중이면 **1**을 입력하여 **Azure Container Registry 만들기 및 컨테이너 이미지 빌드(Create Azure Container Registry and build container image)**를 시작합니다.

1. 이전 작업이 완료되면 **2**를 입력하여 **Container Apps 환경 만들기(Create Container Apps environment)**를 시작합니다.

1. 이전 작업이 완료되면 **3**을 입력하여 **Container App 만들기(Create Container App)**를 시작합니다.

    >**Note:** 컨테이너 앱이 만들어진 후 환경 변수가 들어 있는 파일이 생성됩니다. 이 변수는 연습 전반에서 사용합니다.

1. 배포가 완료되면 **5**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션으로 불러오는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

1. 앱 엔드포인트에 연결할 수 있는지 확인합니다.

   **Bash**
    ```bash
    curl -sS "$CONTAINER_APP_URL/" | head
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod "$env:CONTAINER_APP_URL/"
    ```

    >**Note:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

## 자동 크기 조정 구성

이 섹션에서는 **동시 요청**을 기준으로 크기 조정을 트리거하는 HTTP 크기 조정 규칙을 구성합니다. 다른 Azure 서비스를 추가하지 않고도 “진행 중인 에이전트 요청”을 파악하는 데 유용한 방법입니다.

>**Note:** 크기 조정 변경을 포함하여 구성을 업데이트하면 **새 리비전**이 만들어집니다.

1. 다음 명령을 실행하여 HTTP 크기 조정 규칙으로 컨테이너 앱을 업데이트합니다. 이 규칙은 처리 중인 동시 요청을 모니터링하고 수요가 증가하면 앱을 확장합니다.

    **Bash**
    ```bash
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --min-replicas 0 \
        --max-replicas 10 \
        --scale-rule-name http-scaling \
        --scale-rule-type http \
        --scale-rule-http-concurrency 10
    ```

    **PowerShell**
    ```powershell
    az containerapp update `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --min-replicas 0 `
        --max-replicas 10 `
        --scale-rule-name http-scaling `
        --scale-rule-type http `
        --scale-rule-http-concurrency 10
    ```

1. 다음 명령을 실행하여 크기 조정 규칙이 구성되었는지 확인합니다. 출력에서 **minReplicas**가 **0**이고 **maxReplicas**가 **10**으로 설정된 **http-scaling** 규칙을 찾습니다.

    **Bash**
    ```bash
    az containerapp show \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.template.scale"
    ```

    **PowerShell**
    ```powershell
    az containerapp show `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --query "properties.template.scale"
    ```

## 부하 생성 및 크기 조정 관찰

이 섹션에서는 동시 요청을 생성하고 Container App 리비전 및 복제본을 표시하는 로컬 Flask 대시보드를 실행합니다.

1. 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 클라이언트 앱용 가상 환경을 만듭니다. 환경에 따라 명령은 **python** 또는 **python3**일 수 있습니다.

    ```python
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

1. 다음 명령을 실행하여 클라이언트 앱의 종속성을 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

1. 다음 명령을 실행하여 대시보드를 시작합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 다음 URL로 이동합니다. `http://127.0.0.1:5000`.

1. 앱의 왼쪽 창에서 **리비전 및 복제본 새로 고침(Refresh Revisions & Replicas)**을 선택합니다. 앱의 오른쪽 위에 실행 중인 복제본 수로 **1** 또는 **0**이 표시됩니다.

    앱을 배포했을 때 기본값은 실행 중인 복제본 **1**개였습니다. 이전 단계에서 KEDA 크기 조정 규칙을 적용했으며, 워크로드가 유휴 상태가 된 뒤 기본 **300초(5분)**의 쿨다운 기간이 지나야 0개로 축소될 수 있습니다. 따라서 축소까지 추가로 **~5분**이 걸릴 수 있습니다.

1. **부하 생성기(Load Generator)** 섹션에서 **시작(Start)**을 선택하여 컨테이너 앱으로 데이터를 보내기 시작합니다.

1. 5~10초마다 **리비전 및 복제본 새로 고침(Refresh Revisions & Replicas)**을 선택하면 복제본 수가 증가하는 것을 볼 수 있습니다. **부하 생성기(Load Generator)**가 중지된 후 다시 실행하여 트래픽과 복제본 수를 더 늘릴 수 있습니다.

작업을 마치면 브라우저 창을 닫고 터미널에서 **Ctrl+c**를 입력하여 클라이언트 앱을 종료합니다.

## YAML을 사용하여 크기 조정 규칙 구성

이 섹션에서는 Container App YAML을 편집하여 자동 크기 조정을 구성합니다. 크기 조정 규칙을 관리하는 반복 가능한 방법이며, 여러 규칙이 있을 때 특히 중요합니다.

1. 다음 명령을 실행하여 앱 구성을 YAML 파일로 내보냅니다.

    **Bash**
    ```bash
    az containerapp show \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --output yaml > app-config.yaml
    ```

    **PowerShell**
    ```powershell
    az containerapp show `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --output yaml > app-config.yaml
    ```

1. VS Code에서 *app-config.yaml* 파일을 엽니다. **properties > template** 아래의 **scale** 섹션을 찾습니다. 크기 조정 구성을 수정하여 **cooldownPeriod**를 **200**초(더 빠른 축소)로 줄이고, **maxReplicas**를 **5**로 설정하고, 앱에 항상 복제본이 하나 이상 실행되도록 **minReplicas**를 **1**로 설정합니다. **scale** 섹션은 다음 예제와 비슷해야 합니다.

    ```yaml
    scale:
      cooldownPeriod: 200
      maxReplicas: 5
      minReplicas: 1
      pollingInterval: 30
    ```

1. 파일을 저장하고 다음 명령을 실행하여 업데이트된 구성을 적용합니다.

    **Bash**
    ```bash
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yaml app-config.yaml
    ```

    **PowerShell**
    ```powershell
    az containerapp update `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --yaml app-config.yaml
    ```

1. 다음 명령을 실행하여 방금 적용한 변경 사항을 확인합니다.

    **Bash**
    ```bash
    az containerapp show \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.template.scale"
    ```

    **PowerShell**
    ```powershell
    az containerapp show `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --query "properties.template.scale"
    ```

# 리소스 정리

이제 연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 앞에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **CAUTION:** 리소스 그룹을 삭제하면 그 안에 포함된 모든 리소스가 삭제됩니다. 기존 리소스 그룹을 선택한 경우 연습 범위를 벗어난 기존 리소스도 삭제됩니다.

## 문제 해결

연습 중 문제가 발생하면 다음 단계를 시도합니다.

**앱이 부하에 따라 확장되지 않음**
- HTTP 크기 조정 규칙이 구성되었는지 확인합니다. **az containerapp show --query "properties.template.scale"**
- 동시 요청을 생성하고 있는지 확인합니다(지연 시간이 0보다 큰 대시보드 사용).
- 요청이 겹쳐 동시성이 누적되도록 **delayMs**를 늘립니다(500~1500ms).
- 시스템 로그에서 크기 조정 이벤트를 확인합니다. **az containerapp logs show --type system --tail 50**

**대시보드가 시작되지 않거나 리비전/복제본을 나열할 수 없음**
- Python 가상 환경이 활성화되어 있는지 확인합니다(터미널 프롬프트에 **(.venv)**가 표시되어야 합니다).
- 종속성이 설치되어 있는지 확인합니다. **pip install -r client/requirements.txt**
- Azure CLI가 설치되어 있고 **az login**을 실행했는지 확인합니다.
- **containerapp** 확장이 설치되어 있는지 확인합니다. **az extension add --name containerapp**
- **.env**가 로드되어 있고 **RESOURCE_GROUP** 및 **CONTAINER_APP_NAME**이 포함되어 있는지 확인합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 다음을 사용합니다. **source client/.venv/bin/activate**
- Windows PowerShell에서는 다음을 사용합니다. **.\client\.venv\Scripts\Activate.ps1**
- **activate** 스크립트가 없으면 **python3-venv** 패키지를 다시 설치하고 venv를 다시 만듭니다.

**YAML 업데이트 실패**
- YAML 파일 구문이 올바른지 확인합니다(들여쓰기 확인).
- **id**, **systemData**, **type**과 같은 일부 읽기 전용 속성 때문에 오류가 발생할 수 있습니다. 필요한 경우 해당 속성을 제거합니다.
- scale 섹션이 **properties > template > scale** 아래의 올바른 구조를 따르는지 확인합니다.
