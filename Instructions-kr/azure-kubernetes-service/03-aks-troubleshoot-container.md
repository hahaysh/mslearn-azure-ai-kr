---
lab:
  topic: Azure Kubernetes Service
  title: Azure Kubernetes Service에서 앱 문제 해결
  description: 레이블 불일치, CrashLoopBackOff 오류, 준비 프로브 실패 등 일반적인 Kubernetes 문제를 진단하고 해결하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
---

# Azure Kubernetes Service에서 앱 문제 해결

이 연습에서는 컨테이너화된 API를 Azure Kubernetes Service(AKS)에 배포한 다음 일반적인 Kubernetes 문제를 진단하고 해결합니다. **kubectl** 명령을 사용하여 문제를 식별하고, Pod 상태를 검사하고, 로그를 확인하고, 이벤트를 살펴봅니다. 그런 다음 **kubectl edit**을 사용하여 Service 선택기 불일치, 누락된 환경 변수, 잘못된 준비 프로브 경로를 포함한 잘못된 구성을 수정합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure에 리소스 배포(ACR, AKS 클러스터)
- 일반적인 문제를 진단하고 해결
- Azure 리소스 정리

이 연습을 완료하는 데 약 **30**분이 걸립니다.

>**중요:** Azure 무료 크레딧에서는 Azure Container Registry 작업 실행이 일시 중지되어 있습니다. 이 연습에는 종량제 또는 다른 유료 플랜이 필요합니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Kubernetes 명령줄 도구인 [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Python 3.12](https://www.python.org/downloads/) 이상

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 콘솔 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Azure 리소스 배포에는 10~15분이 걸릴 수 있습니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aks-troubleshoot-python.zip
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

1. ACR 리소스를 만든 후 **2**를 입력하여 **Build and push API image to ACR**을 시작합니다. 이 옵션은 ACR 작업을 사용하여 이미지를 빌드하고 ACR 리포지토리에 추가합니다. 이 작업을 완료하는 데 3~5분이 걸릴 수 있습니다.

1. 이미지가 빌드되어 ACR에 푸시된 후 **3**을 입력하여 **Create AKS cluster** 옵션을 시작합니다. 이 옵션은 관리 ID로 구성된 AKS 리소스를 만들고, ACR 리소스에서 이미지를 가져올 수 있는 권한을 서비스에 부여합니다.

1. AKS 클러스터 배포가 완료된 후 **4**를 입력하여 **Get AKS credentials for kubectl** 옵션을 시작합니다. 이 옵션은 **az aks get-credentials** 명령을 사용하여 자격 증명을 가져오고 **kubectl**을 구성합니다.

1. 자격 증명이 설정된 후 **5**를 입력하여 **Deploy application to AKS** 옵션을 시작합니다. 이 옵션은 AKS 클러스터에 API를 배포합니다.

1. 앱이 배포된 후 **6**을 입력하여 **Check deployment status** 옵션을 시작합니다. 이 옵션은 각 리소스가 성공적으로 배포되었는지 보고합니다.

    모든 서비스가 **successful** 메시지를 반환하면 **8**을 입력하여 배포 스크립트를 종료합니다.

    AKS 클러스터 상태가 **Failed** 또는 **Canceled**이면 보고된 문제를 해결한 다음 **7**을 입력하여 **Delete failed AKS deployment** 옵션을 시작한 후 옵션 **3**을 다시 실행합니다. 이 보호 기능이 적용된 옵션은 정상 상태이거나 진행 중인 클러스터를 삭제하지 않습니다.

>**참고:** 터미널을 열어 둡니다. 연습의 모든 단계는 터미널에서 수행합니다.

## 배포 문제 해결

배포 스크립트는 모든 Kubernetes 리소스를 **aks-troubleshoot**라는 **namespace**에 만들었습니다. Namespace는 Kubernetes 클러스터 내에서 리소스를 구성하고 격리하는 방법입니다. 관련 리소스를 그룹화하고, 리소스 할당량을 적용하고, 액세스 제어를 관리할 수 있습니다. Namespace를 지정하지 않으면 리소스가 **default** namespace에 생성됩니다. 이 연습의 모든 **kubectl** 명령에는 올바른 namespace를 대상으로 하도록 **-n aks-troubleshoot**가 포함됩니다.

배포를 확인한 다음 세 가지 문제 해결 시나리오를 진행합니다. 각 시나리오에서 배포에 특정 오류를 일으키는 매니페스트 파일을 적용합니다. 그런 다음 **kubectl** 명령을 사용하여 문제를 진단하고 구성을 편집하여 해결합니다.

### 배포 확인

이 섹션에서는 오류를 발생시키기 전에 설정 스크립트로 배포한 애플리케이션이 올바르게 실행 중인지 확인합니다.

1. 다음 명령을 실행하여 namespace에서 Pod가 실행 중인지 확인합니다. 명령은 **Running** 상태이며 READY 열에 **1/1**로 표시된 Pod 하나를 반환해야 합니다.

    ```
    kubectl get pods -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Service에 엔드포인트가 있는지 확인합니다. 명령은 IP 주소가 나열된 엔드포인트 슬라이스 하나를 반환해야 합니다.

    ```
    kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 포트 전달을 통해 연결을 테스트합니다. 이 명령은 로컬 컴퓨터에서 클러스터의 Service까지 터널을 만들어 **http://localhost:8080**에서 액세스할 수 있게 합니다.

    ```
    kubectl port-forward service/api-service 8080:80 -n aks-troubleshoot
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 두 번째 터미널 창을 엽니다. 다음 명령을 실행하여 연결을 테스트합니다. **"status": "healthy"**가 포함된 JSON 응답이 반환되어야 합니다.

    ```bash
    # Bash
    curl http://localhost:8080/healthz
    ```

    ```powershell
    # PowerShell
    Invoke-RestMethod http://localhost:8080/healthz
    ```

1. **port-forward**가 실행 중인 터미널로 돌아가 **ctrl+c**를 입력하여 명령을 종료합니다.

배포가 정상적으로 작동하는 것을 확인했습니다. 이제 레이블 불일치 문제를 진단합니다.

### 레이블 불일치 진단

Service는 레이블 선택기에 따라 Pod로 트래픽을 라우팅합니다. 레이블이 일치하지 않으면 Service에 엔드포인트가 없어 요청이 실패합니다. API는 **app: api** 레이블이 지정된 Pod와 **app: api**에 일치하는 Service 선택기로 배포되었습니다. 이 섹션에서는 선택기를 **app: api-v2**로 변경하여 연결을 끊는 Service 구성을 적용합니다.

1. 다음 명령을 실행하여 레이블 불일치 오류를 일으키는 Service 구성을 적용합니다.

    ```
    kubectl apply -f k8s/label-mismatch-service.yaml -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Pod가 여전히 실행 중인지 확인합니다. Pod는 **Running** 상태와 **1/1** 준비 상태를 표시하며 레이블에는 **app=api**가 표시됩니다.

    ```
    kubectl get pods --show-labels -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Service 엔드포인트 슬라이스를 확인합니다. ENDPOINTS 열에 **<unset>**이 표시된 엔드포인트 슬라이스가 반환되어야 합니다. 이는 Service 선택기와 일치하는 Pod가 없음을 나타냅니다.

    ```
    kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Service 세부 정보를 봅니다. 출력에서 **Selector** 필드를 찾습니다. 이제 **app=api-v2**로 표시됩니다.

    ```
    kubectl describe service api-service -n aks-troubleshoot
    ```

    이 결과는 레이블 불일치를 확인해 줍니다. Service 선택기는 **app=api-v2**이지만 Pod 레이블은 **app=api**입니다.

1. 다음 명령을 실행하여 편집기에서 Service 구성을 엽니다.

    ```
    kubectl edit service api-service -n aks-troubleshoot
    ```

    **참고:** **kubectl edit** 명령은 클러스터에서 라이브 리소스 구성을 가져와 로컬 텍스트 편집기에서 엽니다. 변경 내용을 저장하고 편집기를 닫으면 kubectl이 변경 내용을 Kubernetes API 서버로 자동 전송하고, 서버에서 유효성을 검사한 후 실행 중인 클러스터에 적용합니다. 편집기는 환경에 따라 다릅니다.

    - **Bash:** 기본적으로 **vi**가 열립니다. **i**를 눌러 삽입 모드로 전환하고 변경한 다음 **Esc**를 누르고 **:wq**를 입력한 후 **Enter**를 눌러 저장하고 종료합니다. 저장하지 않고 종료하려면 **:q!**를 입력합니다.
    - **PowerShell (Windows):** 기본적으로 **Notepad**가 열립니다. 변경한 다음 **파일(File) > 저장(Save)**(또는 **Ctrl+S**)을 선택하고 창을 닫습니다. 저장하지 않고 닫으면 편집이 취소됩니다.

1. 편집기에서 **selector** 섹션을 찾아 **app: api-v2**를 **app: api**로 변경합니다. 변경 내용을 저장하고 편집기를 닫습니다.

1. 다음 명령을 실행하여 엔드포인트 슬라이스 주소가 복원되었는지 확인합니다. IP 주소가 나열된 엔드포인트 슬라이스가 반환되어야 합니다.

    ```
    kubectl get endpointslices -l kubernetes.io/service-name=api-service -n aks-troubleshoot
    ```

레이블 불일치 문제를 해결했습니다. 이제 CrashLoopBackOff를 진단합니다.

### CrashLoopBackOff 진단

컨테이너 시작에 실패하면 Kubernetes가 컨테이너를 반복해서 다시 시작하므로 **CrashLoopBackOff** 상태가 됩니다. 로그를 읽으면 애플리케이션이 충돌한 이유를 확인할 수 있습니다.

1. 다음 명령을 실행하여 필수 **API_KEY** 환경 변수를 제거하는 배포 구성을 적용합니다.

    ```
    kubectl apply -f k8s/crashloop-deployment.yaml -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Pod 상태를 확인합니다. 잠시 후 Pod가 **CrashLoopBackOff** 상태가 됩니다. **ctrl-c**를 입력하여 명령을 종료합니다.

    ```
    kubectl get pods -n aks-troubleshoot -w
    ```

1. 다음 명령을 실행하여 오류 메시지에 대한 Pod 로그를 확인합니다. 환경 변수가 누락되었음을 나타내는 오류가 표시되어야 합니다.

    ```
    kubectl logs -l app=api -n aks-troubleshoot
    ```

1. Deployment를 편집하여 **API_KEY** 환경 변수를 추가함으로써 문제를 해결합니다.

    ```
    kubectl edit deployment api-deployment -n aks-troubleshoot
    ```

    편집기에서 **spec.template.spec** 아래의 **containers** 섹션을 찾습니다. **name: api** 줄을 찾아 들여쓰기 수준이 **name**과 일치하도록 바로 아래에 **env** 블록을 추가합니다.

    ```yaml
        name: api
        env:
        - name: API_KEY
          value: "demo-api-key-12345"
        ports:
    ```

    변경 내용을 저장하고 편집기를 닫습니다.

1. 다음 명령을 실행하여 Pod 상태를 확인합니다. 잠시 후 Pod가 **Running** 상태가 됩니다. **ctrl-c**를 입력하여 명령을 종료합니다.

    ```
    kubectl get pods -n aks-troubleshoot -w
    ```

CrashLoopBackOff 문제를 해결했습니다. 이제 준비 프로브 실패를 진단합니다.

### 준비 프로브 실패 진단

준비 프로브가 실패하면 Pod는 **Running**으로 표시되지만 컨테이너의 준비 상태는 **0/1**입니다. Kubernetes는 준비 상태 확인을 통과할 때까지 Pod를 Service 엔드포인트에 추가하지 않습니다. 롤링 업데이트 전략에서는 새 Pod가 준비되지 않은 상태에 머무는 동안 기존의 정상 Pod가 계속 트래픽을 처리합니다.

1. 다음 명령을 실행하여 준비 프로브 실패를 일으키는 배포 구성을 적용합니다. 준비 상태 확인에 잘못된 경로를 적용합니다.

    ```
    kubectl apply -f k8s/probe-failure-deployment.yaml -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 Pod 상태를 확인합니다. Pod 두 개가 표시되어야 합니다. 새 Pod는 **Running**이지만 READY 열에서 **0/1**로 표시되고, 기존 Pod는 계속 **1/1** 준비 상태를 유지합니다. 새 Pod가 준비되지 않아 롤링 업데이트가 차단됩니다.

    ```
    kubectl get pods -n aks-troubleshoot
    ```

1. 다음 명령을 실행하여 프로브 실패 이벤트를 확인합니다. 이 명령은 준비 프로브와 활성 프로브 실패를 모두 포함하는 **Unhealthy** 이벤트를 반환합니다. 준비 프로브가 404 상태 코드로 실패했다는 메시지를 찾습니다.

    ```
    kubectl get events -n aks-troubleshoot --field-selector reason=Unhealthy
    ```

1. 다음 명령을 실행하여 Deployment를 편집하고 경로를 수정함으로써 준비 프로브 문제를 해결합니다.

    ```
    kubectl edit deployment api-deployment -n aks-troubleshoot
    ```

    편집기에서 **readinessProbe** 섹션을 찾아 **path: /invalid-path**를 **path: /healthz**로 변경합니다. 변경 내용을 저장하고 편집기를 닫습니다.

1. 다음 명령을 실행하여 새 Pod가 준비되고 기존 Pod가 종료되는지 확인합니다. **Running** 상태이고 READY 열에 **1/1**로 표시된 Pod 하나만 보여야 합니다.

    ```
    kubectl get pods -n aks-troubleshoot
    ```

준비 프로브 오류를 진단하고 해결했습니다. 이제 종단 간 연결을 확인합니다.

### 종단 간 연결 확인

모든 문제 해결 시나리오를 완료한 후 애플리케이션이 완전히 작동하는지 확인합니다.

1. 다음 명령을 실행하여 포트 전달로 Service에 액세스합니다.

    ```
    kubectl port-forward service/api-service 8080:80 -n aks-troubleshoot
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 두 번째 터미널 창을 엽니다. 다음 명령을 실행하여 모든 엔드포인트를 테스트합니다.

    ```bash
    # Bash
    curl http://localhost:8080/healthz
    curl http://localhost:8080/readyz
    curl http://localhost:8080/api/info
    ```

    ```powershell
    # PowerShell
    Invoke-RestMethod http://localhost:8080/healthz
    Invoke-RestMethod http://localhost:8080/readyz
    Invoke-RestMethod http://localhost:8080/api/info
    ```

1. 다음 명령을 실행하여 요청을 확인할 Pod 로그를 봅니다.

    ```
    kubectl logs -l app=api -n aks-troubleshoot
    ```

애플리케이션이 완전히 작동하는 것을 확인했습니다. 이제 리소스를 정리합니다.

## 리소스 정리

연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 연습 앞부분에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹 삭제 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택한 경우 연습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

이 연습을 설정하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**배포 스크립트로 배포 상태 확인**
- 배포 스크립트를 실행하고 **6. Check deployment status** 옵션을 선택하여 배포된 모든 리소스의 상태를 확인합니다.
- 이 명령은 ACR 프로비저닝 상태, AKS 클러스터 프로비저닝 상태, Kubernetes 리소스 가용성을 확인합니다.
- 이 출력을 사용하여 문제를 일으키는 구성 요소를 식별합니다.

**AKS 클러스터 생성 실패 해결**
- AKS 리소스를 만들기 전에 할당량 검증이 실패할 수 있고, 프로비전 후반의 실패로 클러스터 상태가 **Failed** 또는 **Canceled**가 될 수 있습니다.
- 오류에 **Standard_D2s_v7**을 사용할 수 없거나 해당 지역의 용량이 부족하다고 표시되면 옵션 **8**로 종료합니다. **AKS_VM_SIZE**를 배포 스크립트 상단에 나열된 v5 또는 v6 대체 크기 중 하나로 변경하거나 **location** 값을 변경한 다음 **3. Create AKS cluster** 옵션을 다시 실행합니다.
- 오류에 할당량 부족이 표시되면 구독에 사용 가능한 Dsv5 계열 할당량이 있는 지역을 선택하거나 할당량 증가를 요청합니다. 다른 지역에 충분한 할당량이 있는 경우에만 지역 변경이 도움이 됩니다.
- 리소스 그룹이 다른 지역에 이미 있더라도 AKS 클러스터는 스크립트에 구성된 **location**을 사용합니다.
- 옵션 **6**에서 **Failed** 또는 **Canceled**가 보고되면 근본 문제를 해결하고 옵션 **3**을 다시 시도하기 전에 **7. Delete failed AKS deployment**를 실행합니다. AKS 리소스가 생성되지 않았다면 삭제할 필요가 없습니다.

**ACR 이미지 가져오기 오류**
- Pod 상태가 **ImagePullBackOff** 또는 **ErrImagePull**이면 ACR 리소스가 생성되었고 이미지가 성공적으로 푸시되었는지 확인합니다.
- 필요한 경우 배포 스크립트 옵션 **2. Build and push API image to ACR**을 다시 실행합니다.
- 배포 스크립트 출력에서 역할 할당이 성공했는지 확인하여 AKS 클러스터에 ACR에서 가져올 권한이 있는지 확인합니다.

**kubectl 연결 문제**
- kubectl 명령에서 연결 오류가 발생하면 배포 스크립트 옵션 **4. Get AKS credentials for kubectl**을 실행하여 자격 증명을 새로 고칩니다.
- Azure portal에서 확인하거나 **az aks show --resource-group <rg-name> --name <aks-name> --query provisioningState**를 실행하여 AKS 클러스터가 실행 중인지 확인합니다.

**연습 초기화**
- 문제 해결 시나리오를 다시 시작해야 하는 경우 배포 스크립트 옵션 **5. Deploy application to AKS**를 실행하여 원래 작동하던 구성을 다시 배포합니다.
- 이 옵션은 기본 배포 및 서비스 파일을 다시 적용하여 연습 중 변경한 내용을 초기화합니다.
