---
lab:
  topic: 백엔드 서비스 통합
  title: Azure Web PubSub로 AI 조사 업데이트 스트리밍
  description: Azure Web PubSub를 통해 권한이 있는 인시던트 대응 담당자에게 하나의 AI 조사의 진행 상황, 일괄 처리된 조사 결과 및 완료 업데이트를 공유합니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Web PubSub
---

# Azure Web PubSub로 AI 조사 업데이트 스트리밍

Azure Web PubSub는 지속적인 클라이언트 연결을 관리하므로 백엔드가 자체 WebSocket 인프라를 관리하지 않고도 여러 관찰자에게 업데이트를 브로드캐스트할 수 있습니다. 오래 실행되는 AI 조사에서는 실시간 알림으로 대응 담당자에게 상황을 전달하고, 영구 저장소에는 브라우저 연결과 독립적으로 조사 결과를 보존합니다.

이 실습에서는 Azure Web PubSub와 Azure Blob Storage를 배포한 다음 Python Flask 앱을 완성하여 한 페이지에서 당직 개발자와 데이터베이스 전문가에게 하나의 조사를 공유합니다. 결정적 시뮬레이터가 가상의 데이터베이스 인시던트에 대한 진행 상황과 조사 결과를 제공하므로 AI 모델을 배포하지 않고도 전달 및 복구에 집중할 수 있습니다. 범위가 제한된 연결 정보를 생성하고, 이벤트를 기록하여 게시하며, 조사 결과를 일괄 처리한 뒤 두 대응 담당자에게 알립니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드합니다.
- Microsoft Entra ID 액세스를 사용하여 Azure Web PubSub와 Blob Storage를 배포합니다.
- 관찰자를 연결하고 저장된 조사 업데이트를 게시하는 Python 코드를 추가합니다.
- 앱을 실행하여 공유 전달, 독립적인 연결 및 연결 해제 후 복구를 확인합니다.

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

이 섹션에서는 리소스를 프로비저닝하고 로컬 앱을 실행하는 데 필요한 도구와 권한을 확인합니다.

실습을 완료하려면 다음이 필요합니다.

- Azure Web PubSub 및 스토리지 리소스 생성, 리소스 공급자 등록 및 Azure 역할 할당에 필요한 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/). 적절한 범위의 **Owner** 역할 또는 **Contributor**와 **Role Based Access Control Administrator** 역할의 조합이 리소스 생성 및 역할 할당에 필요한 권한을 제공합니다.
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상.
- 최신 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli). 이후 단계에서 **webpubsub** 확장을 설치하거나 업그레이드합니다.
- **선택 사항:** Python 코드의 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

배포에는 Web PubSub **Standard_S1** 계층과 **Standard_LRS** 스토리지 계정을 사용합니다. 프로비저닝된 동안 요금이 발생합니다. [Azure Web PubSub 가격](https://azure.microsoft.com/pricing/details/web-pubsub/)을 검토하고 실습을 완료하면 리소스를 삭제합니다.

## 프로젝트 시작 파일 다운로드 및 Azure Web PubSub 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 배포 스크립트를 실행하여 Azure Web PubSub, 스토리지 계정 및 프라이빗 Blob 컨테이너를 만듭니다. 그런 다음 Microsoft Entra ID 액세스를 확인하고 리소스 값을 터미널에 로드합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/azure-web-pubsub-python.zip
    ```

1. 프로젝트 작업에 사용할 위치로 파일을 복사하거나 이동한 다음 폴더에 압축을 해제합니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 맨 위의 두 값을 필요에 맞게 변경한 다음 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```python
    rg = "<your-resource-group-name>"  # Resource Group name
    location = "<your-azure-region>"   # Azure region for the resources
    ```

    실습 전용 리소스 그룹과 Azure Web PubSub를 지원하는 Azure 지역을 선택합니다.

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code 터미널 창을 엽니다.

1. 다음 명령을 실행하여 **Azure에 로그인**합니다. 안내에 따라 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 **실습에 필요한 리소스 공급자를 등록**합니다. 명령은 등록이 완료될 때까지 기다립니다. 배포 스크립트는 리소스를 만들기 전에 두 공급자가 모두 등록되었는지 확인합니다.

    ```
    az provider register --namespace Microsoft.SignalRService --wait
    az provider register --namespace Microsoft.Storage --wait
    ```

1. 다음 명령을 실행하여 **Web PubSub CLI 확장을 설치하거나 업그레이드**합니다. 배포 스크립트는 이 확장을 사용하여 Azure Web PubSub를 프로비저닝합니다.

    ```
    az extension add --upgrade --name webpubsub
    ```

1. 다음 명령을 실행하여 **배포 스크립트를 시작**합니다. 스크립트는 실습 리소스를 필요한 순서대로 프로비저닝하는 메뉴를 제공합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 표시되면 **1**을 입력하여 **1. Create Azure Web PubSub and assign its Entra role**를 실행합니다. 이 옵션은 다음을 만들거나 구성합니다.

    - 리소스 그룹이 없으면 리소스 그룹을 생성합니다.
    - 고유한 이름을 가진 Azure Web PubSub 리소스를 만들고 키 인증을 비활성화합니다.
    - 로그인한 ID에 Web PubSub 리소스 범위의 **Web PubSub Service Owner** 역할을 할당합니다. 백엔드는 이 역할로 Microsoft Entra 인증을 사용하여 클라이언트 연결 토큰을 생성하고 업데이트를 게시할 수 있습니다.

    스크립트는 작업이 완료될 때까지 기다리고 배포 실패를 보고합니다. 배포에 실패하면 **문제 해결** 섹션을 참조합니다. 각 메뉴 작업이 끝나면 **Enter**를 눌러 메뉴로 돌아갑니다.

1. **2**를 입력하여 **2. Create storage account and assign its Entra role**를 실행합니다. 이 옵션은 다음을 만들거나 구성합니다.

    - 고유한 이름을 가진 스토리지 계정을 만들고 공유 키 액세스와 익명 Blob 액세스를 비활성화합니다.
    - 로그인한 ID에 스토리지 계정 범위의 **Storage Blob Data Contributor** 역할을 할당합니다. 앱은 이 역할로 Microsoft Entra 인증을 사용하여 조사 상태와 결과를 만들고, 읽고, 업데이트할 수 있습니다.

1. **3**을 입력하여 **3. Create the private Blob container**를 실행합니다. 이 옵션은 Microsoft Entra ID를 사용하여 프라이빗 **investigations** 컨테이너를 만듭니다. 새 스토리지 역할 할당이 적용되는 동안 스크립트가 잠시 재시도합니다.

1. **4**를 입력하여 **4. Verify deployment and create environment files**를 실행합니다. 두 리소스 모두 **Succeeded**로 표시되고 Web PubSub 클라이언트 토큰 API 및 Blob 컨테이너 읽기 액세스 검사 결과가 **Ready**인지 확인합니다.

    확인에 성공하면 이 옵션은 앱에서 사용하는 **WEBPUBSUB_ENDPOINT**, **WEBPUBSUB_HUB**, **BLOB_ACCOUNT_URL**, **BLOB_CONTAINER** 값이 포함된 *.env*와 *.env.ps1*을 프로젝트 루트에 만듭니다.

1. **5**를 입력하여 배포 스크립트를 종료합니다.

1. 적절한 명령을 실행하여 **Web PubSub 및 Blob Storage 리소스 값을 터미널 세션에 로드**합니다.

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    **Bash**
    ```bash
    source .env
    ```

    > **참고:** 터미널을 열어 둡니다. 나중에 새 터미널을 열면 적절한 명령을 다시 실행하여 환경 변수를 다시 로드합니다.

## 앱 완성

이 섹션에서는 *client/webpubsub_functions.py*의 함수 네 개를 완성하여 범위가 제한된 연결 정보를 생성하고, 업데이트를 저장하여 게시하며, 조사 결과를 일괄 처리합니다. Flask 앱, 스토리지 도우미, 시뮬레이터 및 브라우저 인터페이스는 미리 작성되어 있습니다. 앱은 Web PubSub와 Blob Storage에 **DefaultAzureCredential**을 사용하며, **authorize()**는 조사를 시작할 수 있는 사용자를 조사의 소유자인 당직 개발자로 제한합니다. 두 대응 담당자 보기는 한 페이지에 있는 데모 역할이며 각각 로그인한 별도의 사용자가 아닙니다.

1. VS Code에서 *client/webpubsub_functions.py*를 엽니다. **BEGIN / END** 표시 밖에 있는 가져오기, 상수 및 도우미 함수는 변경하지 않습니다.

> **팁:** 코드 들여쓰기를 올바르게 유지하려면 코드를 왼쪽 여백의 첫 번째 열에 맞춰 붙여넣습니다. 붙여넣은 줄 전체를 선택하고 **Tab**을 눌러 **BEGIN / END** 표시와 정렬합니다. 필요하면 **Shift+Tab**을 눌러 들여쓰기를 줄입니다.

### 연결 정보를 생성하는 코드 추가

이 섹션에서는 관찰자가 선택한 조사 그룹에만 참여할 수 있도록 유효 기간이 짧은 연결 URL을 생성합니다.

**connection_details()** 함수는 액세스를 확인하고 해당 조사 그룹의 참여 또는 나가기 권한만 있는 단기 URL을 요청합니다. 브라우저는 URL을 사용하여 연결하고 그룹에 참여하며, 메시지를 게시할 수는 없습니다.

1. **# BEGIN GENERATE CONNECTION DETAILS** 주석을 찾고 그 아래에 다음 코드를 추가합니다.

    ```python
    def connection_details(
        client: WebPubSubServiceClient, operation: Operation, observer: str,
    ) -> dict[str, str]:
        """Issue a short-lived connection URL and the authorized investigation group."""
        authorize(operation, observer)
        group = group_name(operation.operation_id)
        # Scope group membership permission to this investigation; do not grant send permission.
        token = client.get_client_access_token(
            user_id=observer,
            roles=[f"webpubsub.joinLeaveGroup.{group}"],
            minutes_to_expire=5,
        )
        return {"url": token["url"], "group": group}
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 이벤트를 기록하는 코드 추가

이 섹션에서는 실시간 전달을 시도하기 전에 조사 업데이트를 영구 저장하여 연결이 끊어진 관찰자가 나중에 현재 상태를 복구할 수 있도록 합니다.

**record_event()** 함수는 미리 제공된 **OperationStore.record()** 메서드에 작업을 위임합니다. 이 메서드는 저장된 조사를 업데이트하고 작업 ID, 이벤트 유형, 페이로드, 시퀀스 번호 및 고정된 이벤트 ID가 포함된 이벤트 봉투를 반환합니다. 브라우저는 시퀀스 정보를 사용하여 중복 이벤트를 무시하고, 누락을 감지하면 저장된 스냅샷과 보기의 상태를 일치시킵니다.

1. **# BEGIN RECORD EVENT** 주석을 찾고 그 아래에 다음 코드를 추가합니다.

    ```python
    def record_event(
        store: OperationStore, operation_id: str,
        event_type: EventType, payload: dict[str, object],
    ) -> Event:
        """Persist an investigation update and return its sequenced event envelope."""
        return store.record(operation_id, event_type, payload)
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 이벤트를 게시하는 코드 추가

이 섹션에서는 저장된 각 이벤트를 조사의 Web PubSub 그룹에 게시하고, 저장된 조사 결과를 버리지 않으면서 일시적인 전달 실패를 처리합니다.

**publish_event()** 함수는 JSON 이벤트로 **send_to_group()**을 호출합니다. 최대 세 번 전달을 시도하며 재시도 사이에 잠시 기다립니다. 계속 실패하면 전달 경고를 기록하고 처리를 계속합니다. 전송에 성공하면 경고를 해제합니다. 재시도로 중복 알림이 발생할 수 있으므로 브라우저는 정확히 한 번 전달된다고 가정하지 않고 이벤트의 고정된 ID와 시퀀스를 사용합니다.

1. **# BEGIN PUBLISH EVENT** 주석을 찾고 그 아래에 다음 코드를 추가합니다.

    ```python
    def publish_event(
        client: WebPubSubServiceClient, store: OperationStore, event: Event,
    ) -> None:
        """Deliver a stored event with bounded retries and track live-delivery problems."""
        for attempt in range(PUBLISH_ATTEMPTS):
            try:
                client.send_to_group(
                    group=group_name(event["operation_id"]),
                    message=event, content_type="application/json",
                )
            except AzureError as exc:
                logger.warning(
                    "Delivery attempt %s failed for event %s (%s).",
                    attempt + 1, event["event_id"], type(exc).__name__,
                )
                if attempt + 1 < PUBLISH_ATTEMPTS:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                # Keep processing: observers can recover stored findings after reconnecting.
                store.delivery_problem(
                    event["operation_id"],
                    "Live delivery failed. Findings remain stored; reconnect this view to recover them.",
                )
                return
            store.delivery_problem(event["operation_id"], None)
            return
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 조사를 실행하는 코드 추가

이 섹션에서는 시뮬레이터를 영구 저장 및 전달 작업과 연결하고, 조사 결과를 일괄 처리하여 게시합니다.

**run_investigation()** 함수는 진행 상황과 조사 결과를 게시하기 전에 기록하고, 마지막 배치를 내보낸 다음 저장된 결과에 대한 참조를 게시합니다. 처리에 실패하면 조사가 아직 실행 중일 때만 실패 이벤트를 발생시킵니다. 전달 실패는 작업자를 중지하지 않습니다.

1. **# BEGIN RUN INVESTIGATION** 주석을 찾고 그 아래에 다음 코드를 추가합니다.

    ```python
    def run_investigation(
        store: OperationStore,
        client: WebPubSubServiceClient,
        operation_id: str,
        fragments: Callable[[], Iterable[tuple[str, str, int]]] = simulate,
    ) -> None:
        """Batch simulated findings, store each update, and notify connected observers."""
        def emit(event_type: EventType, payload: dict[str, object]) -> None:
            # Persist first so a missed live message does not lose investigation state.
            event = record_event(store, operation_id, event_type, payload)
            publish_event(client, store, event)

        pending: list[str] = []
        current_stage = ""
        try:
            for stage, fragment, progress in fragments():
                if stage != current_stage:
                    emit("progress", {"stage": stage, "progress": progress})
                    current_stage = stage
                pending.append(fragment)
                # Batch small fragments to reduce live-message traffic.
                if len(pending) == BATCH_FRAGMENTS:
                    emit("findings", {"text": "".join(pending)})
                    pending.clear()
            if pending:
                emit("findings", {"text": "".join(pending)})
            # Publish a reference to the stored result rather than resending all findings.
            emit("completed", {"result_ref": f"/api/operations/{operation_id}/result"})
        except (AzureError, ValueError, RuntimeError) as exc:
            logger.exception("Investigation %s failed (%s).", operation_id, type(exc).__name__)
            operation, _ = store.load(operation_id)
            # Do not replace a terminal status if the failure occurred after completion.
            if operation.status == "running":
                emit("failed", {"error": "The investigation failed. Check the backend terminal for details."})
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

## Python 환경 구성

이 섹션에서는 클라이언트 앱 디렉터리로 이동하고 Python 가상 환경을 만든 뒤 활성화하여 버전이 고정된 애플리케이션 종속성을 설치합니다.

1. 다음 명령을 실행하여 **클라이언트 디렉터리로 이동**합니다. 생성된 리소스 값을 로드한 터미널을 그대로 사용합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 **가상 환경을 생성**합니다. 가상 환경은 실습 종속성을 다른 Python 프로젝트와 분리합니다.

    ```
    python -m venv .venv
    ```

1. 적절한 명령을 실행하여 **Python 가상 환경을 활성화**합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 실행합니다.

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

1. 다음 명령을 실행하여 **앱 종속성을 설치**합니다. 종속성에는 Flask, Microsoft Entra 인증, Web PubSub 및 Blob Storage SDK가 포함됩니다.

    ```
    pip install -r requirements.txt
    ```

## 앱 실행

이 섹션에서는 하나의 백엔드 조사가 두 대응 담당자 보기에 업데이트를 보내는지 확인합니다. 그런 다음 한 보기의 연결을 끊고 다른 작업자를 시작하지 않고도 조사 결과를 복구합니다.

1. 다음 명령을 실행하여 **Flask 앱을 시작**합니다. 가상 환경이 활성화되어 있고 이 터미널에 Web PubSub 및 Blob Storage 환경 변수가 로드되어 있는지 확인합니다. 브라우저를 사용하는 동안 터미널에서 앱을 계속 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다. 페이지에는 **조사 작업(Investigation actions)**, **당직 개발자(On-call developer)**, **데이터베이스 전문가(Database specialist)**가 표시됩니다.

1. **조사 만들기(Create investigation)**를 선택합니다. 앱은 Blob Storage에 새 조사를 저장하고 두 대응 담당자 보기를 해당 Web PubSub 그룹에 연결합니다. 두 **연결(Connection)** 표시가 모두 **Connected**이고 **처리(Processing)**가 **pending**인지 확인합니다.

1. **조사 시작(Start investigation)**을 선택합니다. 작업은 조사의 소유자인 당직 개발자 역할로 실행됩니다. 두 보기가 **애플리케이션 로그 검사(Inspecting application logs)**, **데이터베이스 연결 검사(Inspecting database connections)**, **조사 결과 준비(Preparing the investigation result)** 단계를 거치는지 확인합니다.

    조사 결과는 시뮬레이션된 조각마다 메시지 하나를 보내는 대신 배치로 도착합니다. **실시간 이벤트(Live events)** 카운터가 증가해야 합니다. 이는 보기가 저장된 스냅샷을 검색하기만 하는 것이 아니라 Web PubSub 메시지를 수신하고 있음을 나타냅니다.

1. 두 보기가 모두 **Processing: completed**와 꽉 찬 진행률 표시줄을 표시할 때까지 기다립니다. 비프로덕션 환경에서 수정 사항을 검증하라는 최종 권장 사항을 포함하여 동일하게 누적된 조사 결과가 표시되는지 확인합니다. 각 보기에는 **Worker starts: 1**이 표시되어야 합니다.

    **시퀀스(Sequence)**에는 저장된 스냅샷을 통해 복구된 업데이트도 포함됩니다. **Live events**는 이 페이지에서 수신한 새 Web PubSub 알림만 셉니다. 정상적인 전달에서는 **무시한 중복(Duplicates ignored)**이 0일 수 있습니다. **Worker starts: 1**은 두 번째 관찰자의 연결이 다른 조사 작업자를 시작하지 않았음을 확인합니다.

1. **Create investigation**을 다시 선택한 다음 **Start investigation**을 선택합니다. 조사 결과가 나타나기 시작하면 **Database specialist** 보기에서 **연결 해제(Disconnect)**를 선택합니다.

    연결이 **Disconnected by you**로 바뀌는지 확인합니다. 해당 보기의 조사 결과는 더 이상 업데이트되지 않지만 **On-call developer** 보기는 같은 실행 중인 조사에서 결과를 계속 수신합니다. 시뮬레이션 분석은 일반적으로 서비스 요청 시간을 제외하고 약 10초가 걸립니다.

1. 당직 개발자 보기가 **completed**가 될 때까지 기다린 다음 데이터베이스 전문가 보기에서 **다시 연결(Reconnect)**을 선택합니다.

    보기가 연결을 설정하고 조사 그룹에 다시 참여한 뒤 현재 저장된 스냅샷을 검색합니다. 전체 조사 결과와 **completed** 상태가 **Worker starts: 1**과 함께 복구되는지 확인합니다. 스냅샷은 놓친 알림을 하나씩 재생하지 않고 상태를 복원하므로 **Live events** 수는 더 적을 수 있습니다.

1. URL을 바꾸지 않고 페이지를 새로 고칩니다. URL에 선택한 조사 ID가 포함되어 있으므로 두 보기는 해당 조사에 다시 연결하고 저장된 상태를 복원합니다. 다른 조사를 시작하지 않고 완료된 조사 결과가 다시 표시되는지 확인합니다.

    작업자는 Azure Web PubSub가 아니라 로컬 Flask 프로세스에서 실행됩니다. Blob Storage는 저장된 상태를 보존하지만 Flask를 다시 시작해도 완료되지 않은 작업은 재개되지 않습니다. 연결 해제 및 새로 고침 확인 중에는 백엔드를 계속 실행합니다.

1. 브라우저를 닫고 VS Code 터미널로 돌아가 **Ctrl+C**를 눌러 앱을 중지합니다.

## 리소스 정리

실습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹의 모든 리소스를 삭제합니다. **\<rg-name>**을 실습에서 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 실습에 기존 리소스 그룹을 사용한 경우 실습 범위 밖의 기존 리소스도 삭제됩니다.

## 문제 해결

이 섹션에서는 실시간 연결 상태와 조사 처리 상태를 구분하면서 배포, 인증 및 전달 문제를 진단합니다.

**배포 실패 해결**

- 계정에 리소스 생성, 공급자 등록 및 Azure 역할 할당 권한이 있는지 확인합니다. **Contributor** 역할만으로는 역할을 할당할 수 없습니다.
- Web PubSub SKU를 사용할 수 없거나 지역의 용량이 부족하거나 구독 할당량이 부족하면 다른 지원 지역을 선택하거나 필요한 할당량을 요청합니다.
- 지역을 변경하려면 스크립트를 종료하고 *azdeploy.py* 구분선 위의 **location**을 업데이트합니다. 기존 리소스는 지역을 옮길 수 없습니다. 같은 이름으로 재배포하기 전에 이전 지역의 실습 리소스를 제거하거나 새 전용 리소스 그룹을 사용합니다.
- Web PubSub는 메뉴 옵션 **1**, 스토리지는 **2**를 다시 시도합니다. 스크립트는 실패 또는 취소된 리소스를 감지하여 삭제하고, 삭제가 완료될 때까지 기다린 뒤 생성을 다시 시도합니다. 관련 없는 리소스는 삭제하지 않습니다.
- 공급자 등록이 진행 중이면 등록 명령이 완료될 때까지 기다린 뒤 배포를 다시 시도합니다.

**Microsoft Entra 액세스 확인**

- 배포와 로컬 SDK 인증에 같은 Azure 계정을 사용합니다. Azure CLI 세션이 만료되면 로그인 단계를 반복합니다.
- 메뉴 옵션 **1**은 **Web PubSub Service Owner**, 옵션 **2**는 **Storage Blob Data Contributor**를 할당합니다. 새 할당이 적용되는 데 몇 분이 걸릴 수 있습니다.
- 컨테이너 생성 시 권한 오류가 보고되면 역할이 적용될 시간을 기다린 뒤 옵션 **3**을 다시 시도합니다. 앱을 시작하기 전에 두 데이터 평면 검사가 모두 성공할 때까지 옵션 **4**를 다시 시도합니다.
- 액세스 오류를 우회하려고 키 인증을 활성화하거나 서비스 키를 추가하지 않습니다. 실습은 서비스 요청에 **DefaultAzureCredential**을 사용합니다.

**생성된 구성 확인**

- 앱의 프로세스 환경에는 **WEBPUBSUB_ENDPOINT**, **WEBPUBSUB_HUB**, **BLOB_ACCOUNT_URL**, **BLOB_CONTAINER**가 필요합니다.
- 메뉴 옵션 **4**는 확인에 성공한 뒤에만 *.env*와 *.env.ps1*을 생성합니다. 구성을 다시 생성하려면 이 옵션을 다시 실행하며 파일을 수동으로 편집하지 않습니다.
- 앱을 시작할 터미널에서 생성된 파일을 로드합니다. 프로젝트 루트에서 Bash는 **source .env**, PowerShell은 **. .\.env.ps1**을 실행한 뒤 *client*로 이동합니다. *client*에서는 대신 **source ../.env** 또는 **. ..\.env.ps1**을 사용합니다.
- 배포 설정을 변경한 뒤에는 값을 다시 생성하고 로드한 다음 앱을 다시 시작합니다.

**코드 완성 여부 및 종속성 확인**

- 네 코드 블록이 모두 *webpubsub_functions.py*의 해당 **BEGIN / END** 표시 안에 있는지 확인합니다. 중첩된 **emit()** 도우미는 **run_investigation()** 내부에 유지하고 공백을 사용하여 일관되게 들여씁니다.
- 미리 작성된 **authorize()** 도우미와 앱, 스토리지, 시뮬레이터 및 브라우저 파일은 변경하지 않습니다.

**Python 환경 확인**

- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- *requirements.txt*의 모든 패키지가 설치되었는지 확인합니다. 필요하면 환경을 활성화하고 *client* 디렉터리에서 **pip install -r requirements.txt**를 실행합니다.
- *client* 디렉터리에서 **python app.py**를 실행합니다. Python 실행 파일 이름이 **python3**뿐인 시스템에서는 배포 스크립트, 가상 환경 생성 및 앱 시작에 해당 실행 파일을 사용합니다.

**연결 실패 또는 실시간 업데이트 누락 조사**

- Flask 터미널과 브라우저 오류 메시지를 확인합니다. 두 대응 담당자 보기가 모두 조사 그룹에 참여해야 합니다. 백엔드가 실행 중이라는 사실만으로 실시간 전달을 확인할 수는 없습니다.
- 브라우저가 보안 WebSocket을 통해 Web PubSub 엔드포인트에 연결하고 **esm.sh**에서 JavaScript SDK를 로드할 수 있는지 확인합니다. 회사 방화벽, 프록시 또는 브라우저 확장이 두 연결 중 하나를 차단할 수 있습니다.
- **Connection failed**, **Group recovery failed** 또는 **Stopped**가 나타나면 보고된 문제를 해결하고 해당 보기에서 **Reconnect**를 선택합니다.
- **completed** 상태인데 **Live events** 수가 0이면 보기가 실시간 전달이 아닌 스냅샷을 통해 복구되었을 수 있습니다. 새 조사를 만들고 시작 전에 두 보기를 모두 연결한 다음 실행 중 카운터가 증가하는지 확인합니다.
- 앱이 실시간 전달 경고를 보고해도 조사 결과는 Blob Storage에 남아 있습니다. 서비스 액세스 또는 네트워크 문제를 해결하고 해당 보기를 다시 연결하여 저장된 상태를 복구합니다.
- 작업에서 알 수 없는 관찰자 컨텍스트를 보고하거나 새로 고침을 요청하면 페이지를 새로 고쳐 현재 데모 컨텍스트 및 요청 보호 토큰을 받습니다.

**중단된 처리 이해**

- Flask가 계속 실행 중이면 대응 담당자의 연결을 해제하거나 브라우저를 새로 고쳐도 작업자가 중지되지 않습니다.
- Flask를 중지하면 백그라운드 작업자가 중지됩니다. 다음 시작 시 앱은 완료되지 않은 실행 중 조사를 재개하는 대신 **interrupted**로 표시합니다.
- 백엔드를 다시 시작한 후 분석을 다시 실행하려면 새 조사를 만듭니다. 실습 중 같은 컨테이너를 대상으로 여러 Flask 인스턴스를 실행하지 않습니다.