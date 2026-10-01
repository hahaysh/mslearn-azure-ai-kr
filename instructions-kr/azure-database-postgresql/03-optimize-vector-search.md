---
lab:
  topic: Azure Database for PostgreSQL
  title: Azure Database for PostgreSQL에서 벡터 검색 성능 최적화
  description: 인덱스와 매개 변수 튜닝을 사용하여 Azure Database for PostgreSQL의 벡터 검색 성능을 최적화하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Database for PostgreSQL
---

# Azure Database for PostgreSQL에서 벡터 검색 성능 최적화

이 실습에서는 Azure Database for PostgreSQL 인스턴스를 배포하고 벡터 검색 워크로드에 맞게 최적화합니다. 벡터 임베딩이 포함된 테스트 데이터를 만들고, 기준 성능을 분석하고, IVFFlat 및 HNSW 인덱스를 빌드하고 비교한 다음, 검색 매개 변수를 조정합니다. 이러한 기술은 대규모 데이터 세트에서 빠른 유사도 검색이 필요한 프로덕션 AI 애플리케이션에 필수적입니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트 구성
- Microsoft Entra 인증을 사용하는 Azure Database for PostgreSQL Flexible Server 배포
- 벡터 임베딩이 포함된 테스트 데이터 세트 만들기
- 인덱스 없이 기준 벡터 검색 성능 분석
- IVFFlat 및 HNSW 벡터 인덱스 만들기 및 비교
- 속도와 재현율 간 균형을 맞추도록 인덱스 매개 변수 조정

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에서 사용합니다.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Python 3.12](https://www.python.org/downloads/) 이상
- [PostgreSQL 명령줄 도구](https://www.postgresql.org/download/) (**psql**)

## 프로젝트 시작 파일 다운로드 및 Azure 서비스 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 스크립트를 사용하여 Azure 구독에 필요한 서비스를 배포합니다. PostgreSQL 서버를 배포하는 데 몇 분 정도 걸립니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-optimize-vector-search-python.zip
    ```

1. 파일을 프로젝트 작업에 사용할 시스템 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **File > Open Folder...**를 선택한 다음 프로젝트 파일이 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위에 있는 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 부분은 변경하지 마세요.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **Terminal(터미널) > New Terminal(새 터미널)**을 선택하여 VS Code에서 터미널 창을 엽니다.

    >**팁:** 이 실습은 전부 터미널에서 진행됩니다. 명령 결과를 쉽게 볼 수 있도록 패널을 최대화합니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 실습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 실습에 필요한 리소스 공급자가 있는지 확인합니다.

    ```azurecli
    az provider register --namespace Microsoft.DBforPostgreSQL
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 PostgreSQL 서버를 배포하고 인증을 구성합니다.

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Create PostgreSQL server with Entra authentication(Entra 인증으로 PostgreSQL 서버 만들기)** 옵션을 실행합니다. 이 옵션은 Entra 전용 인증이 사용하도록 설정된 서버를 만듭니다. **참고:** 배포를 완료하는 데 5~10분 정도 걸릴 수 있습니다.

    >**중요:** 실습이 끝날 때까지 배포를 실행하는 터미널을 열어 둡니다. 터미널에서 배포가 계속되는 동안 실습의 다음 섹션으로 이동할 수 있습니다.

## 벡터 인덱스 개념 검토

이 섹션에서는 실습의 뒷부분에서 적용할 벡터 인덱싱의 주요 개념을 검토합니다. 이러한 장단점을 이해하면 벡터 검색을 최적화할 때 적절한 결정을 내리는 데 도움이 됩니다.

### IVFFlat 인덱스

IVFFlat(Inverted File with Flat compression)은 벡터를 **lists**라는 클러스터로 나눕니다. 검색할 때 전체 데이터 세트 대신 인접 클러스터의 벡터만 검사합니다.

주요 매개 변수:

- **lists**: 만들 클러스터 수입니다. 최대 100만 행에서는 `rows / 1000`을 시작 값으로 사용할 수 있습니다. lists가 많을수록 검색은 빨라지지만 인덱스 빌드는 느려집니다.
- **probes**: 쿼리 시 검색할 클러스터 수입니다. 값이 높을수록 재현율(실제 최근접 이웃을 찾는 비율)이 향상되지만 대기 시간이 늘어납니다.

### HNSW 인덱스

HNSW(Hierarchical Navigable Small World)는 다중 계층 그래프 구조를 만듭니다. 상위 계층에는 빠른 탐색을 위한 노드가 적고, 하위 계층에는 정밀한 검색을 위한 노드가 더 많습니다.

주요 매개 변수:

- **m**: 노드당 최대 연결 수입니다. 값이 높을수록 재현율이 향상되지만 메모리 사용량과 빌드 시간이 늘어납니다. 기본값은 16입니다.
- **ef_construction**: 인덱스를 빌드하는 동안 사용하는 동적 후보 목록의 크기입니다. 값이 높을수록 품질이 좋은 그래프가 만들어지지만 빌드 시간이 늘어납니다. 기본값은 64입니다.
- **ef_search**: 검색 중 사용하는 동적 후보 목록의 크기입니다. 값이 높을수록 재현율이 향상되지만 대기 시간이 늘어납니다. 기본값은 40입니다.

### 각 인덱스를 사용하는 경우

| 고려 사항 | IVFFlat | HNSW |
|---------------|---------|------|
| 빌드 시간 | 빠름 | 느림 |
| 쿼리 속도 | 빠름 | 더 빠름 |
| 메모리 사용량 | 낮음 | 높음 |
| 재현율 정확도 | 튜닝하면 양호 | 기본 상태에서도 더 우수 |
| 업데이트 성능 | 다시 빌드해야 함 | 점진적 업데이트 지원 |

이 실습에서는 두 인덱스 유형을 모두 테스트하고 장단점을 직접 측정합니다.

## Azure 리소스 배포 완료

이 섹션에서는 배포 스크립트로 돌아가 PostgreSQL 서버의 연결 정보를 가져옵니다.

1. **Create PostgreSQL server with Entra authentication** 작업이 완료되면 **2**를 입력하여 **Configure vector extension allow-list(벡터 확장 허용 목록 구성)** 옵션을 실행합니다. 이 옵션은 서버의 **azure.extensions** 허용 목록에 **vector** 확장을 추가하므로 다음 섹션에서 pgvector를 사용하도록 설정할 수 있습니다. 변경 내용을 적용하기 위해 서버가 다시 시작됩니다. **참고:** 다시 시작하는 데 1~2분 정도 걸릴 수 있습니다.

1. **3**을 입력하여 **Check deployment status(배포 상태 확인)** 옵션을 실행합니다. 이 옵션은 서버가 준비되었는지 확인합니다.

1. **4**를 입력하여 **Retrieve connection info and access token(연결 정보 및 액세스 토큰 검색)** 옵션을 실행합니다. 이 옵션은 필요한 환경 변수가 포함된 파일을 만듭니다.

1. **5**를 입력하여 배포 스크립트를 종료합니다.

1. 다음 명령을 실행하여 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 로드하는 명령을 실행해야 할 수 있습니다.

    >**참고:** 액세스 토큰은 약 1시간 후 만료됩니다. 나중에 다시 연결해야 하는 경우 스크립트를 다시 실행하고 옵션 **4**를 선택하여 새 토큰을 만든 다음 변수를 다시 내보냅니다.

## 데이터베이스 스키마 및 테스트 데이터 만들기

이 섹션에서는 PostgreSQL 서버에 연결하고 테스트용 제품 데이터와 벡터 임베딩이 포함된 테이블을 만듭니다.

1. 환경 변수를 사용하여 서버에 연결하려면 다음 명령을 실행합니다. 인증에는 **PGPASSWORD** 환경 변수가 자동으로 사용됩니다.

    **Bash**
    ```bash
    psql "host=$DB_HOST port=5432 dbname=$DB_NAME user=$DB_USER sslmode=require"
    ```

    **PowerShell**
    ```powershell
    psql "host=$env:DB_HOST port=5432 dbname=$env:DB_NAME user=$env:DB_USER sslmode=require"
    ```

    >**팁:** 쿼리 결과가 현재 터미널 창에 모두 표시되지 않으면 psql은 페이저를 사용합니다. 페이저가 표시되면 **q**를 눌러 페이저를 닫고 psql 프롬프트로 돌아갑니다. 터미널 창을 최대화하면 페이저가 나타나는 상황을 줄이고 명령 결과를 더 쉽게 검토할 수 있습니다.

1. pgvector 확장을 사용하도록 설정하려면 다음 명령을 실행합니다. PostgreSQL 확장은 사용하기 전에 명시적으로 사용하도록 설정해야 합니다. pgvector 확장은 이 실습에서 사용하는 **vector** 데이터 형식과 **<=>**(코사인 거리) 같은 연산자를 추가합니다. Azure Database for PostgreSQL에는 pgvector가 포함되어 있지만 기본적으로 사용하도록 설정되지는 않습니다.

    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

1. 벡터 열이 포함된 products 테이블을 만들려면 다음 명령을 실행합니다. **vector(384)** 데이터 형식은 문장 임베딩 모델에서 일반적으로 사용하는 384차원 임베딩을 저장합니다.

    ```sql
    CREATE TABLE products (
        id BIGSERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        price NUMERIC(10,2) NOT NULL,
        in_stock BOOLEAN DEFAULT true,
        embedding vector(384)
    );
    ```

1. 임의 임베딩으로 테스트 데이터를 생성하려면 다음 명령을 실행합니다. 이 명령은 임의의 384차원 벡터가 포함된 제품 100,000개를 만듭니다.

    ```sql
    INSERT INTO products (name, category_id, price, in_stock, embedding)
    SELECT
        'Product ' || i,
        (random() * 20)::int + 1,
        (random() * 1000)::numeric(10,2),
        random() > 0.1,
        ('[' || array_to_string(ARRAY(
            SELECT (random() * 2 - 1)::float4
            FROM generate_series(1, 384)
        ), ',') || ']')::vector
    FROM generate_series(1, 100000) AS i;
    ```

1. 데이터가 만들어졌는지 확인하려면 다음 명령을 실행합니다. 100,000개 행이 표시되어야 합니다.

    ```sql
    SELECT COUNT(*) FROM products;
    ```

1. 일관된 테스트를 위한 쿼리 벡터를 만들려면 다음 명령을 실행합니다. 이 임시 테이블에는 실습 전체에서 사용하는 임의 임베딩이 저장됩니다.

    ```sql
    CREATE TEMP TABLE query_vectors AS
    SELECT ('[' || array_to_string(ARRAY(
        SELECT (random() * 2 - 1)::float4
        FROM generate_series(1, 384)
    ), ',') || ']')::vector AS embedding;
    ```

## 기준 성능 분석

이 섹션에서는 인덱스가 없는 벡터 검색 성능을 측정하여 기준을 설정합니다.

1. 벡터 유사도 쿼리를 실행하고 실행 계획을 캡처하려면 다음 명령을 실행합니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. 출력을 살펴봅니다. 계획에 **Seq Scan**이 표시되어 PostgreSQL이 100,000개 행을 모두 검사함을 알 수 있습니다. 맨 아래의 **Execution Time** 값을 기록합니다.

1. 일관된 측정값을 얻으려면 쿼리를 두 번 더 실행합니다. 첫 실행은 캐시가 비어 있어 더 느릴 수 있습니다. 마지막 실행 시간을 기준값으로 기록합니다.

## IVFFlat 및 HNSW 인덱스 만들기 및 비교

이 섹션에서는 두 인덱스 유형을 만들고 성능을 비교합니다.

### IVFFlat 인덱스 만들기

1. IVFFlat 인덱스를 만들려면 다음 명령을 실행합니다. 100,000개 행에서는 100 lists가 적절한 시작 값입니다(`rows / 1000` 지침 사용). 인덱스 빌드에 걸린 시간을 기록합니다.

    ```sql
    CREATE INDEX idx_products_embedding_ivfflat
    ON products USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    ```

1. IVFFlat 인덱스를 사용하여 동일한 쿼리를 실행하려면 다음 명령을 실행합니다. 계획에 **Index Scan using idx_products_embedding_ivfflat**가 표시되는지 확인합니다. 실행 시간을 기록합니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. probes 값을 낮게 설정하여 테스트하려면 다음 명령을 실행합니다. 클러스터 하나만 검색하므로 전체 검색보다 빠르지만 실제 최근접 이웃을 놓칠 수 있습니다. 재현율에 미치는 영향은 시간 출력으로 확인할 수 없으며 실제 결과를 비교해야 측정할 수 있습니다.

    ```sql
    SET ivfflat.probes = 1;
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. probes 값을 높여 테스트하려면 다음 명령을 실행합니다(더 느리지만 재현율은 높음). 실행 시간을 기록합니다.

    ```sql
    SET ivfflat.probes = 50;
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

### HNSW 인덱스 만들기

1. HNSW를 독립적으로 테스트할 수 있도록 IVFFlat 인덱스를 삭제하려면 다음 명령을 실행합니다.

    ```sql
    DROP INDEX idx_products_embedding_ivfflat;
    ```

1. 인덱스 빌드에 사용할 메모리를 늘리려면 다음 명령을 실행합니다. HNSW 인덱스는 IVFFlat보다 빌드 중 더 많은 메모리가 필요합니다.

    ```sql
    SET maintenance_work_mem = '256MB';
    ```

1. HNSW 인덱스를 만들려면 다음 명령을 실행합니다. 일반적으로 IVFFlat보다 빌드 시간이 더 오래 걸립니다.

    ```sql
    CREATE INDEX idx_products_embedding_hnsw
    ON products USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    ```

1. HNSW 인덱스로 쿼리를 실행하려면 다음 명령을 실행합니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. ef_search 값을 낮게 설정하여 테스트하려면 다음 명령을 실행합니다. 검색 경로 후보를 더 적게 탐색하므로 빠르지만 실제 최근접 이웃 일부를 놓칠 수 있습니다. 재현율에 미치는 영향은 시간 출력으로 확인할 수 없습니다.

    ```sql
    SET hnsw.ef_search = 20;
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. ef_search 값을 높여 테스트하려면 다음 명령을 실행합니다(재현율이 더 높음). 실행 시간을 기록합니다.

    ```sql
    SET hnsw.ef_search = 100;
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

### 결과 비교

서로 다른 구성의 실행 시간을 비교합니다. 다음과 같은 결과를 확인할 수 있습니다.

- **Sequential scan**은 100,000개 행을 모두 검사하므로 가장 느립니다.
- **probes=1인 IVFFlat**은 인덱스 사용 옵션 중 가장 빠르지만 실제 최근접 이웃 일부를 놓칠 수 있습니다.
- 비슷한 재현율 수준에서는 일반적으로 **HNSW**가 IVFFlat보다 쿼리가 빠릅니다.
- **probes**(IVFFlat) 또는 **ef_search**(HNSW)를 늘리면 정확도가 향상되지만 대기 시간도 늘어납니다.

## 인덱스를 사용하여 메타데이터 필터링 구현

이 섹션에서는 벡터 유사도와 메타데이터 필터를 결합하는 쿼리를 테스트합니다. 프로덕션 애플리케이션에서는 벡터 검색만 수행하는 경우가 드뭅니다. 일반적으로 유사 항목을 찾기 전에 범주, 날짜 범위, 가격 또는 기타 특성으로 필터링합니다. 이러한 결합 쿼리를 최적화하려면 PostgreSQL이 여러 인덱스 유형을 함께 사용하는 방식을 이해해야 합니다.

1. 범주 열에 B-tree 인덱스를 만들려면 다음 명령을 실행합니다.

    ```sql
    CREATE INDEX idx_products_category ON products (category_id);
    ```

1. 필터링된 벡터 검색을 실행하려면 다음 명령을 실행합니다. 실행 계획을 살펴보면 PostgreSQL이 벡터 유사도에 HNSW 인덱스를 사용한 다음 범주 필터를 적용하는 것을 확인할 수 있습니다. 실행 시간을 기록합니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    WHERE category_id = 5
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. 더 선택적인 필터로 테스트하려면 다음 명령을 실행합니다. 여러 필터 조건을 사용하면 B-tree 인덱스에 대한 **Bitmap Index Scan**과 후속 필터링이 표시될 수 있으며, 쿼리 플래너가 다른 전략을 선택할 수도 있습니다. 이전 쿼리와 실행 시간을 비교합니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    WHERE category_id = 5 AND price BETWEEN 100 AND 200
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

1. 필터 조합을 위한 복합 인덱스를 만들려면 다음 명령을 실행합니다.

    ```sql
    CREATE INDEX idx_products_category_price ON products (category_id, price);
    ```

1. 이전 쿼리를 다시 실행하고 실행 계획을 비교합니다. 복합 인덱스를 사용하면 PostgreSQL이 벡터 검색 전이나 검색과 함께 더 효율적으로 필터링하여 실행 시간을 줄일 수 있습니다.

    ```sql
    EXPLAIN ANALYZE
    SELECT id, name, embedding <=> (SELECT embedding FROM query_vectors) AS distance
    FROM products
    WHERE category_id = 5 AND price BETWEEN 100 AND 200
    ORDER BY embedding <=> (SELECT embedding FROM query_vectors)
    LIMIT 10;
    ```

## 요약

이 실습에서는 다음 작업을 수행했습니다.

- Microsoft Entra 인증을 사용하는 Azure Database for PostgreSQL Flexible Server 배포
- 벡터 임베딩 100,000개가 포함된 테스트 데이터 세트 만들기
- 인덱스가 없는 벡터 쿼리의 기준 성능 설정
- IVFFlat 및 HNSW 인덱스 만들기 및 비교
- 정확도와 속도의 균형을 맞추도록 인덱스 매개 변수(**probes** 및 **ef_search**) 조정
- B-tree 인덱스를 사용하여 메타데이터 필터링 구현

이러한 기술을 사용하면 프로덕션 벡터 검색 워크로드에 맞게 Azure Database for PostgreSQL을 최적화할 수 있습니다.

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
- 옵션 **1**이 완료된 후 옵션 **2**를 선택하여 서버의 **azure.extensions** 허용 목록에 **vector** 확장을 추가합니다.
- Azure에서 PostgreSQL 서버 이름을 5분 이내에 해제하지 않으면 배포 스크립트를 종료하고 5분 동안 기다린 다음 스크립트를 다시 실행하여 옵션 **1**을 선택합니다.

**psql 연결 실패**
- 배포 스크립트 옵션 **4**를 실행하여 *.env* 및 *.env.ps1* 파일이 모두 만들어졌는지 확인합니다.
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수를 로드했는지 확인합니다.
- 액세스 토큰은 약 1시간 후 만료됩니다. 새 토큰을 만들려면 배포 스크립트 옵션 **4**를 다시 실행합니다.
- 배포 스크립트 옵션 **3**을 실행하여 서버가 준비되었는지 확인합니다.

**액세스 거부 또는 인증 오류**
- 옵션 **1**에서 서버를 만들 때 Microsoft Entra 관리자가 자동으로 구성됩니다. 액세스가 계속 거부되면 옵션 **3**을 실행하여 관리자를 확인합니다. 관리자가 없으면 옵션 **1**을 실행하고 서버 삭제 및 재배포를 확인합니다.
- 터미널 세션에서 **PGPASSWORD**가 올바르게 설정되었는지 확인합니다.
- 올바른 **DB_USER** 값(Azure 계정 이메일)을 사용하고 있는지 확인합니다.

**인덱스 빌드가 너무 오래 걸리거나 실패함**
- HNSW 인덱스는 IVFFlat보다 빌드 시간이 오래 걸립니다. 벡터 100,000개를 기준으로 1~2분 정도 기다립니다.
- 빌드 시간이 초과되면 Azure Monitor에서 CPU 및 메모리 메트릭을 확인합니다.
- 테스트용 데이터 세트의 크기를 줄이는 방법을 고려합니다.
