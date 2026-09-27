---
lab:
  topic: 컨테이너 호스팅
  title: ACR Tasks를 사용하여 컨테이너 이미지를 빌드하고 실행하기
  description: 로컬 Docker 설치 없이 Azure Container Registry(ACR) Tasks를 사용하여 클라우드에서 컨테이너 이미지를 빌드하고 관리하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Container Registry
---

# ACR Tasks를 사용하여 컨테이너 이미지를 빌드하고 실행하기

이 연습에서는 Azure Container Registry(ACR) Tasks를 사용하여 로컬 Docker 설치 없이 클라우드에서 컨테이너 이미지를 빌드하고 관리합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Container Registry 배포
- ACR Tasks를 사용하여 컨테이너 이미지 빌드 및 확인
- 이미지 버전 관리 및 프로덕션 이미지 보호

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**Important:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시적으로 중단되었습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

이 연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure Container Registry를 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/acr-tasks-python.zip
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

1. 다음 명령을 실행하여 구독에 Azure Container Registry(ACR)를 설치하는 데 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```
    az provider register --namespace Microsoft.ContainerRegistry
    ```

1. 프로젝트의 루트 디렉터리에 있는지 확인한 다음 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다. 배포 스크립트는 ACR을 배포하고 연습에 필요한 환경 변수 파일을 만듭니다.

    ```
    python azdeploy.py
    ```

1. 적절한 명령을 실행하여 환경 변수를 터미널 세션에 로드합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

## ACR Tasks로 이미지 빌드

이 섹션에서는 로컬 컴퓨터에 Docker가 없어도 Azure에서 이미지를 빌드하는 빠른 작업을 사용합니다. **az acr build** 명령은 소스 파일을 업로드하고 클라우드에서 이미지를 빌드한 다음 레지스트리에 푸시합니다.

1. 다음 명령을 실행하여 이미지를 빌드하고 레지스트리에 푸시합니다. 빌드는 Azure에서 완전히 수행되므로 로컬 Docker를 설치할 필요가 없습니다.

    **Bash**
    ```bash
    az acr build \
        --registry $ACR_NAME \
        --image inference-api:v1.0.0 \
        ./api
    ```

   **PowerShell**
    ```powershell
    az acr build `
        --registry $env:ACR_NAME `
        --image inference-api:v1.0.0 `
        ./api
    ```

1. ACR Tasks의 출력에서 다음 작업을 확인합니다.

    - 소스 컨텍스트를 패키징하여 Azure에 업로드
    - 빌드 작업을 대기열에 추가하고 시작
    - 각 계층을 보여 주는 Docker 빌드 출력 스트리밍
    - 완성된 이미지를 레지스트리에 푸시
    - 이미지 다이제스트와 작업 상태 보고


## 레지스트리에서 이미지 확인

이 섹션에서는 리포지토리와 태그를 나열하여 레지스트리에 이미지가 있는지 확인합니다.

1. 다음 명령을 실행하여 레지스트리의 모든 리포지토리를 나열합니다.

    **Bash**
    ```bash
    az acr repository list --name $ACR_NAME --output table
    ```

    **PowerShell**
    ```powershell
    az acr repository list --name $env:ACR_NAME --output table
    ```

    출력에 만든 **inference-api** 리포지토리가 표시됩니다.

1. 다음 명령을 실행하여 **inference-api** 리포지토리의 태그를 나열합니다.

    **Bash**
    ```bash
    az acr repository show-tags \
        --name $ACR_NAME \
        --repository inference-api \
        --output table
    ```

    **PowerShell**
    ```powershell
    az acr repository show-tags `
        --name $env:ACR_NAME `
        --repository inference-api `
        --output table
    ```

    출력에 빌드 중 지정한 **v1.0.0** 태그가 표시됩니다.

1. 다음 명령을 실행하여 다이제스트를 포함한 자세한 매니페스트 정보를 확인합니다.

    **Bash**
    ```bash
    az acr manifest list-metadata \
        --registry $ACR_NAME \
        --name inference-api \
        --output table
    ```

    **PowerShell**
    ```powershell
    az acr manifest list-metadata `
        --registry $env:ACR_NAME `
        --name inference-api `
        --output table
    ```

    다이제스트 값을 확인합니다. 이 SHA-256 해시는 태그와 관계없이 이미지를 고유하게 식별합니다.

## ACR Tasks로 이미지 실행

이 섹션에서는 **az acr run** 명령을 사용하여 빌드한 이미지 안에서 명령을 실행하고 이미지가 올바르게 작동하는지 확인합니다.

1. 다음 명령을 실행하여 컨테이너에서 Flask 애플리케이션이 올바르게 로드되는지 확인합니다.

    **Bash**
    ```bash
    az acr run \
        --registry $ACR_NAME \
        --cmd "$ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" \
        /dev/null
    ```

    **PowerShell**
    ```powershell
    az acr run `
        --registry $env:ACR_NAME `
        --cmd "$env:ACR_NAME.azurecr.io/inference-api:v1.0.0 python -c 'from app import app'" `
        /dev/null
    ```

    출력에는 이미지를 다운로드하는 Docker 풀 진행 상황이 포함됩니다. 성공적으로 실행되면 **Run ID: xxx was successful after xxx**로 끝납니다. 이는 컨테이너가 올바르게 실행되고 Flask 애플리케이션이 오류 없이 가져와졌음을 확인합니다.

## 다른 태그로 빌드

이 섹션에서는 새 태그로 이미지의 새 버전을 빌드하여 레지스트리에서 여러 버전을 유지하는 방법을 확인합니다.

1. 다음 명령을 실행하여 새 버전 태그로 이미지를 다시 빌드합니다.

    **Bash**
    ```bash
    az acr build \
        --registry $ACR_NAME \
        --image inference-api:v1.1.0 \
        ./api
    ```

    **PowerShell**
    ```powershell
    az acr build `
        --registry $env:ACR_NAME `
        --image inference-api:v1.1.0 `
        ./api
    ```

1. 다음 명령을 실행하여 모든 태그를 나열하고 두 버전을 확인합니다.

    **Bash**
    ```bash
    az acr repository show-tags \
        --name $ACR_NAME \
        --repository inference-api \
        --output table
    ```

    **PowerShell**
    ```powershell
    az acr repository show-tags `
        --name $env:ACR_NAME `
        --repository inference-api `
        --output table
    ```

    출력에 **v1.0.0**과 **v1.1.0**이 모두 표시됩니다. 이를 통해 레지스트리에서 여러 버전을 유지하는 방법을 확인할 수 있습니다.

## 빌드 기록 확인 및 프로덕션 이미지 잠금

이 섹션에서는 ACR 작업 실행 기록을 검토하고 이미지가 실수로 변경되지 않도록 잠급니다.

1. 다음 명령을 실행하여 수행한 모든 빌드를 확인할 수 있도록 ACR 작업 실행 기록을 검토합니다.

    **Bash**
    ```bash
    az acr task list-runs \
        --registry $ACR_NAME \
        --output table
    ```

    **PowerShell**
    ```powershell
    az acr task list-runs `
        --registry $env:ACR_NAME `
        --output table
    ```

    출력에는 각 빌드 작업의 실행 ID, 상태, 트리거 유형 및 기간이 표시됩니다. 이 기록을 통해 빌드를 추적하고 문제를 진단할 수 있습니다.

1. 다음 명령을 실행하여 v1.0.0 이미지를 잠그고 실수로 삭제되거나 수정되지 않도록 합니다.

    **Bash**
    ```bash
    az acr repository update \
        --name $ACR_NAME \
        --image inference-api:v1.0.0 \
        --write-enabled false
    ```

    **PowerShell**
    ```powershell
    az acr repository update `
        --name $env:ACR_NAME `
        --image inference-api:v1.0.0 `
        --write-enabled false
    ```

1. 다음 명령을 실행하여 잠금이 설정되었는지 확인합니다.

    **Bash**
    ```bash
    az acr repository show \
        --name $ACR_NAME \
        --image inference-api:v1.0.0
    ```

    **PowerShell**
    ```powershell
    az acr repository show `
        --name $env:ACR_NAME `
        --image inference-api:v1.0.0
    ```

    **writeEnabled** 필드에 **False**가 표시되면 이미지가 보호되고 있는 것입니다.

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
- 빌드 출력의 오류 메시지를 확인합니다. 일반적인 문제에는 Dockerfile 누락이나 잘못된 파일 경로가 있습니다.
- *api* 폴더가 있는 프로젝트 루트 디렉터리에서 명령을 실행하는지 확인합니다.
- **az acr task list-runs --registry $ACR_NAME --output table**을 실행하여 최근 빌드 상태를 확인합니다.
