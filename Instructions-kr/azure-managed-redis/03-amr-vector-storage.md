---
lab:
  topic: Azure Managed Redis
  title: Azure Managed Redis에서 의미 체계 검색 구현
  description: redis-py와 RediSearch를 사용하여 Azure Managed Redis에 임베딩이 포함된 제품 벡터를 저장하고 의미 체계 검색 인덱스를 만들며 유사도 검색을 수행하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Managed Redis
---

# Azure Managed Redis에서 의미 체계 검색 구현

이 실습에서는 Azure Managed Redis를 배포하고 제품 임베딩과 메타데이터를 저장하고 벡터 인덱스를 만들며 코사인 거리를 사용하여 유사도 검색을 수행하는 Python Flask 웹 앱을 완성합니다. Microsoft Entra ID로 연결하고, 인덱스를 만들고, 제품 벡터를 저장하고, 브라우저 기반 인터페이스에서 유사 제품을 쿼리하는 코드를 추가합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Managed Redis 리소스 만들기
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 제품을 로드하고 벡터를 저장한 다음 유사도 검색 수행

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

이 섹션에서는 실습에 필요한 사전 요구 사항을 검토합니다.

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
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/amr-vector-query-python.zip
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

이 섹션에서는 *client/vector_functions.py* 파일에 코드를 추가하여 벡터 저장 및 검색 작업을 완성합니다. *client/app.py*의 Flask 앱은 브라우저에서 이 함수를 호출하여 워크플로를 실행합니다. *client/app.py*는 편집할 필요가 없습니다. 실습 후반에 앱을 실행합니다.

1. 코드 추가를 시작하려면 *client/vector_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 들여쓰기가 일치해야 합니다.

### Azure Managed Redis 연결 코드 추가

이 섹션에서는 Microsoft Entra ID로 인증하는 Redis 클라이언트를 만드는 코드를 추가합니다. Entra ID를 사용하면 앱이 액세스 키를 처리하지 않아도 됩니다.

**get_client()** 함수는 **REDIS_HOST** 환경 변수에서 Redis 엔드포인트를 읽고 **create_from_default_azure_credential()**을 호출하여 자격 증명 공급자를 빌드합니다. 이 공급자는 **DefaultAzureCredential**을 사용하여 Microsoft Entra 토큰을 가져오고 백그라운드에서 자동으로 새로 고칩니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 같은 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN CONNECTION CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def get_client() -> redis.Redis:
        """Create a Redis client for Azure Managed Redis using Microsoft Entra ID."""
        redis_host = os.environ.get("REDIS_HOST")

        if not redis_host:
            raise ValueError("REDIS_HOST environment variable must be set")

        credential_provider = create_from_default_azure_credential(
            ("https://redis.azure.com/.default",),
        )

        return redis.Redis(
            host=redis_host,
            port=10000,
            ssl=True,
            decode_responses=False,
            credential_provider=credential_provider,
            socket_timeout=30,
            socket_connect_timeout=30,
        )
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 벡터 인덱스 생성 코드 추가

이 섹션에서는 유사도 검색에 사용할 RediSearch 인덱스를 만드는 코드를 추가합니다.

**_create_vector_index()** 함수는 텍스트 필드와 **embedding**이라는 벡터 필드를 정의합니다. 벡터 필드는 HNSW 알고리즘과 코사인 거리를 사용하며, 샘플 데이터와 일치하도록 임베딩 차원을 8로 설정합니다.

1. **# BEGIN CREATE VECTOR INDEX CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def _create_vector_index(self):
        """Create a RediSearch index for product semantic search."""
        try:
            schema = (
                TextField("name"),
                TextField("category"),
                TextField("product_id"),
                VectorField(
                    "embedding",
                    "HNSW",
                    {
                        "TYPE": "FLOAT32",
                        "DIM": VECTOR_DIM,
                        "DISTANCE_METRIC": "COSINE",
                    },
                ),
            )

            definition = IndexDefinition(
                prefix=["product:"],
                index_type=IndexType.HASH,
            )

            self.r.ft(VECTOR_INDEX_NAME).create_index(
                fields=schema,
                definition=definition,
            )
        except redis.ResponseError as e:
            if "already exists" not in str(e):
                raise Exception(f"Error creating vector index: {e}")
        except Exception as e:
            raise Exception(f"Error creating vector index: {e}")
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 제품 벡터 저장 코드 추가

이 섹션에서는 제품 임베딩과 메타데이터를 Redis에 저장하는 코드를 추가합니다.

**store_product()** 함수는 numpy를 사용하여 임베딩 목록을 **float32** 바이트로 변환하고, **hset()**을 사용하여 임베딩과 메타데이터를 Redis 해시에 씁니다.

1. **# BEGIN STORE PRODUCT CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def store_product(
        self,
        vector_key: str,
        vector: list[float],
        metadata: dict[str, str] | None = None,
    ) -> tuple[bool, str]:
        """Store or update a product hash containing embedding and metadata."""
        try:
            embedding = np.array(vector, dtype=np.float32)
            data: dict[str, Any] = {"embedding": embedding.tobytes()}

            if metadata:
                for key, value in metadata.items():
                    data[key] = str(value)

            result = self.r.hset(vector_key, mapping=data)
            if result > 0:
                return True, f"Product stored successfully under key '{vector_key}'"
            return True, f"Product updated successfully under key '{vector_key}'"
        except Exception as e:
            return False, f"Error storing product: {e}"
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

### 유사 제품 검색 코드 추가

이 섹션에서는 벡터 인덱스에 대해 KNN 유사도 검색을 실행하는 코드를 추가합니다.

**search_similar_products()** 함수는 쿼리 임베딩을 바이트로 변환하고 RediSearch KNN 쿼리를 구성한 다음 점수순으로 정렬된 가장 가까운 제품 일치 항목을 반환합니다.

1. **# BEGIN SEARCH SIMILAR PRODUCTS CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def search_similar_products(
        self,
        query_vector: list[float],
        top_k: int = 3,
    ) -> tuple[bool, list[dict[str, Any]] | str]:
        """Run a KNN vector query against product embeddings."""
        try:
            query_bytes = np.array(query_vector, dtype=np.float32).tobytes()

            knn_query = (
                Query(f"*=>[KNN {top_k} @embedding $query_vec AS score]")
                .return_fields("name", "category", "product_id", "score")
                .sort_by("score")
                .dialect(2)
            )

            results = self.r.ft(VECTOR_INDEX_NAME).search(
                knn_query,
                query_params={"query_vec": query_bytes},
            )

            if results.total == 0:
                return False, "No products found in Redis. Load sample products first."

            similarities: list[dict[str, Any]] = []
            for doc in results.docs:
                similarities.append(
                    {
                        "key": doc.id,
                        "similarity": float(doc.score),
                        "product_id": doc.product_id.decode() if isinstance(doc.product_id, bytes) else doc.product_id,
                        "name": doc.name.decode() if isinstance(doc.name, bytes) else doc.name,
                        "category": doc.category.decode() if isinstance(doc.category, bytes) else doc.category,
                    }
                )

            return True, similarities
        except Exception as e:
            return False, f"Error searching products: {e}"
    ```

1. 변경 내용을 저장하고 잠시 시간을 내어 코드를 검토합니다.

## 리소스 배포 확인

이 섹션에서는 실행 중인 배포 스크립트로 돌아가 벡터 데이터베이스를 만들고, Microsoft Entra ID 액세스를 구성하고, Redis 엔드포인트가 포함된 환경 변수 파일을 생성합니다.

1. 배포 스크립트가 실행 중인 터미널로 돌아갑니다. Azure Managed Redis 리소스가 성공적으로 만들어졌다는 스크립트 메시지가 표시되면 **Enter**를 눌러 배포 메뉴로 돌아갑니다.

1. **2**를 입력하여 **2. Create database and configure access** 옵션을 실행합니다. 이 옵션은 RediSearch 모듈이 포함된 벡터 지원 데이터베이스를 만들고, 계정에 데이터 액세스 정책을 할당하고, **REDIS_HOST**가 포함된 *.env* 및 *.env.ps1* 파일을 만듭니다.

1. 최종 확인으로 **3**을 입력하여 **3. Check deployment status** 옵션을 실행합니다.

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

이 섹션에서는 클라이언트 디렉터리로 이동하고 Python 환경을 만든 다음 종속성을 설치합니다.

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

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 단일 웹 페이지에서 벡터를 저장하고 유사도 검색을 수행합니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 이 실습 앞부분의 명령을 참조하여 환경을 활성화하고 환경 변수를 불러옵니다. *client* 디렉터리에서 다른 위치로 이동했다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

### 샘플 데이터 로드 및 유사도 검색 수행

이 섹션에서는 샘플 제품 임베딩을 로드하고 첫 번째 유사도 검색을 수행합니다.

1. **데이터 작업(Data Operations)**에서 **샘플 제품 로드(Load Sample Products)**를 선택합니다.

1. **모든 제품 나열(List All Products)**을 선택하고 **작업 결과(Operation Results)**에 제품 키가 표시되는지 확인합니다.

1. **유사도 검색(Similarity Search)**에서 **product:001**을 입력하고 **top_k**를 **5**로 둔 다음 **유사 항목 찾기(Find Similar)**를 선택합니다.

1. **작업 결과(Operation Results)**에서 반환된 제품과 거리 점수를 검토합니다.

### 새 제품 저장 후 다시 검색

이 섹션에서는 새 제품 임베딩을 저장하고 유사도 검색을 다시 수행하여 최근접 이웃이 어떻게 바뀌는지 확인합니다.

1. **제품 저장(Store Product)**에 다음 값을 입력하고 **제품 저장(Store Product)**을 선택합니다.

    제품 키:

    ```
    product:011
    ```

    임베딩:

    ```
    [0.53, 0.63, 0.58, 0.37, 0.68, 0.47, 0.73, 0.57]
    ```

    메타데이터:

    ```
    product_id=011
    name=Gym Bag
    category=Sports
    ```

1. **유사도 검색(Similarity Search)**에서 **product:009**를 입력하고 **유사 항목 찾기(Find Similar)**를 선택합니다.

1. 결과를 검토하고 새로 저장한 벡터가 제품 유사도 순서에 반영되었는지 확인합니다.

### 제품 제거

이 섹션에서는 제품 키를 삭제하여 삭제 동작을 확인합니다.

1. **제품 제거(Remove Product)**에서 **product:011**을 입력하고 **제거(Remove)**를 선택합니다.

1. **모든 제품 나열(List All Products)**을 선택하고 제품 목록에 **product:011**이 더 이상 표시되지 않는지 확인합니다.

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
- 앱을 실행하기 전에 배포 스크립트의 **Check deployment status** 옵션을 실행하고 클러스터와 데이터베이스가 준비되었는지 확인합니다.

**배포 실패 해결**
- 배포가 실패하는 가장 일반적인 원인은 선택한 지역에서 해당 SKU의 용량을 일시적으로 사용할 수 없는 것입니다.
- 화면의 안내에 따라 스크립트를 종료하고, 스크립트 맨 위의 **location** 변수를 eastus2, australiaeast 또는 canadacentral과 같은 다른 지역으로 변경한 다음 스크립트를 다시 실행하고 옵션 1을 선택합니다.
- 다음 시도 전에 실패한 리소스가 자동으로 삭제됩니다.

**인증 및 액세스 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- 배포 스크립트의 **Create database and configure access** 옵션이 성공적으로 완료되어 계정에 데이터베이스 데이터 액세스 정책이 있는지 확인합니다.
- 앱에서 인증 오류가 보고되면 액세스 정책 할당이 적용되는 데 잠시 걸릴 수 있으므로 잠시 기다렸다가 다시 시도합니다.

**코드 완성도 및 들여쓰기 확인**
- *client/vector_functions.py*의 적절한 BEGIN/END 주석 사이에 모든 코드 블록을 올바른 섹션에 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 및 *.env.ps1* 파일이 모두 있고 **REDIS_HOST** 값이 포함되어 있는지 확인합니다.
- Bash에서는 **source .env**를, PowerShell에서는 **. .\.env.ps1**를 실행하여 터미널 세션에 환경 변수를 불러옵니다.

**검색 결과가 없거나 제품이 누락됨**
- 유사도 검색을 실행하기 전에 샘플 제품을 로드했는지 확인합니다.
- **모든 제품 나열(List All Products)**을 선택하여 쿼리 제품 키가 있는지 확인합니다.
- 임베딩에 인덱스 구성과 일치하는 숫자 8개가 포함되어 있는지 확인합니다.
