---
lab:
  topic: 컨테이너 호스팅
  title: Azure App Service에 컨테이너 배포
  description: Azure Container Registry(ACR)의 컨테이너 이미지를 관리 ID를 사용하여 Azure App Service에 배포하고, 실행 중인 컨테이너를 확인하고 문제를 해결하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure App Service
    - Azure Container Registry
---

# Azure App Service에 컨테이너 배포

이 연습에서는 Azure Container Registry(ACR)의 Linux 컨테이너 이미지를 Azure App Service에 배포합니다. 웹앱이 앱 설정에 레지스트리 자격 증명을 저장하지 않고도 프라이빗 레지스트리에서 이미지를 가져올 수 있도록 시스템 할당 관리 ID와 **AcrPull** 역할을 구성합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Container Registry를 배포하고 ACR Tasks를 사용하여 컨테이너 이미지 빌드
- Linux 컨테이너용 App Service 계획 배포
- 관리 ID를 사용하여 ACR에서 이미지를 가져오도록 컨테이너용 Web App 만들기 및 구성
- 런타임 설정 구성 및 컨테이너 로깅 사용
- 배포 확인 및 문서 처리 엔드포인트 테스트

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**Important:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시적으로 중단되었습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

이 연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상


## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure Container Registry와 App Service 계획을 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/app-svc-container-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 내 위치로 복사하거나 이동합니다. 그런 다음 파일을 폴더에 압축 해제합니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **File > Open Folder...**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **Terminal > New Terminal**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 메시지가 표시되면 이 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 Azure Container Registry(ACR)와 Azure App Service에 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```
    az provider register --namespace Microsoft.ContainerRegistry
    az provider register --namespace Microsoft.Web
    ```

### Azure에 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 Azure 구독에 필요한 서비스를 배포합니다.

1. 프로젝트의 루트 디렉터리에 있는지 확인한 다음 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다. 배포 스크립트는 ACR을 배포하고 연습에 필요한 환경 변수 파일을 만듭니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Azure Container Registry and build container image** 옵션을 시작합니다. 이 옵션은 레지스트리 관리자 계정을 사용하지 않도록 설정한 상태로 ACR 서비스를 만든 다음 ACR Tasks를 사용하여 이미지를 빌드하고 레지스트리에 푸시합니다. 관리자 계정을 사용하지 않으면 공유 레지스트리 자격 증명을 사용하지 않으며, 웹앱이 관리 ID와 **AcrPull** 역할 대신 해당 자격 증명에 의존하지 않습니다.

1. 이전 작업이 완료되면 **2**를 입력하여 **Create App Service Plan** 옵션을 시작합니다. 이 옵션은 웹앱에 필요한 App Service 계획을 만듭니다.

    >**참고:** App Service 계획이 만들어진 후 환경 변수가 포함된 파일이 만들어집니다. 연습 전반에서 이 변수를 사용합니다.

1. 이전 작업이 완료되면 **4**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드하는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

## 웹앱 만들기

이 섹션에서는 CLI 명령으로 웹앱을 만든 다음 시스템 할당 관리 ID를 구성하여 앱이 ACR의 이미지에 액세스할 수 있도록 합니다.

1. 다음 명령을 실행하여 컨테이너 레지스트리에서 가져오도록 구성된 컨테이너용 Web App을 만듭니다.

    **Bash**
    ```bash
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_PLAN \
        --name $APP_NAME \
        --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1
    ```

    **PowerShell**
    ```powershell
    az webapp create `
        --resource-group $env:RESOURCE_GROUP `
        --plan $env:APP_PLAN `
        --name $env:APP_NAME `
        --container-image-name "$($env:ACR_NAME).azurecr.io/docprocessor:v1"
    ```

    기본적으로 Azure Container Registry는 프라이빗입니다. App Service가 이미지를 가져오려면 먼저 ACR에 인증해야 합니다.

    레지스트리 자격 증명을 앱 설정에 저장하는 대신 시스템 할당 관리 ID(권장)를 사용하여 인증을 구성합니다.

1. 다음 명령을 실행하여 웹앱에서 시스템 할당 관리 ID를 사용하도록 설정합니다.

    **Bash**
    ```bash
    az webapp identity assign \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME
    ```

    **PowerShell**
    ```powershell
    az webapp identity assign `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME
    ```

### 웹앱에 AcrPull 역할 할당

이 섹션에서는 웹앱이 프라이빗 레지스트리에서 이미지를 가져올 수 있는 권한을 부여합니다. 관리 ID는 Microsoft Entra 기반 ID이며 Azure가 만들고 관리합니다. 웹앱에서 시스템 할당 ID를 사용하도록 설정하면 App Service가 해당 ID로 토큰을 요청할 수 있습니다.

웹앱에서 해당 ID를 사용하여 이미지를 가져오도록 하려면 레지스트리 범위에 기본 제공 **AcrPull** 역할을 할당합니다. 이는 최소 권한 액세스 원칙을 따르므로 웹앱은 이미지를 다운로드할 수 있지만 레지스트리에 이미지를 푸시하거나 레지스트리를 관리할 수는 없습니다.

1. 다음 명령을 실행하여 웹앱의 주체 ID를 가져옵니다.

    **Bash**
    ```bash
    PRINCIPAL_ID=$(az webapp identity show \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --query principalId \
        --output tsv)
    ```

    **PowerShell**
    ```powershell
    $PRINCIPAL_ID = az webapp identity show `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --query principalId `
        --output tsv
    ```
1. 다음 명령을 실행하여 ACR ID를 가져옵니다.

    **Bash**
    ```bash
    ACR_ID=$(az acr show \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --query id \
        --output tsv)
    ```

    **PowerShell**
    ```powershell
    $ACR_ID = az acr show `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:ACR_NAME `
        --query id `
        --output tsv
    ```

1. 다음 명령을 실행하여 웹앱에 AcrPull 역할을 할당합니다.

    **Bash**
    ```bash
    az role assignment create \
        --assignee $PRINCIPAL_ID \
        --scope $ACR_ID \
        --role AcrPull
    ```

    **PowerShell**
    ```powershell
    az role assignment create `
        --assignee $PRINCIPAL_ID `
        --scope $ACR_ID `
        --role AcrPull
    ```

    >**참고:** 역할 할당이 전파되는 데 1~2분 정도 걸릴 수 있습니다. 이 단계 직후에도 앱이 이미지를 가져오지 못하면 잠시 기다린 후 다시 시도합니다.

1. 다음 명령을 실행하여 레지스트리 인증에 관리 ID를 사용하도록 웹앱을 구성합니다. 이 설정은 레지스트리에 액세스할 때 레지스트리 관리자 자격 증명 대신 웹앱의 관리 ID를 사용하도록 App Service에 지정합니다.

    **Bash**
    ```bash
    az webapp config set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --acr-use-identity true \
        --acr-identity [system]
    ```

    **PowerShell**
    ```powershell
    az webapp config set `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --acr-use-identity true `
        --acr-identity [system]
    ```

1. 다음 명령을 실행하여 관리 ID를 사용하는 레지스트리로 컨테이너 설정을 업데이트합니다. 이 단계에서는 웹앱이 사용할 이미지와 레지스트리 URL을 명시적으로 설정합니다. 나중에 이미지 태그를 업데이트하면 여기서 웹앱이 새 버전을 가리키도록 지정합니다.

    **Bash**
    ```bash
    az webapp config container set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --container-image-name $ACR_NAME.azurecr.io/docprocessor:v1 \
        --container-registry-url https://$ACR_NAME.azurecr.io
    ```

    **PowerShell**
    ```powershell
    az webapp config container set `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --container-image-name "$($env:ACR_NAME).azurecr.io/docprocessor:v1" `
        --container-registry-url "https://$($env:ACR_NAME).azurecr.io"
    ```

    >**참고:** 이 명령에서 자격 증명 조회 실패가 표시될 수 있습니다. 레지스트리 관리자 계정이 비활성화되어 있고 웹앱이 관리 ID를 사용하므로 무시해도 됩니다. 관리자 계정을 사용하도록 설정하지 마세요.

## 런타임 설정 구성 및 컨테이너 로깅 사용

이 섹션에서는 컨테이너가 더 안정적으로 실행되고 문제 해결에 도움이 되도록 런타임 설정을 구성하고 로깅을 사용하도록 설정합니다.

1. 다음 명령을 실행하여 컨테이너 포트를 구성합니다. 샘플 이미지는 포트 80(기본값)에서 수신 대기하므로 이 단계에서는 동작을 변경하지 않고 설정을 살펴봅니다.

    **Bash**
    ```bash
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --settings WEBSITES_PORT=80
    ```

    **PowerShell**
    ```powershell
    az webapp config appsettings set `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --settings WEBSITES_PORT=80
    ```

1. 다음 명령을 실행하여 처리된 문서의 영구 저장소를 사용하도록 설정합니다. 이 설정은 App Service 저장소 탑재를 활성화합니다(예: Linux 컨테이너의 **/home** 경로).

    **Bash**
    ```bash
    az webapp config appsettings set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
    ```

    **PowerShell**
    ```powershell
    az webapp config appsettings set `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --settings WEBSITES_ENABLE_APP_SERVICE_STORAGE=true
    ```

1. 다음 명령을 실행하여 항상 사용을 설정합니다. 항상 사용은 앱을 활성 상태로 유지하여 콜드 스타트 지연을 줄이는 데 도움이 됩니다.

    **Bash**
    ```bash
    az webapp config set \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --always-on true
    ```

    **PowerShell**
    ```powershell
    az webapp config set `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --always-on true
    ```

1. 다음 명령을 실행하여 컨테이너 로깅을 사용하도록 설정합니다. 이렇게 하면 컨테이너의 stdout/stderr가 캡처되어 CLI에서 로그를 볼 수 있습니다.

    **Bash**
    ```bash
    az webapp log config \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --docker-container-logging filesystem
    ```

    **PowerShell**
    ```powershell
    az webapp log config `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --docker-container-logging filesystem
    ```

## 배포 확인

이 섹션에서는 웹앱이 실행 중이며 응답하는지 확인합니다.

1. 다음 명령을 실행하여 웹앱 호스트 이름을 가져옵니다.

    **Bash**
    ```bash
    APP_URL=$(az webapp show \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --query defaultHostName \
        --output tsv)

    echo "Application URL: https://$APP_URL"
    ```

    **PowerShell**
    ```powershell
    $APP_URL = az webapp show `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --query defaultHostName `
        --output tsv

    Write-Host "Application URL: https://$APP_URL"
    ```

1. 브라우저에서 URL을 열어 애플리케이션이 응답하는지 확인합니다. 연습에서 나중에 다시 사용하므로 브라우저를 열어 둡니다. 애플리케이션은 실행 중임을 나타내는 응답을 반환해야 합니다. App Service가 컨테이너 이미지를 가져와 애플리케이션을 시작하는 동안 첫 요청은 더 오래 걸릴 수 있습니다.

## 문서 처리 테스트

이 섹션에서는 API에 요청을 보내 앱이 작동하고 결과가 영구 저장소에 기록되는지 확인합니다.

1. 다음 명령을 실행하여 프로젝트에 포함된 *document.txt* 파일을 처리 엔드포인트에 제출합니다.

    **Bash**
    ```bash
    curl -X POST "https://$APP_URL/process" \
        -H "Content-Type: text/plain" \
        --data-binary @document.txt
    ```

    **PowerShell**
    ```powershell
    $body = Get-Content -Raw -Path "document.txt"
    Invoke-RestMethod -Method Post -Uri "https://$APP_URL/process" -ContentType "text/plain" -Body $body | ConvertTo-Json -Depth 10
    ```

    API는 추출된 엔터티, 핵심 구문, 감정 분석을 포함한 모의 분석 결과를 반환합니다. 응답에 결과가 영구 저장소에 저장되었는지 표시되는지 확인합니다.

1. 다음 명령을 실행하여 처리된 모든 문서를 나열합니다.

    **Bash**
    ```bash
    curl https://$APP_URL/documents
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$APP_URL/documents" | ConvertTo-Json -Depth 10
    ```

    영구 저장소가 올바르게 사용되도록 설정되었다면 방금 처리한 문서가 목록에 표시됩니다.

## 컨테이너 로그 스트리밍

이 섹션에서는 시작 및 요청 처리 문제를 해결하는 데 도움이 되도록 컨테이너 로그를 스트리밍합니다.

1. 다음 명령을 실행하여 컨테이너의 실시간 로그를 확인합니다.

    **Bash**
    ```bash
    az webapp log tail \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME
    ```

    **PowerShell**
    ```powershell
    az webapp log tail `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME
    ```

1. 브라우저를 새로 고쳐 애플리케이션에 요청을 더 보냅니다. 스트림에 로그 항목이 표시되어야 합니다. Ctrl+C를 눌러 스트리밍을 중지합니다.

## 진단 콘솔 검사

이 섹션에서는 SCM(Kudu) 사이트를 열어 구성 보기와 일반적인 로그 위치를 검사합니다.

1. 다음 명령을 실행하여 SCM(Kudu) URL을 출력합니다.

    **Bash**
    ```bash
    echo "Kudu URL: https://$APP_NAME.scm.azurewebsites.net"
    ```

    **PowerShell**
    ```powershell
    Write-Host "Kudu URL: https://$($env:APP_NAME).scm.azurewebsites.net"
    ```

1. 브라우저에서 이 URL을 엽니다. 왼쪽 탐색 창에서 다음으로 이동합니다.

    1. **Environment(환경)**를 선택하여 환경 변수를 보고 앱 설정이 있는지 확인합니다.
    1. **SSH**를 확장한 다음 **Kudu**를 선택하여 브라우저 기반 셸을 엽니다.
    1. **File Manager(파일 관리자)**를 선택한 다음 **/home/LogFiles/**로 이동하여 로그 파일을 확인합니다.

    >**Tip:** 왼쪽 탐색 창에서 Logs를 확장하고 Log Stream을 선택하여 브라우저에서 로그를 볼 수도 있습니다. 또한 SSH 아래의 Application 항목을 사용하여 앱 컨테이너에 연결할 수 있습니다.

    SCM 사이트는 앱 컨테이너와 분리되어 있으므로 컨테이너의 파일 시스템이나 실행 중인 프로세스를 완전히 확인할 수는 없습니다.

## 애플리케이션 설정 보기

이 섹션에서는 구성한 앱 설정이 있는지 확인합니다.

1. 다음 명령을 실행하여 애플리케이션 설정을 나열합니다.

    **Bash**
    ```bash
    az webapp config appsettings list \
        --resource-group $RESOURCE_GROUP \
        --name $APP_NAME \
        --output table
    ```

    **PowerShell**
    ```powershell
    az webapp config appsettings list `
        --resource-group $env:RESOURCE_GROUP `
        --name $env:APP_NAME `
        --output table
    ```

    시스템에서 제공하는 설정과 함께 사용자가 설정한 값이 목록에 표시되는지 확인합니다.

## 리소스 정리

연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **\<rg-name>**을 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제를 백그라운드 작업으로 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **CAUTION:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습 범위에 속하지 않는 기존 리소스가 있는 리소스 그룹을 선택했다면 해당 리소스도 삭제됩니다.

## 문제 해결

연습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure 인증 및 환경 변수 확인**

- **az account show**를 실행하여 올바른 Azure 구독에 로그인했는지 확인합니다.
- **echo $ACR_NAME**(Bash) 또는 **$env:ACR_NAME**(PowerShell)을 실행하여 환경 변수가 설정되었는지 확인합니다.
- 변수가 비어 있으면 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 다시 실행합니다.

**ACR 배포 확인**

- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Azure Container Registry가 있고 **Provisioning State**가 **Succeeded**인지 확인합니다.
- **az acr list --output table**을 실행하여 레지스트리에 액세스할 수 있는지 확인합니다.

**빌드 실패 문제 해결**

- 배포 스크립트는 자세한 **az acr build** 출력을 숨깁니다. 실패 문제를 해결하려면 가장 최근 ACR Task 실행의 상태와 로그를 확인합니다.
- *api* 폴더가 있는 프로젝트 루트 디렉터리에서 배포 스크립트를 실행하는지 확인합니다.
- 최근 ACR Task 실행을 나열합니다.
    - **Bash:** **az acr task list-runs --registry $ACR_NAME --output table**
    - **PowerShell:** **az acr task list-runs --registry $env:ACR_NAME --output table**
- 특정 실행의 로그를 확인합니다(앞 명령의 값으로 **<run-id>**를 바꿉니다).
    - **Bash:** **az acr task logs --registry $ACR_NAME --run-id <run-id>**
    - **PowerShell:** **az acr task logs --registry $env:ACR_NAME --run-id <run-id>**

**"No credential was provided to access Azure Container Registry" 메시지**

- 이 메시지는 컨테이너를 구성할 때 예상되는 메시지입니다. 레지스트리 관리자 계정은 의도적으로 비활성화되어 있으며 웹앱은 대신 관리 ID를 사용합니다.
- 레지스트리 관리자 계정을 사용하도록 설정하거나 레지스트리 자격 증명을 추가하지 마세요.
- 관리 ID 인증이 사용하도록 설정되어 있는지 확인합니다.
    - **Bash:** **az webapp config show --resource-group $RESOURCE_GROUP --name $APP_NAME --query acrUseManagedIdentityCreds --output tsv**
    - **PowerShell:** **az webapp config show --resource-group $env:RESOURCE_GROUP --name $env:APP_NAME --query acrUseManagedIdentityCreds --output tsv**
- 명령이 **true**를 반환하는지 확인합니다. 다른 작업은 필요하지 않습니다.

**컨테이너 이미지 가져오기 실패 문제 해결(ImagePullBackOff / unauthorized / 403)**

- **az webapp identity show**를 실행하여 웹앱에 시스템 할당 관리 ID가 사용하도록 설정되어 있는지 확인합니다.
- 웹앱에 레지스트리 범위의 **AcrPull** 역할 할당이 있는지 확인합니다. 역할 할당이 만들어진 후 전파되는 데 1~2분 정도 걸릴 수 있습니다.
- 컨테이너 구성 단계를 다시 실행하여 이미지 이름과 레지스트리 URL이 올바른지 확인합니다.

**컨테이너 시작 및 애플리케이션 오류 문제 해결**

- 컨테이너 로깅을 사용하도록 설정한 다음 로그를 스트리밍합니다.
    - **Bash:** **az webapp log tail --resource-group $RESOURCE_GROUP --name $APP_NAME**
    - **PowerShell:** **az webapp log tail --resource-group $env:RESOURCE_GROUP --name $env:APP_NAME**
- 배포 직후 앱이 502/503을 반환하면 1분 정도 기다린 후 다시 시도합니다. App Service가 컨테이너를 가져와 시작하는 동안 첫 시작은 더 오래 걸릴 수 있습니다.

**영구 저장소 사용 여부 확인**

- **WEBSITES_ENABLE_APP_SERVICE_STORAGE** 설정이 있고 값이 **true**인지 확인합니다.
- 문서를 제출한 후 **/documents** 엔드포인트를 호출하여 결과가 영구 저장소에 기록되는지 확인합니다.
