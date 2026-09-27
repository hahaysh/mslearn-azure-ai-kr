---
lab:
  topic: Azure Managed Redis
  title: Azure Managed Redis에서 데이터 작업 수행
  description: redis-py Python 라이브러리를 사용하여 Azure Managed Redis에서 데이터 작업을 수행하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Managed Redis
---

# Azure Managed Redis에서 데이터 작업 수행

이 실습에서는 Azure Managed Redis 리소스를 만들고 **redis-py** 라이브러리를 사용하여 일반적인 데이터 작업을 수행하는 Python 콘솔 애플리케이션을 빌드합니다. Redis 해시 데이터 구조를 사용하여 키-값 쌍을 저장하고 검색하고, TTL(Time-To-Live) 설정으로 키 만료를 관리하고, 캐시에서 키를 삭제합니다.

이 실습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure Managed Redis 리소스 만들기
- 콘솔 앱을 완성하기 위해 시작 파일에 코드 추가
- 콘솔 앱을 실행하여 데이터 작업 수행

이 실습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

실습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Azure CLI **redisenterprise** 확장. **az extension add --name redisenterprise** 명령을 실행하여 설치할 수 있습니다.
- **선택 사항:** Python 코드를 서식 지정하고 린트하기 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 Azure Managed Redis 배포

이 섹션에서는 콘솔 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 구독에 Azure Managed Redis를 배포합니다. 배포에는 5~10분이 걸리므로 먼저 배포를 시작한 다음 프로비전이 진행되는 동안 앱 코드를 완성합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/amr-data-operations-python.zip
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

1. 다음 명령을 실행하여 Azure CLI용 **redisenterprise** 확장을 설치합니다.

    ```
    az extension add --name redisenterprise
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create Azure Managed Redis resource** 옵션을 시작합니다.

    이 옵션은 리소스 그룹이 아직 없는 경우 만들고 Azure Managed Redis를 배포합니다. 스크립트는 배포가 완료될 때까지 기다린 다음 터미널에 결과를 표시합니다.

1. 배포 스크립트를 계속 실행한 채 다음 섹션으로 이동하여 Azure Managed Redis가 프로비전되는 동안 앱 코드를 완성합니다. 터미널에서 완료 또는 오류 메시지가 표시되는지 주기적으로 확인합니다.


## 앱 완성

이 섹션에서는 *main.py* 스크립트에 코드를 추가하여 콘솔 앱을 완성합니다. 실습 후반에 Azure Managed Redis 리소스가 완전히 배포되었는지 확인하고 *.env* 파일을 만든 다음 앱을 실행합니다.

1. 코드 추가를 시작하려면 *main.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 들여쓰기가 일치해야 합니다.

### 클라이언트 연결 추가

이 섹션에서는 redis-py 라이브러리를 사용하여 Azure Managed Redis에 연결하는 코드를 추가합니다. 이 코드는 환경 변수에서 Redis 엔드포인트를 읽고 **redis-entraid** 자격 증명 공급자를 통해 **DefaultAzureCredential**을 사용하므로 클라이언트가 Microsoft Entra ID로 인증하고 토큰을 자동으로 새로 고칩니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 같은 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 정렬되지 않으면 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 사용하여 전체 블록을 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN CONNECTION CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    try:
        # Azure Managed Redis using Microsoft Entra ID authentication
        redis_host = os.getenv("REDIS_HOST")

        # create_from_default_azure_credential uses DefaultAzureCredential to
        # acquire and refresh a Microsoft Entra token for Redis.
        credential_provider = create_from_default_azure_credential(
            ("https://redis.azure.com/.default",),
        )

        r = redis.Redis(
            host=redis_host,
            port=10000,  # Azure Managed Redis uses port 10000
            ssl=True,
            decode_responses=True, # Decode responses to strings
            credential_provider=credential_provider,
            socket_timeout=30,  # Add timeout for better reliability
            socket_connect_timeout=30,
        )

        print(f"Connected to Redis at {redis_host}")
        input("\nPress Enter to continue...")
        return r
    ```

### 데이터 저장 및 검색 코드 추가

이 섹션에서는 **hset** 및 **hgetall** 명령을 사용하여 Redis 해시 데이터 구조를 처리하는 코드를 추가합니다. **hset** 메서드는 여러 필드-값 쌍을 단일 키에 저장하고, **hgetall**은 지정된 키의 모든 필드와 값을 검색합니다.

1. **# BEGIN STORE AND RETRIEVE CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def store_hash_data(r, key, value) -> None:
        """Store a hash data in Redis"""
        clear_screen()
        print(f"Storing hash data for key: {key}")
        result = r.hset(key, mapping=value) # Store hash data
        if result > 0: # New fields were added
            print(f"Data stored successfully under key '{key}' ({result} new fields added)")
        else:
            print(f"Data updated successfully under key '{key}' (all fields already existed)")
        input("\nPress Enter to continue...")

    def retrieve_hash_data(r, key) -> None:
        """Retrieve hash data from Redis"""
        clear_screen()
        print(f"Retrieving hash data for key: {key}")
        retrieved_value = r.hgetall(key) # Retrieve hash data
        if retrieved_value:
            print("\nRetrieved hash data:")
            for field, value in retrieved_value.items():
                print(f"  {field}: {value}")
        else:
            print(f"Key '{key}' does not exist.")

        input("\nPress Enter to continue...")
    ```

### 만료 설정 및 검색 코드 추가

이 섹션에서는 **expire** 및 **ttl** 명령을 사용하여 키 만료를 관리하는 코드를 추가합니다. **expire** 메서드는 키에 TTL(Time-To-Live)을 설정하여 지정된 초가 지나면 자동으로 만료되게 하고, **ttl**은 키가 만료되기까지 남은 시간을 검색합니다.

1. **# BEGIN EXPIRATION CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def set_expiration(r, key) -> None:
        """Set an expiration time for a key"""
        clear_screen()
        print("Set expiration time for a key")
        # Set expiration time, 1 hour equals 3600 seconds
        expiration = int(input("Enter expiration time in seconds (default 3600): ") or 3600)
        result = r.expire(key, expiration) # Set expiration time
        if result:
            print(f"Expiration time of {expiration} seconds set for key '{key}'")
        else:
            print(f"Key '{key}' does not exist. Expiration not set.")

        input("\nPress Enter to continue...")

    def retrieve_expiration(r, key) -> None:
        """Retrieve TTL of a key"""
        clear_screen()
        print(f"Retrieving the current TTL of {key}...")
        ttl = r.ttl(key) # Get current TTL
        if ttl == -2: # Key does not exist
            print(f"\nKey '{key}' does not exist.")
        elif ttl == -1: # No expiration set
            print(f"\nKey '{key}' has no expiration set (persists indefinitely).")
        else:
            print(f"\nCurrent TTL for '{key}': {ttl} seconds")
        input("\nPress Enter to continue...")
    ```

### 데이터 삭제 코드 추가

이 섹션에서는 **delete** 명령을 사용하여 Redis에서 키를 제거하는 코드를 추가합니다. **delete** 메서드는 키와 연결된 값을 캐시에서 영구적으로 제거하여 메모리를 확보하고 데이터에 더 이상 액세스할 수 없게 합니다.

1. **# BEGIN DELETE CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드 들여쓰기가 올바른지 확인합니다.

    ```python
    def delete_key(r, key) -> None:
        """Delete a key"""
        clear_screen()
        print(f"Deleting key: {key}...")
        result = r.delete(key) # Delete the key
        if result == 1:
            print(f"Key '{key}' deleted successfully.")
        else:
            print(f"Key '{key}' does not exist.")
        input("\nPress Enter to continue...")
    ```

1. 변경 내용을 *main.py* 파일에 저장합니다.

## 리소스 배포 확인

이 섹션에서는 Azure Managed Redis 배포를 확인하고, 데이터베이스를 만들고, Microsoft Entra ID 액세스를 구성하고, Redis 엔드포인트가 포함된 환경 변수 파일을 만듭니다.

1. 배포 스크립트가 실행 중인 터미널로 돌아갑니다. Azure Managed Redis 리소스가 성공적으로 만들어졌다는 스크립트 메시지가 표시되면 **Enter**를 눌러 배포 메뉴로 돌아갑니다.

1. 배포 메뉴가 나타나면 **2**를 입력하여 **2. Check deployment status** 옵션을 실행합니다. 상태가 **Succeeded**이면 다음 단계로 진행합니다. 그렇지 않으면 몇 분 기다린 후 옵션을 다시 실행합니다.

1. **3**을 입력하여 **3. Create database and configure access** 옵션을 실행합니다. 이 옵션은 데이터베이스를 만들고, 앱이 사용자 ID를 사용하여 연결할 수 있도록 Microsoft Entra ID 데이터 액세스 정책을 계정에 할당하고, **REDIS_HOST** 엔드포인트가 포함된 *.env* 및 *.env.ps1* 파일을 만듭니다.

1. 사용 중인 셸에 해당하는 환경 변수 파일을 검토하여 값이 있는지 확인한 다음 **4**를 입력하여 배포 스크립트를 종료합니다.

## Python 환경 구성

이 섹션에서는 Azure 배포를 완료한 후 Python 환경을 만들고 종속성을 설치합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 Python 환경을 만듭니다.

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

## 콘솔 앱 실행

이 섹션에서는 완성된 콘솔 애플리케이션을 실행하여 다양한 Redis 데이터 작업을 수행합니다. 앱에는 해시 데이터 저장, 값 검색, 키 만료 관리, 키 삭제를 위한 메뉴 기반 인터페이스가 있습니다.

1. 배포 스크립트가 만든 파일에서 환경 변수를 터미널 세션으로 불러오려면 적절한 명령을 실행합니다.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    >**참고:** 터미널을 열어 둡니다. 터미널을 닫고 새 터미널을 만들면 환경 변수를 다시 불러오기 위해 이 명령을 실행해야 합니다.

1. 터미널에서 다음 명령을 실행하여 콘솔 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 이 실습 앞부분의 명령을 참조하여 환경을 활성화합니다.

    ```
    python main.py
    ```

1. 앱에 다음 옵션이 표시됩니다. 시작하려면 **1. Store hash data**를 선택합니다.

    ```
    1. Store hash data
    2. Retrieve hash data
    3. Set expiration
    4. Retrieve expiration (TTL)
    5. Delete key
    6. Exit
    ```

1. 나머지 옵션을 차례로 선택하여 여러 작업을 실행합니다.

>**참고:** 원하는 순서대로 옵션을 실행할 수 있습니다. 예를 들어 해시 데이터를 저장한 다음 만료 정보를 검색하여 키에 만료가 설정되지 않았음을 확인할 수 있습니다.

앱에서 사용하는 예시 해시 데이터는 **main()** 함수 시작 부분에 정의되어 있습니다. 다른 키를 사용하거나 해시 데이터에 값을 더 추가하도록 코드를 업데이트할 수 있습니다.

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
- 리소스에서 **Public network access**가 사용하도록 설정되어 있는지 확인합니다.

**코드 완성도 및 들여쓰기 확인**
- *main.py*의 적절한 BEGIN/END 주석 사이에 모든 코드 블록을 올바른 섹션에 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인하고 모든 코드가 함수 안에서 올바르게 정렬되었는지 확인합니다.
- 지정된 섹션 밖의 코드가 실수로 제거되거나 수정되지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 폴더에 *.env* 및 *.env.ps1* 파일이 모두 있고 유효한 **REDIS_HOST** 값이 포함되어 있는지 확인합니다.
- 두 파일이 모두 *main.py*와 같은 디렉터리에 있는지 확인합니다.

**인증 및 액세스 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- 배포 스크립트의 **Create database and configure access** 옵션이 성공적으로 완료되어 계정에 데이터베이스 데이터 액세스 정책이 있는지 확인합니다.
- 앱에서 인증 오류가 보고되면 액세스 정책 할당이 적용되는 데 잠시 걸릴 수 있으므로 잠시 기다렸다가 다시 시도합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
