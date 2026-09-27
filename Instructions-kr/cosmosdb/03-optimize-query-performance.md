---
lab:
  topic: Azure Cosmos DB for NoSQL
  title: Azure Cosmos DB for NoSQL에서 벡터 인덱스를 사용하여 쿼리 성능 최적화
  description: Azure Cosmos DB for NoSQL에서 벡터 인덱싱 전략을 비교하고 조정하여 쿼리 성능을 최적화하고 RU 비용을 줄이는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Cosmos DB
---

# Azure Cosmos DB for NoSQL에서 벡터 인덱스를 사용하여 쿼리 성능 최적화

이 연습에서는 벡터 인덱싱 전략을 비교하고 조정하여 Azure Cosmos DB for NoSQL의 쿼리 성능을 최적화합니다. 벡터 인덱스는 검색 품질과 요청 단위(Request Unit, RU) 사용량 모두에 큰 영향을 줍니다. flat, quantizedFlat, diskANN의 세 가지 인덱스 유형으로 컨테이너를 만들고, 동일한 샘플 데이터를 로드한 다음, 성능 차이를 측정하기 위해 비교 검색을 실행합니다. 이 실습을 통해 AI 애플리케이션의 요구 사항에 적합한 인덱싱 전략을 선택할 수 있습니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트를 구성합니다.
- 벡터 검색 기능이 있는 Azure Cosmos DB for NoSQL 계정을 배포합니다.
- 벡터 인덱스 성능을 비교하는 Python 함수를 작성합니다.
- flat, quantizedFlat, diskANN 인덱스를 사용하여 컨테이너를 만듭니다.
- Flask 웹 애플리케이션을 사용하여 인덱스 성능을 테스트하고 비교합니다.

이 연습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에서 실행합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. Cosmos DB 계정을 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/cosmosdb-optimize-query-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기(Open Folder)...**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위에 있는 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 부분은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 안내에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 연습에 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.DocumentDB
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 벡터 검색 기능이 있는 Cosmos DB 계정을 배포합니다.

1. 프로젝트의 루트 디렉터리에 있는지 확인한 다음 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Cosmos DB 계정 만들기(Create Cosmos DB account)** 옵션을 실행합니다. 그러면 **EnableNoSQLVectorSearch** 기능이 활성화된 Cosmos DB for NoSQL 계정과 데이터베이스가 만들어집니다. **참고:** 배포를 완료하는 데 5~10분이 걸릴 수 있습니다.

    >**중요:** 연습이 끝날 때까지 배포를 실행하는 터미널을 열어 두세요. 터미널에서 배포가 계속되는 동안 연습의 다음 섹션으로 진행할 수 있습니다.

## 인덱스 비교 함수 완성

이 섹션에서는 벡터 인덱스 성능을 비교하는 Python 코드를 완성하고 컨테이너 설정 스크립트를 검토합니다. 유사도 검색을 수행하고 RU 사용량 및 실행 시간을 추적하는 함수를 추가합니다. 또한 각 인덱스 유형을 만드는 방법을 이해하기 위해 서로 다른 벡터 인덱싱 구성을 살펴봅니다.

### 벡터 유사도 검색 스크립트 완성

이 섹션에서는 성능 추적 기능을 사용하여 벡터 유사도 검색을 수행하는 함수를 추가해 *index_functions.py* 파일을 완성합니다. 이 함수는 각 컨테이너에서 호출되어 서로 다른 인덱스 유형이 동일한 쿼리를 처리하는 방식을 비교합니다.

1. VS Code에서 *client/index_functions.py* 파일을 엽니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 동일한 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **BEGIN VECTOR SIMILARITY SEARCH FUNCTION** 주석을 검색하고 해당 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 쿼리와 유사한 문서를 찾고 성능 메트릭을 추적합니다.

    ```python
    def vector_similarity_search(
        container_name: str,
        query_embedding: list,
        top_n: int = 5
    ) -> dict:
        """
        Find documents most similar to the query using vector distance.

        This function performs a vector similarity search using the VectorDistance
        function and tracks the RU consumption and execution time. Results are
        ordered by distance (lowest = most similar).

        Args:
            container_name: Name of the container to search
            query_embedding: 256-dimensional query vector
            top_n: Number of results to return

        Returns:
            Dictionary containing results, ru_charge, and execution_time_ms
        """
        container = get_container(container_name)

        # Track execution time for performance comparison
        start_time = time.time()

        # The VectorDistance function calculates distance between vectors
        # Using cosine distance: 0 = identical, 2 = opposite
        # Results ordered by distance ascending (most similar first)
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

        items = list(container.query_items(
            query=query,
            parameters=[
                {"name": "@topN", "value": top_n},
                {"name": "@queryVector", "value": query_embedding}
            ],
            enable_cross_partition_query=True
        ))

        end_time = time.time()
        execution_time_ms = (end_time - start_time) * 1000

        # Get RU charge from the query - note: this is approximate for multi-page results
        # For accurate RU tracking in production, use Azure Monitor
        ru_charge = 0.0
        try:
            # The last_response_headers contains the RU charge
            ru_charge = float(container.client_connection.last_response_headers.get(
                'x-ms-request-charge', 0
            ))
        except Exception:
            pass  # RU tracking may not be available in all scenarios

        results = [
            {
                "chunk_id": item["id"],
                "document_id": item["documentId"],
                "content": item["content"],
                "metadata": item["metadata"],
                "similarity_score": item["similarityScore"]
            }
            for item in items
        ]

        return {
            "results": results,
            "ru_charge": ru_charge,
            "execution_time_ms": round(execution_time_ms, 2)
        }
    ```

1. **BEGIN COMPARE INDEX PERFORMANCE FUNCTION** 주석을 검색하고 해당 주석 바로 뒤에 다음 코드를 추가합니다. 이 함수는 세 컨테이너 모두에 동일한 쿼리를 실행하고 비교 결과를 반환합니다.

    ```python
    def compare_index_performance(
        query_embedding: list,
        top_n: int = 5
    ) -> dict:
        """
        Run the same vector search query against all three containers and compare performance.

        This function executes identical vector similarity searches against containers
        with different indexing strategies (flat, quantizedFlat, diskANN) to demonstrate
        the performance characteristics of each approach.

        Args:
            query_embedding: 256-dimensional query vector
            top_n: Number of results to return from each container

        Returns:
            Dictionary with results from each container including RU costs and timing
        """
        comparison = {}

        # Test each container with the same query
        for index_type, container_name in [
            ("flat", CONTAINER_FLAT),
            ("quantizedFlat", CONTAINER_QUANTIZED),
            ("diskANN", CONTAINER_DISKANN)
        ]:
            try:
                result = vector_similarity_search(container_name, query_embedding, top_n)
                comparison[index_type] = {
                    "container": container_name,
                    "results": result["results"],
                    "ru_charge": result["ru_charge"],
                    "execution_time_ms": result["execution_time_ms"],
                    "result_count": len(result["results"]),
                    "status": "success"
                }
            except Exception as e:
                comparison[index_type] = {
                    "container": container_name,
                    "results": [],
                    "ru_charge": 0,
                    "execution_time_ms": 0,
                    "result_count": 0,
                    "status": "error",
                    "error": str(e)
                }

        return comparison
    ```

1. *index_functions.py* 파일의 변경 내용을 저장합니다.

1. 잠시 시간을 내어 스크립트의 코드를 모두 검토합니다.

### 컨테이너 설정 코드 검토

이 섹션에서는 서로 다른 벡터 인덱싱 전략으로 컨테이너를 만드는 *setup_containers.py* 스크립트를 검토합니다. 벡터 임베딩 정책(경로, 차원, 데이터 형식, 거리 함수)은 컨테이너를 만들 때 설정되며 이후에는 변경할 수 없습니다. 그러나 벡터 인덱스 유형은 인덱싱 정책의 일부이므로 기존 컨테이너에서 업데이트할 수 있습니다. 인덱스 유형을 변경하면 Cosmos DB가 백그라운드에서 인덱스 변환을 수행합니다. 이러한 유연성이 있더라도 인덱스 유형을 미리 테스트하는 것이 여전히 모범 사례입니다. 일반적으로 각 인덱스 유형을 사용하는 테스트 컨테이너를 만들고, 대표 샘플 데이터를 로드한 다음, 벤치마크 쿼리를 실행하여 프로덕션 구성을 확정하기 전에 RU 비용과 대기 시간을 측정합니다.

1. VS Code에서 *client/setup_containers.py* 파일을 엽니다.

1. **BEGIN CREATE FLAT CONTAINER FUNCTION** 주석을 검색하고 코드를 검토합니다. flat 인덱스가 어떻게 구성되는지 살펴봅니다.

    ```python
    def create_flat_container():
        """
        Create a container with a flat vector index.
        """
        database = get_database()
        container_name = "vectors-flat"

        # Vector embedding policy defines how Cosmos DB handles vector data
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

        # Flat index: exact search, compares query against all vectors
        # Higher RU cost for large datasets but guaranteed best results
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
                    "type": "flat"
                }
            ]
        }

        print(f"Creating container '{container_name}' with flat vector index...")

        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/documentId"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )

        print(f"✓ Container '{container_name}' created with flat index")
        print("  - Index type: flat (exact nearest neighbor)")
        print("  - Best for: small datasets, exact results required")

        return container
    ```

1. **BEGIN CREATE QUANTIZED CONTAINER FUNCTION** 주석을 검색하고 quantizedFlat 구성을 검토합니다.

    ```python
    def create_quantized_container():
        """
        Create a container with a quantized flat vector index.

        The quantizedFlat index compresses vectors using scalar quantization,
        reducing memory usage while maintaining good search quality. It still
        performs exact search but on compressed representations. Suitable for:
        - Medium datasets (10,000 - 100,000 vectors)
        - Memory-constrained environments
        - Balance between performance and accuracy
        """
        database = get_database()
        container_name = "vectors-quantized"

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

        # QuantizedFlat index: compressed vectors for memory efficiency
        # Lower memory footprint with slight accuracy trade-off
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
                    "type": "quantizedFlat"
                }
            ]
        }

        print(f"Creating container '{container_name}' with quantizedFlat vector index...")

        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/documentId"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )

        print(f"✓ Container '{container_name}' created with quantizedFlat index")
        print("  - Index type: quantizedFlat (compressed exact search)")
        print("  - Best for: medium datasets, memory efficiency")

        return container
    ```

1. **BEGIN CREATE DISKANN CONTAINER FUNCTION** 주석을 검색하고 diskANN 구성을 검토합니다.

    ```python
    def create_diskann_container():
        """
        Create a container with a DiskANN vector index.

        DiskANN (Disk-based Approximate Nearest Neighbor) uses a graph-based
        algorithm for efficient similarity search. It provides excellent
        performance with high recall rates (typically 95%+). Recommended for:
        - Large datasets (> 100,000 vectors)
        - Production workloads
        - Low-latency requirements
        """
        database = get_database()
        container_name = "vectors-diskann"

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

        # DiskANN index: approximate nearest neighbor with graph-based search
        # Best performance for large datasets, slight accuracy trade-off
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

        print(f"Creating container '{container_name}' with diskANN vector index...")

        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/documentId"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )

        print(f"✓ Container '{container_name}' created with diskANN index")
        print("  - Index type: diskANN (approximate nearest neighbor)")
        print("  - Best for: large datasets, production workloads")

        return container
    ```

1. 인덱스 유형 간 주요 차이점을 잠시 살펴봅니다.

    | 인덱스 유형 | 검색 방법 | 적합한 용도 | 장단점 |
    |------------|----------|------------|--------|
    | **flat** | 정확한 최근접 이웃 | 소규모 데이터 세트, 높은 정확도 | 대규모 데이터 세트에서는 RU가 더 많이 필요함 |
    | **quantizedFlat** | 압축된 정확 검색 | 중간 규모 데이터 세트, 메모리 효율성 | 정확도가 약간 낮아짐 |
    | **diskANN** | 근사 그래프 검색 | 대규모 데이터 세트, 프로덕션 | 재현율 약 95%, 최고 성능 |

다음으로 Azure 리소스 배포를 마무리합니다.

## Azure 리소스 배포 완료

이 섹션에서는 배포 스크립트로 돌아가 컨테이너를 만들고, Entra ID 액세스를 구성하고, 연결 정보를 가져옵니다.

1. **Cosmos DB 계정 만들기(Create Cosmos DB account)** 작업이 완료되면 **2**를 입력하여 **컨테이너 만들기(Create containers)** 옵션을 실행합니다. 그러면 서로 다른 벡터 인덱싱 전략인 flat, quantizedFlat, diskANN을 사용하는 컨테이너 세 개가 만들어집니다.

1. **3**을 입력하여 **Entra ID 액세스 구성(Configure Entra ID access)** 옵션을 실행합니다. 그러면 Cosmos DB 데이터 평면에 액세스하는 데 필요한 역할이 사용자 계정에 할당됩니다.

1. **4**를 입력하여 **배포 상태 확인(Check deployment status)** 옵션을 실행합니다. Cosmos DB 계정이 벡터 검색 기능이 활성화된 준비 완료 상태인지 확인합니다.

1. **5**를 입력하여 **연결 정보 검색(Retrieve connection info)** 옵션을 실행합니다. 그러면 필요한 환경 변수가 포함된 파일이 만들어집니다.

1. **6**을 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드하려면 다음 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 만드는 명령을 실행해야 할 수 있습니다.

다음으로 Python 환경을 설정하고 애플리케이션을 실행합니다.

## Python 환경 설정

이 섹션에서는 Python 가상 환경을 만들고 컨테이너 설정 스크립트와 Flask 애플리케이션에 필요한 종속성을 설치합니다.

1. *client* 디렉터리로 이동하려면 다음 명령을 실행합니다.

    ```
    cd client
    ```

1. Python 스크립트용 가상 환경을 만들려면 다음 명령을 실행합니다. 환경에 따라 **python** 또는 **python3** 명령을 사용해야 할 수 있습니다.

    ```
    python -m venv .venv
    ```

1. Python 환경을 활성화하려면 다음 명령을 실행합니다. **참고:** Linux/macOS에서는 Bash 명령을 사용하고 Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

1. Python 종속성을 설치하려면 다음 명령을 실행합니다. 그러면 **flask**, **azure-cosmos**, **azure-identity** 라이브러리가 설치됩니다.

    ```bash
    pip install -r requirements.txt
    ```

다음으로 Flask 애플리케이션을 사용하여 벡터 인덱스 성능을 테스트합니다.

## Flask 앱으로 벡터 인덱스 성능 테스트

이 섹션에서는 Flask 웹 애플리케이션을 시작하고 인터페이스에서 세 가지 인덱싱 전략의 벡터 검색 성능을 비교합니다. 앱은 모든 컨테이너에서 동일한 쿼리를 실행하고 결과를 나란히 표시합니다.

1. 가상 환경이 활성화된 상태로 *client* 디렉터리에 있는지 확인합니다. 터미널 프롬프트에 **(.venv)**가 표시되어야 합니다.

1. Flask 애플리케이션을 시작하려면 다음 명령을 실행합니다.

    ```bash
    python app.py
    ```

1. 브라우저를 열고 `http://127.0.0.1:5000`으로 이동하여 애플리케이션을 확인합니다.

### 샘플 데이터 로드

이 섹션에서는 앱을 사용해 미리 계산된 임베딩이 포함된 샘플 지원 티켓을 세 컨테이너 모두에 로드합니다. 동일한 데이터를 로드하면 인덱스 성능을 공정하게 비교할 수 있습니다.

1. 페이지 상단의 **컨테이너 상태(Container Status)** 섹션을 확인합니다. 처음에는 세 컨테이너 모두 문서가 0개로 표시되어야 합니다.

1. **샘플 데이터 로드(Load Sample Data)** 섹션에서 **모든 컨테이너에 데이터 로드(Load Data to All Containers)**를 선택합니다. 그러면 *sample_vectors.json* 파일의 미리 계산된 임베딩이 포함된 지원 티켓 500개가 각 컨테이너에 삽입됩니다. 업로드는 병렬 처리를 사용하여 데이터를 효율적으로 로드하며 일반적으로 30~45초가 걸립니다.

1. 로드된 문서 수와 각 컨테이너의 RU 비용이 표시된 성공 메시지가 나타나는지 확인합니다. 쓰기 RU 비용은 인덱스 유형에 따라 약간 다를 수 있습니다.

### 벡터 검색 성능 비교

이 섹션에서는 벡터 유사도 검색을 수행하고 각 인덱스 유형이 동일한 쿼리를 처리하는 방식을 비교합니다. 앱은 RU 비용과 실행 시간을 나란히 표시합니다.

1. **벡터 검색 비교(Vector Search Comparison)** 섹션에서 **쿼리 선택(Select Query)** 드롭다운의 **I can't login to my account**(계정에 로그인할 수 없습니다)를 선택합니다.

1. 기본값인 **상위 5개(Top 5)** 결과를 유지하고 **인덱스 성능 비교(Compare Index Performance)**를 선택합니다.

1. 다음 항목이 표시된 **인덱스 성능 비교(Index Performance Comparison)** 테이블을 검토합니다.
    - 각 컨테이너의 **결과(Results)** 수
    - 각 쿼리의 **RU 비용(RU Cost)**
    - 실행에 걸린 **시간(ms)(Time (ms))**

1. 아래로 스크롤하여 각 컨테이너에서 반환된 결과를 나란히 확인합니다. 다음 사항에 유의합니다.
    - 이처럼 작은 데이터 세트에서는 세 인덱스 모두 비슷한 결과를 반환해야 합니다.
    - RU 비용은 인덱스 유형에 따라 다를 수 있습니다.
    - diskANN 인덱스는 일반적으로 규모가 커질수록 RU 소비량이 더 적습니다.

1. **My payment was charged twice**(결제가 두 번 청구되었습니다) 또는 **Package hasn't arrived yet**(패키지가 아직 도착하지 않았습니다)와 같은 다른 쿼리도 시도하여 검색 전반에서 일관된 패턴이 나타나는지 확인합니다.

### 필터링된 검색 성능 비교

이 섹션에서는 메타데이터 필터링과 벡터 유사도 검색을 결합합니다. 필터링은 벡터 순위를 적용하기 전에 검색 범위를 좁히므로 인덱스 유형마다 성능에 미치는 영향이 다를 수 있습니다.

1. **필터링된 벡터 검색 비교(Filtered Vector Search Comparison)** 섹션에서 **쿼리 선택(Select Query)** 드롭다운의 **Protect my account from hackers**(해커로부터 내 계정 보호)를 선택합니다.

1. **범주별 필터링(Filter by Category)** 드롭다운에서 **account**를 선택합니다.

1. **필터링된 검색 비교(Compare Filtered Search)**를 선택하여 모든 컨테이너에서 필터링된 검색을 실행합니다.

1. 결과를 검토합니다. 다음 사항에 유의합니다.
    - **account** 범주의 문서만 반환됩니다.
    - 필터링과 벡터 검색을 함께 사용하면 RU 패턴이 달라질 수 있습니다.
    - 모든 인덱스 유형에서 벡터 순위 지정 전에 필터를 적용합니다.

1. 다른 필터링 결과를 확인하려면 같은 쿼리에서 **technical** 범주를 선택해 봅니다.

### 결과 분석

테스트 결과를 바탕으로 인덱스 유형 선택 지침을 살펴봅니다.

| 시나리오 | 권장 인덱스 | 이유 |
|----------|------------|------|
| 소규모 데이터 세트(벡터 10K개 미만) | flat | 정확한 결과와 감당할 수 있는 RU 비용 |
| 중간 규모 데이터 세트, 메모리 제약 | quantizedFlat | 정확도를 유지하면서 메모리 사용량 감소 |
| 대규모 데이터 세트, 프로덕션 워크로드 | diskANN | 최고의 RU 효율성, 재현율 약 95% |

1. 터미널로 돌아가 **Ctrl+C**를 눌러 Flask 애플리케이션을 중지합니다.

## 요약

이 연습에서는 Azure Cosmos DB for NoSQL의 벡터 인덱싱 전략을 비교했습니다. **EnableNoSQLVectorSearch** 기능을 사용하는 Azure Cosmos DB 계정을 배포하고 Entra ID 인증을 구성했습니다. Python SDK를 사용하여 서로 다른 벡터 인덱스 유형인 정확 검색용 flat, 메모리 효율성을 위한 quantizedFlat, 프로덕션 규모의 근사 검색용 diskANN으로 컨테이너 세 개를 만들었습니다. RU 소비량과 실행 시간을 추적하면서 벡터 유사도 검색을 수행하는 Python 함수를 만들었습니다. Flask 웹 애플리케이션으로 비교 검색을 실행하고 성능 차이를 분석했습니다. 이 패턴을 사용하면 데이터 세트 크기, 정확도 요구 사항, 비용 제약을 기준으로 AI 애플리케이션에 적합한 인덱싱 전략을 선택할 수 있습니다.

## 리소스 정리

이제 연습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. 리소스 그룹과 그룹 내 모든 리소스를 삭제하려면 VS Code 터미널에서 다음 명령을 실행합니다. 앞서 선택한 이름으로 **\<rg-name>**을 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그 안에 포함된 모든 리소스가 삭제됩니다. 기존 리소스 그룹을 이 연습에 사용한 경우 이 연습 범위에 속하지 않는 기존 리소스도 삭제됩니다.

## 문제 해결

이 연습 중 문제가 발생하면 다음 단계를 시도합니다.

**Flask 앱이 시작되지 않음**
- Python 가상 환경이 활성화되어 있는지 확인합니다(터미널 프롬프트에 **(.venv)**가 표시되어야 함).
- 종속성이 설치되어 있는지 확인합니다(**pip install -r requirements.txt**).
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수가 로드되었는지 확인합니다.
- **python app.py**를 실행할 때 *client* 디렉터리에 있는지 확인합니다.

**인증 또는 액세스 거부 오류**
- 배포 스크립트의 **3**번 옵션을 실행하여 Entra ID 액세스를 구성했는지 확인합니다.
- 사용자에게 **Contributor** 역할과 **Cosmos DB Built-in Data Contributor** 역할이 모두 있는지 확인합니다.
- 터미널 세션에 **COSMOS_ENDPOINT**가 올바르게 설정되어 있는지 확인합니다.

**setup_containers.py 실행 실패**
- Python 가상 환경이 활성화되어 있는지 확인합니다.
- 환경 변수가 설정되어 있는지 확인합니다(**COSMOS_ENDPOINT**, **COSMOS_DATABASE**).
- 컨테이너가 이미 있으면 스크립트는 기존 컨테이너를 사용합니다.

**벡터 검색에서 오류 반환**
- 배포 스크립트의 **2**번 옵션을 실행하여 컨테이너가 만들어졌는지 확인합니다.
- 검색을 실행하기 전에 샘플 데이터를 로드했는지 확인합니다.
- 컨테이너에 벡터 임베딩 정책이 구성되어 있는지 확인합니다.

**Cosmos DB 작업 실패**
- 배포 스크립트의 **4**번 옵션을 실행하여 Cosmos DB 계정이 준비되었는지 확인합니다.
- 배포 중 데이터베이스가 만들어졌는지 확인합니다.
- 계정에 **EnableNoSQLVectorSearch** 기능이 있는지 확인합니다.

**환경 변수 문제**
- 배포 스크립트의 **5**번 옵션을 실행하여 *.env* 파일이 만들어졌는지 확인합니다.
- 새 터미널을 만든 후 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행합니다.
- **echo $COSMOS_ENDPOINT**(Bash) 또는 **$env:COSMOS_ENDPOINT**(PowerShell)을 실행하여 변수가 설정되었는지 확인합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 **source .venv/bin/activate**를 사용합니다.
- Windows PowerShell에서는 **.\.venv\Scripts\Activate.ps1**을 사용합니다.
- **activate** 스크립트가 없으면 **python3-venv** 패키지를 다시 설치하고 venv를 다시 만듭니다.
