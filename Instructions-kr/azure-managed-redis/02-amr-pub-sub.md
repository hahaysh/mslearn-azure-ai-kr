---
lab:
  topic: Azure Managed Redis
  title: Azure Managed Redis에서 이벤트 게시 및 구독
  description: redis-py Python 라이브러리와 Microsoft Entra ID를 사용하여 Azure Managed Redis에서 게시/구독 메시징 패턴을 구현하는 Flask 웹 앱을 빌드하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Managed Redis
---

# Azure Managed Redis에서 이벤트 게시 및 구독

이 실습에서는 Azure Managed Redis 리소스를 배포하고 단일 페이지에서 Redis 채널에 게시하고 구독하는 Python Flask 웹 앱을 완성합니다. Microsoft Entra ID를 사용하여 Redis에 연결하고, 이벤트 메시지를 게시하고, 모든 채널에 브로드캐스트하고, 수신한 메시지를 서식 지정하고, 백그라운드 스레드에서 메시지를 수신하고, 채널과 패턴을 구독하는 코드를 추가합니다. 그런 다음 앱을 실행하고 메시지를 게시하면서 메시지가 실시간으로 도착하는 것을 확인합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Managed Redis 리소스 만들기
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 메시지 게시 및 구독

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Azure CLI **redisenterprise** 확장(버전 2.75.0 이상). 이후 단계에서 확장을 설치하거나 업그레이드합니다.
- **선택 사항:** Python 코드를 서식 지정하고 린트하기 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure Managed Redis 배포

이 섹션에서는 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 구독에 Azure Managed Redis 배포를 초기화합니다. Azure Managed Redis 배포를 완료하는 데 5~10분이 걸리므로 먼저 배포를 시작한 다음 프로비전이 진행되는 동안 앱에 코드를 추가합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/amr-pub-sub-python.zip
    ```

1. 파일을 복사하거나 이동하여 프로젝트 작업에 사용할 시스템 위치에 둡니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 Azure Managed Redis에 필요한 리소스 공급자가 있는지 확인합니다.

    ```
    az provider register --namespace Microsoft.Cache
    ```

1. 다음 명령을 실행하여 Azure CLI용 **redisenterprise** 확장을 설치하거나 업그레이드합니다. 데이터베이스에서 Microsoft Entra ID 액세스를 구성하려면 버전 2.75.0 이상이 필요합니다.

    ```
    az extension add --upgrade --name redisenterprise
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Azure Managed Redis resource** 옵션을 시작합니다.

    이 옵션은 리소스 그룹이 아직 없는 경우 만들고 Azure Managed Redis를 배포합니다. 스크립트는 5~10분이 걸리는 배포가 완료될 때까지 기다린 다음 터미널에 결과를 표시합니다. 스크립트를 실행한 채 두고 다음 섹션으로 이동하여 배포가 진행되는 동안 코드를 추가합니다. 터미널을 주기적으로 확인하여 오류가 있는지 살펴봅니다.

    배포가 성공하면 다음과 비슷한 확인 메시지가 표시되고 메뉴로 돌아갑니다.

    *Azure Managed Redis resource created successfully: amr-exercise-\<hash>*

## 앱 완성

이 섹션에서는 *pubsub_functions.py* 파일에 코드를 추가하여 게시/구독 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수들을 호출하여 메시지를 게시하고, 구독을 관리하고, 수신 메시지를 브라우저로 스트리밍합니다. *app.py*는 편집할 필요가 없습니다. 실습 후반에 앱을 실행합니다.

1. 코드 추가를 시작하려면 *client/pubsub_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 들여쓰기가 일치해야 합니다.

### Azure Managed Redis 연결 코드 추가

이 섹션에서는 Microsoft Entra ID로 인증하는 Redis 클라이언트를 만드는 코드를 추가합니다. Entra ID를 사용하면 앱이 액세스 키를 처리하지 않아도 됩니다.

**get_client()** 함수는 **REDIS_HOST** 환경 변수에서 Redis 엔드포인트를 읽고 **create_from_default_azure_credential()**을 호출하여 자격 증명 공급자를 빌드합니다. 이 공급자는 **DefaultAzureCredential**을 사용하여 Microsoft Entra 토큰을 가져오고 백그라운드에서 자동으로 새로 고치므로 장시간 실행되는 수신기 연결도 인증된 상태를 유지합니다. 클라이언트는 TLS를 통해 포트 10000으로 연결하고 응답을 문자열로 디코딩합니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 같은 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN CONNECTION CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def get_client() -> redis.Redis:
        """Create a Redis client for Azure Managed Redis using Microsoft Entra ID."""
        redis_host = os.environ.get("REDIS_HOST")

        if not redis_host:
            raise ValueError("REDIS_HOST environment variable must be set")

        # create_from_default_azure_credential uses DefaultAzureCredential to
        # acquire a Microsoft Entra token for Redis. The credential provider
        # refreshes the token automatically in the background so long-lived
        # connections (like the pub/sub listener) stay authenticated.
        credential_provider = create_from_default_azure_credential(
            ("https://redis.azure.com/.default",),
        )

        return redis.Redis(
            host=redis_host,
            port=10000,
            ssl=True,
            decode_responses=True,
            credential_provider=credential_provider,
            socket_timeout=30,
            socket_connect_timeout=30,
        )
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 이벤트 게시 코드 추가

이 섹션에서는 주문 생성 이벤트를 게시하는 코드를 추가합니다. 이를 통해 단일 채널로 메시지를 보내는 핵심 게시 작업을 확인합니다.

**publish_order_created()** 함수는 이벤트를 설명하는 사전을 만들고 JSON으로 직렬화한 다음 **orders:created** 채널에서 **publish()**를 호출합니다. **publish()** 메서드는 메시지를 받은 구독자 수를 반환하며, 앱에서 이를 표시하여 메시지가 전달되었는지 확인할 수 있습니다.

1. **# BEGIN PUBLISH MESSAGE CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def publish_order_created(r: redis.Redis) -> dict:
        """Publish an order created event to the 'orders:created' channel."""
        order_data = {
            "event": "order_created",
            "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer": "Jane Doe",
            "total": 129.99,
            "timestamp": datetime.now().isoformat(),
        }
        channel = "orders:created"

        # publish() sends the message to every subscriber of the channel and
        # returns the number of subscribers that received it.
        subscribers = r.publish(channel, json.dumps(order_data))

        return {"channel": channel, "subscribers": subscribers, "message": order_data}
    ```

    > **참고:** 시작 파일에는 **publish_order_shipped()**, **publish_inventory_alert()**, **publish_notification()** 함수가 이미 포함되어 있어 여러 이벤트 유형을 사용할 수 있습니다. 잠시 시간을 내어 검토합니다.

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 모든 채널에 브로드캐스트하는 코드 추가

이 섹션에서는 단일 메시지를 모든 채널에 브로드캐스트하는 코드를 추가합니다. 브로드캐스트는 구독한 채널과 관계없이 모든 구독자가 받아야 하는 시스템 전체 공지에 유용합니다.

**broadcast_to_all()** 함수는 **AVAILABLE_CHANNELS**를 반복하고 각 채널에서 같은 메시지로 **publish()**를 호출합니다. 모든 채널의 구독자 수를 합산하여 앱이 도달한 구독자 수를 보고할 수 있습니다.

1. **# BEGIN BROADCAST CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def broadcast_to_all(r: redis.Redis) -> dict:
        """Broadcast the same message to every channel using publish() in a loop."""
        announcement = {
            "event": "system_announcement",
            "message": "System maintenance scheduled for 2 AM",
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
        }
        message = json.dumps(announcement)

        results = []
        total_subscribers = 0
        for channel in AVAILABLE_CHANNELS:
            # Send the same message to multiple channels for multi-channel delivery.
            count = r.publish(channel, message)
            total_subscribers += count
            results.append({"channel": channel, "subscribers": count})

        return {
            "channels": results,
            "total_subscribers": total_subscribers,
            "message": announcement,
        }
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 수신 메시지 서식 지정 코드 추가

이 섹션에서는 수신 메시지를 화면에 표시할 서식으로 만드는 코드를 추가합니다. 백그라운드 수신기는 수신한 모든 메시지에 이 함수를 호출하여 웹 페이지에 깔끔한 요약을 표시합니다.

**format_message()** 함수는 원시 게시/구독 메시지에서 채널, 패턴, 데이터를 읽습니다. JSON 페이로드를 구문 분석하고 이벤트 유형과 **order_id**, **customer** 등의 알려진 필드를 추출합니다. 페이로드가 유효한 JSON이 아니면 데이터가 손실되지 않도록 원시 값을 대신 반환합니다.

1. **# BEGIN MESSAGE FORMATTING CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def format_message(message: dict) -> dict:
        """Parse a pub/sub message and extract relevant fields for display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        channel = message.get("channel", "unknown")
        pattern = message.get("pattern")

        try:
            data = json.loads(message["data"])
        except (json.JSONDecodeError, TypeError):
            # Non-JSON payloads are returned as-is under a "raw" key.
            return {
                "timestamp": timestamp,
                "channel": channel,
                "pattern": pattern,
                "event": None,
                "details": {"raw": message.get("data")},
            }

        # Pull out the fields that the demo events include so the UI can
        # display a clean summary of each message.
        field_names = [
            "order_id", "customer", "total", "tracking_number",
            "product_name", "current_stock", "message",
        ]
        details = {name: data[name] for name in field_names if name in data}

        return {
            "timestamp": timestamp,
            "channel": channel,
            "pattern": pattern,
            "event": data.get("event", "unknown"),
            "details": details,
        }
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 메시지 수신 코드 추가

이 섹션에서는 **PubSubManager** 클래스의 **listen_messages()** 메서드에 코드를 추가합니다. 이 메서드는 백그라운드 스레드에서 실행되므로 앱이 웹 요청에 계속 응답하면서 메시지를 지속해서 받을 수 있습니다.

이 메서드는 메시지가 게시될 때 이를 생성하는 블로킹 반복자인 **pubsub.listen()**을 순회합니다. **message**(직접 채널) 및 **pmessage**(패턴) 유형을 처리하고, 각 메시지를 **format_message()**로 서식 지정한 다음 웹 페이지가 폴링하는 스레드 안전 버퍼에 추가합니다. 오류는 시스템 메시지로 포착하여 표시하므로 UI에서 실패를 확인할 수 있습니다.

1. **# BEGIN MESSAGE LISTENER CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def listen_messages(self) -> None:
        """Background thread that reads messages from subscribed channels."""
        self.listener_active = True
        try:
            # listen() blocks and yields messages as they are published.
            for message in self.pubsub.listen():
                if not self.listening:
                    break

                # Handle both direct channel messages and pattern messages.
                if message["type"] in ("message", "pmessage"):
                    self._add_message(format_message(message))

        except Exception as e:
            if self.listening:
                self._add_message({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "channel": "system",
                    "pattern": None,
                    "event": "listener_error",
                    "details": {"error": str(e)},
                })
        finally:
            self.listener_active = False
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 채널 및 패턴 구독 코드 추가

이 섹션에서는 **subscribe_to_channel()** 및 **subscribe_to_pattern()** 메서드에 코드를 추가합니다. 이 두 가지는 Redis 게시/구독의 주요 구독 방식입니다. 특정 이벤트에는 직접 채널 구독을 사용하고, 와일드카드 일치에는 패턴 구독을 사용합니다.

**subscribe_to_channel()** 메서드는 **subscribe()**를 호출하여 단일 채널에 대한 관심을 등록하고, **subscribe_to_pattern()**은 **orders:***와 같은 패턴으로 여러 채널을 일치시키기 위해 **psubscribe()**를 호출합니다. 각 구독이 변경된 후 코드는 수신기를 다시 시작하여 새 채널의 메시지를 수신합니다.

1. **# BEGIN SUBSCRIBE CHANNEL/PATTERN CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def subscribe_to_channel(self, channel: str) -> str:
        """Subscribe to a specific channel using subscribe()."""
        self.pubsub.subscribe(channel)  # Register interest in the channel.
        self.restart_listener()
        return f"Subscribed to channel: {channel}"

    def subscribe_to_pattern(self, pattern: str) -> str:
        """Subscribe using a pattern with psubscribe() (e.g. 'orders:*')."""
        self.pubsub.psubscribe(pattern)  # Register interest in matching channels.
        self.restart_listener()
        return f"Subscribed to pattern: {pattern}"
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

## 리소스 배포 확인

이 섹션에서는 실행 중인 배포 스크립트로 돌아가 Azure Managed Redis 배포가 완료되었는지 확인한 다음 데이터베이스를 만들고, Microsoft Entra ID 액세스를 구성하고, 엔드포인트가 포함된 환경 변수 파일을 생성합니다.

1. 배포 스크립트가 실행 중인 터미널로 돌아갑니다. Azure Managed Redis 리소스가 성공적으로 만들어졌다는 스크립트 메시지가 표시되면 **Enter**를 눌러 배포 메뉴로 돌아갑니다.

1. **2**를 입력하여 **2. Create database and configure access** 옵션을 실행합니다. 이 옵션은 Microsoft Entra ID 인증을 사용하여 데이터베이스를 만들고, 앱이 사용자 ID를 사용하여 연결할 수 있도록 계정에 데이터 액세스 정책을 할당하고, **REDIS_HOST** 엔드포인트가 포함된 *.env* 및 *.env.ps1* 파일을 만듭니다.

1. 마지막으로 **3**을 입력하여 **3. Check deployment status** 옵션을 실행합니다.

1. **4**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션으로 불러오려면 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 불러오기 위해 이 명령을 실행해야 합니다.

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

1. 다음 명령을 실행하여 Python 환경을 활성화합니다. **참고:** Linux/macOS에서는 Bash 명령을 사용합니다. Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

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

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 단일 웹 페이지에서 메시지를 게시하고 구독합니다. 왼쪽 패널에서는 이벤트를 게시하고 구독을 관리하며, 오른쪽 패널에서는 마지막 게시 결과와 수신 메시지의 실시간 스트림을 표시합니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 이 실습 앞부분의 명령을 참조하여 환경을 활성화하고 환경 변수를 불러옵니다. *client* 디렉터리에서 다른 위치로 이동했다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 패널의 **구독(Subscriptions)** 영역에서 채널 상자를 선택하여 드롭다운 목록을 열고 **notifications**를 선택한 다음 **구독(Subscribe)**을 선택합니다. 성공 메시지가 구독을 확인하고 **활성 구독(Active subscriptions)** 목록에 채널이 추가됩니다. 메시지를 받으려면 먼저 채널을 구독해야 합니다.

1. **이벤트 게시(Publish Events)** 영역에서 **알림(Notification)**을 선택합니다. 오른쪽 패널에는 채널과 메시지를 받은 구독자 수를 포함한 게시 결과가 표시됩니다. 백그라운드 수신기가 메시지를 구독 항목으로 전달하므로 1~2초 안에 **수신 메시지(Received Messages)** 목록에 메시지가 나타납니다.

1. **인벤토리 경고(Inventory Alert)**를 선택합니다. 게시 결과에는 메시지가 **inventory:alerts** 채널로 전송되었다고 표시되지만, **notifications**만 구독했으므로 **수신 메시지(Received Messages)**에는 나타나지 않습니다.

1. **구독(Subscriptions)** 영역에서 패턴 상자에 **orders:\***를 입력하고 **패턴 구독(Subscribe to Pattern)**을 선택합니다. 그러면 **orders:**로 시작하는 모든 채널을 구독하고, 패턴이 **notifications**와 함께 **활성 구독(Active subscriptions)** 목록에 나타납니다.

1. **주문 생성(Order Created)**을 선택한 다음 **주문 배송(Order Shipped)**을 선택합니다. **orders:\*** 패턴이 **orders:created** 및 **orders:shipped** 채널과 모두 일치하므로 두 메시지가 **수신 메시지(Received Messages)** 목록에 나타납니다.

1. **모두 브로드캐스트(Broadcast to All)**를 선택하여 모든 채널에 공지 메시지 하나를 보냅니다. 현재 구독과 일치하는 각 메시지에 따라 **수신 메시지(Received Messages)** 목록이 실시간으로 업데이트되는 것을 확인합니다.

1. **모두 구독 취소(Unsubscribe from All)**를 선택하여 구독을 지운 다음 **모두 브로드캐스트(Broadcast to All)**를 다시 선택합니다. 활성 구독이 더 이상 없으므로 **수신 메시지(Received Messages)**에 새 메시지가 도착하지 않는지 확인합니다.

## 리소스 정리

이제 실습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **\<rg-name>**을 실습 앞부분에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 실습에서 기존 리소스 그룹을 선택했다면 실습 범위에 포함되지 않은 기존 리소스도 함께 삭제됩니다.

## 문제 해결

실습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure Managed Redis 리소스 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Azure Managed Redis 리소스의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- 배포 스크립트의 **Check deployment status** 옵션을 실행하고 데이터베이스를 만들고 액세스를 구성하기 전에 클러스터와 데이터베이스가 준비되었는지 확인합니다.
**배포 실패 해결**
- 배포가 실패하는 가장 일반적인 원인은 선택한 지역에서 해당 SKU의 용량을 일시적으로 사용할 수 없는 것입니다.
- 화면의 안내에 따라 스크립트를 종료하고, 스크립트 맨 위의 **location** 변수를 eastus2, australiaeast 또는 canadacentral과 같은 다른 지역으로 변경한 다음 스크립트를 다시 실행하고 옵션 1을 선택합니다.
- 다음 시도 전에 실패한 리소스가 자동으로 삭제됩니다.
**인증 및 액세스 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- 배포 스크립트의 **Create database and configure access** 옵션이 성공적으로 완료되어 계정에 데이터베이스 데이터 액세스 정책이 있는지 확인합니다.
- 앱에서 인증 오류가 보고되면 액세스 정책 할당이 적용되는 데 잠시 걸릴 수 있으므로 잠시 기다렸다가 다시 시도합니다.

**코드 완성도 및 들여쓰기 확인**
- *pubsub_functions.py*의 적절한 BEGIN/END 주석 사이에 모든 코드 블록을 올바른 섹션에 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인합니다. **listen_messages()**, **subscribe_to_channel()**, **subscribe_to_pattern()** 메서드는 **PubSubManager** 클래스 안에 있으므로 코드 들여쓰기가 한 단계 더 들어가야 합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **REDIS_HOST** 값이 포함되어 있는지 확인합니다.
- Bash에서는 **source .env**를, PowerShell에서는 **. .\.env.ps1**를 실행하여 터미널 세션에 환경 변수를 불러옵니다.

**메시지가 표시되지 않음**
- 게시하는 채널을 구독했는지 확인합니다. 구독한 채널이나 패턴의 메시지만 도착합니다.
- 브라우저의 **활성 구독(Active Subscriptions)** 목록에서 현재 구독을 확인합니다.
- 앱이 터미널에서 계속 실행 중이고 페이지의 메시지 스트림이 업데이트되는지 확인합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
