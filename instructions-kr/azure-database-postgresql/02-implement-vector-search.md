---
lab:
  topic: Azure Database for PostgreSQL
  title: Azure Database for PostgreSQL에서 벡터 검색 구현
  description: Azure Database for PostgreSQL 및 pgvector 확장을 사용하여 벡터 유사도 검색을 구현하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Database for PostgreSQL
---

# Azure Database for PostgreSQL에서 벡터 검색 구현

이 실습에서는 Azure Database for PostgreSQL과 pgvector 확장을 사용하여 제품 유사도 검색 애플리케이션을 빌드합니다. 벡터 저장 기능을 사용하도록 설정하고, 임베딩을 포함하는 제품 데이터베이스 스키마를 만들고, Flask 웹 애플리케이션을 통해 샘플 데이터를 로드한 다음, 관련 제품을 찾기 위한 유사도 검색을 수행합니다. 이 패턴은 추천 시스템, 의미 체계 검색 기능 및 기타 AI 기반 애플리케이션을 빌드하기 위한 기반을 제공합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 배포 스크립트 구성
- Microsoft Entra 인증을 사용하는 Azure Database for PostgreSQL Flexible Server 배포
- 서버가 배포되는 동안 Flask 애플리케이션 코드 완성
- pgvector 확장을 사용하도록 설정하고 products 테이블 스키마 만들기
- Flask 애플리케이션을 실행하여 제품을 로드하고 유사도 검색 수행
- 새 제품을 추가하고 유사도 검색 결과가 어떻게 바뀌는지 확인

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
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/postgresql-vector-search-python.zip
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

이 섹션에서는 배포 스크립트를 실행하여 PostgreSQL 서버를 배포하고 인증을 구성합니다.

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트 메뉴가 나타나면 **1**을 입력하여 **Create PostgreSQL server with Entra authentication(Entra 인증으로 PostgreSQL 서버 만들기)** 옵션을 실행합니다. 이 옵션은 Entra 전용 인증이 사용하도록 설정된 서버를 만듭니다. **참고:** 배포를 완료하는 데 5~10분 정도 걸릴 수 있습니다.

    >**중요:** 실습이 끝날 때까지 배포를 실행하는 터미널을 열어 둡니다. 터미널에서 배포가 계속되는 동안 실습의 다음 섹션으로 이동할 수 있습니다.

## 클라이언트 애플리케이션 완성

이 섹션에서는 PostgreSQL 데이터베이스와 상호 작용하는 경로 처리기를 추가하여 *app.py* 파일을 완성합니다. 이 경로는 샘플 제품 로드, 유사도 검색 수행, 새 제품 추가를 처리합니다. Flask 애플리케이션은 벡터 유사도 검색을 테스트하기 위한 웹 인터페이스를 제공합니다.

1. VS Code에서 *client/app.py* 파일을 엽니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 동일한 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **BEGIN LOAD DATA SECTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 경로는 JSON 파일에서 제품을 로드하고 임베딩과 함께 데이터베이스에 삽입합니다.

    ```python
    @app.route("/load-data", methods=["POST"])
    def load_data():
        """Load sample products into the database."""
        try:
            products = load_json_file("sample_products.json")

            with get_connection() as conn:
                with conn.cursor() as cur:
                    for product in products:
                        # Check if product already exists
                        cur.execute("SELECT id FROM products WHERE name = %s", (product["name"],))
                        if cur.fetchone():
                            continue

                        # Format embedding as PostgreSQL array (pgvector expects bracket notation)
                        embedding_str = "[" + ",".join(str(x) for x in product["embedding"]) + "]"

                        cur.execute("""
                            INSERT INTO products (name, category, description, price, embedding)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            product["name"],
                            product["category"],
                            product["description"],
                            product["price"],
                            embedding_str
                        ))
                    # Commit all inserts in a single transaction
                    conn.commit()

            flash(f"Successfully loaded {len(products)} sample products!", "success")
        except Exception as e:
            flash(f"Error loading data: {str(e)}", "error")

        return redirect(url_for("index"))
    ```

1. **BEGIN SEARCH SECTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 경로는 선택한 제품의 세부 정보와 임베딩을 검색하고, 코사인 거리를 사용하여 유사한 제품을 찾은 다음, 선택한 제품과 결과를 템플릿에 전달하여 표시합니다.

    ```python
    @app.route("/search", methods=["POST"])
    def search():
        """Find products similar to the selected product using vector similarity."""
        product_id = request.form.get("product_id")

        if not product_id:
            flash("Please select a product", "error")
            return redirect(url_for("index"))

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Get the selected product details and embedding
                    cur.execute("""
                        SELECT id, name, category, description, price, embedding
                        FROM products WHERE id = %s
                    """, (product_id,))
                    row = cur.fetchone()

                    if not row:
                        flash("Product not found", "error")
                        return redirect(url_for("index"))

                    searched_product = {
                        "id": row[0], "name": row[1], "category": row[2],
                        "description": row[3], "price": row[4]
                    }
                    embedding = row[5]

                    # Find similar products using cosine distance
                    # The <=> operator is pgvector's cosine distance operator
                    # Lower distance = more similar (0 = identical, 2 = opposite)
                    cur.execute("""
                        SELECT id, name, category, description, price, embedding <=> %s AS distance
                        FROM products
                        WHERE id != %s
                        ORDER BY distance
                        LIMIT 5
                    """, (embedding, product_id))

                    results = [
                        {"id": r[0], "name": r[1], "category": r[2], "description": r[3], "price": r[4], "distance": r[5]}
                        for r in cur.fetchall()
                    ]

            products = get_products()
            new_products = get_new_products()
            return render_template("index.html", products=products, new_products=new_products, results=results, searched_product=searched_product)

        except Exception as e:
            flash(f"Error searching: {str(e)}", "error")
            return redirect(url_for("index"))
    ```

1. **BEGIN ADD PRODUCT SECTION** 주석을 검색하고 주석 바로 뒤에 다음 코드를 추가합니다. 이 경로는 *new_products.json* 파일의 제품을 데이터베이스에 추가합니다.

    ```python
    @app.route("/add-product", methods=["POST"])
    def add_product():
        """Add a new product from the new_products.json file."""
        product_index = request.form.get("product_index")

        if product_index is None or product_index == "":
            flash("Please select a product to add", "error")
            return redirect(url_for("index"))

        try:
            new_products = load_json_file("new_products.json")
            product = new_products[int(product_index)]

            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Check if product already exists
                    cur.execute("SELECT id FROM products WHERE name = %s", (product["name"],))
                    if cur.fetchone():
                        flash(f"Product '{product['name']}' already exists", "error")
                        return redirect(url_for("index"))

                    # Format embedding as PostgreSQL array
                    embedding_str = "[" + ",".join(str(x) for x in product["embedding"]) + "]"

                    cur.execute("""
                        INSERT INTO products (name, category, description, price, embedding)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        product["name"],
                        product["category"],
                        product["description"],
                        product["price"],
                        embedding_str
                    ))
                    conn.commit()

            flash(f"Successfully added '{product['name']}'!", "success")
        except Exception as e:
            flash(f"Error adding product: {str(e)}", "error")

        return redirect(url_for("index"))
    ```

1. *app.py* 파일의 변경 내용을 저장합니다.

1. 앱의 모든 코드를 검토하는 데 몇 분 정도 할애합니다. 각 경로가 **get_connection()** 함수를 사용하여 Microsoft Entra 인증으로 PostgreSQL에 연결하고, **<=>** 연산자가 유사도 검색을 위한 코사인 거리 계산을 수행하는 방식을 살펴봅니다.

## Azure 리소스 배포 완료 및 스키마 만들기

이 섹션에서는 pgvector 확장을 사용하도록 설정하고 임베딩을 저장할 벡터 열이 있는 products 테이블을 만듭니다. 스키마에는 제품 세부 정보 열과 유사도 검색에 사용하는 384차원 임베딩 벡터가 포함됩니다.

1. 터미널에 PostgreSQL 서버 배포가 완료되었다고 표시될 때까지 기다립니다.

1. 배포 스크립트 메뉴에서 **2**를 입력하여 **Configure vector extension allow-list(벡터 확장 허용 목록 구성)** 옵션을 실행합니다. 이 옵션은 서버의 **azure.extensions** 허용 목록에 **vector** 확장을 추가하므로 다음 섹션에서 pgvector를 사용하도록 설정할 수 있습니다. 변경 내용을 적용하기 위해 서버가 다시 시작됩니다. **참고:** 다시 시작하는 데 1~2분 정도 걸릴 수 있습니다.

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

1. **psql**을 사용하여 PostgreSQL 서버에 연결하려면 다음 명령을 실행합니다. 이 명령은 이전 단계에서 로드한 환경 변수를 사용합니다.

    **Bash**
    ```bash
    psql "host=$DB_HOST dbname=$DB_NAME user=$DB_USER sslmode=require"
    ```

    **PowerShell**
    ```powershell
    psql "host=$env:DB_HOST port=5432 dbname=$env:DB_NAME user=$env:DB_USER sslmode=require"
    ```

1. pgvector 확장을 사용하도록 설정합니다. 벡터 데이터 형식을 사용하려면 먼저 이 확장을 사용하도록 설정해야 합니다.

    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```

1. 임베딩을 위한 벡터 열이 있는 products 테이블을 만듭니다. 임베딩 열은 일반적인 문장 변환기 모델에 맞는 384차원을 사용합니다.

    ```sql
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        price NUMERIC(10, 2),
        embedding vector(330)
    );
    ```

1. 빠른 유사도 검색을 위해 HNSW 인덱스를 만듭니다. 이 인덱스 유형은 벡터 데이터에 대한 근사 최근접 이웃 쿼리에 최적화되어 있습니다.

    ```sql
    CREATE INDEX products_embedding_idx
    ON products USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    ```

1. 테이블 구조를 나열하여 테이블과 인덱스가 만들어졌는지 확인합니다.

    ```sql
    \d products
    ```

    id, name, category, description, price, embedding 열과 HNSW 인덱스가 있는 테이블 구조가 표시되어야 합니다.

1. **quit**를 입력하여 세션을 종료합니다.


## Flask 애플리케이션 설정 및 실행

이 섹션에서는 Python 종속성을 설치하고 Flask 웹 애플리케이션을 실행합니다. 애플리케이션은 제품 로드, 유사 제품 검색, 데이터베이스에 새 제품 추가를 위한 브라우저 인터페이스를 제공합니다.

1. 다음 명령을 실행하여 *client* 폴더로 이동합니다.

    ```
    cd client
    ```

1. Python 가상 환경을 만들려면 다음 명령을 실행합니다. 환경에 따라 **python** 또는 **python3** 명령을 사용할 수 있습니다.

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

1. 필요한 Python 패키지를 설치하려면 다음 명령을 실행합니다. *requirements.txt* 파일에는 웹 프레임워크용 **flask**, PostgreSQL 연결용 **psycopg**, 인증용 **azure-identity**가 포함됩니다.

    ```bash
    pip install -r requirements.txt
    ```

1. Flask 애플리케이션을 실행합니다. 애플리케이션은 포트 5000에서 시작되며 브라우저에서 액세스할 수 있습니다.

    ```bash
    python app.py
    ```

1. 웹 브라우저를 열고 `http://127.0.0.1:5000`으로 이동합니다. 제품 목록이 비어 있는 Vector Search Demo 페이지가 표시되어야 합니다.

## 제품 로드 및 유사도 검색 수행

이 섹션에서는 웹 애플리케이션을 사용하여 샘플 제품을 데이터베이스에 로드하고 유사도 검색을 수행합니다. 제품에는 각 제품의 의미를 나타내는 사전 계산 임베딩이 포함되어 있어 설명을 기반으로 유사한 항목을 찾을 수 있습니다.

1. 웹 페이지에서 **Load Sample Products(샘플 제품 로드)**를 선택합니다. 임베딩이 포함된 제품 10개가 데이터베이스에 삽입됩니다.

    성공 메시지가 표시되고 제품 목록에 "Wireless Bluetooth Headphones", "Gaming Laptop", "Running Shoes"와 같은 항목이 나타납니다.

1. **Find Similar Products(유사 제품 찾기)** 섹션에서 드롭다운의 **Wireless Bluetooth Headphones**를 선택하고 **Find Similar(유사 항목 찾기)**를 선택합니다.

    애플리케이션은 벡터 유사도를 사용하여 데이터베이스를 쿼리하고 선택한 항목과 의미상 가까운 순서로 제품을 반환합니다. 두 항목이 모두 오디오 장치이므로 결과 상단에 "Noise Cancelling Earbuds"가 표시되어야 합니다.

1. 다른 제품을 선택하여 선택한 항목의 범주와 설명에 따라 유사 제품이 어떻게 바뀌는지 확인합니다.

## 새 제품 추가 및 변경 사항 확인

이 섹션에서는 데이터베이스에 새 제품을 추가하고 유사도 검색 결과에 어떻게 나타나는지 확인합니다. 이를 통해 데이터가 변경될 때 벡터 검색이 어떻게 적응하는지 살펴봅니다.

1. Flask 애플리케이션이 열린 웹 브라우저로 돌아갑니다.

1. **Add New Product(새 제품 추가)** 섹션에서 드롭다운의 **Espresso Machine**을 선택하고 **Add Product(제품 추가)**를 선택합니다.

1. 이제 **Find Similar Products** 드롭다운에서 **Coffee Maker**를 선택하고 **Find Similar**를 선택하여 유사 제품을 검색합니다.

    두 제품이 가정용 커피 기기라는 점에서 의미상 관련이 있으므로, 이제 결과에 "Espresso Machine"이 낮은 거리 점수로 표시됩니다.

1. 드롭다운에서 나머지 제품(**Wireless Gaming Mouse** 및 **Fitness Tracker Band**)을 추가하고 관련 제품 검색 결과에 나타나는지 확인합니다.

## 요약

이 실습에서는 Azure Database for PostgreSQL과 pgvector 확장을 사용하여 제품 유사도 검색 애플리케이션을 빌드했습니다. Microsoft Entra 인증으로 PostgreSQL Flexible Server를 배포하고 pgvector 확장을 사용하도록 설정했으며, 임베딩을 저장할 384차원 벡터 열이 있는 products 테이블을 만들었습니다. 유사도 쿼리를 최적화하는 HNSW 인덱스를 추가한 다음 Flask 웹 애플리케이션을 사용하여 샘플 제품을 로드하고 코사인 거리 연산자(**<=>**)로 벡터 유사도 검색을 수행했습니다. 이 패턴은 정확히 일치하는 키워드가 아니라 의미를 기반으로 관련 항목을 찾는 추천 시스템과 의미 체계 검색 기능을 빌드하는 방법을 보여 줍니다.

## 리소스 정리

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

**Flask 애플리케이션 시작 실패**
- Python 가상 환경이 활성화되어 있는지 확인합니다(터미널 프롬프트에 **(.venv)**가 표시되어야 합니다).
- 종속성이 설치되었는지 확인합니다(**pip install -r requirements.txt**).
- 세 개의 경로 함수가 모두 *app.py*에 올바르게 추가되었는지 확인합니다.

**Flask의 데이터베이스 연결 오류**
- Flask를 실행하는 터미널에 환경 변수가 로드되었는지 확인합니다.
- **psql**로 연결하고 **\d products**를 실행하여 products 테이블이 있는지 확인합니다.
- pgvector 확장이 사용하도록 설정되었는지 확인합니다(**CREATE EXTENSION IF NOT EXISTS vector;**).

**로드 후 제품이 표시되지 않음**
- Flask 터미널에서 오류 메시지를 확인합니다.
- *sample_products.json* 파일이 *client* 폴더에 있는지 확인합니다.
- products 테이블이 올바른 스키마로 만들어졌는지 확인합니다.

**Python venv 활성화 문제**
- Linux/macOS에서는 **source .venv/bin/activate**를 사용합니다.
- Windows PowerShell에서는 **.\.venv\Scripts\Activate.ps1**을 사용합니다.
- Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.
