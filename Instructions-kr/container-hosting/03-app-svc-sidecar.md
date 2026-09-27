---
lab:
    topic: '컨테이너 호스팅'
    title: '로컬 모델 제공 사이드카를 사용하여 AI API 배포'
    description: '채팅 API와 로컬 Phi-3 모델 사이드카를 Azure App Service에 배포한 다음 로컬 Flask 클라이언트로 애플리케이션을 테스트합니다.'
    level: 300
    duration: 30
---

# 로컬 모델 제공 사이드카를 사용하여 AI API 배포

이 연습에서는 Python 채팅 API를 기본 App Service 컨테이너로 배포하고 로컬 모델 서버를 사이드카로 배포합니다. 배포 스크립트는 두 이미지를 Azure Container Registry에서 빌드합니다. 별도의 Flask 클라이언트는 개발 컴퓨터에서 실행되어 공개 채팅 API를 호출합니다. 관리 ID 이미지 가져오기, `localhost` 통신, 공유 임시 볼륨 및 컨테이너별 진단을 구성합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Container Registry를 배포하고 ACR Tasks를 사용하여 채팅 API 및 모델 서버 이미지 빌드
- 관리 ID 이미지 가져오기가 사용하도록 설정된 App Service 계획 및 사이드카 지원 웹앱 배포
- 기본 컨테이너 및 사이드카 컨테이너 구성을 정의하고 적용
- 모델 사이드카 준비 상태 및 공유 볼륨 액세스 확인
- 로컬 Flask 클라이언트용 Python 환경 구성
- 채팅 클라이언트를 실행하고 엔드투엔드 모델 추론 테스트

이 연습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

이 연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상

## 프로젝트 시작 파일 다운로드 및 Azure 리소스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 배포 스크립트를 실행합니다. 스크립트는 리소스 그룹, Azure Container Registry, 두 컨테이너 이미지, 레지스트리에서 **AcrPull** 역할을 부여받은 사용자 할당 관리 ID, App Service 계획 및 ID가 생성 시 연결된 사이드카 지원 웹앱을 만듭니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/app-svc-sidecar-python.zip
    ```

1. 다운로드한 파일을 작업 폴더로 복사하거나 이동한 다음 압축을 풉니다.

1. 압축을 푼 폴더를 Visual Studio Code에서 엽니다.

1. 1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 마세요.

1. Visual Studio Code에서 새 터미널을 엽니다.

1. 다음 명령을 실행하여 Azure에 로그인합니다. 이 명령은 Azure CLI를 인증하고 연습 리소스를 만들 구독을 선택할 수 있게 합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 연습에서 사용하는 Azure 리소스 공급자를 등록합니다. 등록하면 구독에서 Azure Container Registry 및 App Service 리소스를 만들 수 있습니다.

    ```
    az provider register --namespace Microsoft.ContainerRegistry
    az provider register --namespace Microsoft.Web
    ```

1. 다음 명령을 실행하여 배포 스크립트를 시작합니다. 스크립트는 필요한 순서로 연습 리소스를 프로비전하는 메뉴를 제공합니다.

    ```
    python azdeploy.py
    ```

1. **1**을 입력하여 **Create Azure Container Registry and build both images**를 선택합니다. 이 옵션은 레지스트리를 만들고 해당 인증-as-ARM 정책에서 관리 ID 이미지 가져오기를 지원하는지 확인한 다음 ACR Tasks를 사용하여 채팅 API와 Phi-3 모델 서버 이미지를 빌드하고 푸시합니다.

    첫 모델 서버 빌드는 약 2.7GB의 Phi-3 CPU INT4 모델을 다운로드하므로 5~10분 정도 걸릴 수 있습니다. 두 빌드가 모두 끝날 때까지 터미널을 열어 둡니다. 배포가 실패하면 **문제 해결** 섹션을 확인합니다.

1. **2**를 입력하여 **Create user-assigned managed identity and assign AcrPull**을 선택합니다. 이 옵션은 사용자 할당 관리 ID를 만들고 레지스트리에 **AcrPull** 역할을 부여하여 App Service가 프라이빗 이미지를 가져올 수 있게 합니다.

1. **3**을 입력하여 **Create App Service resources with the managed identity attached**를 선택합니다. 이 옵션은 사용자 할당 관리 ID가 생성 시 연결된 App Service 계획과 사이드카 지원 웹앱을 만들고, 준비 작업 중 모델 준비 상태 작업을 기다리도록 App Service를 구성하고, 레지스트리 이름과 ID의 클라이언트 ID를 사용하여 *sitecontainers-spec.json*을 만들고, 리소스 값을 *.env* 및 *.env.ps1*에 씁니다.

1. **4**를 입력하여 **Check deployment status**를 선택합니다. 레지스트리, 두 이미지, 관리 ID, AcrPull 할당, 계획 및 웹앱을 모두 사용할 수 있는지 확인합니다.

1. **5**를 입력하여 배포 스크립트를 종료합니다.

1. Bash에서 리소스 값을 로드하려면 다음 명령을 실행합니다. 이 명령은 *.env*의 값을 내보내어 나머지 Azure CLI 명령과 로컬 클라이언트에서 사용할 수 있게 합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

기본 API는 포트 **8080**, 모델 서버는 포트 **11434**를 사용합니다. 기본 API는 **MODEL_ENDPOINT**를 읽고 **http://localhost:11434**를 통해 사이드카에 추론 요청을 보냅니다. **isMain**을 **true**로 설정한 컨테이너를 정의하고 적용하기 전에는 웹앱이 채팅 API를 제공하지 않습니다.

## 기본 컨테이너 및 사이드카 컨테이너 정의

이 섹션에서는 배포 스크립트가 생성한 *sitecontainers-spec.json* 파일에 정의된 기본 채팅 API 컨테이너와 Phi-3 모델 사이드카를 검토한 다음 사이드카 지원 웹앱에 사양을 적용합니다. 기본 API는 포트 **8080**에서 외부 트래픽을 받고 모델 서버는 포트 **11434**에서 내부 통신만 수행합니다. 두 컨테이너 모두 동일한 사용자 할당 관리 ID를 사용하여 프라이빗 이미지를 가져옵니다.

프로젝트에는 레지스트리 이름과 ID 클라이언트 ID의 자리 표시자가 포함된 *sitecontainers-spec.template.json*이 있습니다. 배포 스크립트는 이 템플릿을 유지하고 레지스트리 이름과 클라이언트 ID를 사용하여 *sitecontainers-spec.json*을 생성하지만 사양을 적용하지는 않습니다. 이 섹션에서는 생성된 구성을 검토한 후 두 컨테이너를 배포합니다.

1. Visual Studio Code에서 *sitecontainers-spec.json*을 엽니다.

1. **chat-api** 컨테이너 정의를 검토하고 다음 설정을 확인합니다.

    - **image**는 Azure Container Registry의 **chat-api:v1** 이미지를 가리킵니다.
    - **targetPort**는 **8080**이며, 이는 외부 App Service 트래픽을 받는 지원 포트입니다.
    - **isMain**은 **true**이며, 이 컨테이너를 공개 애플리케이션으로 지정합니다.
    - **authType**은 **UserAssigned**이며, App Service가 사용자 할당 관리 ID를 사용하여 이미지를 가져오도록 지정합니다.
    - **userManagedIdentityClientId**는 레지스트리에서 **AcrPull** 역할을 가진 공유 사용자 할당 관리 ID의 클라이언트 ID입니다.

1. **model-server** 컨테이너 정의를 검토하고 다음 설정을 확인합니다.

    - **image**는 Azure Container Registry의 **model-server:v1** 이미지를 가리킵니다.
    - **targetPort**는 **11434**이고 **isMain**은 **false**이므로 모델 서버는 내부 사이드카로 유지됩니다.
    - 컨테이너는 기본 API와 동일한 사용자 할당 관리 ID를 사용하여 이미지를 가져옵니다.

1. 다음 명령을 실행하여 기본 컨테이너와 사이드카 컨테이너 정의를 적용합니다. 이 작업은 공개 채팅 API와 내부 모델 사이드카 간의 런타임 관계를 만들고 최초 컨테이너 가져오기를 시작합니다.

    **Bash**
    ```bash
    az webapp sitecontainers create \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --sitecontainers-spec-file ./sitecontainers-spec.json
    ```

    **PowerShell**
    ```powershell
    az webapp sitecontainers create `
        --name $env:APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --sitecontainers-spec-file ./sitecontainers-spec.json
    ```

1. 다음 명령을 실행하여 저장된 컨테이너 정의를 확인합니다. App Service가 두 컨테이너를 할당된 역할 및 대상 포트와 함께 저장했는지 확인합니다.

    **Bash**
    ```bash
    az webapp sitecontainers list \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --output table
    ```

    **PowerShell**
    ```powershell
    az webapp sitecontainers list `
        --name $env:APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --output table
    ```

1. **chat-api**가 기본 컨테이너이고 **model-server**가 사이드카인지, 대상 포트가 서로 다른지, 두 정의가 모두 동일한 **userManagedIdentityClientId**를 사용하는 **UserAssigned** 인증으로 설정되었는지 확인합니다.

## 모델 사이드카 준비 상태 확인

이 섹션에서는 App Service가 두 이미지를 가져왔고 Phi-3 모델 사이드카가 로드를 마쳤는지 확인한 후 로컬 채팅 클라이언트를 시작합니다. 첫 컨테이너 시작에는 몇 분 정도 걸릴 수 있습니다.

1. 다음 명령을 실행하여 모델 서버 로그를 가져옵니다. 컨테이너별 로그를 사용하면 모델 로딩 및 시작 문제를 기본 API 오류와 구분할 수 있습니다.

    **Bash**
    ```bash
    az webapp sitecontainers log \
      --name "$APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --container-name model-server
    ```

    **PowerShell**
    ```powershell
    az webapp sitecontainers log `
      --name $env:APP_NAME `
      --resource-group $env:RESOURCE_GROUP `
      --container-name model-server
    ```

1. 로그에 모델이 성공적으로 로드되었다고 표시되고 모델 서버가 포트 **11434**에서 수신 대기하는지 확인합니다.

1. 다음 명령을 실행하여 API 준비 상태 작업을 호출합니다. 기본 API가 공유 네트워크 네임스페이스를 통해 모델 사이드카에 연결할 수 있는지 확인합니다. 응답에는 모델 구성이나 내부 경로를 노출하지 않고 로컬 모델 종속성을 사용할 수 있다고 표시되어야 합니다.

    **Bash**
    ```bash
    curl --fail-with-body "${CHAT_API_URL}/health/ready"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "$env:CHAT_API_URL/health/ready"
    ```

## 공유 볼륨 확인

이 섹션에서는 기본 API와 모델 사이드카가 App Service 기본 **/home** 공유 볼륨에 액세스하는지 확인합니다. Linux 웹앱의 모든 sitecontainers는 **/home** 볼륨을 자동으로 공유하므로 모델 서버는 모델을 로드한 뒤 **/home/models/manifest.json**에 작은 매니페스트를 기록하고 기본 API는 같은 파일을 읽습니다.

1. 다음 명령을 실행하여 민감하지 않은 모델 매니페스트 필드를 요청합니다. 응답이 성공하면 사이드카가 매니페스트를 기록했고 기본 API가 공유 **/home** 볼륨을 통해 읽었음을 확인할 수 있습니다.

    **Bash**
    ```bash
    curl --fail-with-body "${CHAT_API_URL}/model-info"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "$env:CHAT_API_URL/model-info"
    ```

1. 응답에 Microsoft Phi-3 Mini 모델, Microsoft ONNX Runtime GenAI, CPU INT4 양자화 및 준비 상태가 표시되는지 확인합니다.

App Service는 모든 sitecontainer 간에 **/home** 볼륨을 자동으로 공유하므로 사양에 **volumeMounts**를 정의할 필요가 없습니다. 사이드카가 시작할 때마다 매니페스트를 다시 만들 수 있으므로 이 볼륨은 영구적이지 않습니다. 다시 시작한 후에도 유지되거나 스케일 아웃 인스턴스 간에 공유되어야 하는 데이터는 영구 저장소에 보관해야 합니다.

## Python 환경 설정

이 섹션에서는 로컬 Flask 클라이언트에 필요한 Python 가상 환경을 만들고 종속성을 설치합니다. 클라이언트는 App Service 애플리케이션에 세 번째 컨테이너를 추가하지 않고 브라우저 채팅 환경을 제공합니다.

1. 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 Python 애플리케이션의 가상 환경을 만듭니다. 환경에 따라 **python** 또는 **python3** 명령을 사용할 수 있습니다.

    ```
    python -m venv .venv
    ```

1. 다음 명령을 실행하여 Python 환경을 활성화합니다.

    > **참고:** Linux/macOS에서는 Bash 명령을 사용합니다. Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

1. 다음 명령을 실행하여 Python 종속성을 설치합니다. 이 명령은 **flask** 및 **requests** 라이브러리를 설치합니다.

    ```
    pip install -r requirements.txt
    ```

이제 로컬 Flask 애플리케이션을 시작하여 Azure의 채팅 API 및 모델 사이드카와 통신합니다.

## 채팅 클라이언트 실행

이 섹션에서는 로컬 Flask 웹 애플리케이션을 시작하고 채팅 API 및 Phi-3 모델 사이드카를 통한 엔드투엔드 추론을 확인합니다. 클라이언트는 *.env* 또는 *.env.ps1*에서 로드한 **CHAT_API_URL** 값을 읽습니다.

1. 계속 *client* 디렉터리에 있고 가상 환경이 활성화되어 있는지 확인합니다. 터미널 프롬프트에 **(.venv)**가 표시되어야 합니다.

1. 다음 명령을 실행하여 Flask 애플리케이션을 시작합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://127.0.0.1:5000`으로 이동합니다.

1. 페이지에 **Model ready**가 표시되는지 확인한 다음 짧은 메시지를 보냅니다. 브라우저는 현재 탭에서 최근 사용자 및 어시스턴트 메시지를 최대 8개까지 유지하고, 제한된 대화 기록을 로컬 Flask 클라이언트를 통해 채팅 API로 보냅니다. 어느 서버도 이 기록을 저장하지 않으며 페이지를 다시 로드하면 기록이 지워집니다.

응답에서 몇 가지 경계를 확인할 수 있습니다. App Service는 외부 트래픽을 기본 컨테이너로 라우팅하고, 채팅 API는 **localhost:11434**에 연결하며, 모델 서버는 완성된 응답을 반환합니다.

## 리소스 정리

연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **\<rg-name>**을 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제를 백그라운드 작업으로 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **CAUTION:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습 범위에 속하지 않는 기존 리소스가 있는 리소스 그룹을 선택했다면 해당 리소스도 삭제됩니다.

## 문제 해결

연습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**리소스 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Azure Container Registry, App Service 계획 및 웹앱의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- sitecontainers 사양을 적용하기 전에 배포 스크립트의 **Check deployment status** 옵션을 실행하여 레지스트리, 두 컨테이너 이미지, 계획, 웹앱 및 관리 ID를 모두 사용할 수 있는지 확인합니다.

**배포 실패 해결**
- 옵션 1 또는 옵션 3이 실패하는 가장 일반적인 원인은 선택한 지역에서 컨테이너 레지스트리 또는 App Service 계획 SKU 용량이 일시적으로 부족한 것입니다.
- 스크립트를 종료하고 *azdeploy.py* 맨 위의 **location** 변수를 eastus2, australiaeast 또는 canadacentral과 같은 다른 지역으로 변경한 다음 스크립트를 다시 실행하고 실패한 옵션을 선택합니다.
- 실패한 리소스는 다음 시도 전에 자동으로 삭제됩니다.

**모델 서버 빌드 시간 초과 또는 실패**
- 첫 모델 서버 빌드는 약 2.7GB의 Phi-3 CPU INT4 모델을 다운로드하므로 5~10분 정도 걸릴 수 있습니다.
- 빌드가 진행 중 실패하는 경우 모델 다운로드 중의 네트워크 불안정이 가장 일반적인 원인입니다. 옵션 1을 다시 실행하여 재시도합니다.
- 두 번째 빌드도 계속 실패하면 Azure portal에서 레지스트리의 **Services** > **Tasks** > **Runs** 블레이드에 있는 ACR 빌드 로그를 확인하여 구체적인 오류를 찾습니다.

**관리 ID 이미지 가져오기에서 토큰 유효성 검사 실패 보고**
- App Service 관리 ID 이미지 가져오기를 사용하려면 레지스트리의 인증-as-ARM 정책을 사용하도록 설정해야 합니다. 옵션 1은 이미지를 빌드하기 전에 이 정책을 확인합니다.
- 스크립트에서 정책이 비활성화되었다고 보고하면 다음 명령을 실행하여 사용하도록 설정한 다음 옵션 1을 다시 실행합니다.

    **Bash**
    ```bash
    az acr config authentication-as-arm update \
        --registry "$ACR_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --status enabled
    ```

    **PowerShell**
    ```powershell
    az acr config authentication-as-arm update `
        --registry $env:ACR_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --status enabled
    ```

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **RESOURCE_GROUP**, **APP_NAME**, **ACR_NAME**, **CHAT_API_URL** 값이 포함되어 있는지 확인합니다.
- Azure CLI 명령이나 로컬 클라이언트를 실행하기 전에 Bash에서는 **source .env**, PowerShell에서는 **. .\.env.ps1**을 실행하여 터미널 세션에 환경 변수를 로드합니다.

**sitecontainers 사양 확인**
- *sitecontainers-spec.json*이 *azdeploy.py*와 같은 위치에 있는지, 각 **image** 필드의 레지스트리 이름이 사용자의 레지스트리(**$ACR_NAME.azurecr.io**)와 일치하는지 확인합니다.
- 파일이 없거나 **<registry-name>** 또는 **<managed-identity-client-id>** 자리 표시자가 남아 있으면 배포 스크립트에서 옵션 3을 실행하여 다시 생성합니다.
- **az webapp sitecontainers create**가 실패하면 **az webapp sitecontainers list --name $APP_NAME --resource-group $RESOURCE_GROUP --output table**을 실행하여 현재 저장된 정의를 확인합니다.

**채팅 API 준비 상태 검사에서 모델을 사용할 수 없다고 보고**
- **/health/ready** 작업은 모델 서버 사이드카가 Phi-3 로드를 마치고 공유 매니페스트를 기록한 후에만 모델 종속성을 사용 가능으로 보고합니다.
- **az webapp sitecontainers log --container-name model-server**로 모델 서버 로그를 가져와 모델이 성공적으로 로드되었다고 표시되는지, 모델 서버가 포트 **11434**에서 수신 대기하는지 확인합니다.
- 로그에 모델을 로드하는 중이라고 표시되면 몇 분 기다린 후 **/health/ready**를 다시 호출합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다. 터미널 프롬프트에 **(.venv)**가 표시되어야 합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
- 로컬 Flask 앱이 채팅 API에 연결할 수 없으면 **CHAT_API_URL**이 **https://\<your-app-name>.azurewebsites.net**을 가리키는지, 준비 상태 작업이 성공적인 응답을 반환하는지 확인합니다.
