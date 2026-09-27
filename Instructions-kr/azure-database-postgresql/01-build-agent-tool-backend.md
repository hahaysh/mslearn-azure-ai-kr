---
lab:
  topic: Azure Database for PostgreSQL
  title: Azure Database for PostgreSQL에서 에이전트 도구 백엔드 빌드
  description: Azure Database for PostgreSQL을 사용하여 AI 에이전트용 영구 메모리 저장소를 빌드하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Database for PostgreSQL
---

# Azure Database for PostgreSQL에서 에이전트 도구 백엔드 빌드

이 실습에서는 AI 에이전트의 도구 백엔드 역할을 하는 Azure Database for PostgreSQL 인스턴스를 만듭니다. 데이터베이스는 에이전트가 작동 중 읽고 쓸 수 있는 대화 컨텍스트와 작업 상태를 저장합니다. 에이전트 메모리용 스키마를 설계하고, 에이전트 도구 역할을 하는 Python 함수를 빌드한 다음, 전체 워크플로를 테스트합니다. 이 패턴은 세션 간 영구 메모리를 유지하고 중단된 작업을 재개할 수 있는 AI 에이전트를 빌드하기 위한 기반을 제공합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트 구성
- Microsoft Entra 인증을 사용하는 Azure Database for PostgreSQL Flexible Server 배포
- 대화 및 작업 상태를 관리하는 Python 도구 함수 빌드
- 대화, 메시지, 작업 체크포인트 테이블을 포함하는 에이전트 메모리용 데이터베이스 스키마 만들기
- 제공된 테스트 스크립트를 사용하여 에이전트 메모리 워크플로 테스트
- SQL을 사용하여 대화 컨텍스트 쿼리

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에서 사용합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상
- [PostgreSQL 명령줄 도구](https://www.postgresql.org/download/) (**psql**)
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. PostgreSQL 서버를 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-build-agent-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **File > Open Folder...**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위에 있는 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 부분은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **Terminal(터미널) > New Terminal(새 터미널)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 실습에 필요한 리소스 공급자가 있는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.DBforPostgreSQL
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 PostgreSQL을 배포합니다.

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Create PostgreSQL server with Entra authentication(Entra 인증으로 PostgreSQL 서버 만들기)** 옵션을 실행합니다. 이 옵션은 Entra 전용 인증이 사용하도록 설정된 서버를 만듭니다. **참고:** 배포를 완료하는 데 5~10분 정도 걸릴 수 있습니다.

    >**중요:** 실습이 끝날 때까지 배포를 실행하는 터미널을 열어 둡니다. 터미널에서 배포가 계속되는 동안 실습의 다음 섹션으로 이동할 수 있습니다.

## 도구 함수 앱 완성

이 섹션에서는 *agent_tools.py* 파일에 AI 에이전트가 상태를 저장하고 검색하기 위해 호출할 수 있는 함수를 추가합니다. 이 함수들은 에이전트와 데이터베이스 사이의 인터페이스 역할을 합니다. 이 실습의 뒷부분에서 실행하는 *test_workflow.py* 스크립트는 이러한 함수를 가져와 에이전트의 사용 방식을 보여 줍니다.

1. VS Code에서 *agent-backend/agent_tools.py* 파일을 엽니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 동일한 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **BEGIN CREATE CONVERSATION FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 고유한 세션 ID로 새 대화 레코드를 만들고 선택적 메타데이터를 JSONB로 저장합니다.

    ```python
    def create_conversation(user_id: str, metadata: dict = None) -> dict:
        """Create a new conversation and return its details."""
        session_id = uuid.uuid4()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO conversations (session_id, user_id, metadata)
                    VALUES (%s, %s, %s)
                    RETURNING id, session_id, started_at
                    """,
                    (str(session_id), user_id, psycopg.types.json.Json(metadata or {}))
                )
                row = cur.fetchone()
                conn.commit()
                return {
                    "conversation_id": row[0],
                    "session_id": str(row[1]),
                    "started_at": row[2].isoformat()
                }
    ```

1. **BEGIN RETRIEVE CONVERSATION HISTORY FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 대화의 메시지를 시간순으로 검색합니다.

    ```python
    def get_conversation_history(conversation_id: int, limit: int = 50) -> list:
        """Retrieve recent messages from a conversation."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, role, content, created_at, metadata
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (conversation_id, limit)
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": row[0],
                        "role": row[1],
                        "content": row[2],
                        "created_at": row[3].isoformat(),
                        "metadata": row[4]
                    }
                    for row in reversed(rows)  # Return in chronological order
                ]
    ```

1. **BEGIN TASK CHECKPOINT FUNCTIONS** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 업서트 패턴을 사용하여 작업 상태를 저장하거나 업데이트하므로, 에이전트가 중단된 작업을 재개할 수 있습니다.

    ```python
    def save_task_state(conversation_id: int, task_name: str, status: str, checkpoint_data: dict) -> dict:
        """Save or update a task checkpoint."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO task_checkpoints (conversation_id, task_name, status, checkpoint_data)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (conversation_id, task_name)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        checkpoint_data = EXCLUDED.checkpoint_data,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id, updated_at
                    """,
                    (conversation_id, task_name, status, psycopg.types.json.Json(checkpoint_data))
                )
                # Note: The ON CONFLICT requires a unique constraint we need to add
                row = cur.fetchone()
                conn.commit()
                return {
                    "checkpoint_id": row[0],
                    "updated_at": row[1].isoformat()
                }
    ```

1. *agent_tools.py* 파일의 변경 내용을 저장합니다.

1. 앱의 모든 코드를 검토하는 데 몇 분 정도 할애합니다.

다음으로 Azure 리소스 배포를 마무리합니다.

## Azure 리소스 배포 완료

이 섹션에서는 배포 스크립트로 돌아가 PostgreSQL 서버의 연결 정보를 가져옵니다.

1. **Create PostgreSQL server with Entra authentication** 작업이 완료되면 **2**를 입력하여 **Check deployment status(배포 상태 확인)** 옵션을 실행합니다. 이 옵션은 서버가 준비되었는지 확인합니다.

1. **3**을 입력하여 **Retrieve connection info and access token(연결 정보 및 액세스 토큰 검색)** 옵션을 실행합니다. 이 옵션은 필요한 환경 변수가 포함된 파일을 만듭니다.

1. **4**를 입력하여 배포 스크립트를 종료합니다.

1. 다음 명령을 실행하여 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

    >**참고:** 액세스 토큰은 약 1시간 후 만료됩니다. 나중에 다시 연결해야 하는 경우 스크립트를 다시 실행하고 옵션 **3**을 선택하여 새 토큰을 만든 다음 변수를 다시 내보냅니다.

다음으로 에이전트를 지원하는 스키마를 만듭니다.

## **psql**로 에이전트 메모리 스키마 만들기

이 섹션에서는 **psql** 명령줄 도구를 사용하여 PostgreSQL 서버에 연결하고 에이전트 메모리용 데이터베이스 스키마를 만듭니다. 스키마에는 대화(에이전트 세션)용 테이블, 대화 내 메시지용 테이블, 에이전트가 중단된 작업을 재개하도록 하는 작업 체크포인트용 테이블이 포함됩니다.

1. 환경 변수를 사용하여 서버에 연결하려면 다음 명령을 실행합니다. 인증에는 **PGPASSWORD** 환경 변수가 자동으로 사용됩니다.

    **Bash**
    ```bash
    psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
    ```

    **PowerShell**
    ```powershell
    psql "host=$env:DB_HOST port=5432 dbname=$env:DB_NAME user=$env:DB_USER sslmode=require"
    ```

1. PostgreSQL 버전을 확인하여 연결을 검증하려면 다음 명령을 실행합니다.

    ```sql
    SELECT version();
    ```
1. 에이전트 백엔드용 데이터베이스를 만들려면 다음 명령을 실행합니다. **\c** 명령은 새 데이터베이스에 연결합니다.

    ```sql
    CREATE DATABASE agent_memory;
    \c agent_memory
    ```

1. 대화(에이전트 세션)용 테이블을 만들려면 다음 명령을 실행합니다. 이 테이블은 세션 메타데이터를 저장하고 메시지를 특정 대화에 연결합니다.

    ```sql
    CREATE TABLE conversations (
        id BIGSERIAL PRIMARY KEY,
        session_id UUID NOT NULL UNIQUE,
        user_id VARCHAR(255) NOT NULL,
        started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP WITH TIME ZONE,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    ```

1. 대화 내 메시지용 테이블을 만들려면 다음 명령을 실행합니다. 이 테이블은 각 메시지의 역할(user, assistant, system 또는 tool)과 콘텐츠를 저장합니다.

    ```sql
    CREATE TABLE messages (
        id BIGSERIAL PRIMARY KEY,
        conversation_id BIGINT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
        role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        metadata JSONB DEFAULT '{}'::jsonb
    );
    ```

1. 작업 체크포인트용 테이블을 만들려면 다음 명령을 실행합니다. 이 테이블은 에이전트 상태를 유지하여 중단된 작업을 재개할 수 있게 합니다.

    ```sql
    CREATE TABLE task_checkpoints (
        id BIGSERIAL PRIMARY KEY,
        conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
        task_name VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
        checkpoint_data JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    ```

1. 일반적인 쿼리를 최적화하는 인덱스를 만들려면 다음 명령을 실행합니다. 이러한 인덱스는 대화 또는 타임스탬프를 기준으로 메시지를 검색할 때 성능을 높여 줍니다.

    ```sql
    CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
    CREATE INDEX idx_messages_created_at ON messages(created_at);
    CREATE INDEX idx_task_checkpoints_conversation_id ON task_checkpoints(conversation_id);
    CREATE INDEX idx_conversations_session_id ON conversations(session_id);
    ```

1. 앞서 완성한 앱은 **ON CONFLICT**를 사용하므로 고유 제약 조건이 필요합니다. **psql** 세션에서 다음 명령을 실행하여 제약 조건을 추가합니다.

    ```sql
    ALTER TABLE task_checkpoints
    ADD CONSTRAINT unique_conversation_task
    UNIQUE (conversation_id, task_name);
    ```

1. 다음 명령을 실행하여 스키마가 올바르게 만들어졌는지 확인합니다.

    ```sql
    \dt
    ```

    세 테이블이 표시되어야 합니다.

1. `exit`를 입력하여 **psql** 세션을 닫고 터미널로 돌아갑니다.

## 에이전트 메모리 워크플로 테스트

이 섹션에서는 테스트 스크립트를 실행하여 도구 함수가 올바르게 작동하는지 확인합니다. 프로젝트 파일에 포함된 *test_workflow.py* 스크립트는 대화를 만들고, 메시지를 저장하고, 작업 체크포인트를 관리하는 방법을 보여 줍니다.

1. 다음 명령을 실행하여 *agent-backend* 디렉터리로 이동합니다.

    ```
    cd agent-backend
    ```

1. *test_workflow.py* 앱용 가상 환경을 만들려면 다음 명령을 실행합니다. 환경에 따라 **python** 또는 **python3** 명령을 사용할 수 있습니다.

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

1. 앱에 필요한 Python 종속성을 설치하려면 다음 명령을 실행합니다. 이 명령은 PostgreSQL 연결을 위한 **psycopg** 라이브러리와 Microsoft Entra 인증을 위한 **azure-identity**를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

1. 다음 명령을 실행하여 테스트 스크립트를 실행합니다. 이 스크립트는 작성한 에이전트 도구 함수를 모두 테스트합니다.

    ```bash
    python test_workflow.py
    ```

1. 각 단계가 성공적으로 완료되는 출력이 표시되어야 합니다. 이를 통해 에이전트가 대화를 만들고, 메시지를 저장하고, 작업 상태를 저장하고, 기록을 검색할 수 있음을 확인합니다.

1. 선택 사항: *test_workflow.py* 파일을 열어 코드를 검토합니다.

## 대화 컨텍스트 쿼리

이 섹션에서는 에이전트가 의사 결정을 내릴 때 사용할 데이터를 쿼리하는 연습을 합니다.

1. 환경 변수를 사용하여 **agent_memory** 데이터베이스에 연결하려면 다음 명령을 실행합니다.

    **Bash**
    ```bash
    psql "host=$DB_HOST port=5432 dbname=agent_memory user=$DB_USER sslmode=require"
    ```

    **PowerShell**
    ```powershell
    psql "host=$env:DB_HOST port=5432 dbname=agent_memory user=$env:DB_USER sslmode=require"
    ```

    >**팁:** 쿼리 결과가 현재 터미널 창에 모두 표시되지 않으면 psql은 페이저를 사용합니다. 페이저가 표시되면 **q**를 눌러 페이저를 닫고 psql 프롬프트로 돌아갑니다. 터미널 창을 최대화하면 페이저가 나타나는 상황을 줄이고 명령 결과를 더 쉽게 검토할 수 있습니다.

1. 특정 사용자의 모든 대화를 찾으려면 다음 쿼리를 실행합니다. 테스트 스크립트는 **user_id**가 **user_123**으로 설정된 대화를 만들었습니다.

    ```sql
    SELECT id, session_id, started_at, metadata
    FROM conversations
    WHERE user_id = 'user_123'
    ORDER BY started_at DESC;
    ```

1. 모든 대화에서 최근 메시지를 가져오려면 다음 쿼리를 실행합니다. 테스트 스크립트가 저장한 메시지가 반환됩니다.

    ```sql
    SELECT c.session_id, m.role, m.content, m.created_at
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    ORDER BY m.created_at DESC
    LIMIT 10;
    ```

1. 완료된 작업을 찾으려면 다음 쿼리를 실행합니다. 테스트 스크립트는 워크플로가 끝날 때 작업 상태를 **completed**로 업데이트했습니다.

    ```sql
    SELECT
        c.session_id,
        t.task_name,
        t.status,
        t.checkpoint_data,
        t.updated_at
    FROM task_checkpoints t
    JOIN conversations c ON t.conversation_id = c.id
    WHERE t.status = 'completed';
    ```

1. 대화별 역할에 따른 메시지 수를 계산하려면 다음 쿼리를 실행합니다. 이 쿼리는 user, assistant, system, tool 메시지의 분포를 파악하는 데 도움이 됩니다.

    ```sql
    SELECT
        c.id AS conversation_id,
        m.role,
        COUNT(*) AS message_count
    FROM conversations c
    JOIN messages m ON c.id = m.conversation_id
    GROUP BY c.id, m.role
    ORDER BY c.id, m.role;
    ```

1. psql 프롬프트에서 **quit**를 입력하여 종료합니다.

## 요약

이 실습에서는 AI 에이전트용 PostgreSQL 기반 도구 백엔드를 빌드했습니다. Microsoft Entra 인증을 사용하는 Azure Database for PostgreSQL Flexible Server를 배포하고, 에이전트가 대화와 작업 상태를 관리하기 위해 호출할 수 있는 Python 함수를 만들었으며, 대화, 메시지, 작업 체크포인트 테이블이 있는 데이터베이스 스키마를 설계했습니다. 에이전트 작업을 시뮬레이션하는 스크립트를 실행하여 워크플로를 테스트한 다음 SQL을 사용해 저장된 데이터를 쿼리했습니다. 이 패턴을 사용하면 AI 에이전트가 세션 간 영구 메모리를 유지하고 중단된 작업을 재개할 수 있습니다.

# 리소스 정리

실습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹의 모든 리소스를 삭제합니다. **<rg-name>**을 앞에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그 안에 포함된 모든 리소스가 삭제됩니다. 이 실습을 위해 기존 리소스 그룹을 선택한 경우 실습 범위에 포함되지 않은 기존 리소스도 삭제됩니다.

## 문제 해결

실습 중 문제가 발생하면 다음 단계를 시도합니다.

**배포 실패**
- 배포 스크립트를 다시 실행하고 옵션 **1**을 선택합니다.
- 스크립트가 기존 PostgreSQL 서버를 감지하면 재배포 시 서버와 모든 데이터가 영구적으로 삭제된다고 경고합니다. 서버를 삭제하고 다시 배포하려면 `yes`를 입력합니다.
- Azure에서 PostgreSQL 서버 이름을 5분 이내에 해제하지 않으면 배포 스크립트를 종료하고 5분 동안 기다린 다음 스크립트를 다시 실행하여 옵션 **1**을 선택합니다.

**psql 연결 실패**
- 배포 스크립트 옵션 **3**을 실행하여 *.env* 및 *.env.ps1* 파일이 모두 만들어졌는지 확인합니다.
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수를 로드했는지 확인합니다.
- 액세스 토큰은 약 1시간 후 만료됩니다. 새 토큰을 만들려면 배포 스크립트 옵션 **3**을 다시 실행합니다.
- 배포 스크립트 옵션 **2**를 실행하여 서버가 준비되었는지 확인합니다.

**액세스 거부 또는 인증 오류**
- 옵션 **1**에서 서버를 만들 때 Microsoft Entra 관리자가 자동으로 구성됩니다. 액세스가 계속 거부되면 옵션 **2**를 실행하여 관리자를 확인합니다. 관리자가 없으면 옵션 **1**을 실행하고 서버 삭제 및 재배포를 확인합니다.
- 터미널 세션에서 **PGPASSWORD**가 올바르게 설정되었는지 확인합니다.
- 올바른 **DB_USER** 값(Azure 계정 이메일)을 사용하고 있는지 확인합니다.

**Python 테스트 스크립트 실패**
- Python 가상 환경이 활성화되어 있는지 확인합니다(터미널 프롬프트에 **(.venv)**가 표시되어야 합니다).
- 종속성이 설치되었는지 확인합니다(**pip install -r requirements.txt**).
- **psql**에서 **agent_memory** 데이터베이스와 모든 테이블을 만들었는지 확인합니다.
- **task_checkpoints** 테이블에 고유 제약 조건을 추가했는지 확인합니다.

**데이터베이스 또는 테이블을 찾을 수 없음 오류**
- **psql**에서 **\c agent_memory**를 사용하여 **agent_memory** 데이터베이스에 연결했는지 확인합니다.
- **psql**에서 **\dt**를 실행하여 테이블이 있는지 확인합니다.
- 테이블이 없으면 CREATE TABLE 문을 다시 실행합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 **source .venv/bin/activate**를 사용합니다.
- Windows PowerShell에서는 **.\.venv\Scripts\Activate.ps1**을 사용합니다.
- **activate** 스크립트가 없으면 **python3-venv** 패키지를 다시 설치하고 venv를 다시 만듭니다.
