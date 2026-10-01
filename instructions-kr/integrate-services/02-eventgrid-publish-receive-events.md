---
lab:
  topic: 백엔드 서비스 통합
  title: Azure Event Grid를 사용하여 이벤트 게시 및 수신
  description: 풀 배달 및 필터링된 구독을 사용하여 Azure Event Grid Namespaces에서 콘텐츠 조정 이벤트를 게시하고, 받고, 라우팅하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Event Grid
---

# Azure Event Grid를 사용하여 이벤트 게시 및 수신

AI 콘텐츠 조정 시스템은 제출된 콘텐츠를 분류하고 검토하면서 많은 이벤트를 생성합니다. Azure Event Grid는 이벤트 유형에 따라 이벤트를 적절한 다운스트림 소비자로 전달하는 라우팅 계층을 제공하므로, 폴링이나 수동 필터링 없이 각 처리기가 필요한 이벤트만 받습니다.

이 실습에서는 Event Grid Namespace와 네임스페이스 토픽 및 필터링된 이벤트 구독을 배포한 다음, 콘텐츠 조정 이벤트를 게시하고 풀 배달 방식으로 받는 Python Flask 애플리케이션을 빌드합니다. Event Grid 구독은 플래그가 지정된 콘텐츠, 승인된 콘텐츠 및 모든 이벤트를 별도의 구독으로 라우팅하므로 필터링이 실제로 작동하는 모습을 확인할 수 있습니다. 또한 풀 배달에서 제공하는 수신, 승인 및 거부 작업을 사용하여 애플리케이션이 이벤트를 처리하는 방식을 제어합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- 네임스페이스 토픽이 있는 Event Grid Namespace 배포
- 유형 필터가 있는 이벤트 구독 만들기
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 조정 이벤트 게시, 수신 및 처리

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비저닝할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)는 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치되어 있어야 합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상
- Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)(선택 사항)
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)

## 프로젝트 시작 파일 다운로드 및 리소스 배포

이 섹션에서는 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 Event Grid Namespace를 배포합니다. 네임스페이스에는 애플리케이션이 조정 이벤트를 게시하는 토픽과 풀 배달을 위해 이벤트를 필터링하고 보관하는 이벤트 구독이 포함됩니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/event-grid-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 상단의 두 값을 필요에 맞게 변경한 다음 저장합니다. **참고:** 스크립트의 다른 항목은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 실습에 필요한 리소스 공급자가 등록되었는지 확인합니다.

    ```
    az provider register --namespace Microsoft.EventGrid
    ```

1. 다음 명령을 실행하여 Event Grid CLI 확장을 설치합니다. 배포 스크립트에서 사용하는 네임스페이스 명령에는 이 확장이 필요합니다.

    ```
    az extension add --name eventgrid --yes
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Event Grid namespace and topic** 옵션을 시작합니다.

    이 옵션은 아직 없는 경우 리소스 그룹을 만들고 Standard SKU의 Event Grid Namespace를 배포한 다음, CloudEvents v1.0 입력으로 구성된 **moderation-events** 네임스페이스 토픽을 만듭니다. 네임스페이스는 토픽과 이벤트 구독을 담는 컨테이너입니다. 풀 배달을 사용하면 별도의 메시징 서비스 없이 애플리케이션이 Event Grid에 직접 연결하여 이벤트를 받을 수 있습니다.

1. **2**를 입력하여 **2. Create event subscriptions** 옵션을 실행합니다.

    이 옵션은 네임스페이스 토픽에 이벤트 구독 세 개를 만듭니다. **sub-flagged** 구독은 **com.contoso.ai.ContentFlagged** 이벤트만 전달하는 이벤트 유형 필터를 사용합니다. **sub-approved** 구독은 **com.contoso.ai.ContentApproved** 이벤트만 전달합니다. **sub-all-events** 구독에는 필터가 없으며 토픽에 게시된 모든 이벤트를 전달하므로 감사 로그로 사용할 수 있습니다. 각 구독은 풀 배달 모드, 60초 수신 잠금 기간, 최대 배달 횟수 10회, 이벤트 TTL 1일로 구성됩니다.

1. **3**을 입력하여 **3. Assign user roles** 옵션을 실행합니다. 이 옵션은 네임스페이스에 EventGrid Data Sender 역할과 EventGrid Data Receiver 역할을 할당하여 Microsoft Entra 인증으로 이벤트를 게시하고 받을 수 있도록 합니다.

1. **4**를 입력하여 **4. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 리소스 그룹 이름, 네임스페이스 이름, 토픽 이름 및 네임스페이스 엔드포인트가 포함된 환경 변수 파일을 만듭니다.

1. **6**을 입력하여 배포 스크립트를 종료합니다.

    > **참고:** 실습 중 문제가 발생하면 스크립트를 다시 실행하고 **5**를 입력하여 **5. Check deployment status**를 실행할 수 있습니다. 이 문제 해결 옵션은 네임스페이스 상태가 **Succeeded**인지, 토픽이 생성되었는지, 역할이 할당되었는지, 모든 이벤트 구독이 프로비저닝되었는지 확인합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 불러오는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 불러오도록 이 명령을 다시 실행해야 합니다.

## 앱 완성

이 섹션에서는 *event_grid_functions.py* 파일에 코드를 추가하여 Event Grid 게시 및 풀 배달 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수를 호출하고 결과를 브라우저에 표시합니다. 실습 뒷부분에서 앱을 실행합니다.

1. 코드 추가를 시작하려면 *client/event_grid_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 정렬해야 합니다.

### 조정 이벤트 게시 코드 추가

이 섹션에서는 Event Grid 네임스페이스 토픽에 콘텐츠 조정 이벤트 다섯 개를 게시하는 코드를 추가합니다. 이벤트는 CloudEvents v1.0 스키마를 사용하며 플래그가 지정된 콘텐츠, 승인된 콘텐츠 및 상향 검토 등 서로 다른 조정 결과를 나타냅니다. 각 구독의 이벤트 유형 필터가 어떤 이벤트를 전달하는지 확인할 수 있습니다.

이 함수는 이벤트 정의를 **type**, **source**, **subject** CloudEvent 봉투 필드와 **data** 페이로드가 포함된 *moderation_events.json* 파일에서 불러옵니다. 게시 시 함수는 각 이벤트에 고유한 **id**와 현재 UTC **timestamp**를 추가한 다음, **CloudEvent** 개체를 만들고 단일 요청으로 **send()** 메서드를 사용하여 게시합니다. **EventGridPublisherClient**는 네임스페이스 토픽 엔드포인트를 대상으로 하는 **namespace_topic** 매개 변수로 구성되며 Microsoft Entra 인증에 **DefaultAzureCredential**을 사용합니다.

> **팁:** 코드 블록을 해당 BEGIN 및 END 주석과 같은 들여쓰기 수준에 붙여 넣습니다. 블록이 정렬되지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN PUBLISH EVENTS FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def publish_moderation_events():
        """Publish content moderation events to the Event Grid namespace topic."""
        client = get_publisher_client()
        results = []

        # Load event definitions from the JSON file. Each entry contains the
        # CloudEvent envelope fields (type, source, subject) and the data
        # payload that mirrors a realistic AI content moderation pipeline.
        json_path = os.path.join(os.path.dirname(__file__), "moderation_events.json")
        with open(json_path, "r") as f:
            event_definitions = json.load(f)

        # Build CloudEvent objects from the definitions, adding a unique id
        # and a current UTC timestamp to each event at publish time.
        events = []
        for defn in event_definitions:
            defn["data"]["timestamp"] = datetime.now(timezone.utc).isoformat()
            events.append(
                CloudEvent(
                    type=defn["type"],
                    source=defn["source"],
                    subject=defn["subject"],
                    data=defn["data"],
                    id=str(uuid.uuid4())
                )
            )

        # send() publishes all events to the Event Grid namespace topic in a
        # single request. Event Grid then evaluates each subscription's
        # filters and routes matching events to the configured subscriptions.
        client.send(events)

        for event in events:
            results.append({
                "content_id": event.data["contentId"],
                "event_type": event.type.split(".")[-1],
                "category": event.data["category"],
                "confidence": event.data["confidence"],
                "status": "published"
            })

        return results
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 이벤트 수신 및 승인 코드 추가

이 섹션에서는 각 구독에서 이벤트를 받고 승인하여 필터링이 작동하는지 확인하는 코드를 추가합니다. 풀 배달에서는 Event Grid가 엔드포인트로 이벤트를 푸시하는 대신 애플리케이션이 Event Grid에 연결하여 이벤트를 요청합니다. 수신한 각 이벤트에는 잠금 토큰이 포함됩니다. 이 토큰으로 이벤트를 승인하면 구독에서 이벤트가 영구적으로 제거됩니다. 승인하지 않으면 잠금 기간이 만료된 후 이벤트가 다시 배달됩니다.

이 함수는 세 구독 각각에 대해 **EventGridConsumerClient**를 만듭니다. **receive()** 메서드는 **CloudEvent**(**.event**)와 **lock_token**이 있는 브로커 속성을 포함하는 **ReceiveDetails** 개체 목록을 반환합니다. 처리한 후 함수는 수집된 잠금 토큰으로 **acknowledge()**를 호출하여 이벤트가 성공적으로 처리되었음을 확인합니다.

1. **# BEGIN CHECK DELIVERY FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def check_filtered_delivery():
        """Receive and acknowledge events from each subscription to verify filtering."""
        flagged = []
        approved = []
        all_events = []

        # Receive from the sub-flagged subscription, which only delivers
        # events where the event type is com.contoso.ai.ContentFlagged.
        # receive() returns a list of ReceiveDetails, each containing
        # the CloudEvent and a lock token for acknowledgment.
        consumer = get_consumer_client(SUB_FLAGGED)
        details = consumer.receive(max_events=10, max_wait_time=10)
        tokens = []
        for detail in details:
            event = detail.event
            flagged.append({
                "content_id": event.data.get("contentId"),
                "category": event.data.get("category"),
                "severity": event.data.get("severity"),
                "confidence": event.data.get("confidence")
            })
            tokens.append(detail.broker_properties.lock_token)
        # acknowledge() removes the events from the subscription so they
        # are not delivered again on the next receive call.
        if tokens:
            consumer.acknowledge(lock_tokens=tokens)

        # Receive from the sub-approved subscription, which only delivers
        # events where the event type is com.contoso.ai.ContentApproved.
        consumer = get_consumer_client(SUB_APPROVED)
        details = consumer.receive(max_events=10, max_wait_time=10)
        tokens = []
        for detail in details:
            event = detail.event
            approved.append({
                "content_id": event.data.get("contentId"),
                "category": event.data.get("category"),
                "severity": event.data.get("severity"),
                "confidence": event.data.get("confidence")
            })
            tokens.append(detail.broker_properties.lock_token)
        if tokens:
            consumer.acknowledge(lock_tokens=tokens)

        # Receive from the sub-all-events subscription, which has no filter
        # and delivers every event published to the topic (audit log).
        consumer = get_consumer_client(SUB_ALL)
        details = consumer.receive(max_events=10, max_wait_time=10)
        tokens = []
        for detail in details:
            event = detail.event
            all_events.append({
                "content_id": event.data.get("contentId"),
                "event_type": event.data.get("modelName", "unknown"),
                "category": event.data.get("category"),
                "confidence": event.data.get("confidence")
            })
            tokens.append(detail.broker_properties.lock_token)
        if tokens:
            consumer.acknowledge(lock_tokens=tokens)

        return {
            "flagged": flagged,
            "approved": approved,
            "all_events": all_events
        }
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 이벤트 확인 및 거부 코드 추가

이 섹션에서는 테스트 이벤트 하나를 게시하고, 수신하여, 전체 CloudEvent 봉투를 확인한 다음 거부하는 코드를 추가합니다. 이벤트를 거부하면 Event Grid에 해당 이벤트를 처리할 수 없다고 알립니다. 성공적으로 처리되었음을 확인하는 승인과는 다릅니다. 거부된 이벤트는 삭제되거나 구성된 경우 배달 못한 편지 대상으로 이동됩니다.

이 함수는 먼저 **EventGridPublisherClient**를 사용하여 테스트 이벤트를 게시하므로 이전 이벤트가 이미 승인되었는지와 관계없이 항상 이벤트를 사용할 수 있습니다. 그런 다음 **sub-flagged** 구독에서 이벤트를 받고 **delivery_count**를 포함한 CloudEvent 특성과 브로커 속성을 추출한 후 잠금 토큰과 함께 **reject()**를 호출합니다.

1. **# BEGIN INSPECT AND REJECT FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def inspect_and_reject():
        """Publish one event, receive it, inspect the CloudEvent envelope, then reject it."""
        publisher = get_publisher_client()

        # Publish a single test event so there is always something to inspect,
        # regardless of whether the student already acknowledged earlier events.
        test_event = CloudEvent(
            type="com.contoso.ai.ContentFlagged",
            source="/services/content-moderation",
            subject="/content/text/test-inspect",
            data={
                "contentId": "test-inspect",
                "contentType": "text",
                "modelName": "text-moderator-v2",
                "modelVersion": "2.4.0",
                "confidence": 0.76,
                "category": "misinformation",
                "severity": "medium",
                "reviewRequired": True,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            id=str(uuid.uuid4())
        )
        publisher.send([test_event])

        # Receive from the sub-flagged subscription to pick up the test event.
        consumer = get_consumer_client(SUB_FLAGGED)
        details = consumer.receive(max_events=1, max_wait_time=10)

        if not details:
            return None

        detail = details[0]
        event = detail.event
        lock_token = detail.broker_properties.lock_token
        delivery_count = detail.broker_properties.delivery_count

        # Capture the full CloudEvent envelope before rejecting.
        result = {
            "specversion": "1.0",
            "type": event.type,
            "source": event.source,
            "subject": event.subject,
            "id": event.id,
            "time": str(event.time) if event.time else "",
            "data": event.data,
            "delivery_count": delivery_count,
            "action": "rejected"
        }

        # reject() tells Event Grid this event cannot be processed. The event
        # is moved to the dead-letter location if configured, or discarded
        # if max delivery count has been reached.
        consumer.reject(lock_tokens=[lock_token])

        return result
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

## Python 환경 구성

이 섹션에서는 클라이언트 앱 디렉터리로 이동하고 Python 환경을 만든 다음 종속성을 설치합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 Python 환경을 만듭니다.

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

## 앱 실행

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 콘텐츠 조정 이벤트를 게시하고 필터링된 구독이 이벤트를 올바르게 전달하는지 확인합니다. 웹 인터페이스에서 이벤트를 게시하고, 필터링된 구독에서 이벤트를 수신 및 승인하고, 이벤트를 확인하고 거부하여 전체 CloudEvent 구조와 풀 배달 작업을 살펴볼 수 있습니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 앞 단계의 명령을 참고하여 명령을 실행하기 전에 환경을 활성화합니다. *client* 디렉터리에서 나왔다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 패널에서 **조정 이벤트 게시(Publish Moderation Events)**를 선택합니다. 두 개의 플래그 지정 콘텐츠 이벤트, 두 개의 승인 콘텐츠 이벤트, 한 개의 상향 검토 이벤트 등 콘텐츠 조정 이벤트 다섯 개를 Event Grid 네임스페이스 토픽에 게시합니다. 오른쪽 패널에는 각 이벤트가 게시되었으며 콘텐츠 ID, 이벤트 유형 및 범주가 표시됩니다.

1. 왼쪽 패널에서 **이벤트 수신 및 승인(Receive & Acknowledge Events)**을 선택합니다. 풀 배달을 사용하여 세 구독에서 이벤트를 받고 처리한 후 승인합니다. 각 구독에 구성된 필터에 따라 다음과 같이 배달되는지 확인합니다.

    - **플래그 지정 구독(Flagged Subscription):** 정책 위반을 나타내는 범주 값(violence 및 hate-speech)이 있는 이벤트 두 개를 포함해야 합니다. 이 이벤트는 **ContentFlagged** 이벤트입니다.
    - **승인 구독(Approved Subscription):** 범주가 **safe**인 이벤트 두 개를 포함해야 합니다. 이 이벤트는 **ContentApproved** 이벤트입니다.
    - **모든 이벤트 구독(All Events Subscription):** 유형과 관계없이 감사 로그로 이벤트 다섯 개를 모두 포함해야 합니다.

    상향 검토 이벤트(**ReviewEscalated**)는 플래그 지정 구독이나 승인 구독의 필터에 해당 이벤트 유형이 포함되지 않으므로 모든 이벤트 구독에만 표시됩니다. 이벤트가 승인되었으므로 이 단추를 다시 선택하면 더 게시할 때까지 이벤트가 표시되지 않습니다.

1. 왼쪽 패널에서 **이벤트 확인 및 거부(Inspect & Reject Event)**를 선택합니다. 새 테스트 이벤트를 게시하고 플래그 지정 구독에서 받은 다음, 브로커 속성의 **delivery_count**를 포함한 전체 CloudEvent 봉투를 표시한 후 이벤트를 거부합니다. 거부는 이벤트를 처리할 수 없음을 Event Grid에 알리므로 Event Grid는 이벤트를 삭제하거나 구성된 경우 배달 못한 편지 대상으로 이동합니다.

## 리소스 정리

실습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 실습에서 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 해당 그룹에 포함된 모든 리소스가 삭제됩니다. 실습에 기존 리소스 그룹을 선택한 경우 실습 범위에 포함되지 않는 기존 리소스도 삭제됩니다.

## 문제 해결

실습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Event Grid Namespace 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Event Grid Namespace의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- 네임스페이스에 **moderation-events** 토픽이 있는지 확인합니다.

**이벤트 구독 확인**
- 배포 스크립트 상태 확인(option 5)을 실행하여 이벤트 구독 세 개가 모두 생성되었는지 확인합니다.
- **sub-flagged**, **sub-approved**, **sub-all-events** 구독의 상태가 **Succeeded**인지 확인합니다.
- 게시 후 이벤트를 받지 못하면 토픽을 만든 후 구독이 생성되었는지 확인합니다. 필요한 경우 배포 스크립트의 option 2를 다시 실행합니다.

**코드 완성도 및 들여쓰기 확인**
- *event_grid_functions.py*의 해당 BEGIN/END 주석 사이에 각 코드 블록을 올바른 섹션으로 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인하고 모든 코드가 함수 안에서 올바르게 정렬되었는지 확인합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **EVENTGRID_ENDPOINT**, **EVENTGRID_TOPIC_NAME**, **RESOURCE_GROUP**, **NAMESPACE_NAME** 값이 포함되어 있는지 확인합니다.
- Bash에서는 **source .env**를, PowerShell에서는 **. .\.env.ps1**를 실행하여 환경 변수를 터미널 세션에 불러옵니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- 네임스페이스에 EventGrid Data Sender 및 EventGrid Data Receiver 역할이 할당되어 있는지 확인합니다. 필요한 경우 배포 스크립트의 역할 할당 옵션(option 3)을 다시 실행합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
