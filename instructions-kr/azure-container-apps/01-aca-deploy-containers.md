---
lab:
  topic: Azure Container Apps
  title: 컨테이너화된 백엔드 API를 Container Apps에 배포
  description: 관리 ID를 사용하여 Azure Container Registry(ACR)의 컨테이너 이미지를 Azure Container Apps에 배포하고, 보안 이미지 가져오기를 설정한 다음 배포를 확인하고 로그를 살펴봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Container Apps
    - Azure Container Registry
---

# 컨테이너화된 백엔드 API를 Azure Container Apps에 배포

이 실습에서는 컨테이너화된 백엔드 API를 Azure Container Apps에 배포합니다. 관리 ID를 사용하여 Azure Container Registry에서 이미지를 안전하게 가져오고, 비밀을 환경 변수로 구성합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 Azure 서비스를 배포합니다.
- 관리 ID 인증을 사용하여 컨테이너 앱을 배포합니다.
- 비밀을 구성하고 환경 변수에서 참조합니다.
- API 엔드포인트를 호출하고 로그를 검토하여 배포를 확인합니다.

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
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aca-deploy-python.zip
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

    >**참고:** Container Apps 환경을 만든 후 환경 변수가 포함된 파일이 생성됩니다. 실습 전체에서 이 변수를 사용합니다.

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

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

## 컨테이너 앱 배포 및 비밀 구성

이 섹션에서는 외부 수신을 사용하여 API를 컨테이너 앱으로 배포합니다. 이미지가 프라이빗 레지스트리에 있으므로 첫 번째 리비전에서 이미지를 가져올 수 있도록 앱을 만들 때 레지스트리 인증을 구성해야 합니다. 그런 다음 비밀을 구성하고 환경 변수에서 참조합니다. 이 패턴은 AI 앱에서 공급자 API 키를 저장하는 방식과 유사합니다.

1. 시스템 할당 관리 ID를 사용하여 컨테이너 앱을 만들고, 앱을 만들 때 레지스트리 인증을 구성합니다. **--registry-identity** 플래그는 Container Apps가 앱의 관리 ID를 사용하여 지정된 레지스트리에서 이미지를 가져오도록 합니다. 이 플래그를 Azure Container Registry와 함께 사용하면 CLI가 **AcrPull** 역할을 자동으로 할당합니다.

    **Bash**
    ```azurecli
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $ACA_ENVIRONMENT \
        --image "$ACR_SERVER/$CONTAINER_IMAGE" \
        --ingress external \
        --target-port $TARGET_PORT \
        --env-vars MODEL_NAME=$MODEL_NAME \
        --registry-server "$ACR_SERVER" \
        --registry-identity system
    ```

    **PowerShell**
    ```powershell
    az containerapp create `
        --name $env:CONTAINER_APP_NAME `
        --resource-group $env:RESOURCE_GROUP `
        --environment $env:ACA_ENVIRONMENT `
        --image "$env:ACR_SERVER/$env:CONTAINER_IMAGE" `
        --ingress external `
        --target-port $env:TARGET_PORT `
        --env-vars MODEL_NAME=$env:MODEL_NAME `
        --registry-server "$env:ACR_SERVER" `
        --registry-identity system
    ```

1. 비밀을 만들고 환경 변수에서 참조합니다.

    **Bash**
    ```azurecli
    az containerapp secret set -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --secrets embeddings-api-key=$EMBEDDINGS_API_KEY
    ```

    **PowerShell**
    ```powershell
    az containerapp secret set -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --secrets embeddings-api-key=$env:EMBEDDINGS_API_KEY
    ```

1. 환경 변수에서 비밀을 참조합니다. 이 명령은 새 리비전을 만들어 앱을 다시 시작하므로 비밀 변경 내용이 적용됩니다.

    **Bash**
    ```azurecli
    az containerapp update -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP \
        --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key
    ```

    **PowerShell**
    ```powershell
    az containerapp update -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP `
        --set-env-vars EMBEDDINGS_API_KEY=secretref:embeddings-api-key
    ```

1. 다음 명령을 실행하여 새 리비전이 만들어졌는지 확인합니다.

    **Bash**
    ```azurecli
    az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table
    ```

    **PowerShell**
    ```powershell
    az containerapp revision list -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP -o table
    ```

    리비전 이름은 `--0000002`와 같은 접미사로 끝나며, 이는 두 번째 리비전임을 나타냅니다. 환경 변수나 비밀을 변경하면 Container Apps는 업데이트된 구성으로 앱을 다시 시작하기 위해 새 리비전을 만듭니다. 오래된 비활성 리비전은 시간이 지나면서 정리될 수 있습니다.

## 배포 확인

앱이 시작되고 수신이 작동하는지 확인해야 합니다. 또한 로그를 사용하여 앱이 예상대로 동작하는지 확인합니다.

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

1. 다음 명령을 실행하여 상태 엔드포인트를 호출합니다. 명령은 **{"status": "healthy"}**를 반환해야 합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/health"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/health"
    ```

1. 다음 명령을 실행하여 루트 엔드포인트를 호출하고 비밀이 구성되었는지 확인합니다. 엔드포인트는 구성된 모델 이름과 API 키 비밀의 구성 여부를 비롯한 앱 정보를 JSON으로 반환합니다.

    **Bash**
    ```bash
    curl -s "https://$FQDN/"
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/"
    ```

1. 다음 명령을 실행하여 문서 처리 엔드포인트를 테스트합니다. 이 명령은 *document.txt* 파일을 엔드포인트로 보냅니다. 작업은 모의 데이터 분석 정보가 포함된 JSON을 반환합니다.

    **Bash**
    ```bash
    curl -s -X POST "https://$FQDN/process" \
        -H "Content-Type: text/plain" \
        -d @document.txt
    ```

    **PowerShell**
    ```powershell
    Invoke-RestMethod -Uri "https://$FQDN/process" `
        -Method Post `
        -ContentType "text/plain" `
        -Body (Get-Content -Raw document.txt)
    ```

1. 다음 명령을 실행하여 시작 및 런타임 신호를 확인하는 로그를 검토합니다. 이 명령은 최근 콘솔 출력만 표시합니다. 기록 로그 및 고급 문제 해결 데이터는 Container Apps 환경과 연결된 Log Analytics 작업 영역에 유지됩니다.

    **Bash**
    ```azurecli
    az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP
    ```

    **Powershell**
    ```powershell
    az containerapp logs show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP
    ```

    작업자가 생성되고 포트 8000에서 수신 대기 중임을 보여 주는 **gunicorn** 시작 메시지를 확인합니다. 또한 curl 명령의 HTTP 요청 로그(GET /health, POST /process 등)도 확인할 수 있습니다.

## 리소스 정리

실습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 앞에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 포함된 모든 리소스가 삭제됩니다. 이 실습의 기존 리소스 그룹을 선택했다면 실습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

실습을 완료하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**스크립트로 배포 상태 확인**

- 배포 스크립트를 실행하고 옵션 **3**을 선택하여 ACR 및 Container Apps 환경의 상태를 확인합니다. 이 작업은 기본 인프라가 배포되었고 컨테이너 이미지가 있는지 확인합니다.

**Azure 인증 및 환경 변수 확인**

- **az account show**를 실행하여 올바른 Azure 구독에 로그인했는지 확인합니다.
- **echo $ACR_NAME**(Bash) 또는 **$env:ACR_NAME**(PowerShell)을 실행하여 환경 변수가 설정되었는지 확인합니다.
- 변수가 비어 있으면 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 다시 실행합니다.

**ACR 배포 확인**

- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Azure Container Registry가 있는지, **Provisioning State**가 **Succeeded**인지 확인합니다.
- **az acr list --output table**을 실행하여 레지스트리에 액세스할 수 있는지 확인합니다.

**빌드 실패 문제 해결**

- 배포 스크립트는 자세한 **az acr build** 출력을 표시하지 않습니다. 실패를 해결하려면 가장 최근 ACR Task 실행의 상태와 로그를 확인합니다.
- *api* 폴더가 있는 프로젝트 루트 디렉터리에서 배포 스크립트를 실행하는지 확인합니다.
- 최근 ACR Task 실행을 나열합니다.
    - **Bash:** **az acr task list-runs --registry $ACR_NAME --output table**
    - **PowerShell:** **az acr task list-runs --registry $env:ACR_NAME --output table**
- 특정 실행의 로그를 확인합니다(앞의 명령에서 가져온 값으로 **<run-id>**를 바꿉니다).
    - **Bash:** **az acr task logs --registry $ACR_NAME --run-id \<run-id>**
    - **PowerShell:** **az acr task logs --registry $env:ACR_NAME --run-id \<run-id>**

**컨테이너 가져오기 실패(ImagePullBackOff / unauthorized / 403) 문제 해결**

- 컨테이너 앱에서 시스템 할당 관리 ID가 사용하도록 설정되었는지 확인합니다.
    - **Bash:** **az containerapp identity show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP**
    - **PowerShell:** **az containerapp identity show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP**
- 컨테이너 앱에 레지스트리 범위의 **AcrPull** 역할 할당이 있는지 확인합니다. 역할 할당이 전파되는 데 생성 후 1~2분 정도 걸릴 수 있습니다.

**컨테이너 시작 및 애플리케이션 오류 문제 해결**

- 시작 문제를 진단하려면 컨테이너 로그를 스트리밍합니다.
    - **Bash:** **az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --follow**
    - **PowerShell:** **az containerapp logs show -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP --follow**
- 배포 직후 앱에서 502/503을 반환하면 1분 정도 기다린 후 다시 시도합니다. Container Apps가 컨테이너를 가져와 시작하는 동안 첫 시작에 시간이 더 걸릴 수 있습니다.
- 프로비저닝 오류가 있는지 리비전 상태를 확인합니다.
    - **Bash:** **az containerapp revision list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table**
    - **PowerShell:** **az containerapp revision list -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP -o table**

**비밀 구성 문제 해결**

- 비밀이 만들어졌는지 확인합니다.
    - **Bash:** **az containerapp secret list -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP -o table**
    - **PowerShell:** **az containerapp secret list -n $env:CONTAINER_APP_NAME -g $env:RESOURCE_GROUP -o table**
- 루트 엔드포인트(**/**)를 호출하여 환경 변수가 비밀을 올바르게 참조하는지 확인합니다. 이 엔드포인트는 API 키가 구성되었는지 보여 줍니다.
