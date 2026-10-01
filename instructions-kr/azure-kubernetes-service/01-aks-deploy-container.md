---
lab:
  topic: Azure Kubernetes Service
  title: Azure Kubernetes Service에 AI 추론 API 배포
  description: Kubernetes 배포 및 서비스 매니페스트를 만들어 AI 추론 API 컨테이너를 Azure Kubernetes Service에 배포하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
---

# Azure Kubernetes Service에 AI 추론 API 배포

이 연습에서는 Microsoft Foundry AI 모델, Azure Container Registry(ACR), Azure Kubernetes Service(AKS) 클러스터를 비롯한 Azure 리소스를 배포합니다. 그런 다음 Kubernetes 매니페스트 파일을 완성하여 컨테이너 사양, 상태 프로브, 리소스 제한, 부하 분산을 정의합니다. 컨테이너화된 API를 AKS에 배포한 후 Python 클라이언트 애플리케이션을 사용하여 상태 확인, 준비 상태 검증, AI 모델 추론 요청을 포함한 배포된 API 엔드포인트를 테스트합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure에 리소스 배포
- *deployment.yaml* 및 *service.yaml* 파일을 완성하고 컨테이너를 AKS에 배포
- 클라이언트 앱을 실행하여 API 테스트

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**중요:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시 중지되어 있습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Kubernetes 명령줄 도구인 [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Python 3.12](https://www.python.org/downloads/) 이상
- **선택 사항:** YAML 언어 지원, 유효성 검사 및 서식 지정을 위한 [Visual Studio Code용 YAML 확장](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 콘솔 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure 리소스 배포에는 15~20분이 걸릴 수 있습니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aks-deploy-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder)...**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 상단의 리소스 그룹 및 위치 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```python
    rg = "<your-resource-group-name>"  # Resource Group name
    location = "<your-azure-region>"   # Azure region for the resources
    ```

    > **참고:** 배포에는 다음 세 Azure 지역 중 하나를 사용하는 것이 좋습니다. **eastus2**, **swedencentral**, **australiaeast**. 이 지역은 연습에서 사용하는 AI 추론 모델 배포를 지원합니다.

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 AKS, ACR 및 Foundry AI 모델을 설치하는 데 필요한 리소스 공급자가 등록되어 있는지 확인합니다. **Microsoft.Compute**, **Microsoft.Network**, **Microsoft.Storage** 공급자는 AKS의 종속 항목이며 Azure에서 보통 자동으로 등록하지만, 새 구독에서 가끔 발생하는 클러스터 생성 실패를 방지하려면 명시적으로 등록하는 것이 좋습니다.

    ```
    az provider register --namespace Microsoft.CognitiveServices
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

1. **1. Provision gpt-5-mini model in Microsoft Foundry** 옵션을 시작하려면 **1**을 입력합니다. 이 옵션은 리소스 그룹이 아직 없는 경우 만들고, Microsoft Foundry에 리소스를 만든 다음 **gpt-5-mini** 모델을 해당 리소스에 배포합니다.

    > **중요:** 모델 배포 중 오류가 발생하면 **7**을 입력하여 **7. Delete/Purge Foundry deployment** 옵션을 시작합니다. 그러면 배포가 삭제되고 리소스 이름이 제거됩니다. 메뉴를 종료한 후 배포 스크립트의 지역을 권장 지역 중 다른 하나로 변경합니다. 그런 다음 배포 스크립트를 다시 시작하고 모델 프로비전 옵션을 다시 실행합니다.

1. 모델이 배포된 후 **2**를 입력하여 **2. Create Azure Container Registry (ACR)**를 시작합니다. 이 리소스에는 API 컨테이너를 저장하고 나중에 AKS 리소스로 가져옵니다.

1. ACR 리소스를 만든 후 **3**을 입력하여 **3. Build and push API image to ACR**을 시작합니다. 이 옵션은 ACR 작업을 사용하여 이미지를 빌드하고 ACR 리포지토리에 추가합니다. 이 작업을 완료하는 데 3~5분이 걸릴 수 있습니다.

1. 이미지가 빌드되어 ACR에 푸시된 후 **4**를 입력하여 **4. Create AKS cluster** 옵션을 시작합니다. 이 옵션은 관리 ID로 구성된 AKS 리소스를 만들고, ACR 리소스에서 이미지를 가져올 수 있는 권한을 서비스에 부여합니다. 이 작업을 완료하는 데 5~10분이 걸릴 수 있습니다.

1. AKS 리소스가 배포된 후 **5**를 입력하여 **5. Check deployment status** 옵션을 시작합니다. 이 옵션은 세 리소스가 모두 성공적으로 배포되었는지 보고합니다.

    모든 서비스가 **successful** 메시지를 반환하면 **9**를 입력하여 배포 스크립트를 종료합니다.

    AKS 클러스터 상태가 **Failed** 또는 **Canceled**이면 보고된 문제를 해결한 다음 **8**을 입력하여 **8. Delete failed AKS deployment** 옵션을 시작한 후 옵션 **4**를 다시 실행합니다. 이 보호 기능이 적용된 옵션은 정상 상태이거나 진행 중인 클러스터를 삭제하지 않습니다.

이제 API를 AKS에 배포하는 데 필요한 YAML 파일을 완성합니다.

## YAML 배포 파일 완성 및 AKS에 배포

이 섹션에서는 *deployment.yaml* 및 *service.yaml* 파일을 모두 완성합니다. 배포 매니페스트는 AKS에서 API 컨테이너를 배포하고 관리하는 방법을 정의하며, 서비스 매니페스트는 부하 분산 장치를 통해 외부 트래픽에 API를 노출합니다.

1. *k8s/deployment.yaml* 파일을 열어 파일 작성을 시작합니다.

> **팁:** YAML을 해당 **BEGIN** 및 **END** 주석과 같은 들여쓰기 수준에 붙여 넣습니다. 블록의 들여쓰기가 맞지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN: Container specification** 주석을 찾아 그 아래에 다음 YAML 섹션을 매니페스트에 추가합니다. YAML 들여쓰기가 올바른지 확인합니다.

    ```yml
    containers:  # List of containers to run in the pod
    - name: api
      image: ACR_ENDPOINT/aks-api:latest  # Container image from ACR
      imagePullPolicy: Always  # Always pull the latest image from registry
      ports:  # Ports exposed by the container
      - name: http
        containerPort: 8000
        protocol: TCP
    ```

    이 섹션에서는 사용할 ACR 컨테이너 이미지, 가져오기 정책, HTTP 트래픽에 컨테이너가 노출하는 포트를 포함한 컨테이너 사양을 정의합니다.

1. **# BEGIN: Liveness Probe Configuration** 주석을 찾아 그 아래에 다음 YAML 섹션을 매니페스트에 추가합니다. YAML 들여쓰기가 올바른지 확인합니다.

    ```yml
    livenessProbe:  # Detects if container is alive or needs restart
      httpGet:
        path: /healthz  # Health check endpoint path
        port: http
      initialDelaySeconds: 10  # Seconds to wait before first check
      periodSeconds: 30
      timeoutSeconds: 5
      failureThreshold: 3  # Consecutive failures before restarting container
    ```

    이 섹션은 **/healthz** 엔드포인트에 HTTP 요청을 보내 컨테이너가 정상인지 주기적으로 확인하는 활성 프로브를 구성합니다. 프로브가 연속 세 번 실패하면 Kubernetes가 컨테이너를 자동으로 다시 시작합니다.

1. **# BEGIN: Resource Limits Configuration** 주석을 찾아 그 아래에 다음 YAML 섹션을 매니페스트에 추가합니다. YAML 들여쓰기가 올바른지 확인합니다.

    ```yml
    resources:  # CPU and memory resource specifications
      requests:  # Minimum resources guaranteed to the container
        memory: "256Mi"
        cpu: "250m"
      limits:  # Maximum resources the container can use
        memory: "512Mi"
        cpu: "500m"
    ```

    이 섹션은 컨테이너의 CPU 및 메모리 리소스를 정의합니다. requests는 보장되는 최소 리소스를 지정하고 limits는 컨테이너가 사용할 수 있는 최대 리소스를 설정합니다. 이를 통해 Kubernetes가 Pod를 효율적으로 예약하고 리소스 고갈을 방지합니다.

1. 변경 내용을 저장하고 완성된 *deployment.yaml* 파일을 잠시 검토합니다.

다음으로 *service.yaml* 파일을 업데이트합니다.

1. 비어 있는 *k8s/service.yaml* 파일을 엽니다.

1. 다음 YAML을 매니페스트에 추가합니다. YAML 들여쓰기가 올바른지 확인합니다.

    ```yml
    apiVersion: v1
    kind: Service  # Service: exposes pods on a network and provides load balancing
    metadata:
      name: aks-api-service  # Unique name for the service
      labels:
        app: aks-api # Matches deployment and pod labels
      annotations:
        service.beta.kubernetes.io/azure-load-balancer-internal: "false"  # Use public load balancer
    spec:  # Service specification
      type: LoadBalancer  # Exposes service externally
      selector:  # Selects which pods to route traffic to based on labels
        app: aks-api
        version: v1
      ports:  # Port mappings between service and pods
      - name: http
        port: 80  # Service port exposed externally
        targetPort: http  # Pod container port to forward traffic to
        protocol: TCP
      sessionAffinity: None  # Client requests not pinned to specific pods
    ```

    이 매니페스트는 Azure Load Balancer를 통해 API Pod를 외부에 노출하는 LoadBalancer Service를 만듭니다. 레이블 선택기를 사용하여 트래픽을 받을 Pod를 식별하고, 포트 80으로 들어오는 트래픽을 컨테이너의 포트 8000으로 라우팅합니다.

1. 변경 내용을 저장하고 파일을 잠시 검토합니다.

### 매니페스트를 AKS에 적용

이 섹션에서는 배포 스크립트를 사용하여 매니페스트를 AKS에 적용합니다.

1. 프로젝트 루트 디렉터리에 있는지 확인하고 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. **6. Deploy to AKS** 옵션을 시작하려면 **6**을 입력합니다. 이 옵션은 AKS 자격 증명을 가져와 kubectl을 구성하고, API가 Microsoft Entra ID를 사용하여 Foundry에 인증할 수 있도록 AKS kubelet 관리 ID에 **Cognitive Services OpenAI User** 역할을 할당하고, 배포 매니페스트의 ACR 엔드포인트와 Foundry 엔드포인트를 업데이트한 다음 **kubectl apply**를 사용하여 두 매니페스트를 AKS 클러스터에 배포합니다. 작업이 완료되면 **9**를 입력하여 배포 스크립트를 종료합니다.

1. 터미널에서 다음 명령을 실행하여 배포를 확인합니다. **kubectl get deploy,svc**는 Deployment의 **READY**가 **1/1**(또는 복제본 수)이고 Service의 **EXTERNAL-IP**에 공개 IP가 표시되는지(**<pending>**가 아닌지) 확인합니다. 업데이트가 완료되면 rollout 명령은 **deployment "aks-api" successfully rolled out**를 출력합니다.

    ```
    kubectl get deploy,svc
    kubectl rollout status deploy/aks-api
    ```

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

이제 클라이언트 애플리케이션을 실행하여 API에서 여러 작업을 수행합니다. 앱은 메뉴 기반 인터페이스를 제공합니다.

1. 터미널에서 다음 명령을 실행하여 콘솔 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 연습 앞부분의 명령을 참고하여 환경을 활성화합니다.

    ```
    python main.py
    ```

1. **1. Check API Health (Liveness)** 옵션을 시작하려면 **1**을 입력합니다. 이 옵션은 API 컨테이너가 실행 중이며 상태 확인에 응답하는지 검증합니다. Kubernetes 활성 프로브에서 사용하는 것과 동일한 엔드포인트입니다.

1. **2. Check API Readiness (Foundry Connectivity)** 옵션을 시작하려면 **2**를 입력합니다. 이 옵션은 API가 Foundry 모델 엔드포인트에 성공적으로 연결할 수 있으며 추론 요청을 처리할 준비가 되었는지 확인합니다.

1. **3. Send Inference Request** 옵션을 시작하려면 **3**을 입력합니다. 이 옵션은 API에 프롬프트 하나를 보내고 배포된 모델에서 완전한 응답을 받습니다. 단일 추론 요청은 일괄 처리, 자동화된 작업 또는 추가 처리를 위해 전체 응답이 필요한 경우에 유용합니다.

1. **4. Start Chat Session (Streaming)** 옵션을 시작하려면 **4**를 입력합니다. 이 옵션은 모델이 응답을 생성하는 동안 실시간으로 응답을 스트리밍하는 대화형 채팅 세션을 시작합니다.

작업을 마치면 **5**를 입력하여 앱을 종료합니다.

## 리소스 정리

연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 연습 앞부분에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택한 경우 연습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

이 연습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure 리소스 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Microsoft Foundry 리소스의 **Provisioning State**가 **Succeeded**이고 **gpt-5-mini** 모델이 배포되었는지 확인합니다.
- Azure Container Registry(ACR)가 있고 **aks-api** 이미지가 포함되어 있는지 확인합니다.
- AKS 클러스터의 상태가 **Succeeded**이고 노드가 실행 중인지 확인합니다.

**AKS 클러스터 생성 실패 해결**
- 배포 스크립트를 실행하고 **5. Check deployment status** 옵션을 선택합니다. AKS 리소스를 만들기 전에 할당량 검증이 실패할 수 있고, 프로비전 후반의 실패로 클러스터 상태가 **Failed** 또는 **Canceled**가 될 수 있습니다.
- 오류에 **Standard_D2s_v7**을 사용할 수 없거나 해당 지역의 용량이 부족하다고 표시되면 옵션 **9**로 종료합니다. **AKS_VM_SIZE**를 배포 스크립트 상단에 나열된 v5 또는 v6 대체 크기 중 하나로 변경하거나 **location** 값을 다른 권장 지역으로 변경한 다음 옵션 **4. Create AKS cluster**를 다시 실행합니다.
- 오류에 할당량 부족이 표시되면 구독에 사용 가능한 Dsv5 계열 할당량이 있는 지역을 선택하거나 할당량 증가를 요청합니다. 다른 지역에 충분한 할당량이 있는 경우에만 지역 변경이 도움이 됩니다.
- 리소스 그룹이 다른 지역에 이미 있더라도 AKS 클러스터는 스크립트에 구성된 **location**을 사용합니다.
- 옵션 **5**에서 **Failed** 또는 **Canceled**가 보고되면 근본 문제를 해결하고 옵션 **4**를 다시 시도하기 전에 **8. Delete failed AKS deployment**를 실행합니다. AKS 리소스가 생성되지 않았다면 삭제할 필요가 없습니다.

**AKS 배포 상태 확인**
- **kubectl get pods**를 실행하여 API Pod가 실행 중인지 확인합니다. **Running** 상태인지 확인합니다.
- **kubectl get svc**를 실행하여 LoadBalancer 서비스에 외부 IP가 할당되었는지(**<pending>**가 아닌지) 확인합니다.
- 문제가 발생하면 **kubectl describe pod <pod-name>**을 실행하여 Pod 상태와 이벤트의 세부 정보를 확인합니다.
- **kubectl logs <pod-name>**을 실행하여 컨테이너 시작 오류나 런타임 문제를 확인합니다.

**YAML 파일 완전성 확인**
- 적절한 주석 표시 사이에 모든 YAML 섹션을 *deployment.yaml* 및 *service.yaml*에 올바르게 추가했는지 확인합니다.
- 잘못된 들여쓰기는 배포 실패를 일으키므로 YAML 들여쓰기가 올바른지 확인합니다(탭이 아닌 공백 사용).
- 배포 스크립트가 배포 매니페스트의 ACR 엔드포인트를 올바르게 대체했는지 확인합니다.

**클라이언트 연결 확인**
- API 엔드포인트가 LoadBalancer 서비스의 올바른 외부 IP를 사용하는지 확인합니다.
- 터미널에서 **curl http://<external-ip>/healthz**를 실행하여 API 엔드포인트에 연결할 수 있는지 확인합니다.

**Python 환경 및 종속성 확인**
- 클라이언트 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
- *client* 디렉터리에서 클라이언트를 실행하는지 확인합니다.
