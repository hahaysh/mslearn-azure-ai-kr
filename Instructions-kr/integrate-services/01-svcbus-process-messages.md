---
lab:
  topic: 백엔드 서비스 통합
  title: Azure Service Bus를 사용하여 메시지 처리
  description: Python SDK를 사용하여 Azure Service Bus 큐, 토픽 및 구독에서 메시지를 보내고, 받고, 라우팅하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Service Bus
---

# Azure Service Bus를 사용하여 메시지 처리

AI 워크플로는 요청 수신과 모델 추론을 분리하고 결과를 여러 다운스트림 소비자로 라우팅하기 위해 메시징에 의존하는 경우가 많습니다. Azure Service Bus는 이러한 구성 요소를 연결하는 안정적인 라우팅 계층을 제공하므로 각 구성 요소를 독립적으로 확장하고 장애에 대응할 수 있습니다.

이 실습에서는 Azure Service Bus 네임스페이스를 만들고, AI 추론 시나리오를 사용하여 핵심 메시징 패턴을 보여 주는 Python Flask 웹 애플리케이션을 빌드합니다. 큐를 사용하여 peek-lock 배달 방식으로 추론 요청을 보내고 받으며, 처리에 실패한 잘못된 페이로드의 배달 못한 편지 큐를 확인하고, 필터링된 구독이 있는 토픽을 사용하여 우선순위별로 추론 결과를 여러 대상으로 전달합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Service Bus 네임스페이스 및 메시징 엔터티 만들기
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 메시징 작업 수행

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비저닝할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)는 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치되어 있어야 합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure Service Bus 배포

이 섹션에서는 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 Azure Service Bus 네임스페이스와 메시징 엔터티를 배포합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/service-bus-python.zip
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
    az provider register --namespace Microsoft.ServiceBus
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Service Bus namespace** 옵션을 시작합니다.

    이 옵션은 아직 없는 경우 리소스 그룹을 만들고 Standard 계층의 Azure Service Bus 네임스페이스를 배포합니다. 네임스페이스는 이 실습에서 만드는 모든 메시징 엔터티를 담는 컨테이너입니다.

1. **2**를 입력하여 **2. Create messaging entities** 옵션을 실행합니다. 이 옵션은 앱에서 사용하는 큐, 토픽, 구독 및 SQL 필터를 만듭니다. **inference-requests** 큐는 최대 배달 횟수 5회와 메시지 만료 시 배달 못한 편지 처리 기능으로 구성됩니다. **inference-results** 토픽에는 두 개의 구독이 있습니다. **notifications**는 모든 메시지를 받고, **high-priority**는 **priority** 속성이 **high**와 같은 메시지만 받도록 필터링됩니다.

1. **3**을 입력하여 **3. Assign role** 옵션을 실행합니다. 이 옵션은 Microsoft Entra 인증을 사용하여 메시지를 보내고 받을 수 있도록 Azure Service Bus Data Owner 역할을 계정에 할당합니다.

1. **4**를 입력하여 **4. Check deployment status** 옵션을 실행합니다. 계속하기 전에 네임스페이스 상태가 **Succeeded**이고 메시징 엔터티가 생성되었으며 역할이 할당되었는지 확인합니다. 네임스페이스가 아직 프로비저닝 중이면 잠시 기다린 후 다시 확인합니다.

1. **5**를 입력하여 **5. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 앱에 필요한 정규화된 도메인 이름(FQDN)이 포함된 환경 변수 파일을 만듭니다.

1. **6**을 입력하여 배포 스크립트를 종료합니다.

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

이 섹션에서는 *service_bus_functions.py* 파일에 코드를 추가하여 Service Bus 메시징 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수를 호출하고 결과를 브라우저에 표시합니다. 실습 뒷부분에서 앱을 실행합니다.

1. 코드 추가를 시작하려면 *client/service_bus_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 정렬해야 합니다.

### 큐로 메시지를 보내는 코드 추가

이 섹션에서는 큐에 메시지 세 개를 보내는 코드를 추가합니다. 두 메시지에는 추론 요청을 나타내는 유효한 JSON 페이로드가 있고, 하나에는 처리 실패를 시뮬레이션하여 배달 못한 편지 큐를 보여 주는 의도적으로 잘못된 JSON이 있습니다.

이 함수는 **DefaultAzureCredential**을 사용하여 **ServiceBusClient**를 열고 **get_queue_sender()**로 큐 발신자를 만듭니다. 각 메시지에는 중복 제거용 **message_id**, 추적용 **correlation_id**, 사용자 지정 메타데이터용 **application_properties**가 있는 **ServiceBusMessage** 개체 세 개를 구성합니다. 두 메시지에는 유효한 JSON 페이로드를 넣고 한 메시지에는 의도적으로 잘못된 JSON을 넣습니다. **send_messages()** 메서드는 각 메시지를 개별적으로 큐에 보냅니다.

> **팁:** 코드 블록을 해당 BEGIN 및 END 주석과 같은 들여쓰기 수준에 붙여 넣습니다. 블록이 정렬되지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN SEND MESSAGES FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def send_messages():
        """Send messages to the queue including one malformed message."""
        # Create a ServiceBusClient using DefaultAzureCredential
        client = get_client()
        results = []

        with client:
            # Open a sender bound to the queue
            with client.get_queue_sender(QUEUE_NAME) as sender:
                # Valid message 1 — message_id enables deduplication,
                # correlation_id links related messages for tracking,
                # and application_properties carry custom metadata for routing
                msg1 = ServiceBusMessage(
                    body=json.dumps({
                        "prompt": "Extract parties and effective date.",
                        "model": "gpt-4o",
                        "document_id": "doc-001"
                    }),
                    content_type="application/json",
                    message_id=str(uuid.uuid4()),
                    correlation_id="req-doc-001",
                    application_properties={"priority": "standard", "document_type": "contract"}
                )
                sender.send_messages(msg1)
                results.append({
                    "correlation_id": msg1.correlation_id,
                    "type": "valid",
                    "status": "sent"
                })

                # Valid message 2 — priority is set to "high" so it matches
                # the SQL filter on the high-priority topic subscription
                msg2 = ServiceBusMessage(
                    body=json.dumps({
                        "prompt": "Summarize the key terms.",
                        "model": "gpt-4o",
                        "document_id": "doc-002"
                    }),
                    content_type="application/json",
                    message_id=str(uuid.uuid4()),
                    correlation_id="req-doc-002",
                    application_properties={"priority": "high", "document_type": "contract"}
                )
                sender.send_messages(msg2)
                results.append({
                    "correlation_id": msg2.correlation_id,
                    "type": "valid",
                    "status": "sent"
                })

                # Invalid message — intentionally malformed JSON body to
                # demonstrate dead-lettering during processing
                msg3 = ServiceBusMessage(
                    body="not valid json: [broken",
                    content_type="application/json",
                    message_id=str(uuid.uuid4()),
                    correlation_id="req-doc-003",
                    application_properties={"priority": "standard"}
                )
                sender.send_messages(msg3)
                results.append({
                    "correlation_id": msg3.correlation_id,
                    "type": "malformed",
                    "status": "sent"
                })

        return results
    ```

1. 몇 분 동안 코드를 검토합니다.

### peek-lock을 사용하여 메시지를 처리하는 코드 추가

이 섹션에서는 peek-lock 모드로 큐에서 메시지를 받는 코드를 추가합니다. 프로세서는 JSON 페이로드를 검증하고 유효한 메시지를 완료하며, 잘못된 JSON이 있는 메시지는 이유와 오류 설명을 제공하여 배달 못한 편지로 처리합니다.

이 함수는 기본 peek-lock 모드를 사용하는 **get_queue_receiver()**로 큐 수신자를 만듭니다. 이 모드에서는 메시지를 처리하는 동안 잠그지만 처리가 완료될 때까지 큐에 남겨 둡니다. 각 메시지의 JSON 본문을 구문 분석합니다. 유효한 메시지는 **complete_message()**로 큐에서 제거합니다. 잘못된 메시지는 진단에 사용할 **reason**과 **error_description**을 지정하는 **dead_letter_message()**로 배달 못한 편지 하위 큐로 이동합니다.

1. **# BEGIN PROCESS MESSAGES FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def process_messages():
        """Receive and process messages from the queue using peek-lock."""
        client = get_client()
        results = []

        with client:
            # Peek-lock is the default receive mode — the message is locked
            # but stays in the queue until explicitly completed or dead-lettered.
            # max_wait_time sets how long the receiver waits for new messages.
            with client.get_queue_receiver(
                queue_name=QUEUE_NAME,
                max_wait_time=5
            ) as receiver:
                for msg in receiver:
                    try:
                        payload = json.loads(str(msg))
                        # Complete removes the message from the queue
                        receiver.complete_message(msg)
                        results.append({
                            "correlation_id": msg.correlation_id,
                            "document_id": payload.get("document_id"),
                            "model": payload.get("model"),
                            "prompt": payload.get("prompt", "")[:50],
                            "status": "completed"
                        })
                    except json.JSONDecodeError:
                        # Dead-letter moves the message to the dead-letter
                        # sub-queue with a reason and description for diagnostics
                        receiver.dead_letter_message(
                            msg,
                            reason="MalformedPayload",
                            error_description="Message body is not valid JSON"
                        )
                        results.append({
                            "correlation_id": msg.correlation_id,
                            "document_id": None,
                            "model": None,
                            "prompt": str(msg)[:50],
                            "status": "dead-lettered"
                        })

        return results
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 배달 못한 편지 큐를 확인하는 코드 추가

이 섹션에서는 배달 못한 편지 큐의 메시지를 읽고 진단 정보를 표시하는 코드를 추가합니다. 배달 못한 편지 큐에는 처리할 수 없었던 메시지와 문제 해결에 필요한 이유 및 오류 설명이 함께 저장됩니다.

이 함수는 **get_queue_receiver()**에 **sub_queue=ServiceBusSubQueue.DEAD_LETTER**를 전달하여 배달 못한 편지 하위 큐를 대상으로 하는 수신자를 만듭니다. 각 배달 못한 메시지에서 **dead_letter_reason**, **dead_letter_error_description**, **delivery_count** 진단 속성을 읽습니다. 읽은 후 **complete_message()**를 호출하여 배달 못한 편지 큐에서 메시지를 제거합니다.

1. **# BEGIN INSPECT DLQ FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def inspect_dead_letter_queue():
        """Inspect and remove messages from the dead-letter queue."""
        client = get_client()
        results = []

        with client:
            # ServiceBusSubQueue.DEAD_LETTER targets the dead-letter sub-queue,
            # which holds messages that failed processing
            with client.get_queue_receiver(
                queue_name=QUEUE_NAME,
                sub_queue=ServiceBusSubQueue.DEAD_LETTER,
                max_wait_time=5
            ) as dlq_receiver:
                for msg in dlq_receiver:
                    # Dead-lettered messages include diagnostic properties:
                    # dead_letter_reason, dead_letter_error_description,
                    # and delivery_count (number of delivery attempts)
                    results.append({
                        "message_id": msg.message_id,
                        "correlation_id": msg.correlation_id,
                        "dead_letter_reason": msg.dead_letter_reason,
                        "error_description": msg.dead_letter_error_description,
                        "delivery_count": msg.delivery_count,
                        "body": str(msg)[:100]
                    })
                    # Complete removes the message from the dead-letter queue
                    dlq_receiver.complete_message(msg)

        return results
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 필터링된 구독을 사용한 토픽 메시징 코드 추가

이 섹션에서는 우선순위가 서로 다른 메시지를 토픽으로 보내고 각 구독에서 메시지를 받아 필터링이 작동하는지 확인하는 코드를 추가합니다. **notifications** 구독은 모든 메시지를 받고, **high-priority** 구독은 **priority** 애플리케이션 속성이 **high**인 메시지만 받습니다.

이 함수는 **get_topic_sender()**를 사용하여 토픽에 연결된 발신자를 연 다음 **application_properties**에 우선순위 값이 다른 메시지 다섯 개를 보냅니다. 그런 다음 **get_subscription_receiver()**로 두 구독 수신자를 엽니다. 필터가 없는 **notifications** 구독은 메시지 다섯 개를 모두 받습니다. **high-priority** 구독은 SQL 필터와 일치하는 메시지만 전달합니다. AMQP 인코딩으로 인해 애플리케이션 속성이 바이트로 도착할 수 있으므로 코드는 문자열 키와 바이트 키를 모두 처리합니다.

1. **# BEGIN TOPIC MESSAGING FUNCTION** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드 정렬 상태를 확인합니다.

    ```python
    def topic_messaging():
        """Send messages to a topic and receive from filtered subscriptions."""
        client = get_client()
        sent = []
        notifications = []
        high_priority = []

        with client:
            # get_topic_sender opens a sender bound to a topic instead of a queue.
            # Each message is broadcast to all matching subscriptions.
            with client.get_topic_sender(TOPIC_NAME) as sender:
                for i, priority in enumerate(["standard", "high", "standard", "high", "low"]):
                    result = {
                        "document_id": f"doc-{i+1:03d}",
                        "status": "completed",
                        "confidence": 0.95
                    }
                    # The "priority" application property is what the SQL
                    # filter on the high-priority subscription evaluates
                    msg = ServiceBusMessage(
                        body=json.dumps(result),
                        content_type="application/json",
                        message_id=str(uuid.uuid4()),
                        application_properties={"priority": priority}
                    )
                    sender.send_messages(msg)
                    sent.append({
                        "document_id": f"doc-{i+1:03d}",
                        "priority": priority
                    })

            # Receive from the notifications subscription, which has no filter
            # and therefore receives all messages sent to the topic
            with client.get_subscription_receiver(
                topic_name=TOPIC_NAME,
                subscription_name="notifications",
                max_wait_time=5
            ) as receiver:
                for msg in receiver:
                    body = json.loads(str(msg))
                    # Application properties may arrive as bytes depending
                    # on the AMQP encoding, so handle both str and bytes keys
                    props = msg.application_properties or {}
                    priority_val = props.get("priority") or props.get(b"priority", b"unknown")
                    if isinstance(priority_val, bytes):
                        priority_val = priority_val.decode("utf-8")
                    notifications.append({
                        "document_id": body["document_id"],
                        "priority": priority_val
                    })
                    receiver.complete_message(msg)

            # Receive from the high-priority subscription, which only delivers
            # messages where the SQL filter "priority = 'high'" matches
            with client.get_subscription_receiver(
                topic_name=TOPIC_NAME,
                subscription_name="high-priority",
                max_wait_time=5
            ) as receiver:
                for msg in receiver:
                    body = json.loads(str(msg))
                    props = msg.application_properties or {}
                    priority_val = props.get("priority") or props.get(b"priority", b"unknown")
                    if isinstance(priority_val, bytes):
                        priority_val = priority_val.decode("utf-8")
                    high_priority.append({
                        "document_id": body["document_id"],
                        "priority": priority_val
                    })
                    receiver.complete_message(msg)

        return {
            "sent": sent,
            "notifications": notifications,
            "high_priority": high_priority
        }
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

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 다양한 Service Bus 메시징 작업을 수행합니다. 웹 인터페이스에서 메시지를 보내고, peek-lock 배달 방식으로 처리하고, 배달 못한 편지 큐를 확인하고, 필터링된 구독을 사용한 토픽 메시징을 테스트할 수 있습니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 앞 단계의 명령을 참고하여 명령을 실행하기 전에 환경을 활성화합니다. *client* 디렉터리에서 나왔다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 패널에서 **메시지 보내기(Send Messages)**를 선택합니다. 추론 요청을 나타내는 유효한 JSON 페이로드가 있는 메시지 두 개와 의도적으로 잘못된 JSON이 있는 메시지 하나, 총 세 개의 메시지를 큐로 보냅니다. 오른쪽 패널에는 각 메시지가 전송되었으며 상관 관계 ID와 유형이 표시됩니다.

1. **메시지 처리(Process Messages)**를 선택합니다. peek-lock 배달 방식으로 큐에서 메시지 세 개를 받습니다. 프로세서는 각 메시지의 JSON 페이로드를 검증하고 유효한 메시지 두 개를 완료하며, 잘못된 메시지는 **MalformedPayload** 사유와 함께 배달 못한 편지로 처리합니다. 결과에는 처리 후 각 메시지의 상태가 표시됩니다.

1. **배달 못한 편지 큐 확인(Inspect Dead-Letter Queue)**을 선택합니다. 배달 못한 메시지를 읽고 배달 못한 편지 사유, 오류 설명, 배달 횟수 등 진단 정보를 표시합니다. 배달 못한 편지 큐에는 처리할 수 없었던 메시지가 저장되므로 실패 원인을 조사할 수 있습니다.

1. **토픽 메시지 보내기 및 받기(Send & Receive Topic Messages)**를 선택합니다. 우선순위 수준이 서로 다른 메시지 다섯 개를 **inference-results** 토픽으로 보낸 다음 두 구독에서 읽어 필터링된 배달을 확인합니다. **notifications** 구독은 메시지 다섯 개를 모두 받고, **high-priority** 구독은 **priority** 속성이 **high**인 메시지만 받습니다.

## 리소스 정리

실습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 실습에서 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 해당 그룹에 포함된 모든 리소스가 삭제됩니다. 실습에 기존 리소스 그룹을 선택한 경우 실습 범위에 포함되지 않는 기존 리소스도 삭제됩니다.

## 문제 해결

실습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure Service Bus 네임스페이스 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Service Bus 네임스페이스의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- 토픽과 구독에 필요한 네임스페이스 계층이 **Standard**인지 확인합니다.

**메시징 엔터티 확인**
- 배포 스크립트의 **Check deployment status** 옵션을 실행하여 큐, 토픽, 구독 및 SQL 필터가 모두 성공적으로 생성되었는지 확인합니다.
- 엔터티가 누락된 경우 **Create messaging entities** 옵션을 다시 실행합니다.

**코드 완성도 및 들여쓰기 확인**
- *service_bus_functions.py*의 해당 BEGIN/END 주석 사이에 각 코드 블록을 올바른 섹션으로 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인하고 모든 코드가 함수 안에서 올바르게 정렬되었는지 확인합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **SERVICE_BUS_FQDN** 값이 포함되어 있는지 확인합니다.
- Bash에서는 **source .env**를, PowerShell에서는 **. .\.env.ps1**를 실행하여 환경 변수를 터미널 세션에 불러옵니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- Azure portal에서 역할 할당을 확인하거나 배포 스크립트의 역할 할당 옵션을 다시 실행하여 Azure Service Bus Data Owner 역할이 계정에 할당되어 있는지 확인합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
