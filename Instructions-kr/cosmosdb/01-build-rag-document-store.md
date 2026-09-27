---
lab:
  topic: Azure Cosmos DB for NoSQL
  title: Azure Cosmos DB for NoSQL에서 RAG 문서 저장소 구축
  description: Azure Cosmos DB for NoSQL을 사용하여 검색 증강 생성(RAG) 애플리케이션용 문서 저장 백엔드를 구축하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Cosmos DB
---

# Azure Cosmos DB for NoSQL에서 RAG 문서 저장소 구축

이 연습에서는 검색 증강 생성(RAG) 애플리케이션의 문서 저장소 역할을 하는 Azure Cosmos DB for NoSQL 데이터베이스를 만듭니다. 데이터베이스는 AI 애플리케이션이 언어 모델에 컨텍스트를 제공할 때 검색할 수 있도록 청크로 나눈 문서와 메타데이터를 저장합니다. 문서 검색에 최적화된 스키마를 설계하고, 문서 청크를 저장하고 쿼리하는 Python 함수를 만들며, Flask 웹 애플리케이션을 사용해 전체 워크플로를 테스트합니다. 이 패턴은 조직의 문서에 기반해 언어 모델 응답을 생성하는 AI 애플리케이션의 토대가 됩니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트 구성
- 데이터베이스와 컨테이너가 포함된 Azure Cosmos DB for NoSQL 계정 배포
- 문서 청크를 저장하고 검색하는 Python 함수 작성
- Flask 웹 애플리케이션을 사용하여 RAG 함수 테스트
- Cosmos DB SQL API를 사용하여 문서 컨텍스트 쿼리

이 연습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음 항목이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)가 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치되어 있어야 합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상
- **선택 사항:** Python 코드의 형식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Cosmos DB 계정을 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-build-query-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 내 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder...)**를 선택한 다음 프로젝트 파일이 포함된 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 연습에 필요한 리소스 공급자가 등록되었는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.DocumentDB
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 Cosmos DB 계정을 배포합니다.

1. 프로젝트 루트 디렉터리에 있는지 확인한 다음 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Cosmos DB 계정 만들기(Create Cosmos DB account)** 옵션을 실행합니다. 데이터베이스와 컨테이너가 포함된 Cosmos DB for NoSQL 계정이 만들어집니다. **참고:** 배포를 완료하는 데 5~10분 정도 걸릴 수 있습니다.

    >**IMPORTANT:** 연습을 진행하는 동안 배포가 실행 중인 터미널을 열어 두세요. 터미널에서 배포가 계속되는 동안 연습의 다음 섹션으로 진행할 수 있습니다.

## RAG 문서 함수 완성

이 섹션에서는 AI 애플리케이션이 문서 청크를 저장하고 검색하기 위해 호출할 수 있는 함수를 추가하여 *rag_functions.py* 파일을 완성합니다. 이 함수는 애플리케이션과 문서 저장소 사이의 인터페이스 역할을 합니다. 이 연습 후반에 실행할 앱은 이 함수를 가져와 AI 애플리케이션에서 사용하는 방식을 보여 줍니다.

1. VS Code에서 *client/rag_functions.py* 파일을 엽니다.

> **Tip:** 일치하는 **BEGIN** 및 **END** 주석과 들여쓰기 수준이 같도록 코드를 붙여 넣습니다. 코드 블록의 정렬이 맞지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **BEGIN STORE DOCUMENT CHUNK FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 메타데이터와 함께 문서 청크를 저장하고 upsert를 사용하여 삽입과 업데이트를 모두 처리합니다.

    ```python
    def store_document_chunk(
        document_id: str,
        chunk_id: str,
        content: str,
        metadata: dict = None,
        embedding: list = None
    ) -> dict:
        """Store a document chunk with metadata and optional embedding placeholder."""
        container = get_container()

        # Build the document structure following our RAG schema
        # The 'id' field is required by Cosmos DB and must be unique within the partition
        # The 'documentId' field is our partition key - chunks from the same source document
        # are stored together for efficient retrieval
        chunk = {
            "id": chunk_id,
            "documentId": document_id,
            "content": content,
            "metadata": metadata or {},
            "embedding": embedding or [],  # Placeholder for vector embeddings
            "createdAt": datetime.utcnow().isoformat(),
            "chunkIndex": metadata.get("chunkIndex", 0) if metadata else 0
        }

        # upsert_item inserts if new, updates if exists (based on id + partition key)
        # This is idempotent - safe to call multiple times with the same data
        response = container.upsert_item(body=chunk)

        # Request Units (RUs) measure the cost of database operations in Cosmos DB
        # Tracking RU consumption helps optimize queries and estimate costs
        ru_charge = response.get_response_headers()['x-ms-request-charge']

        return {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "ru_charge": float(ru_charge)
        }
    ```

1. **BEGIN GET CHUNKS BY DOCUMENT FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 특정 문서의 모든 청크를 청크 인덱스 순서로 검색하여 순차적으로 읽을 수 있도록 합니다.

    ```python
    def get_chunks_by_document(document_id: str, limit: int = 100) -> list:
        """Retrieve all chunks for a specific document, ordered by chunk index."""
        container = get_container()

        # SQL query using parameterized values (@documentId, @limit) to prevent injection
        # The 'c' alias represents each document in the container
        query = """
            SELECT c.id, c.content, c.metadata, c.chunkIndex, c.createdAt
            FROM c
            WHERE c.documentId = @documentId
            ORDER BY c.chunkIndex
            OFFSET 0 LIMIT @limit
        """

        # Single-partition query: providing partition_key limits the query to one partition
        # This is more efficient than cross-partition queries because Cosmos DB only
        # needs to read from one physical partition instead of fanning out to all partitions
        items = container.query_items(
            query=query,
            parameters=[
                {"name": "@documentId", "value": document_id},
                {"name": "@limit", "value": limit}
            ],
            partition_key=document_id  # Scopes query to a single partition
        )

        # Transform Cosmos DB items into a consistent response format
        return [
            {
                "chunk_id": item["id"],
                "content": item["content"],
                "metadata": item["metadata"],
                "chunk_index": item["chunkIndex"],
                "created_at": item["createdAt"]
            }
            for item in items
        ]
    ```

1. **BEGIN SEARCH CHUNKS BY METADATA FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 메타데이터 필터를 사용해 여러 문서의 청크를 검색하므로 태그, 범주 또는 다른 특성을 기준으로 관련 컨텍스트를 찾는 데 유용합니다.

    ```python
    def search_chunks_by_metadata(
        filters: dict,
        limit: int = 10
    ) -> list:
        """Search for chunks across documents using metadata filters."""
        container = get_container()

        # Build WHERE clauses dynamically based on provided filters
        # This allows flexible querying by any combination of metadata fields
        where_clauses = []
        parameters = []

        if "source" in filters and filters["source"]:
            where_clauses.append("c.metadata.source = @source")
            parameters.append({"name": "@source", "value": filters["source"]})

        if "category" in filters and filters["category"]:
            where_clauses.append("c.metadata.category = @category")
            parameters.append({"name": "@category", "value": filters["category"]})

        if "tags" in filters and filters["tags"]:
            # ARRAY_CONTAINS checks if a value exists within an array field
            # This is useful for searching tags, keywords, or other list-based metadata
            where_clauses.append("ARRAY_CONTAINS(c.metadata.tags, @tag)")
            parameters.append({"name": "@tag", "value": filters["tags"][0]})

        # Default to "1=1" (always true) if no filters provided
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        parameters.append({"name": "@limit", "value": limit})

        query = f"""
            SELECT c.id, c.documentId, c.content, c.metadata, c.chunkIndex
            FROM c
            WHERE {where_clause}
            OFFSET 0 LIMIT @limit
        """

        # Cross-partition query: searches across ALL partitions in the container
        # Required when you don't know which partition contains the data you need
        # More expensive than single-partition queries but necessary for metadata searches
        items = container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True  # Fan out to all partitions
        )

        return [
            {
                "chunk_id": item["id"],
                "document_id": item["documentId"],
                "content": item["content"],
                "metadata": item["metadata"],
                "chunk_index": item["chunkIndex"]
            }
            for item in items
        ]
    ```

1. **BEGIN GET CHUNK BY ID FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 청크 ID와 문서 ID를 사용해 특정 청크를 효율적인 점 읽기로 검색합니다.

    ```python
    def get_chunk_by_id(document_id: str, chunk_id: str) -> dict:
        """Retrieve a specific chunk using a point read (most efficient)."""
        container = get_container()

        try:
            # Point read: the most efficient Cosmos DB operation
            # By providing both the item ID and partition key, Cosmos DB can go
            # directly to the exact location of the document without any query execution
            # This results in the lowest latency and RU cost (typically 1 RU for small docs)
            item = container.read_item(
                item=chunk_id,         # The unique ID within the partition
                partition_key=document_id  # The partition where this item lives
            )
            return {
                "chunk_id": item["id"],
                "document_id": item["documentId"],
                "content": item["content"],
                "metadata": item["metadata"],
                "chunk_index": item["chunkIndex"],
                "created_at": item["createdAt"],
                "embedding": item.get("embedding", [])
            }
        except exceptions.CosmosResourceNotFoundError:
            # Return None if the item doesn't exist rather than raising an exception
            # This allows the caller to handle missing items gracefully
            return None
    ```

1. *rag_functions.py* 파일의 변경 내용을 저장합니다.

1. 잠시 시간을 내어 앱의 모든 코드를 검토합니다.

이어서 Azure 리소스 배포를 마무리합니다.

## Azure 리소스 배포 완료

이 섹션에서는 배포 스크립트로 돌아가 Entra ID 액세스를 구성하고 Cosmos DB 계정의 연결 정보를 검색합니다.

1. **Cosmos DB 계정 만들기(Create Cosmos DB account)** 작업이 완료되면 **2**를 입력하여 **Entra ID 액세스 구성(Configure Entra ID access)** 옵션을 실행합니다. 이 옵션은 Cosmos DB 데이터 평면에 액세스하는 데 필요한 역할을 사용자 계정에 할당합니다.

1. **3**을 입력하여 **배포 상태 확인(Check deployment status)** 옵션을 실행합니다. 모든 리소스가 준비되었는지 확인합니다.

1. **4**를 입력하여 **연결 정보 검색(Retrieve connection info)** 옵션을 실행합니다. 필요한 환경 변수가 포함된 파일이 만들어집니다.

1. **5**를 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 불러오려면 다음 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**Note:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 설정하는 명령을 실행해야 할 수 있습니다.

이어서 문서 저장소에 사용되는 RAG 문서 스키마를 살펴봅니다.

## RAG 문서 스키마 이해

이 섹션에서는 RAG 애플리케이션용으로 설계된 문서 스키마를 알아봅니다. 관계형 데이터베이스와 달리 Cosmos DB for NoSQL은 유연한 JSON 문서 모델을 사용합니다. 컨테이너는 **documentId**를 파티션 키로 사용하도록 만들어졌으며, 이 키는 원본 문서의 모든 청크를 함께 그룹화하여 효율적으로 검색할 수 있게 합니다.

각 청크의 문서 스키마에는 다음 필드가 포함됩니다.

| 필드(Field) | 설명(Description) |
|-------|-------------|
| **id** | 청크의 고유 식별자(Cosmos DB에 필요) |
| **documentId** | 원본 문서 식별자(파티션 키) |
| **content** | 청크의 실제 텍스트 콘텐츠 |
| **metadata** | 원본, 범주, 태그 및 사용자 지정 특성을 위한 유연한 개체 |
| **embedding** | 벡터 임베딩을 위한 배열 자리 표시자(벡터 검색 시나리오에서 사용) |
| **chunkIndex** | 원본 문서 내 청크의 위치 |
| **createdAt** | 청크가 저장된 시각의 타임스탬프 |

이 스키마는 일반적인 RAG 패턴을 지원합니다.

- **Point reads**: ID와 문서 ID로 특정 청크 검색(최저 대기 시간)
- **Single-partition queries**: 한 문서의 모든 청크를 효율적으로 가져오기
- **Cross-partition queries**: 메타데이터로 여러 문서 검색
- **Vector search**: 벡터 인덱싱과 결합하는 경우

## Flask 앱으로 RAG 함수 테스트

이 섹션에서는 Flask 웹 애플리케이션을 시작하고 인터페이스를 사용하여 만든 RAG 함수를 테스트합니다. 앱에서 데이터를 로드하고, 테스트를 실행하고, 청크를 쿼리하고, 사용자 지정 SQL 쿼리를 실행할 수 있습니다.

1. 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 Flask 앱용 가상 환경을 만듭니다. 환경에 따라 **python** 또는 **python3** 명령을 사용할 수 있습니다.

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

1. 다음 명령을 실행하여 앱의 Python 종속성을 설치합니다. 이 명령은 **flask** 및 **azure-cosmos** 라이브러리를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

1. 다음 명령을 실행하여 Flask 애플리케이션을 시작합니다.

    ```bash
    python app.py
    ```

1. 브라우저를 열고 `http://127.0.0.1:5000`으로 이동하여 애플리케이션을 확인합니다.

### 샘플 데이터 로드

이 섹션에서는 앱을 사용하여 샘플 문서 청크를 Cosmos DB 컨테이너에 로드합니다. 앱은 *rag_functions.py*에서 만든 **store_document_chunk()** 함수를 호출하여 각 청크를 삽입합니다.

1. **샘플 데이터 로드(Load Sample Data)** 섹션에서 **샘플 청크 로드(Load Sample Chunks)**를 선택합니다. 가상의 Azure 설명서 문서 네 개에서 가져온 샘플 청크 12개가 삽입됩니다.

1. **결과(Results)** 섹션에 로드된 청크 수와 총 RU(Request Unit) 사용량을 표시하는 성공 메시지가 나타나는지 확인합니다.

### 테스트 워크플로 실행

이 섹션에서는 *rag_functions.py*에서 만든 RAG 함수가 올바르게 작동하는지 확인하는 자동화된 테스트를 실행합니다.

1. **테스트 워크플로 실행(Run Test Workflow)** 섹션에서 **테스트 실행(Run Tests)**을 선택합니다. 각 함수를 실행하는 테스트 다섯 개가 수행됩니다.

1. **결과(Results)** 패널에서 테스트 결과를 검토합니다. 각 테스트의 상태가 **passed**여야 합니다.
    - 문서 청크 저장
    - 문서 ID로 청크 가져오기
    - 범주로 검색
    - 태그로 검색
    - ID로 점 읽기

### 문서별 청크 가져오기

이 섹션에서는 특정 문서의 모든 청크를 검색합니다. 앱은 *rag_functions.py*에서 만든 **get_chunks_by_document()** 함수를 호출합니다.

1. **문서별 청크 가져오기(Get Chunks by Document)** 섹션의 드롭다운에서 문서를 선택합니다(예: **doc-azure-overview**).

1. **청크 가져오기(Get Chunks)**를 선택하여 해당 문서의 모든 청크를 검색합니다.

1. 콘텐츠와 메타데이터 태그를 포함한 청크가 인덱스 순서로 정렬되어 결과에 표시되는지 확인합니다.

### 메타데이터로 검색

이 섹션에서는 메타데이터 필터를 사용하여 모든 문서에서 청크를 검색합니다. 앱은 *rag_functions.py*에서 만든 **search_chunks_by_metadata()** 함수를 호출합니다. 필터를 조합하면 결과가 어떻게 좁혀지는지 확인합니다.

1. **메타데이터로 검색(Search by Metadata)** 섹션의 **범주(Category)** 드롭다운에서 **ai-applications**를 선택합니다. **태그(Tag)** 필드는 비워 둡니다.

1. **검색(Search)**을 선택하여 해당 범주가 지정된 모든 청크를 찾습니다.

1. **결과(Results)** 패널에서 결과를 검토합니다. **rag**, **embeddings**, **chunking**, **metadata** 등 서로 다른 태그가 있는 청크 네 개가 반환되어야 합니다.

1. 이제 태그 필터를 추가하여 결과를 좁힙니다. **태그(Tag)** 필드에 **embeddings**를 입력하고 **검색(Search)**을 다시 선택합니다.

1. 결과가 줄어들어 **ai-applications** 범주와 일치하고 **embeddings** 태그를 포함하는 청크만 반환되는지 확인합니다. 메타데이터 필터를 조합하면 RAG 애플리케이션이 더 구체적인 컨텍스트를 검색할 수 있습니다.

## 문서 컨텍스트 쿼리

이 섹션에서는 Query Explorer를 사용하여 Cosmos DB 컨테이너에 SQL 쿼리를 작성하는 방법을 연습합니다. 이러한 쿼리는 RAG 애플리케이션에서 문서 컨텍스트를 검색할 때 흔히 사용하는 패턴을 보여 줍니다.

1. **쿼리 탐색기(Query Explorer)** 섹션의 **SQL 쿼리(SQL Query)** 필드에 다음 쿼리를 입력하여 특정 문서의 모든 청크를 찾습니다. 이 쿼리는 순차적으로 읽을 수 있도록 청크를 인덱스 순으로 검색합니다.

    ```sql
    SELECT c.id, c.chunkIndex, c.content, c.metadata
    FROM c
    WHERE c.documentId = 'doc-azure-overview'
    ORDER BY c.chunkIndex
    ```

1. **쿼리 실행(Execute Query)**을 선택하고 결과를 검토합니다.

1. **SQL 쿼리(SQL Query)** 필드에 다음 쿼리를 입력하여 모든 문서에서 특정 범주의 청크를 검색합니다. 이 쿼리는 메타데이터를 검색하는 파티션 간 쿼리입니다.

    ```sql
    SELECT c.documentId, c.id, c.content, c.metadata.category
    FROM c
    WHERE c.metadata.category = 'cloud-services'
    ```

1. **쿼리 실행(Execute Query)**을 선택하고 결과를 검토합니다.

1. **SQL 쿼리(SQL Query)** 필드에 다음 쿼리를 입력하여 범주 및 원본 메타데이터와 함께 컨테이너에 저장된 문서를 확인합니다. 이를 통해 RAG 검색에 사용할 수 있는 콘텐츠를 파악할 수 있습니다.

    ```sql
    SELECT DISTINCT c.documentId, c.metadata.category, c.metadata.source
    FROM c
    ```

1. **쿼리 실행(Execute Query)**을 선택하고 결과를 검토합니다.

1. **SQL 쿼리(SQL Query)** 필드에 다음 쿼리를 입력하여 메타데이터에 특정 태그가 포함된 청크를 찾습니다. 이 쿼리는 **ARRAY_CONTAINS**를 사용하여 배열 안의 값을 검색하는 방법을 보여 줍니다.

    ```sql
    SELECT c.documentId, c.id, c.content, c.metadata.tags
    FROM c
    WHERE ARRAY_CONTAINS(c.metadata.tags, 'compute')
    ```

1. **쿼리 실행(Execute Query)**을 선택하고 결과를 검토합니다.

1. 터미널로 돌아가 **Ctrl+C**를 눌러 Flask 애플리케이션을 중지합니다.

## 요약

이 연습에서는 RAG 애플리케이션용 Cosmos DB 기반 문서 저장소를 구축했습니다. 문서 검색 패턴에 최적화된 데이터베이스와 컨테이너가 포함된 Azure Cosmos DB for NoSQL 계정을 배포했습니다. 메타데이터와 함께 문서 청크를 저장하고, 문서 ID로 청크를 가져오고, 메타데이터 필터로 여러 문서를 검색하고, 효율적인 점 읽기를 수행하는 Python 함수를 만들었습니다. 각 함수를 실행하는 Flask 웹 애플리케이션으로 워크플로를 테스트한 다음 Cosmos DB SQL API를 사용하여 저장된 데이터를 쿼리했습니다. 이 패턴을 사용하면 AI 애플리케이션이 청크로 나눈 문서를 저장하고 관련 컨텍스트를 검색하여 언어 모델 응답의 근거로 활용할 수 있습니다.

## 리소스 정리

이제 연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **\<rg-name>**을 앞서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **CAUTION:** 리소스 그룹을 삭제하면 포함된 모든 리소스가 삭제됩니다. 이 연습의 기존 리소스 그룹을 선택한 경우 연습 범위 밖의 기존 리소스도 모두 삭제됩니다.

## 문제 해결

연습 중 문제가 발생하면 다음 단계를 시도합니다.

**Flask 앱이 시작되지 않음**
- Python 가상 환경이 활성화되어 있는지 확인합니다(터미널 프롬프트에 **(.venv)**가 표시되어야 함).
- 종속성이 설치되어 있는지 확인합니다(**pip install -r requirements.txt**).
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수를 불러왔는지 확인합니다.
- **python app.py**를 실행할 때 *client* 디렉터리에 있는지 확인합니다.

**인증 또는 액세스 거부 오류**
- 배포 스크립트 옵션 **2**를 실행하여 Entra ID 액세스를 구성했는지 확인합니다.
- 사용자에게 **Contributor** 역할과 **Cosmos DB Built-in Data Contributor** 역할이 모두 있는지 확인합니다.
- 터미널 세션에서 **COSMOS_ENDPOINT**가 올바르게 설정되었는지 확인합니다.

**Cosmos DB 작업 실패**
- 배포 스크립트 옵션 **3**을 실행하여 Cosmos DB 계정이 준비되었는지 확인합니다.
- 배포 중 데이터베이스와 컨테이너가 만들어졌는지 확인합니다.
- 컨테이너가 파티션 키로 **/documentId**를 사용하는지 확인합니다.

**환경 변수 문제**
- 배포 스크립트 옵션 **4**를 실행하여 *.env* 파일이 만들어졌는지 확인합니다.
- 새 터미널을 만든 뒤 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행합니다.
- **echo $COSMOS_ENDPOINT**(Bash) 또는 **$env:COSMOS_ENDPOINT**(PowerShell)를 실행하여 변수가 설정되었는지 확인합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 **source .venv/bin/activate**를 사용합니다.
- Windows PowerShell에서는 **.\venv\Scripts\Activate.ps1**를 사용합니다.
- **activate** 스크립트가 없으면 **python3-venv** 패키지를 다시 설치하고 venv를 다시 만듭니다.
