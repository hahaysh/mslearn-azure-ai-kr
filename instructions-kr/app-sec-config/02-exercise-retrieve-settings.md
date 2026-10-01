---
lab:
  topic: 앱 비밀 및 구성
  title: Azure App Configuration에서 설정 및 비밀 검색
  description: Azure App Configuration 및 Key Vault와 Python SDK를 사용하여 구성 설정을 로드하고 나열하며 동적으로 새로 고치는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure App Configuration
---

# Azure App Configuration에서 설정 및 비밀 검색

AI 애플리케이션은 모델 엔드포인트 및 일괄 처리 크기와 같은 민감하지 않은 구성과 API 키와 같은 중요한 자격 증명에 모두 의존합니다. Azure App Configuration은 레이블 기반 환경 재정의, 비밀을 위한 Key Vault 참조, 애플리케이션을 다시 시작하지 않고 구성 변경 내용을 반영할 수 있는 sentinel 기반 동적 새로 고침 기능을 제공하는 중앙 집중식 설정 관리 저장소입니다.

이 연습에서는 샘플 설정이 미리 저장된 Azure App Configuration 저장소와 Key Vault를 배포하고, Azure SDK를 사용해 핵심 구성 관리 패턴을 보여 주는 Python Flask 웹 애플리케이션을 빌드합니다. 레이블 스택과 자동 Key Vault 참조 확인을 사용하여 설정을 로드하고, 모든 설정 속성과 메타데이터를 나열하고, sentinel 기반 새로 고침을 트리거하여 변경 내용을 동적으로 반영합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Azure App Configuration 저장소와 Key Vault를 만들고 샘플 설정 저장
- 앱을 완성하기 위해 시작 파일에 코드 추가
- 앱을 실행하여 구성 작업 수행

이 연습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- 필요한 Azure 서비스를 프로비전할 수 있는 권한과 할당량이 있는 [Azure 구독](https://azure.microsoft.com/).
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상.
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).
- **선택 사항:** Python 코드의 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

## 프로젝트 시작 파일 다운로드 및 Azure App Configuration 배포

이 섹션에서는 앱의 시작 파일을 다운로드하고 스크립트를 사용하여 샘플 설정이 포함된 Azure App Configuration 저장소와 Key Vault를 구독에 배포합니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/app-config-python.zip
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
    az provider register --namespace Microsoft.AppConfiguration
    az provider register --namespace Microsoft.KeyVault
    ```

1. 터미널에서 다음 명령을 실행하여 배포 스크립트를 시작합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행되면 **1**을 입력하여 **1. Create App Configuration** 옵션을 실행합니다. 이 옵션은 리소스 그룹이 없으면 만들고 Azure App Configuration 저장소를 배포합니다.

    App Configuration은 애플리케이션 설정을 코드와 분리하여 관리하는 중앙 집중식 서비스를 제공합니다.

1. **2**를 입력하여 **2. Create Key Vault** 옵션을 실행합니다. 이 옵션은 RBAC 권한 부여가 활성화된 Azure Key Vault를 만듭니다. Key Vault는 App Configuration이 안전하게 참조하는 API 키와 같은 중요한 값을 저장합니다.

1. **3**을 입력하여 **3. Assign roles** 옵션을 실행합니다. 이 옵션은 Microsoft Entra 인증을 사용하여 설정과 비밀을 읽고 만들고 업데이트할 수 있도록 App Configuration Data Owner 역할과 Key Vault Secrets Officer 역할을 사용자 계정에 할당합니다.

1. **4**를 입력하여 **4. Store settings** 옵션을 실행합니다. 이 옵션은 기본값(레이블 없음)과 환경별 설정을 위한 Production 레이블 재정의 값을 포함하는 구성 설정을 App Configuration 저장소에 저장합니다. 또한 Key Vault에 비밀을 저장하고 해당 비밀을 가리키는 Key Vault 참조를 App Configuration에 만듭니다. 마지막으로 동적 새로 고침에 사용할 sentinel 키를 만듭니다.

1. **5**를 입력하여 **5. Check deployment status** 옵션을 실행합니다. 계속하기 전에 App Configuration 저장소와 Key Vault의 상태가 모두 **Succeeded**이고, 역할이 할당되었으며, 설정이 저장되었는지 확인합니다. 리소스가 아직 프로비전 중이면 잠시 기다렸다가 다시 확인합니다.

1. **6**을 입력하여 **6. Retrieve connection info** 옵션을 실행합니다. 이 옵션은 앱에 필요한 App Configuration 엔드포인트 URL이 포함된 환경 변수 파일을 만듭니다.

1. **7**을 입력하여 배포 스크립트를 종료합니다.

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

이 섹션에서는 *appconfig_functions.py* 파일에 코드를 추가하여 App Configuration 관리 함수를 완성합니다. *app.py*의 Flask 앱은 이 함수를 호출하고 결과를 브라우저에 표시합니다. 연습 후반부에 앱을 실행합니다.

1. 코드를 추가하려면 *client/appconfig_functions.py* 파일을 엽니다.

>**참고:** 애플리케이션에 추가하는 코드 블록은 해당 코드 섹션의 주석과 같은 위치에 맞춰야 합니다.

### 설정을 로드하는 코드 추가

이 섹션에서는 레이블 스택과 자동 Key Vault 참조 확인을 사용하여 App Configuration 저장소의 모든 구성 설정을 로드하는 코드를 추가합니다. 이 함수는 레이블이 없는 기본값과 Production 레이블 재정의 값을 병합하고 Key Vault 참조를 자동으로 확인하는 공급자를 만듭니다.

이 함수는 두 개의 **SettingSelector** 항목과 함께 **load()**를 호출합니다. 첫 번째 항목은 레이블이 없는 모든 설정을 선택하고(null 레이블 필터 **\0** 사용), 두 번째 항목은 Production 레이블이 있는 모든 설정을 선택합니다. Production 선택기가 두 번째에 있으므로 키가 일치하면 해당 값이 기본값을 재정의합니다. **AzureAppConfigurationKeyVaultOptions** 매개 변수는 동일한 자격 증명을 사용하여 공급자가 Key Vault 참조를 자동으로 확인하도록 지정합니다. 따라서 애플리케이션은 참조 URI가 아니라 실제 비밀 값을 받습니다.

> **팁:** 일치하는 **BEGIN** 및 **END** 주석과 동일한 들여쓰기 수준에 코드를 붙여넣습니다. 블록이 어긋난 경우 붙여넣은 줄을 선택하고 **Tab** 또는 **Shift+Tab**을 눌러 블록 전체를 오른쪽이나 왼쪽으로 이동합니다.

1. **# BEGIN LOAD SETTINGS FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def load_settings():
        """Load all settings with label stacking and Key Vault reference resolution."""
        provider = get_provider()
        results = []

        # The provider resolves Key Vault references automatically and
        # applies label stacking: Production-labeled values override
        # unlabeled defaults for matching keys
        known_keys = [
            "OpenAI:Endpoint",
            "OpenAI:DeploymentName",
            "OpenAI:ApiKey",
            "Pipeline:BatchSize",
            "Pipeline:RetryCount",
            "Sentinel"
        ]

        for key in known_keys:
            try:
                value = provider[key]
                is_secret = key == "OpenAI:ApiKey"
                display_value = value[:10] + "..." if is_secret and len(value) > 10 else value
                results.append({
                    "key": key,
                    "value": display_value,
                    "type": "Key Vault reference" if is_secret else "configuration",
                    "status": "loaded"
                })
            except KeyError:
                results.append({
                    "key": key,
                    "value": None,
                    "type": "unknown",
                    "status": "not found"
                })

        return results
    ```

1. 몇 분 동안 코드를 검토합니다.

### 설정 속성을 나열하는 코드 추가

이 섹션에서는 App Configuration 저장소의 모든 설정 속성을 나열하는 코드를 추가합니다. 레이블을 병합하고 Key Vault 참조를 확인하는 **load()** 함수와 달리 이 함수는 모든 레이블과 콘텐츠 형식을 포함하여 개별 설정 항목이 저장된 원시 상태를 보여 줍니다.

이 함수는 관리 클라이언트에서 **list_configuration_settings()**를 호출합니다. 이 메서드는 키, 레이블, 콘텐츠 형식, 마지막 수정 타임스탬프, 읽기 전용 상태 등의 메타데이터가 포함된 설정 개체의 반복 가능 항목을 반환합니다. 레이블이 없는 항목과 Production 레이블이 있는 항목을 구분하여 저장된 내용을 정확히 확인해야 하는 인벤토리 및 감사 작업에 유용합니다.

1. **# BEGIN LIST SETTINGS FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def list_setting_properties():
        """List all setting properties from the App Configuration store."""
        client = get_client()
        results = []

        # list_configuration_settings returns every setting in the store
        # including all labels, showing the raw storage view rather than
        # the merged view that load() provides
        for setting in client.list_configuration_settings():
            results.append({
                "key": setting.key,
                "label": setting.label or "(no label)",
                "content_type": setting.content_type or "—",
                "last_modified": str(setting.last_modified) if setting.last_modified else "—",
                "read_only": setting.read_only
            })

        return results
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 동적 새로 고침 코드 추가

이 섹션에서는 sentinel 기반 동적 새로 고침을 보여 주는 코드를 추가합니다. 이 함수는 설정을 업데이트하고 새 sentinel 값을 설정한 다음 공급자에서 **refresh()**를 호출하여 애플리케이션을 다시 시작하지 않고 구성을 다시 로드합니다.

이 함수는 먼저 현재 공급자 값을 저장한 다음 관리 클라이언트를 사용하여 **Pipeline:BatchSize** 설정을 새 무작위 값으로 업데이트하고 **Sentinel** 키를 새 타임스탬프 값으로 설정합니다. sentinel은 변경 신호 역할을 합니다. 공급자가 sentinel을 감시하고, 값이 변경되면 **refresh()** 호출로 모든 설정을 다시 로드합니다. 함수는 새로 고침 간격이 지나도록 잠시 기다렸다가 **refresh()**를 호출하고, 변경 전후 값을 비교하여 업데이트가 반영되었는지 확인합니다.

1. **# BEGIN REFRESH CONFIGURATION FUNCTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 코드의 들여쓰기가 올바른지 확인합니다.

    ```python
    def refresh_configuration():
        """Demonstrate sentinel-based dynamic refresh of configuration settings."""
        provider = get_provider()
        client = get_client()

        # Capture current values before the change
        tracked_keys = ["Pipeline:BatchSize"]
        before = {}
        for key in tracked_keys:
            try:
                before[key] = provider[key]
            except KeyError:
                before[key] = "—"

        # Update Pipeline:BatchSize with a new value to simulate a
        # configuration change, then increment the Sentinel key to
        # signal the provider that settings have changed
        import random
        new_batch = str(random.randint(100, 999))

        setting = ConfigurationSetting(
            key="Pipeline:BatchSize",
            value=new_batch,
            label="Production",
            content_type="text/plain"
        )
        client.set_configuration_setting(setting)

        # Update the Sentinel to signal the provider that settings have changed.
        # Using a timestamp ensures the value is always different from whatever
        # the provider has cached, even if settings were reset externally.
        new_sentinel = str(int(time.time()))

        sentinel_setting = ConfigurationSetting(
            key="Sentinel",
            value=new_sentinel
        )
        client.set_configuration_setting(sentinel_setting)

        # Wait briefly for the refresh interval to elapse, then call
        # refresh() to reload settings from the store
        time.sleep(2)
        provider.refresh()

        # Capture values after the refresh
        after = {}
        for key in tracked_keys:
            try:
                after[key] = provider[key]
            except KeyError:
                after[key] = "—"

        settings = []
        for key in tracked_keys:
            settings.append({
                "key": key,
                "before": before[key],
                "after": after[key],
                "changed": before[key] != after[key]
            })

        return {
            "settings": settings,
            "sentinel_value": new_sentinel,
            "new_batch_size": new_batch,
            "batch_size_updated": after["Pipeline:BatchSize"] == new_batch
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

이 섹션에서는 완성된 Flask 애플리케이션을 실행하여 다양한 App Configuration 관리 작업을 수행합니다. 앱의 웹 인터페이스에서 설정을 로드하고, 설정 속성을 나열하고, 동적 새로 고침을 테스트할 수 있습니다.

1. 터미널에서 다음 명령을 실행하여 앱을 시작합니다. 필요한 경우 명령을 실행하기 전에 연습 앞부분의 명령을 참고하여 환경을 활성화합니다. *client* 디렉터리에서 다른 위치로 이동했다면 먼저 **cd client**를 실행합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동하여 앱에 액세스합니다.

1. 왼쪽 패널에서 **설정 로드(Load Settings)**를 선택합니다. 그러면 레이블 스택과 Key Vault 참조 확인을 사용하여 모든 구성 설정을 로드합니다. 결과에는 각 설정의 키, 값 및 형식이 표시됩니다. **configuration**으로 표시된 설정은 일반 App Configuration 값이고, **Key Vault reference**는 Key Vault 비밀에서 확인된 값입니다.

1. **설정 속성 나열(List Setting Properties)**을 선택합니다. 이 작업은 레이블이 없는 기본값과 Production 레이블이 있는 재정의 값을 별도의 행으로 포함하여 저장소의 모든 개별 설정 항목을 나열합니다. 결과에는 각 설정의 키, 레이블, 콘텐츠 형식, 마지막 수정 타임스탬프 및 읽기 전용 상태가 표시됩니다. **Pipeline:BatchSize**가 레이블 없이 값 10으로 한 번, **Production** 레이블과 값 200으로 한 번, 총 두 번 표시됩니다. **설정 로드(Load Settings)** 결과에 200이 표시된 이유는 Production 레이블이 있는 재정의 값이 레이블 없는 기본값보다 우선하기 때문입니다.

1. **구성 새로 고침(Refresh Configuration)**을 선택합니다. 이 작업은 sentinel 기반 동적 새로 고침을 보여 줍니다. 함수는 **Pipeline:BatchSize**를 새 무작위 값으로 업데이트하고, **Sentinel** 키를 새 타임스탬프로 설정하고, 잠시 기다린 다음 공급자에서 **refresh()**를 호출합니다. 결과에는 추적 중인 설정의 변경 전후 값이 표시되어 애플리케이션을 다시 시작하지 않아도 공급자가 변경 내용을 반영했음을 확인할 수 있습니다.

## 리소스 정리

이제 연습을 완료했으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. 앞서 선택한 이름으로 **\<rg-name>**을 바꿉니다. 이 명령은 리소스 그룹을 삭제하는 백그라운드 작업을 Azure에서 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **주의:** 리소스 그룹을 삭제하면 그룹에 포함된 모든 리소스가 삭제됩니다. 이 연습을 위해 기존 리소스 그룹을 선택했다면 연습 범위 밖의 기존 리소스도 모두 삭제됩니다.

## 문제 해결

연습을 완료하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure App Configuration 배포 확인**
- [Azure portal](https://portal.azure.com)로 이동하여 리소스 그룹을 찾습니다.
- App Configuration 저장소의 **Provisioning State**가 **Succeeded**인지 확인합니다.
- Key Vault의 **Provisioning State**가 **Succeeded**이고 RBAC 권한 부여가 활성화되어 있는지 확인합니다.

**설정 확인**
- 배포 스크립트의 **Check deployment status** 옵션을 실행하여 설정이 성공적으로 저장되었는지 확인합니다.
- 설정이 없으면 **Store settings** 옵션을 다시 실행합니다.

**코드 완성도 및 들여쓰기 확인**
- *appconfig_functions.py*의 올바른 섹션에 있는 해당 BEGIN/END 주석 사이에 모든 코드 블록을 추가했는지 확인합니다.
- Python 들여쓰기가 일관적인지(탭이 아닌 공백 사용) 확인하고 함수 안에서 모든 코드의 위치가 올바른지 확인합니다.
- 지정된 섹션 외부의 코드를 실수로 제거하거나 수정하지 않았는지 확인합니다.

**환경 변수 확인**
- 프로젝트 루트에 *.env* 파일이 있고 **AZURE_APPCONFIG_ENDPOINT** 값이 포함되어 있는지 확인합니다.
- **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 실행하여 환경 변수를 터미널 세션에 로드했는지 확인합니다.
- 변수가 비어 있으면 **source .env**(Bash) 또는 **. .\.env.ps1**(PowerShell)을 다시 실행합니다.

**인증 확인**
- **az account show**를 실행하여 Azure CLI에 로그인되어 있는지 확인합니다.
- Azure portal에서 역할 할당을 확인하거나 배포 스크립트의 역할 할당 옵션을 다시 실행하여 App Configuration Data Owner 및 Key Vault Secrets Officer 역할이 사용자 계정에 할당되었는지 확인합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
