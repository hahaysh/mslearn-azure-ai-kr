---
lab:
  topic: Azure Kubernetes Service
  title: Azure Kubernetes Service에서 앱 구성
  description: 영구 저장소로 Kubernetes 배포를 구성하고 민감 정보와 일반 설정을 저장하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
---

# Azure Kubernetes Service에서 앱 구성

이 연습에서는 민감하지 않은 설정에 ConfigMap을 사용하고, 민감한 자격 증명에 Secret을 사용하며, 영구 저장소에 PersistentVolumeClaim을 사용하는 방식으로 Kubernetes 배포를 구성하는 방법을 알아봅니다. 컨테이너화된 API를 Azure Kubernetes Service(AKS)에 배포하고 다양한 Kubernetes 리소스로 구성한 다음 Python 클라이언트 애플리케이션으로 API를 사용합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure에 리소스 배포(ACR, AKS 클러스터)
- 컨테이너 이미지를 빌드하여 Azure Container Registry에 푸시
- AKS 클러스터 액세스를 위한 kubectl 자격 증명 구성
- 업데이트된 YAML 파일을 AKS에 적용하여 Pod를 만들고 LoadBalancer로 API 노출
- 클라이언트 앱을 실행하여 API 엔드포인트 테스트
- 영구 볼륨에 저장된 API 로그 보기
- Azure 리소스 정리

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**중요:** 이 연습의 영구 저장소 구현은 데모 용도일 뿐입니다. 로깅에는 영구 볼륨에 로그를 저장하는 대신 Azure Monitor 또는 Application Insights 같은 중앙 집중식 로깅 솔루션을 프로덕션 애플리케이션에서 사용해야 합니다. 영구 저장소가 필요한 경우 로그 순환 정책을 구현하여 저장 공간이 가득 차 컨테이너 실패와 Pod 축출이 발생하지 않도록 합니다.

> **중요:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시 중지되어 있습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Kubernetes 명령줄 도구인 [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Python 3.12](https://www.python.org/downloads/) 이상
- **선택 사항:** YAML 언어 지원, 유효성 검사 및 서식 지정을 위한 [Visual Studio Code용 YAML 확장](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 콘솔 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure 리소스 배포에는 10~15분이 걸릴 수 있습니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aks-configure-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder)...**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 상단의 리소스 그룹 및 위치 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```python
    rg = "<your-resource-group-name>"  # Resource Group name
    location = "<your-azure-region>"   # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 AKS 및 ACR을 설치하는 데 필요한 리소스 공급자가 등록되어 있는지 확인합니다. **Microsoft.Compute**, **Microsoft.Network**, **Microsoft.Storage** 공급자는 AKS의 종속 항목이며 Azure에서 보통 자동으로 등록하지만, 새 구독에서 가끔 발생하는 클러스터 생성 실패를 방지하려면 명시적으로 등록하는 것이 좋습니다.

    ```
    az provider register --namespace Microsoft.ContainerService
    az provider register --namespace Microsoft.ContainerRegistry
    az provider register --namespace Microsoft.Compute
    az provider register --namespace Microsoft.Network
    az provider register --namespace Microsoft.Storage
    ```

1. 프로젝트 루트 디렉터리에 있는지 확인하고 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

    > **참고:** 시스템 구성에 따라 Python 명령은 **python** 대신 **python3**일 수 있습니다.

### Azure에 리소스 배포

배포 스크립트가 실행되면 다음 단계에 따라 Azure에 필요한 리소스를 만듭니다.

1. **Create Azure Container Registry (ACR)**를 시작하려면 **1**을 입력합니다. 이 리소스에는 API 컨테이너를 저장하고 나중에 AKS 리소스로 가져옵니다.

    작업이 완료되면 ACR 엔드포인트가 반환됩니다. 이 정보는 연습 후반부에서 필요하므로 복사합니다.

1. ACR 리소스를 만든 후 **2**를 입력하여 **Build and push API image to ACR**을 시작합니다. 이 옵션은 ACR 작업을 사용하여 이미지를 빌드하고 ACR 리포지토리에 추가합니다. 이 작업을 완료하는 데 3~5분이 걸릴 수 있습니다.

1. 이미지가 빌드되어 ACR에 푸시된 후 **3**을 입력하여 **Create AKS cluster** 옵션을 시작합니다. 이 옵션은 관리 ID로 구성된 AKS 리소스를 만들고, ACR 리소스에서 이미지를 가져올 수 있는 권한을 서비스에 부여하며, 영구 저장소에 쓸 수 있도록 필요한 RBAC 역할을 할당합니다. 이 작업을 완료하는 데 5~10분이 걸릴 수 있습니다.

1. AKS 클러스터 배포가 완료된 후 **4**를 입력하여 **Get AKS credentials for kubectl** 옵션을 시작합니다. 이 옵션은 **az aks get-credentials** 명령을 사용하여 자격 증명을 가져오고 **kubectl**을 구성합니다.

1. 자격 증명이 구성된 후 **5**를 입력하여 **Check deployment status** 옵션을 시작합니다. 이 옵션은 각 리소스가 성공적으로 배포되었는지 보고합니다.

    모든 서비스가 **successful** 메시지를 반환하면 **7**을 입력하여 배포 스크립트를 종료합니다.

    AKS 클러스터 상태가 **Failed** 또는 **Canceled**이면 보고된 문제를 해결한 다음 **6**을 입력하여 **Delete failed AKS deployment** 옵션을 시작한 후 옵션 **3**을 다시 실행합니다. 이 보호 기능이 적용된 옵션은 정상 상태이거나 진행 중인 클러스터를 삭제하지 않습니다.

이제 API를 AKS에 배포하는 데 필요한 YAML 파일을 완성합니다.

## YAML 배포 파일 완성 및 AKS에 배포

이 섹션에서는 *k8s* 폴더에 있는 YAML 파일을 완성하여 영구 저장소를 사용하고 민감 정보와 일반 설정을 저장하도록 Kubernetes 배포를 구성합니다.

### ConfigMap YAML 파일 완성

ConfigMap은 Pod가 사용할 수 있는 민감하지 않은 구성 데이터를 키-값 쌍으로 저장합니다. 이 섹션에서는 학생 이름, API 버전, 로그 경로와 같은 애플리케이션 설정을 저장하는 ConfigMap을 만듭니다.

1. 비어 있는 *k8s/configmap.yaml* 파일을 열고 다음 코드를 추가합니다. 원하는 경우 **STUDENT_NAME** 값을 자신의 이름으로 바꿀 수 있습니다.

    ```yml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: api-config
      labels:
        app: aks-config-api # Label for the AKS configuration API
    data:
      # Store non-sensitive configuration values
      STUDENT_NAME: "YourNameHere"
      API_VERSION: "1.0.0"
      LOG_PATH: "/var/log/api" # Path for API logs
    ```

1. 코드의 주석을 검토한 다음 변경 내용을 저장합니다.

### Secrets YAML 파일 완성

Secret은 암호, 토큰, 키와 같은 민감한 정보를 base64로 인코딩된 형식으로 저장합니다. 이 섹션에서는 API가 런타임에 액세스할 민감한 자격 증명을 저장하는 Secret을 만듭니다.

1. 비어 있는 *k8s/secrets.yaml* 파일을 열고 다음 코드를 추가합니다.

    ```yml
    apiVersion: v1
    kind: Secret
    metadata:
      name: api-secrets
      labels:
        app: aks-config-api
    type: Opaque
    stringData:
      # Store sensitive credentials as base64-encoded values
      secret-endpoint: "SecretEndpointValue"
      secret-access-key: "SecretAccessKey123456"
    ```

1. 코드의 주석을 잠시 검토한 다음 변경 내용을 저장합니다.

### PVC YAML 파일 완성

PersistentVolumeClaim(PVC)은 Pod에 탑재할 저장소 리소스를 Azure에 요청합니다. 이 섹션에서는 Azure Disk 저장소를 사용하는 PVC를 만들어 Pod가 다시 시작된 후에도 API 로그 파일을 유지합니다.

1. 비어 있는 *k8s/pvc.yaml* 파일을 열고 다음 코드를 추가합니다.

    ```yml
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: api-logs-pvc
      labels:
        app: aks-config-api # Label for the AKS configuration API
    spec:
      accessModes:
        - ReadWriteOnce  # Allow single pod to mount volume for read/write
      resources:
        requests:
          storage: 1Gi  # Request minimum Azure Disk size
      storageClassName: managed-csi  # Use Azure Disk CSI driver (default)
      volumeMode: Filesystem  # Default mode
    ```

1. 코드의 주석을 잠시 검토한 다음 변경 내용을 저장합니다.

### Deployment YAML 파일 업데이트

배포 매니페스트에는 환경 변수, 볼륨 탑재 및 프로브가 이미 부분적으로 구성되어 있습니다. 특정 ACR 엔드포인트를 사용하도록 컨테이너 이미지 참조만 업데이트하면 됩니다.

1. *k8s/deployment.yaml* 파일을 열고 **image: <YOUR_ACR_ENDPOINT>/aks-config-api:latest** 줄을 찾습니다.

1. **<YOUR_ACR_ENDPOINT>**를 앞에서 기록한 값으로 바꿉니다.

1. 코드의 주석을 잠시 검토한 다음 변경 내용을 저장합니다.


## 매니페스트를 AKS에 적용

이 섹션에서는 매니페스트를 AKS에 적용합니다. 다음 단계는 VS Code 터미널에서 수행합니다. 명령을 실행하기 전에 프로젝트 루트에 있는지 확인합니다.

1. 다음 명령을 실행하여 ConfigMap을 적용합니다.

    ```
    kubectl apply -f k8s/configmap.yaml
    ```

1. 다음 명령을 실행하여 Secrets를 적용합니다.

    ```
    kubectl apply -f k8s/secrets.yaml
    ```

1. 다음 명령을 실행하여 PersistentVolumeClaim을 적용합니다.

    ```
    kubectl apply -f k8s/pvc.yaml
    ```

1. 다음 명령을 실행하여 Deployment를 적용합니다.

    ```
    kubectl apply -f k8s/deployment.yaml
    ```

1. 다음 명령을 실행하여 Service를 만듭니다.

    ```
    kubectl apply -f k8s/service.yaml
    ```

1. Service를 만든 후 배포가 완료되기까지 몇 분이 걸릴 수 있습니다. 다음 명령은 서비스를 모니터링하고 Pod의 외부 IP 주소를 사용할 수 있게 되면 업데이트합니다. IP 주소가 표시된 후 **ctrl + c**를 입력하여 명령을 종료합니다.

    ```
    kubectl get svc aks-config-api-service -w
    ```

1. 프로젝트 루트에서 다음 명령을 실행하여 배포 스크립트를 다시 시작합니다.

    ```
    python azdeploy.py
    ```

1. **Check deployment status** 옵션을 실행하려면 **5**를 입력합니다. 스크립트는 LoadBalancer IP를 읽어 *client/.env*에 **API_ENDPOINT**로 씁니다. 상태 확인이 끝나면 **7**을 입력하여 배포 스크립트를 종료합니다.

## 클라이언트 앱 실행

이 섹션에서는 Python 환경을 구성한 다음 클라이언트 앱을 사용하여 API에서 작업을 수행합니다.

### Python 환경 구성

이 섹션에서는 Python 환경을 만들고 종속성을 설치합니다.

1. 터미널에서 프로젝트의 *client* 폴더에 있는지 확인합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 Python 환경을 만듭니다.

    ```
    python -m venv .venv
    ```

1. 다음 명령을 실행하여 Python 환경을 활성화합니다. **참고:** Linux/macOS에서는 Bash 명령을 사용하고 Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

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

### 앱에서 작업 수행

Python 환경을 구성하고 종속성을 설치했으므로 이제 클라이언트 애플리케이션을 실행하여 배포된 API를 테스트할 수 있습니다. API는 모든 작업을 영구 볼륨에 기록하며, 클라이언트는 다양한 엔드포인트와 상호 작용하는 메뉴 기반 인터페이스를 제공합니다.

1. 터미널에서 다음 명령을 실행하여 콘솔 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 연습 앞부분의 명령을 참고하여 환경을 활성화합니다.

    ```
    python main.py
    ```

1. **Check API Health (Liveness)** 옵션을 시작하려면 **1**을 입력합니다. 이 옵션은 API 컨테이너가 실행 중이며 상태 확인에 응답하는지 검증합니다. Kubernetes 활성 프로브에서 사용하는 것과 동일한 엔드포인트입니다. 반환된 정보에 ConfigMap에서 설정한 민감하지 않은 학생 이름이 포함되어 있는지 확인합니다.

    ```
    [*] Checking API health...
    ✓ API is healthy
      Service: aks-config-api
      Version: 1.0.0
      Student: YourNameHere
    ```
1. **Check API Readiness** 옵션을 시작하려면 **2**를 입력합니다. 이 옵션은 ConfigMap의 학생 이름이 로드되었는지 확인하고 구성된 API 버전을 표시하며, Kubernetes Secrets가 로드되었는지와 영구 로그 저장소에 쓸 수 있는지 보고합니다.

1. **View Secrets Information** 옵션을 시작하려면 **3**을 입력합니다. 이 기능은 Pod에 Secret이 설정되었는지 확인하기 위한 데모 용도일 뿐입니다. 출력에서 Secret 정보를 확인할 수 있지만 값은 마스킹됩니다.

    ```
    Secret Details:

      secret_endpoint:
        Loaded: True
        Value: SecretEndp...
        Length: 19 characters

      secret_access_key:
        Loaded: True
        Value: ***3456
        Length: 21 characters
    ```

1. **Get Single Product** 옵션을 시작하려면 **4**를 입력합니다. **1**부터 **10**까지의 제품 ID를 입력하여 API의 모의 제품 중 하나를 가져옵니다.

1. **List All Products** 옵션을 시작하려면 **5**를 입력합니다. 이 옵션은 API에 포함된 모의 데이터를 표시합니다.

1. 이제 API가 여러 엔드포인트의 작업을 기록했으므로 로그를 확인합니다. **View Log Summary** 옵션을 시작하려면 **6**을 입력하여 여러 작업의 요약을 확인합니다. 총 요청 수와 **/readyz**, **/healthz** 엔드포인트에 대한 요청 수를 확인합니다. 이 두 작업은 *deployment.yaml* 파일에 설정된 일정에 따라 자동으로 실행됩니다.

    ```
    ✓ Log summary retrieved

    Log file: /var/log/api/api-requests-2025-12-21.log
    Total requests: 220
    Student: YourNameHere

    First request: 2025-12-21T02:19:48.953308
    Last request: 2025-12-21T02:46:08.952772

    Requests by endpoint:
      /readyz: 160
      /healthz: 56
      /secrets: 1
      /products: 1
    ```

1. 로그 정보를 계속 생성할 수 있습니다. 작업을 마치면 **7**을 입력하여 앱을 종료합니다.

## 리소스 정리

연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 연습 앞부분에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택한 경우 연습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

이 연습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**배포 스크립트로 배포 상태 확인**
- 배포 스크립트를 실행하고 **5. Check deployment status** 옵션을 선택하여 배포된 모든 리소스의 상태를 확인합니다.
- 이 명령은 다음을 확인합니다.
  - ACR 프로비저닝 상태 및 준비 상태
  - AKS 클러스터 프로비저닝 상태
  - Kubernetes 리소스(ConfigMap, Secrets, PVC, Deployment 가용성, Service LoadBalancer IP)
- 이 출력을 사용하여 문제를 일으키는 구성 요소를 식별합니다.

**AKS 클러스터 생성 실패 해결**
- AKS 리소스를 만들기 전에 할당량 검증이 실패할 수 있고, 프로비전 후반의 실패로 클러스터 상태가 **Failed** 또는 **Canceled**가 될 수 있습니다.
- 오류에 **Standard_D2s_v7**을 사용할 수 없거나 해당 지역의 용량이 부족하다고 표시되면 옵션 **7**로 종료합니다. **AKS_VM_SIZE**를 배포 스크립트 상단에 나열된 v5 또는 v6 대체 크기 중 하나로 변경하거나 **location** 값을 변경한 다음 **3. Create AKS cluster** 옵션을 다시 실행합니다.
- 오류에 할당량 부족이 표시되면 구독에 사용 가능한 Dsv5 계열 할당량이 있는 지역을 선택하거나 할당량 증가를 요청합니다. 다른 지역에 충분한 할당량이 있는 경우에만 지역 변경이 도움이 됩니다.
- 리소스 그룹이 다른 지역에 이미 있더라도 AKS 클러스터는 스크립트에 구성된 **location**을 사용합니다.
- 옵션 **5**에서 **Failed** 또는 **Canceled**가 보고되면 근본 문제를 해결하고 옵션 **3**을 다시 시도하기 전에 **6. Delete failed AKS deployment**를 실행합니다. AKS 리소스가 생성되지 않았다면 삭제할 필요가 없습니다.

**YAML 파일 완전성 확인**
- 모든 YAML 콘텐츠를 *configmap.yaml*, *secrets.yaml*, *pvc.yaml*에 올바르게 추가했고 들여쓰기가 올바른지 확인합니다.
- *deployment.yaml*에서 ACR 엔드포인트가 올바르게 업데이트되었는지 확인합니다(**<YOUR_ACR_ENDPOINT>**를 실제 ACR 엔드포인트로 바꿉니다).
- 최초 배포 후 YAML 파일을 변경한 경우 **kubectl apply -f k8s/<filename>.yaml**로 파일을 다시 적용합니다.
- ConfigMap 또는 Secret 파일을 업데이트한 후 구성을 다시 로드하려면 롤링 재시작을 수행합니다. **kubectl rollout restart deployment aks-config-api**

**클라이언트 구성 확인**
- *client/.env*가 있고 **API_ENDPOINT**가 LoadBalancer의 외부 IP(예: **http://20.xxx.xxx.xxx**)로 설정되어 있는지 확인합니다.
- 파일이 없거나 오래된 IP가 표시되면 Service에 외부 IP가 할당된 후 배포 스크립트를 실행하고 **5. Check deployment status** 옵션을 선택하여 *client/.env*를 다시 씁니다.
- 터미널에서 **curl http://<external-ip>/healthz**를 실행하여 API 엔드포인트에 연결할 수 있는지 확인합니다.

**Python 환경 및 종속성 확인**
- 클라이언트 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
- *client* 디렉터리에서 클라이언트를 실행하는지 확인합니다.
