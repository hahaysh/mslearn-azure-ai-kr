---
lab:
  topic: 앱 비밀 및 구성
  title: Azure Key Vault를 사용하여 비밀 관리
  description: Azure Key Vault와 Python SDK를 사용하여 비밀을 저장하고 검색하며, 버전을 관리하고 캐시하는 방법을 알아봅니다.
  level: 300
  duration: 20
  islab: true
  primarytopics:
    - Azure
    - Azure Key Vault
---

# Azure Key Vault를 사용하여 비밀 관리

AI 애플리케이션은 일반적으로 모델 엔드포인트와 데이터 저장소에 액세스하기 위해 API 키, 연결 문자열, 인증서와 같은 중요한 자격 증명을 사용합니다. Azure Key Vault는 RBAC 액세스 제어, 자동 버전 관리, 감사 로깅을 제공하는 중앙 집중식 보안 저장소이므로 애플리케이션의 코드나 구성 파일에 자격 증명을 포함하지 않아도 됩니다.

이 연습에서는 샘플 비밀이 미리 저장된 Azure Key Vault를 배포하고, Azure SDK를 사용해 핵심 비밀 관리 패턴을 보여 주는 Python Flask 웹 애플리케이션을 빌드합니다. 비밀을 검색하고 메타데이터를 확인하며, 값을 노출하지 않고 모든 비밀 속성을 나열하고, 자격 증명 회전을 시뮬레이션하기 위해 새 비밀 버전을 만들고, Key Vault API 호출을 줄이는 시간 기반 캐시를 구현합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Key Vault를 만들고 샘플 비밀 저장
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 비밀 작업 수행

이 연습을 완료하는 데 약 **20**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 수 있는 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/).
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
- **선택 사항:** Python 코드의 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

## 프로젝트 시작 파일 다운로드 및 Azure Key Vault 배포

이 섹션에서는 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 샘플 비밀이 포함된 Azure Key Vault를 구독에 배포합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/key-vault-python.zip
    ```

1. 파일을 복사하거나 이동하여 프로젝트 작업에 사용할 위치에 둡니다. 그런 다음 파일을 폴더에 압축 해제합니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 포함된 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 Azure 계정에 로그인합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 구독에 연습에 필요한 리소스 공급자가 등록되어 있는지 확인합니다.

    ```
    az provider register --namespace Microsoft.KeyVault
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Key Vault** 옵션을 실행합니다. 이 옵션은 리소스 그룹이 없으면 만들고, RBAC 권한 부여가 활성화된 Azure Key Vault를 배포합니다.

    RBAC 권한 부여는 기존 액세스 정책 대신 자격 증명 모음 비밀에 대한 액세스를 제어하는 데 권장되는 모델입니다.

1. **2**를 입력하여 **2. Assign role** 옵션을 실행합니다. 이 옵션은 Microsoft Entra 인증을 사용하여 비밀을 읽고 만들고 업데이트하고 삭제할 수 있도록 Key Vault Secrets Officer 역할을 사용자 계정에 할당합니다.

1. **3**을 입력하여 **3. Store secrets** 옵션을 실행합니다. 이 옵션은 자격 증명 모음에 샘플 비밀 두 개를 저장합니다. 하나는 모델 엔드포인트의 API 키(**openai-api-key**)이고 다른 하나는 데이터베이스 연결 문자열(**cosmosdb-connection-string**)입니다. 두 비밀에는 환경과 서비스를 식별하는 메타데이터 태그가 지정됩니다.

1. **4**를 입력하여 **4. Check deployment status** 옵션을 실행합니다. 계속하기 전에 자격 증명 모음 상태가 **Succeeded**이고, 역할이 할당되었으며, 비밀이 저장되었는지 확인합니다. 자격 증명 모음이 아직 프로비전 중이면 잠시 기다렸다가 다시 확인합니다.

1. **5**를 입력하여 **5. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 앱에 필요한 Key Vault URL이 포함된 환경 변수 파일을 만듭니다.

1. **6**을 입력하여 배포 스크립트를 종료합니다.

1. 이전 단계에서 만든 파일의 환경 변수를 터미널 세션에 로드하는 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 열면 환경 변수를 다시 로드하기 위해 이 명령을 다시 실행해야 합니다.

## 앱 완성

이 섹션에서는 *keyvault_functions.py* 파일에 코드를 추가하여 Key Vault 비밀 관리 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수를 호출하고 결과를 브라우저에 표시합니다. 연습 후반부에 앱을 실행합니다.

1. 코드를 추가하려면 *client/keyvault_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 같은 위치에 맞춰야 합니다.

### 비밀을 검색하는 코드 추가

이 섹션에서는 자격 증명 모음에서 비밀 두 개를 검색하고 해당 메타데이터를 반환하는 코드를 추가합니다. 이 함수는 비밀 값, 버전 식별자, 콘텐츠 형식, 생성 날짜 및 사용자 지정 태그에 액세스하는 방법을 보여 줍니다.

이 함수는 각 비밀 이름에 대해 **get_secret()**을 호출합니다. 이 메서드는 비밀 값과 메타데이터가 포함된 속성 개체를 모두 반환합니다. 비밀이 없을 때는 **ResourceNotFoundError**를, 권한 부여 또는 네트워크 문제가 있을 때는 **HttpResponseError**를 처리합니다. 값을 일부만 표시하여 비밀 검색 여부는 확인하면서 전체 자격 증명은 UI에 노출하지 않습니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 동일한 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 어긋난 경우 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 눌러 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN RETRIEVE SECRETS FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def retrieve_secrets():
        """Retrieve secrets and display their metadata."""
        client = get_client()
        results = []

        secret_names = ["openai-api-key", "cosmosdb-connection-string"]

        for name in secret_names:
            try:
                # get_secret returns the secret value and its properties,
                # including version, content type, creation date, and tags
                secret = client.get_secret(name)
                results.append({
                    "name": secret.name,
                    "value": secret.value[:20] + "..." if len(secret.value) > 20 else secret.value,
                    "version": secret.properties.version,
                    "content_type": secret.properties.content_type,
                    "created_on": str(secret.properties.created_on),
                    "tags": secret.properties.tags or {},
                    "status": "retrieved"
                })
            except ResourceNotFoundError:
                results.append({
                    "name": name,
                    "value": None,
                    "version": None,
                    "content_type": None,
                    "created_on": None,
                    "tags": {},
                    "status": "not found"
                })
            except HttpResponseError as e:
                results.append({
                    "name": name,
                    "value": None,
                    "version": None,
                    "content_type": None,
                    "created_on": None,
                    "tags": {},
                    "status": f"error: {e.message}"
                })

        return results
    ```

1. 몇 분 동안 코드를 검토합니다.

### 비밀 속성을 나열하는 코드 추가

이 섹션에서는 값을 검색하지 않고 자격 증명 모음의 모든 비밀 속성을 나열하는 코드를 추가합니다. 이 방법은 이름, 사용 여부, 콘텐츠 형식, 타임스탬프와 같은 메타데이터만 노출하여 최소 권한 원칙을 따릅니다.

이 함수는 **list_properties_of_secrets()**를 호출하여 비밀 속성 개체의 반복 가능 항목을 반환합니다. **get_secret()**과 달리 이 메서드는 비밀 값을 반환하지 않으므로, 비밀 내용에 액세스하지 않고 존재하는 비밀을 확인해야 하는 인벤토리 및 감사 작업에 적합합니다.

1. **# BEGIN LIST SECRETS FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def list_secret_properties():
        """List all secret properties without retrieving values."""
        client = get_client()
        results = []

        # list_properties_of_secrets returns metadata for every secret
        # in the vault without exposing the secret values, which follows
        # the principle of least privilege
        for prop in client.list_properties_of_secrets():
            results.append({
                "name": prop.name,
                "enabled": prop.enabled,
                "content_type": prop.content_type,
                "created_on": str(prop.created_on),
                "updated_on": str(prop.updated_on)
            })

        return results
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 새 비밀 버전을 만드는 코드 추가

이 섹션에서는 자격 증명 회전을 시뮬레이션하기 위해 비밀의 새 버전을 만드는 코드를 추가합니다. 이 함수는 현재 버전을 검색하고 **set_secret()**으로 새 값을 기록한 다음, 비밀을 다시 검색하여 업데이트를 확인합니다.

이 함수는 **set_secret()**을 사용하여 기존 비밀 이름에 새 값을 기록합니다. 이 작업은 이전 버전을 유지하면서 새 버전을 자동으로 만듭니다. 이전 버전은 버전 ID로 계속 액세스할 수 있지만, 버전 매개 변수가 없는 **get_secret()**은 항상 최신 버전을 반환합니다. 이 함수는 회전 메타데이터를 추적할 수 있도록 새 버전에 업데이트된 태그도 연결합니다.

1. **# BEGIN CREATE SECRET VERSION FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def create_secret_version(secret_name, new_value):
        """Create a new version of a secret and verify the update."""
        client = get_client()

        # Retrieve the current version before updating
        try:
            current = client.get_secret(secret_name)
            old_version = current.properties.version
            old_value = current.value[:20] + "..." if len(current.value) > 20 else current.value
        except ResourceNotFoundError:
            old_version = None
            old_value = None

        # set_secret creates a new version of the secret. The previous
        # version is preserved and can still be retrieved by version ID.
        client.set_secret(
            secret_name,
            new_value,
            content_type="text/plain",
            tags={"environment": "development", "rotated": "true"}
        )

        # Confirm the update by retrieving the secret again —
        # get_secret always returns the latest version
        confirmed = client.get_secret(secret_name)

        return {
            "name": secret_name,
            "old_version": old_version,
            "old_value": old_value,
            "new_version": confirmed.properties.version,
            "new_value": confirmed.value[:20] + "..." if len(confirmed.value) > 20 else confirmed.value,
            "created_on": str(confirmed.properties.created_on),
            "tags": confirmed.properties.tags or {}
        }
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 캐시를 사용하여 비밀을 검색하는 코드 추가

이 섹션에서는 비밀에 자주 액세스할 때 Key Vault API 호출 횟수를 줄이는 시간 기반 캐시를 구현하는 코드를 추가합니다. 캐시는 구성 가능한 TTL(Time-to-Live)을 사용하여 비밀 값을 메모리에 저장하고 캐시 적중과 누락을 추적합니다.

이 함수는 **time.monotonic()**을 사용하여 경과 시간을 추적하는 30초 TTL의 딕셔너리 기반 캐시를 만듭니다. 비밀 두 개에 액세스하는 작업을 다섯 차례 시뮬레이션합니다. 캐시가 비어 있고 반환할 항목이 없기 때문에 첫 번째 차례에는 캐시 누락이 발생합니다. 따라서 코드는 각 비밀을 Key Vault에서 가져와 캐시에 저장합니다. TTL이 만료되기 전의 다음 차례에서는 캐시 항목을 찾아 API 호출 없이 값을 반환합니다. 액세스 로그에는 적중 또는 누락이 표시되고, 요약에는 효율성 향상을 보여 주기 위해 총 API 호출 횟수와 전체 액세스 횟수가 보고됩니다.

1. **# BEGIN CACHED RETRIEVAL FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def cached_retrieval():
        """Demonstrate time-based caching to reduce Key Vault API calls."""
        client = get_client()
        cache = {}
        cache_ttl = 30
        vault_calls = 0
        access_log = []

        secret_names = ["openai-api-key", "cosmosdb-connection-string"]

        # Simulate five rounds of secret access. The first round fetches
        # from Key Vault (cache miss), and subsequent rounds return the
        # cached value if the TTL has not expired.
        for i in range(5):
            for name in secret_names:
                cached = cache.get(name)
                now = time.monotonic()

                if cached and (now - cached["timestamp"]) < cache_ttl:
                    access_log.append({
                        "round": i + 1,
                        "secret": name,
                        "result": "cache hit",
                        "value": cached["value"]
                    })
                else:
                    secret = client.get_secret(name)
                    vault_calls += 1
                    truncated = secret.value[:20] + "..." if len(secret.value) > 20 else secret.value
                    cache[name] = {
                        "value": truncated,
                        "timestamp": now
                    }
                    access_log.append({
                        "round": i + 1,
                        "secret": name,
                        "result": "cache miss",
                        "value": truncated
                    })

        return {
            "access_log": access_log,
            "vault_calls": vault_calls,
            "total_accesses": len(access_log),
            "cache_ttl_seconds": cache_ttl
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

1. 다음 명령을 실행하여 Python 환경을 활성화합니다. **참고:** Linux/macOS에서는 Bash 명령을 사용하고, Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

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

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 다양한 Key Vault 비밀 관리 작업을 수행합니다. 앱의 웹 인터페이스에서 비밀을 검색하고, 속성을 나열하고, 새 버전을 만들고, 캐시 검색을 테스트할 수 있습니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 연습 앞부분의 명령을 참고하여 환경을 활성화합니다. *client* 디렉터리에서 다른 위치로 이동했다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 패널에서 **비밀 검색(Retrieve Secrets)**을 선택합니다. 그러면 자격 증명 모음에 저장된 비밀 두 개를 검색하고, 비밀 이름, 일부만 표시된 값, 버전 식별자, 콘텐츠 형식, 생성 날짜 및 사용자 지정 태그를 비롯한 메타데이터를 오른쪽 패널에 표시합니다. 두 비밀 모두 상태가 **retrieved**로 표시되어야 합니다.

1. **비밀 속성 나열(List Secret Properties)**을 선택합니다. 이 작업은 값을 노출하지 않고 자격 증명 모음의 모든 비밀 속성을 나열합니다. 결과에는 각 비밀의 이름, 사용 여부, 콘텐츠 형식, 생성 날짜 및 마지막 업데이트 날짜가 표시됩니다. 이 작업은 인벤토리 및 감사 시나리오에 유용합니다.

1. **새 버전 만들기(Create New Version)**를 선택합니다. 이 작업은 무작위로 생성된 값으로 **openai-api-key** 비밀의 새 버전을 만들어 자격 증명 회전을 시뮬레이션합니다. 결과에는 이전 버전 및 값과 새 버전 및 값이 함께 표시되어, **set_secret()**이 이전 버전을 유지하면서 새 버전을 만든다는 것을 확인할 수 있습니다.

1. 왼쪽 패널에서 **비밀 검색(Retrieve Secrets)**을 선택하여 비밀이 업데이트되었는지 확인합니다.

1. **캐시 검색 실행(Run Cached Retrieval)**을 선택합니다. 이 작업은 30초 TTL 캐시를 사용하여 두 비밀에 액세스하는 과정을 다섯 차례 시뮬레이션합니다. 첫 번째 차례에는 Key Vault에서 값을 가져오므로 비밀마다 하나씩 총 두 번의 캐시 누락이 표시됩니다. TTL이 만료되지 않았으므로 나머지 차례에서는 캐시 적중이 표시됩니다. 요약을 통해 총 10회 액세스에 Key Vault API 호출은 2회만 수행되었음을 확인할 수 있습니다.

## 리소스 정리

이제 연습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. 앞서 선택한 이름으로 **\<rg-name>**을 바꿉니다. 이 명령은 리소스 그룹을 삭제하는 백그라운드 작업을 Azure에서 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택했다면 연습 범위 밖의 기존 리소스도 모두 삭제됩니다.

## 문제 해결

연습을 완료하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure Key Vault 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- Key Vault의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- 자격 증명 모음에서 액세스 정책 모드가 아닌 RBAC 권한 부여가 활성화되어 있는지 확인합니다.

**비밀 확인**
- 배포 스크립트의 **Check deployment status** 옵션을 실행하여 비밀이 성공적으로 저장되었는지 확인합니다.
- 비밀이 없으면 **Store secrets** 옵션을 다시 실행합니다.

**코드 완성도 및 들여쓰기 확인**
- *keyvault_functions.py*의 올바른 섹션에 있는 해당 BEGIN/END 주석 사이에 모든 코드 블록을 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인하고 함수 안에서 모든 코드의 위치가 올바른지 확인합니다.
- 지정된 섹션 외부의 코드를 실수로 제거하거나 수정하지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 파일이 있고 **KEY_VAULT_URL** 값이 포함되어 있는지 확인합니다.
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수를 터미널 세션에 로드했는지 확인합니다.
- 변수가 비어 있으면 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 다시 실행합니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- Azure portal에서 역할 할당을 확인하거나 배포 스크립트의 역할 할당 옵션을 다시 실행하여 Key Vault Secrets Officer 역할이 사용자 계정에 할당되었는지 확인합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
