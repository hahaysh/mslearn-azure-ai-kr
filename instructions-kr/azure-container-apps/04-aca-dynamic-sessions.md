---
lab:
  topic: Azure Container Apps
  title: Azure Container Apps 동적 세션에서 AI 생성 코드를 안전하게 실행
  description: Azure Container Apps 동적 세션에서 AI 생성 Python 코드를 안전하게 실행하고 파일을 교환하며 격리된 세션을 관리하는 방법을 알아봅니다.
  level: 300
  duration: 30
  islab: true
  primarytopics:
    - Azure
    - Azure Container Apps
---

# Azure Container Apps 동적 세션에서 AI 생성 코드를 안전하게 실행

Azure Container Apps 동적 세션은 AI 생성 코드 또는 사용자가 제출한 코드를 실행할 수 있는 격리된 환경에 빠르게 액세스하도록 지원합니다. 코드 인터프리터 세션은 생성된 코드를 애플리케이션 프로세스 외부에서 실행하고, 관련 요청 간에 임시 파일을 유지하며, 구성 가능한 유휴 기간이 지나면 환경을 자동으로 제거합니다.

이 연습에서는 Python 코드 인터프리터 세션 풀을 배포하고 Microsoft Entra ID로 계정을 인증한 다음, Dynamic Sessions REST API를 호출하는 Flask 앱을 완성합니다. 앱은 샘플 데이터를 업로드하고 제공된 분석 페이로드를 실행하며 결과를 검증하고, 재사용된 세션에서 생성된 차트를 가져오고, 예상된 코드 실패를 감지한 다음 세션을 명시적으로 삭제합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일을 다운로드하고 동적 세션 풀 배포
- 애플리케이션에서 생성한 세션 식별자를 사용하는 보안 클라이언트 만들기
- Microsoft Entra ID를 사용하여 REST 요청 인증
- 격리된 세션에 데이터를 업로드하고 Python 코드 실행
- 재사용된 세션의 파일 나열 및 다운로드
- 실행 실패를 감지하고 세션을 명시적으로 삭제
- Flask 앱을 실행하고 REST 작업 결과 확인

이 연습을 완료하는 데 약 **30**분이 걸립니다.

## 시작하기 전에

이 섹션에서는 연습을 완료하는 데 필요한 도구와 Azure 권한을 검토합니다.

연습을 완료하려면 다음이 필요합니다.

- 리소스 그룹 및 Azure Container Apps 세션 풀을 만들고 Azure 역할을 할당할 권한이 있는 [Azure 구독](https://azure.microsoft.com/)
- [Visual Studio Code](https://code.visualstudio.com/)를 [지원 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나에 설치합니다.
- [Python 3.12](https://www.python.org/downloads/) 이상
- 최신 버전의 [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- Azure Container Apps 동적 세션을 지원하는 지역
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 [Visual Studio Code용 Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

## 프로젝트 시작 파일 다운로드 및 동적 세션 풀 배포

이 섹션에서는 프로젝트 시작 파일을 다운로드하고 Python 코드 인터프리터 세션 풀을 만들며 세션 실행기 역할을 할당한 다음, 코딩을 시작하기 전에 생성된 환경 변수를 불러옵니다. 배포는 일반적으로 몇 분 안에 완료됩니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/aca-dynamic-sessions-python.zip
    ```

1. 파일을 프로젝트 작업 위치로 복사하거나 이동합니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code(VS Code)를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. *azdeploy.py* 배포 스크립트를 열고 스크립트 맨 위의 두 값을 필요에 맞게 변경한 다음 변경 내용을 저장합니다. **참고:** 스크립트의 다른 내용은 변경하지 않습니다.

    ```
    "<your-resource-group-name>" # Resource Group name
    "<your-azure-region>" # Azure region for the resources
    ```

1. 메뉴 모음에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 VS Code에서 터미널 창을 엽니다.

1. 다음 명령을 실행하여 **Azure 계정에 로그인**합니다. 프롬프트에 따라 연습에 사용할 Azure 계정과 구독을 선택합니다.

    ```
    az login
    ```

1. 다음 명령을 실행하여 **Azure Container Apps 확장을 설치하거나 업그레이드**합니다. 동적 세션 명령은 이 확장에서 제공합니다.

    ```
    az extension add --name containerapp --upgrade --allow-preview true --yes
    ```

1. 다음 명령을 실행하여 **Azure Container Apps 리소스 공급자를 등록**합니다.

    ```
    az provider register --namespace Microsoft.App
    ```

### Azure에서 리소스 만들기

이 섹션에서는 배포 스크립트를 실행하여 세션 풀을 만들고, 풀 관리 API를 호출하는 데 필요한 역할을 할당하고, 클라이언트에서 사용할 리소스 값을 저장합니다.

1. 다음 명령을 실행하여 **배포 스크립트를 시작**합니다. 스크립트는 연습 리소스를 필요한 순서로 프로비저닝하는 메뉴를 제공합니다.

    ```
    python azdeploy.py
    ```

1. 스크립트가 실행 중이면 **1**을 입력하여 **코드 인터프리터 세션 풀 만들기(Create the code interpreter session pool)**를 선택합니다. 이 옵션은 리소스 그룹과 세션 동시 실행 한도가 5개이고 유휴 쿨다운이 300초이며 아웃바운드 네트워크 액세스가 비활성화된 PythonLTS 세션 풀을 만듭니다.

    작업이 성공하면 스크립트는 리소스 그룹, 풀 이름, 관리 엔드포인트 및 위치를 *.env*와 *.env.ps1*에 저장합니다.

1. **2**를 입력하여 **세션 실행기 역할 할당(Assign the session executor role)**을 선택합니다. 이 옵션은 로그인한 ID에 세션 풀 범위의 **Azure ContainerApps Session Executor** 역할이 있는지 확인하고, 필요한 경우 역할을 할당합니다. 이 역할을 사용하면 클라이언트가 Microsoft Entra 인증으로 코드를 실행하고 파일을 교환할 수 있습니다. 스크립트에서 역할이 이미 할당되었다고 표시되면 다음 단계로 진행합니다.

1. **3**을 입력하여 **배포 상태 확인(Check deployment status)**을 선택합니다. 세션 풀 상태가 **Succeeded**이고 실행기 역할이 **Yes**인지 확인합니다.

1. **4**를 입력하여 배포 스크립트를 종료합니다.

1. 다음 명령을 실행하여 **리소스 값을 터미널 세션으로 불러옵니다**.

    **Bash**
    ```bash
    source .env
    ```

    **PowerShell**
    ```powershell
    . .\.env.ps1
    ```

    이 터미널을 열어 둡니다. 나중에 새 터미널을 열면 앱을 시작하기 전에 해당 명령을 다시 실행합니다.

## 앱 완성

이 섹션에서는 *dynamic_sessions_functions.py*에 Dynamic Sessions REST 클라이언트 코드를 추가합니다. 미리 작성된 Flask 앱인 *app.py*는 이 함수를 호출하고 브라우저에 세션 워크플로 및 REST 작업 결과를 표시합니다. *app.py*는 편집하지 않아도 됩니다.

1. 코드를 추가할 *client/dynamic_sessions_functions.py* 파일을 엽니다.

> **Tip:** 여러 코드 섹션에는 **DynamicSessionClient** 클래스의 메서드가 있습니다. 해당 메서드의 들여쓰기가 **BEGIN** 및 **END** 마커와 정렬되어 있는지 확인합니다.

### 세션 클라이언트를 만드는 코드 추가

이 섹션에서는 애플리케이션이 제어하는 예측하기 어려운 식별자를 사용하는 Dynamic Sessions 클라이언트를 만듭니다. 식별자를 재사용하면 관련 요청이 동일한 임시 환경으로 전달됩니다. 전체 값을 브라우저에 노출하지 않으면 사용자가 다른 세션을 대상으로 지정하지 못합니다.

**get_session_client()** 함수는 **SESSION_POOL_ENDPOINT**에서 풀 관리 엔드포인트를 읽고 UUID를 생성한 다음 **DefaultAzureCredential**을 만듭니다. 이 자격 증명은 로컬 개발 중에는 Azure CLI 로그인을 사용하고, Azure에서 애플리케이션을 호스팅할 때는 관리 ID를 사용할 수 있습니다.

1. **# BEGIN CREATE SESSION CLIENT CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다.

    ```python
    def get_session_client() -> "DynamicSessionClient":
        """Create a client from the session pool endpoint in the environment."""
        endpoint = os.environ.get("SESSION_POOL_ENDPOINT", "").strip()
        if not endpoint:
            raise ValueError("SESSION_POOL_ENDPOINT environment variable must be set")

        # The backend creates the identifier instead of accepting one from the
        # browser. Reusing this unpredictable value keeps related operations in the
        # same session without letting a user target another session.
        identifier = str(uuid4())

        # DefaultAzureCredential uses developer credentials locally and can use a
        # managed identity after the application is hosted in Azure.
        credential = DefaultAzureCredential()
        return DynamicSessionClient(
            endpoint,
            credential=credential,
            identifier=identifier,
        )
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 세션 요청을 인증하는 코드 추가

이 섹션에서는 각 REST 요청을 인증하고 API 버전 및 세션을 선택하는 쿼리 매개 변수를 추가합니다. 풀 관리 엔드포인트에 대한 모든 호출에는 Dynamic Sessions 대상용 Microsoft Entra 토큰이 필요합니다.

**_headers()** 메서드는 **https://dynamicsessions.io/.default**에 사용할 토큰을 요청하고 전달자 토큰으로 추가합니다. **_params()** 메서드는 모든 작업에 동일한 애플리케이션 생성 식별자를 보내므로 업로드, 실행 및 다운로드가 하나의 세션을 사용합니다.

1. **# BEGIN AUTHENTICATE SESSION REQUESTS CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 메서드가 **DynamicSessionClient** 클래스 안에 들여쓰기되어 있는지 확인합니다.

    ```python
        def _headers(self) -> dict[str, str]:
            # Request a token for the dynamic sessions audience on every operation.
            # DefaultAzureCredential handles token caching and renewal.
            token = self.credential.get_token(TOKEN_SCOPE).token
            return {"Authorization": f"Bearer {token}"}

        def _params(self) -> dict[str, str]:
            # The identifier routes every request to the same temporary environment.
            # A request allocates the session automatically if it does not exist.
            return {
                "api-version": API_VERSION,
                "identifier": self.identifier,
            }
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 세션에 파일을 업로드하는 코드 추가

이 섹션에서는 제공된 분석 코드가 처리할 샘플 CSV 파일을 업로드합니다. 코드 인터프리터는 업로드된 파일을 */mnt/data*에 저장하며, 동일한 식별자를 사용하는 후속 요청에서도 이 파일에 액세스할 수 있습니다.

**upload_file()** 메서드는 로컬 파일을 바이너리 모드로 열고 **POST /files** 엔드포인트에 멀티파트 폼 데이터로 보냅니다. 컨텍스트 관리자는 API에서 오류를 반환하는 경우에도 요청 후 파일을 닫습니다.

1. **# BEGIN UPLOAD SESSION FILE CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 메서드가 **DynamicSessionClient** 클래스 안에 들여쓰기되어 있는지 확인합니다.

    ```python
        def upload_file(self, file_path: Path) -> dict[str, Any]:
            """Upload a local file into the session's /mnt/data directory."""
            # The service stores uploaded files in /mnt/data. Analysis code sent
            # with the same identifier can access the file without another upload.
            with file_path.open("rb") as source:
                response = self._request(
                    "POST",
                    "/files",
                    files={"file": (file_path.name, source, "text/csv")},
                    timeout=(5, 30),
                )
            return self._json_object(response)
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### Python 코드를 실행하고 검증하는 코드 추가

이 섹션에서는 제공된 분석 페이로드를 격리된 Python 인터프리터로 보내고 REST 전송 성공과 코드 실행 성공을 구분합니다. 격리를 통해 Flask 프로세스를 보호할 수 있지만, 제출한 코드가 성공적으로 완료되었는지 애플리케이션에서 검증해야 합니다.

**execute_code()** 메서드는 인라인 동기 실행 요청과 제한 시간을 지정하여 **POST /executions**를 호출합니다. HTTP 응답의 유효성을 검사한 후 실행 상태가 **Succeeded**인지 확인합니다. Python에서 예외가 발생하거나 서비스가 실행 오류를 보고하면 성공 형태의 결과를 반환하는 대신 **CodeExecutionError**를 발생시킵니다.

1. **# BEGIN EXECUTE CODE AND CHECK RESULT CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 메서드가 **DynamicSessionClient** 클래스 안에 들여쓰기되어 있는지 확인합니다.

    ```python
        def execute_code(self, code: str) -> dict[str, Any]:
            """Execute Python code synchronously and verify its final status."""
            # The code runs in the isolated interpreter session, not in the Flask
            # process. The backend must still authorize and validate the task.
            response = self._request(
                "POST",
                "/executions",
                json={
                    "codeInputType": "Inline",
                    "executionType": "Synchronous",
                    "code": code,
                    "timeoutInSeconds": 60,
                    "outputStreamsMaxLength": 4096,
                },
                timeout=(5, 90),
            )
            execution = self._json_object(response)

            # A successful HTTP request only proves that the service accepted and
            # ran the operation. Python can still raise an execution-level error.
            if execution.get("status") != "Succeeded":
                result = execution.get("result")
                stderr = result.get("stderr") if isinstance(result, dict) else None
                error = execution.get("error")
                message = None
                if isinstance(error, dict):
                    message = error.get("message")
                    nested_error = error.get("error")
                    if not message and isinstance(nested_error, dict):
                        message = nested_error.get("message")
                raise CodeExecutionError(
                    str(stderr or message or "Code execution failed")
                )
            return execution
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 세션 파일을 나열하고 다운로드하는 코드 추가

이 섹션에서는 재사용된 세션에 보관된 파일을 나열하고 분석 페이로드에서 생성한 SVG 차트를 다운로드합니다. 파일 목록을 통해 업로드한 CSV와 생성된 아티팩트가 관련 호출 간에 유지되는 것을 확인합니다.

**list_files()** 메서드는 **GET /files**를 호출하고 반환된 컬렉션을 검증합니다. **download_file()** 메서드는 요청 이름에 디렉터리 구성 요소가 없는지 확인하고 안전한 파일 이름을 URL 인코딩한 다음 **GET /files/{name}/content**를 호출합니다. 이름을 검증하면 호출자가 경로 순회를 사용하여 의도하지 않은 위치를 지정하지 못합니다.

1. **# BEGIN MANAGE SESSION FILES CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 두 메서드가 모두 **DynamicSessionClient** 클래스 안에 들여쓰기되어 있는지 확인합니다.

    ```python
        def list_files(self) -> list[dict[str, Any]]:
            """List files retained in the current session."""
            # The same identifier used for upload and execution exposes both the
            # original input and artifacts created by the generated code.
            response = self._request("GET", "/files", timeout=(5, 15))
            body = self._json_object(response)
            files = body.get("value", [])
            if not isinstance(files, list) or not all(
                isinstance(item, dict) for item in files
            ):
                raise DynamicSessionRequestError(
                    "Dynamic sessions API returned an unexpected file list"
                )
            return files

        def download_file(self, file_name: str) -> bytes:
            """Download one file from the current session."""
            # Reject directory components before placing the name in the URL. This
            # keeps file retrieval within the session's managed data directory.
            if Path(file_name).name != file_name:
                raise ValueError("A file name without a directory is required")
            safe_name = quote(file_name, safe="")
            response = self._request(
                "GET",
                f"/files/{safe_name}/content",
                timeout=(5, 30),
            )
            return response.content
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

### 세션을 삭제하는 코드 추가

이 섹션에서는 워크플로가 완료되면 세션을 명시적으로 삭제합니다. 풀이 쿨다운 기간 후 유휴 세션을 제거하지만, 세션을 일찍 삭제하면 임시 데이터와 동시 세션 용량을 바로 확보할 수 있습니다.

**delete_session()** 메서드는 보관된 식별자를 사용하여 **DELETE /session**을 호출하고 HTTP 상태 코드를 반환합니다. 서비스에서 세션 삭제를 확인하면 앱에 **204 No Content**가 표시됩니다.

1. **# BEGIN DELETE SESSION CODE SECTION** 주석을 찾고 그 아래에 다음 코드를 추가합니다. 메서드가 **DynamicSessionClient** 클래스 안에 들여쓰기되어 있는지 확인합니다.

    ```python
        def delete_session(self) -> int:
            """Immediately release the current dynamic session."""
            # The pool cooldown eventually removes idle sessions, but explicit
            # deletion releases capacity and temporary data as soon as work ends.
            response = self._request("DELETE", "/session", timeout=(5, 15))
            return response.status_code
    ```

1. 변경 내용을 저장하고 몇 분 동안 코드를 검토합니다.

## Python 환경 구성

이 섹션에서는 격리된 Python 환경을 만들고 클라이언트에 필요한 Flask, Requests 및 Azure Identity 패키지를 설치합니다.

1. 다음 명령을 실행하여 **client 디렉터리로 이동**합니다.

    ```
    cd client
    ```

1. 다음 명령을 실행하여 **Python 가상 환경을 만듭니다**.

    ```
    python -m venv .venv
    ```

1. 다음 명령을 실행하여 **Python 환경을 활성화**합니다.

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

    Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 실행합니다.

1. 다음 명령을 실행하여 **애플리케이션 종속성을 설치**합니다.

    ```
    pip install -r requirements.txt
    ```

## 앱 실행

이 섹션에서는 완성된 Flask 앱을 실행하고 동적 세션 워크플로를 진행합니다. 왼쪽 패널에는 완료, 다음 및 보류 중인 작업이 표시되고, 오른쪽 패널에는 각 REST 작업의 선별된 결과가 표시됩니다.

1. 다음 명령을 실행하여 **Flask 앱을 시작**합니다. 가상 환경이 활성화되어 있고 앞에서 불러온 환경 변수를 터미널에서 계속 사용할 수 있는지 확인합니다.

    ```
    python app.py
    ```

1. 브라우저를 열고 `http://localhost:5000`으로 이동합니다.

1. **1. 샘플 데이터 업로드(1. Upload Sample Data)**를 선택합니다. 앱은 보안 식별자를 생성하고 **POST /files**를 호출합니다. 이 작업은 자동으로 세션을 할당하고 *operational-data.csv*를 */mnt/data*에 업로드합니다. 이렇게 하면 이후 작업을 동일한 격리 환경으로 전달하는 애플리케이션 제어 세션 ID가 설정됩니다.

    1단계가 **완료(Completed)**로 바뀌고 2단계가 **다음(Next)**으로 바뀌며 결과에 축약된 세션 식별자와 업로드된 파일 메타데이터가 표시되는지 확인합니다.

1. **2. 분석 실행(2. Execute Analysis)**을 선택합니다. 앱은 *analysis_payload.py*를 읽고 **POST /executions**로 보내 실행 상태를 확인한 다음 표준 출력에 작성된 JSON을 검증합니다. 이를 통해 주요 보안 경계, 즉 AI 생성 코드가 Flask 애플리케이션 프로세스가 아닌 격리된 세션에서 실행되는 것을 확인합니다.

    결과에 **Succeeded** 상태, 실행 시간 및 다음 요약이 표시되는지 확인합니다.

    - 4개월
    - 총 요청 1,000건
    - 평균 요청 250건
    - 요청이 가장 많았던 달은 4월

1. **3. 세션 파일 나열(3. List Session Files)**을 선택합니다. 앱은 동일한 세션 식별자를 사용하여 **GET /files**를 호출합니다. 이 작업으로 별도의 REST 작업 간에도 식별자가 세션 상태를 유지하는지 확인합니다.

    결과에 *operational-data.csv*와 *trend.svg*가 모두 포함되는지 확인합니다. 생성된 차트는 실행 출력이 업로드된 입력과 함께 유지되었음을 보여줍니다.

1. **4. 생성된 차트 다운로드(4. Download Generated Chart)**를 선택합니다. 앱은 **GET /files/trend.svg/content**를 호출하고 콘텐츠 형식과 바이트 수를 보고한 다음 *trend.svg*를 브라우저의 다운로드 위치에 다운로드합니다. 이 작업으로 애플리케이션이 세션 파일 시스템을 직접 노출하지 않고도 실행된 코드가 만든 아티팩트를 가져오는 방법을 확인합니다.

    이제 모든 워크플로 단계가 **완료(Completed)**로 표시되는지 확인합니다. *trend.svg*를 열어 높이가 증가하는 막대 4개가 차트에 표시되는지 확인합니다.

1. **실패 처리 테스트(Test Failure Handling)**를 선택합니다. 앱은 Python 예외를 발생시키는 작은 페이로드를 제출합니다. 이 작업으로 REST 교환 성공과 세션 내 코드 실행 실패의 차이를 테스트합니다.

    REST 요청은 완료되었지만 실행 상태는 실패로 표시되고 예상된 **RuntimeError**가 표시되는지 확인합니다.

1. **세션 삭제(Delete Session)**를 선택합니다. 앱은 **DELETE /session**을 호출하고 로컬 워크플로 상태를 지운 다음 워크플로 작업을 초기화합니다. 이 작업으로 유휴 쿨다운을 기다리지 않고 세션 수명 주기를 명시적으로 관리하는 방법을 확인합니다.

    결과에 **204 No Content**가 표시되고 임시 데이터와 세션 용량이 해제되며 워크플로 작업이 초기화되는지 확인합니다.

# 리소스 정리

이제 연습을 마쳤으므로 불필요한 리소스 사용을 방지하기 위해 만든 클라우드 리소스를 삭제해야 합니다.

1. VS Code 터미널에서 다음 명령을 실행하여 리소스 그룹과 그룹 내 모든 리소스를 삭제합니다. **<rg-name>**을 앞에서 선택한 이름으로 바꿉니다. 이 명령은 Azure에서 리소스 그룹을 삭제하는 백그라운드 작업을 시작합니다.

    ```
    az group delete --name <rg-name> --no-wait --yes
    ```

> **CAUTION:** 리소스 그룹을 삭제하면 그 안에 포함된 모든 리소스가 삭제됩니다. 기존 리소스 그룹을 선택한 경우 연습 범위를 벗어난 기존 리소스도 삭제됩니다.

## 문제 해결

이 섹션에서는 연습 중 발생할 수 있는 일반적인 배포, 인증, 환경 및 코드 문제를 검토합니다.

**세션 풀 배포 실패 해결**
- 세션 풀 배포에 실패하면 선택한 지역이 동적 세션을 지원하지 않거나 사용 가능한 용량이 부족할 수 있습니다.
- *azdeploy.py* 맨 위의 **location** 변수를 다른 지원 지역으로 변경하고 `python azdeploy.py`를 다시 실행한 다음 옵션 1을 선택합니다.
- 스크립트는 재시도하기 전에 상태가 **Failed** 또는 **Canceled**인 세션 풀을 자동으로 삭제합니다.

**인증 및 역할 할당 확인**
- `az account show`를 실행하여 Azure CLI가 의도한 구독에 로그인되어 있는지 확인합니다.
- 배포 스크립트를 실행하고 **배포 상태 확인(Check deployment status)**을 선택하여 세션 풀이 준비되었고 실행기 역할이 할당되었는지 확인합니다.
- 배포 직후 앱에서 권한 부여 오류가 보고되면 역할 할당이 전파될 때까지 몇 분 기다린 후 작업을 다시 시도합니다.
- 세션 풀 범위에서 ID에 **Azure ContainerApps Session Executor** 역할이 있는지 확인합니다.

**환경 변수 확인**
- *.env*와 *.env.ps1* 파일이 모두 프로젝트 루트에 있으며 **SESSION_POOL_ENDPOINT**가 포함되어 있는지 확인합니다.
- 프로젝트 루트에서 Bash의 `source .env` 또는 PowerShell의 `. .\.env.ps1`을 실행하여 환경 값을 불러옵니다.
- 새 터미널을 열면 앱을 실행하기 전에 환경 값을 다시 불러옵니다.

**코드 완성도 및 들여쓰기 확인**
- 모든 코드 블록이 *dynamic_sessions_functions.py*의 일치하는 BEGIN 및 END 마커 사이에 추가되었는지 확인합니다.
- **DynamicSessionClient** 안의 메서드는 네 칸 들여쓰기되어 있고 중첩 블록도 일관된 들여쓰기를 사용하는지 확인합니다.
- 지정된 섹션 밖의 코드가 제거되거나 수정되지 않았는지 확인합니다.

**만료된 세션 복구**
- 세션 풀은 요청이 없는 상태로 300초가 지나면 세션을 제거합니다.
- 오랫동안 사용하지 않은 뒤 앱에서 *operational-data.csv*가 없다고 보고하면 **1. 샘플 데이터 업로드(1. Upload Sample Data)**를 다시 선택하여 세션을 할당하고 입력 파일을 복원합니다.

**Python 환경 및 종속성 확인**
- 앱을 실행하기 전에 가상 환경이 활성화되어 있는지 확인합니다.
- Flask, Requests 또는 Azure Identity를 가져올 수 없으면 `pip install -r requirements.txt`를 다시 실행합니다.
- 포트 5000을 이미 사용 중이면 다른 프로세스를 중지한 다음 `python app.py`를 실행합니다.
