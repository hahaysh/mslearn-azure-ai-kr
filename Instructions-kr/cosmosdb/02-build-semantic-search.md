---
lab:
  topic: Azure Cosmos DB for NoSQL
  title: Azure Cosmos DB for NoSQL을 사용하여 의미 체계 검색 애플리케이션 구축
  description: Azure Cosmos DB for NoSQL에서 벡터 유사성 검색을 구현하여 지원 티켓 데이터에 의미 체계 검색을 사용하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Cosmos DB
---

# Azure Cosmos DB for NoSQL을 사용하여 의미 체계 검색 애플리케이션 구축

이 연습에서는 Azure Cosmos DB for NoSQL을 사용하여 벡터 유사성 검색을 구현합니다. 벡터 검색은 텍스트의 고차원 벡터 표현을 비교하여 의미상 일치하는 항목을 찾으므로 정확히 같은 용어가 없어도 관련 결과를 찾을 수 있습니다. 벡터 임베딩 및 인덱싱 정책으로 컨테이너를 구성하고, 미리 계산된 임베딩이 포함된 지원 티켓을 로드한 다음, **VectorDistance** 함수를 사용하여 유사성 쿼리를 실행합니다. 이 패턴은 고객 문제를 더 빠르게 해결하도록 유사한 지원 사례를 찾는 등 의미 체계 검색을 수행하는 AI 애플리케이션의 토대가 됩니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트 구성
- 벡터 검색 기능을 갖춘 Azure Cosmos DB for NoSQL 계정 배포
- 벡터 유사성 검색을 위한 Python 함수 작성
- 벡터 임베딩 및 인덱싱 정책으로 컨테이너 만들기
- Flask 웹 애플리케이션을 사용하여 벡터 검색 테스트

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
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-implement-vector-python.zip
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

이 섹션에서는 배포 스크립트를 실행하여 벡터 검색 기능이 있는 Cosmos DB 계정을 배포합니다.

1. 프로젝트 루트 디렉터리에 있는지 확인한 다음 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Cosmos DB 계정 만들기(Create Cosmos DB account)** 옵션을 실행합니다. **EnableNoSQLVectorSearch** 기능과 데이터베이스가 포함된 Cosmos DB for NoSQL 계정이 만들어집니다. **참고:** 배포를 완료하는 데 5~10분 정도 걸릴 수 있습니다.

    >**IMPORTANT:** 연습을 진행하는 동안 배포가 실행 중인 터미널을 열어 두세요. 터미널에서 배포가 계속되는 동안 연습의 다음 섹션으로 진행할 수 있습니다.

## 앱 완성

이 섹션에서는 벡터 검색 함수와 컨테이너 설정 스크립트의 Python 코드를 완성합니다. 벡터 함수는 **VectorDistance** 함수를 사용하여 유사성 검색을 수행하고, 설정 스크립트는 필요한 벡터 정책으로 컨테이너를 만듭니다.

### 벡터 검색 함수 완성

이 섹션에서는 벡터 유사성 검색을 수행하는 함수를 추가하여 *vector_functions.py* 파일을 완성합니다. 이 함수는 **VectorDistance** 함수를 사용하여 쿼리 벡터와 티켓 임베딩 간의 유사성을 계산합니다. 지원 애플리케이션은 새 문제가 보고될 때 유사한 티켓을 찾는 데 이 함수를 사용할 수 있습니다.

1. VS Code에서 *client/vector_functions.py* 파일을 엽니다.

> **Tip:** 일치하는 **BEGIN** 및 **END** 주석과 들여쓰기 수준이 같도록 코드를 붙여 넣습니다. 코드 블록의 정렬이 맞지 않으면 붙여 넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **BEGIN STORE VECTOR DOCUMENT FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 유사성 검색에 사용할 벡터 임베딩과 함께 지원 티켓을 저장합니다.

    ```python
    def store_vector_document(
        document_id: str,
        chunk_id: str,
        content: str,
        embedding: list,
        metadata: dict = None
    ) -> dict:
        """Store a document with its vector embedding for similarity search."""
        container = get_container()

        # Build the document structure with embedding for vector search
        # The 'id' field is required by Cosmos DB and must be unique within the partition
        # The 'documentId' field is our partition key - chunks from the same source document
        # are stored together for efficient retrieval
        # The 'embedding' field contains the vector that will be used for similarity search
        document = {
            "id": chunk_id,
            "documentId": document_id,
            "content": content,
            "embedding": embedding,  # 256-dimensional vector for similarity search
            "metadata": metadata or {},
            "createdAt": datetime.utcnow().isoformat(),
            "chunkIndex": metadata.get("chunkIndex", 0) if metadata else 0
        }

        # upsert_item inserts if new, updates if exists (based on id + partition key)
        # This is idempotent - safe to call multiple times with the same data
        response = container.upsert_item(body=document)

        # Request Units (RUs) measure the cost of database operations in Cosmos DB
        # Tracking RU consumption helps optimize queries and estimate costs
        ru_charge = response.get_response_headers()['x-ms-request-charge']

        return {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "ru_charge": float(ru_charge)
        }
    ```

1. **BEGIN VECTOR SIMILARITY SEARCH FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 벡터 거리를 사용하여 쿼리와 가장 유사한 티켓을 찾습니다.

    ```python
    def vector_similarity_search(
        query_embedding: list,
        top_n: int = 5
    ) -> list:
        """
        Find documents most similar to the query using vector distance.

        Uses the VectorDistance function to calculate cosine similarity between
        the query embedding and document embeddings stored in Cosmos DB.
        Results are ordered by similarity (lowest distance = most similar).
        """
        container = get_container()

        # The VectorDistance function calculates the distance between two vectors
        # Using cosine distance: 0 = identical, 2 = opposite
        # We order by distance ascending so most similar results come first
        # The @queryVector parameter contains our 256-dimensional query embedding
        query = """
            SELECT TOP @topN
                c.id,
                c.documentId,
                c.content,
                c.metadata,
                VectorDistance(c.embedding, @queryVector) AS similarityScore
            FROM c
            ORDER BY VectorDistance(c.embedding, @queryVector)
        """

        items = container.query_items(
            query=query,
            parameters=[
                {"name": "@topN", "value": top_n},
                {"name": "@queryVector", "value": query_embedding}
            ],
            enable_cross_partition_query=True
        )

        return [
            {
                "chunk_id": item["id"],
                "document_id": item["documentId"],
                "content": item["content"],
                "metadata": item["metadata"],
                "similarity_score": item["similarityScore"]
            }
            for item in items
        ]
    ```

1. **BEGIN FILTERED VECTOR SEARCH FUNCTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 벡터 유사성 검색과 메타데이터 필터링을 결합하여 하이브리드 쿼리를 수행합니다.

    ```python
    def filtered_vector_search(
        query_embedding: list,
        category: str = None,
        top_n: int = 5
    ) -> list:
        """
        Combine vector similarity search with metadata filtering.

        This hybrid approach first filters documents by category (or other metadata),
        then ranks the filtered results by vector similarity. This is useful for
        narrowing results to a specific domain before applying semantic search.
        """
        container = get_container()

        # Build WHERE clause for metadata filtering
        # The filter is applied BEFORE vector ranking, reducing the search space
        where_clause = ""
        parameters = [
            {"name": "@topN", "value": top_n},
            {"name": "@queryVector", "value": query_embedding}
        ]

        if category:
            where_clause = "WHERE c.metadata.category = @category"
            parameters.append({"name": "@category", "value": category})

        # Filtered vector search: apply metadata filter, then rank by similarity
        query = f"""
            SELECT TOP @topN
                c.id,
                c.documentId,
                c.content,
                c.metadata,
                VectorDistance(c.embedding, @queryVector) AS similarityScore
            FROM c
            {where_clause}
            ORDER BY VectorDistance(c.embedding, @queryVector)
        """

        items = container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )

        return [
            {
                "chunk_id": item["id"],
                "document_id": item["documentId"],
                "content": item["content"],
                "metadata": item["metadata"],
                "similarity_score": item["similarityScore"]
            }
            for item in items
        ]
    ```

1. *vector_functions.py* 파일의 변경 내용을 저장합니다.

1. 잠시 시간을 내어 파일의 모든 코드를 검토합니다.

### 컨테이너 설정 코드 검토

이 섹션에서는 벡터 임베딩 및 인덱싱 정책이 포함된 Cosmos DB 컨테이너를 만드는 데 사용하는 *setup_container.py* 스크립트를 검토합니다. 배포 스크립트에서 이러한 정책이 포함된 컨테이너를 이미 만들었지만, 코드를 검토하면 구성을 이해하는 데 도움이 됩니다.

1. VS Code에서 *client/setup_container.py* 파일을 엽니다.

1. **BEGIN CREATE VECTOR CONTAINER FUNCTION** 주석을 검색하고 코드를 검토합니다. 다음 두 가지 주요 정책 구성을 살펴봅니다.

    ```python
    def create_vector_container():
        """
        Create a container with vector embedding and indexing policies.
        """
        database = get_database()
        container_name = os.environ.get("COSMOS_CONTAINER", "vectors")

        # Define the vector embedding policy
        # This tells Cosmos DB how to handle vector data at the /embedding path
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/embedding",
                    "dataType": "float32",
                    "distanceFunction": "cosine",
                    "dimensions": 256
                }
            ]
        }

        # Define the indexing policy with vector index
        # - DiskANN provides efficient approximate nearest neighbor search
        # - Exclude /embedding/* from standard indexing (vectors use their own index)
        indexing_policy = {
            "indexingMode": "consistent",
            "automatic": True,
            "includedPaths": [
                {"path": "/*"}
            ],
            "excludedPaths": [
                {"path": "/embedding/*"}
            ],
            "vectorIndexes": [
                {
                    "path": "/embedding",
                    "type": "diskANN"
                }
            ]
        }

        # Create the container with vector policies
        # partition_key determines how data is distributed across physical partitions
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/documentId"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )

        return container
    ```

1. 잠시 시간을 내어 주요 구성 요소를 이해합니다.

    | 정책(Policy) | 설정(Setting) | 목적(Purpose) |
    |--------|---------|---------|
    | **vectorEmbeddings** | path: /embedding | 벡터 데이터가 저장되는 위치 |
    | **vectorEmbeddings** | dimensions: 256 | 임베딩 모델 출력 차원과 일치해야 함 |
    | **vectorEmbeddings** | distanceFunction: cosine | VectorDistance에 사용할 유사성 메트릭 |
    | **vectorIndexes** | type: diskANN | 효율적인 근사 최근접 이웃 알고리즘 |
    | **excludedPaths** | /embedding/* | 벡터는 표준 인덱스가 아닌 특수 인덱스를 사용 |

이어서 Azure 리소스 배포를 마무리합니다.

## Azure 리소스 배포 완료

이 섹션에서는 배포 스크립트로 돌아가 컨테이너를 만들고 Entra ID 액세스를 구성한 다음 연결 정보를 검색합니다.

1. **Cosmos DB 계정 만들기(Create Cosmos DB account)** 작업이 완료되면 **2**를 입력하여 **컨테이너 만들기(Create container)** 옵션을 실행합니다. 유사성 검색에 필요한 임베딩 및 인덱싱 정책으로 벡터 컨테이너가 만들어집니다.

1. **3**을 입력하여 **Entra ID 액세스 구성(Configure Entra ID access)** 옵션을 실행합니다. 이 옵션은 Cosmos DB 데이터 평면에 액세스하는 데 필요한 역할을 사용자 계정에 할당합니다.

1. **4**를 입력하여 **배포 상태 확인(Check deployment status)** 옵션을 실행합니다. 벡터 검색 기능이 사용하도록 설정된 상태로 Cosmos DB 계정이 준비되었는지 확인합니다.

1. **5**를 입력하여 **연결 정보 검색(Retrieve connection info)** 옵션을 실행합니다. 필요한 환경 변수가 포함된 파일이 만들어집니다.

1. **6**을 입력하여 배포 스크립트를 종료합니다.

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

이어서 Python 환경을 설정하고 애플리케이션을 실행합니다.

## Python 환경 설정

이 섹션에서는 Python 가상 환경을 만들고 컨테이너 설정 스크립트와 Flask 애플리케이션에 필요한 종속성을 설치합니다.

1. 다음 명령을 실행하여 *client* 디렉터리로 이동합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 Python 스크립트용 가상 환경을 만듭니다. 환경에 따라 **python** 또는 **python3** 명령을 사용할 수 있습니다.

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

1. 다음 명령을 실행하여 Python 종속성을 설치합니다. 이 명령은 **flask**, **azure-cosmos**, **azure-identity** 라이브러리를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

이어서 Flask 애플리케이션을 사용하여 벡터 검색 함수를 테스트합니다.

## Flask 앱으로 벡터 검색 함수 테스트

이 섹션에서는 Flask 웹 애플리케이션을 시작하고 인터페이스를 사용하여 만든 벡터 검색 함수를 테스트합니다. 앱에서 샘플 지원 티켓을 로드하고 벡터 유사성 검색을 실행할 수 있습니다.

1. *client* 디렉터리에 있고 가상 환경이 활성화되어 있는지 확인합니다. 터미널 프롬프트에 **(.venv)**가 표시되어야 합니다.

1. 다음 명령을 실행하여 Flask 애플리케이션을 시작합니다.

    ```bash
    python app.py
    ```

1. 브라우저를 열고 `http://127.0.0.1:5000`으로 이동하여 애플리케이션을 확인합니다.

### 샘플 데이터 로드

이 섹션에서는 앱을 사용하여 미리 계산된 임베딩이 포함된 샘플 지원 티켓을 Cosmos DB 컨테이너에 로드합니다. 샘플 데이터에는 청구, 기술, 계정, 배송 등 여러 범주의 지원 티켓 12개가 포함되며, 각 티켓에는 256차원 임베딩 벡터가 있습니다. 앱은 *vector_functions.py*에서 만든 **store_vector_document()** 함수를 호출합니다.

1. **샘플 데이터 로드(Load Sample Data)** 섹션에서 **벡터 데이터 로드(Load Vector Data)**를 선택합니다. *sample_vectors.json* 파일의 미리 계산된 임베딩이 포함된 티켓이 삽입됩니다.

1. **결과(Results)** 섹션에 로드된 티켓 수와 총 RU(Request Unit) 사용량을 표시하는 성공 메시지가 나타나는지 확인합니다.

### 벡터 유사성 검색

이 섹션에서는 미리 계산된 쿼리 벡터를 사용하여 의미 체계 검색을 수행합니다. 앱은 *vector_functions.py*에서 만든 **vector_similarity_search()** 함수를 호출합니다.

1. **벡터 유사성 검색(Vector Similarity Search)** 섹션의 **쿼리 선택(Select Query)** 드롭다운에서 **I can't login to my account**를 선택합니다.

1. 기본값인 **상위 5개(Top 5)**를 유지하고 **검색(Search)**을 선택합니다.

1. 유사성 점수 순으로 정렬된 티켓이 결과에 표시되는지 확인합니다. 쿼리와 다른 용어를 사용하더라도 인증 및 계정 액세스에 관한 티켓이 먼저 나타나는지 살펴봅니다.

1. **My payment was charged twice** 또는 **Package hasn't arrived yet**와 같은 다른 쿼리를 선택하여 의미 체계 검색이 관련 지원 사례를 찾는 방식을 확인합니다.

### 필터링된 벡터 검색

이 섹션에서는 메타데이터 필터링과 벡터 유사성 순위 지정을 결합합니다. 앱은 *vector_functions.py*에서 만든 **filtered_vector_search()** 함수를 호출합니다. 필터링을 통해 결과가 특정 범주로 좁혀지는 것을 확인합니다.

1. **필터링된 벡터 검색(Filtered Vector Search)** 섹션의 **쿼리 선택(Select Query)** 드롭다운에서 **I can't login to my account**를 선택합니다.

1. **범주별 필터링(Filter by Category)** 드롭다운에서 **technical**을 선택합니다.

1. **필터를 적용하여 검색(Search with Filter)**을 선택하여 필터링된 검색을 실행합니다.

1. 결과를 검토합니다. **technical** 범주의 티켓만 반환되고 쿼리와의 유사성 순으로 정렬되는지 확인합니다.

1. 같은 쿼리에 **account** 범주를 적용하여 의미상 관련성은 유지하면서 계정 관련 문제로 결과가 제한되는 것을 확인합니다.

1. 터미널로 돌아가 **Ctrl+C**를 눌러 Flask 애플리케이션을 중지합니다.

## 요약

이 연습에서는 Azure Cosmos DB for NoSQL을 사용하여 벡터 유사성 검색을 구현했습니다. **EnableNoSQLVectorSearch** 기능이 포함된 Azure Cosmos DB 계정을 배포하고 Entra ID 인증을 구성했습니다. **VectorDistance** 함수를 사용할 수 있도록 Python SDK로 벡터 임베딩 및 인덱싱 정책이 포함된 컨테이너를 만들었습니다. 임베딩과 함께 지원 티켓을 저장하고, 벡터 유사성 검색을 수행하고, 벡터 검색과 메타데이터 필터를 결합하는 Python 함수를 작성했습니다. Flask 웹 애플리케이션으로 워크플로를 테스트했습니다. 이 패턴을 사용하면 정확한 키워드가 아니라 의미를 기준으로 지원 데이터에서 유사한 티켓을 찾아 의미 체계 검색을 수행할 수 있습니다.

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
- 배포 스크립트 옵션 **3**을 실행하여 Entra ID 액세스를 구성했는지 확인합니다.
- 사용자에게 **Contributor** 역할과 **Cosmos DB Built-in Data Contributor** 역할이 모두 있는지 확인합니다.
- 터미널 세션에서 **COSMOS_ENDPOINT**가 올바르게 설정되었는지 확인합니다.

**벡터 검색 결과가 없거나 오류가 발생함**
- 배포 스크립트 옵션 **2**를 실행하여 벡터 컨테이너가 만들어졌는지 확인합니다.
- 컨테이너에 벡터 임베딩 정책이 구성되었는지 확인합니다(배포 스크립트 옵션 **4**로 상태 확인).
- 검색을 실행하기 전에 샘플 티켓을 로드했는지 확인합니다.

**setup_container.py 실패**
- Python 가상 환경이 활성화되어 있는지 확인합니다.
- 환경 변수(**COSMOS_ENDPOINT**, **COSMOS_DATABASE**, **COSMOS_CONTAINER**)가 설정되었는지 확인합니다.
- 컨테이너가 이미 있으면 스크립트가 기존 컨테이너를 사용합니다.

**Cosmos DB 작업 실패**
- 배포 스크립트 옵션 **4**를 실행하여 Cosmos DB 계정이 준비되었는지 확인합니다.
- 배포 중 데이터베이스가 만들어졌는지 확인합니다.
- 계정에 **EnableNoSQLVectorSearch** 기능이 있는지 확인합니다.

**환경 변수 문제**
- 배포 스크립트 옵션 **5**를 실행하여 *.env* 파일이 만들어졌는지 확인합니다.
- 새 터미널을 만든 뒤 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행합니다.
- **echo $COSMOS_ENDPOINT**(Bash) 또는 **$env:COSMOS_ENDPOINT**(PowerShell)를 실행하여 변수가 설정되었는지 확인합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 **source .venv/bin/activate**를 사용합니다.
- Windows PowerShell에서는 **.\.venv\Scripts\Activate.ps1**를 사용합니다.
- **activate** 스크립트가 없으면 **python3-venv** 패키지를 다시 설치하고 venv를 다시 만듭니다.
