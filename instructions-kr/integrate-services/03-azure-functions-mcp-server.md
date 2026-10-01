---
lab:
  topic: 백엔드 서비스 통합
  title: Azure Functions로 MCP 서버 만들기
  description: AI 에이전트와 언어 모델이 검색하고 호출할 수 있도록 도구 트리거 함수를 노출하는 MCP 서버를 Azure Functions로 만들고 테스트하는 방법을 알아봅니다.
  level: 300
  duration: 25
  islab: true
  primarytopics:
    - Azure
    - Azure Functions
---

# Azure Functions로 MCP 서버 만들기

Model Context Protocol(MCP)은 AI 에이전트와 언어 모델이 외부 도구를 검색하고 호출하는 방법을 정의하는 개방형 표준입니다. Azure Functions에는 MCP 확장이 포함되어 있어 함수 앱을 MCP 서버로 노출할 수 있으며, 각 함수는 MCP 클라이언트가 호출할 수 있는 도구가 됩니다.

이 연습에서는 MCP 확장을 사용하는 Azure Functions 프로젝트를 만들고, 문서 처리를 위한 도구 트리거 함수를 정의하고, MCP 서버 설정을 구성한 다음, 에이전트 모드의 GitHub Copilot에서 연결하여 서버를 로컬로 테스트합니다.

>**참고:** 이 연습에서는 현재 활발히 발전 중인 Azure Functions MCP 확장을 사용합니다. 최신 설정 지침, API 범위 및 구성 옵션은 [Azure Functions MCP 확장 설명서](https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-mcp)를 참조하세요.

이 연습에서 수행하는 작업:

- MCP 확장을 사용하는 새 Azure Functions 프로젝트 만들기
- *host.json*에서 MCP 서버 설정 구성하기
- *function_app.py*에서 MCP 도구 트리거 함수 정의하기
- Python 환경 구성하기
- 에이전트 모드의 GitHub Copilot을 사용하여 MCP 서버를 로컬로 테스트하기

이 연습을 완료하는 데 약 **25**분이 걸립니다.

## 시작하기 전에

연습을 완료하려면 다음이 필요합니다.

- [Visual Studio Code](https://code.visualstudio.com/) 및 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나.
- Visual Studio Code용 [Azure Functions 확장](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions).
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) v4 이상.
- [Python 3.9](https://www.python.org/downloads/) 이상.
- GitHub Copilot을 사용할 수 있는 [GitHub 계정](https://github.com/). MCP 서버를 테스트하기 전에 Visual Studio Code에서 이 계정으로 로그인해야 합니다.
- Visual Studio Code용 [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) 확장.
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 Visual Studio Code용 [Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

## MCP 확장을 사용하는 새 Functions 프로젝트 만들기

이 섹션에서는 Visual Studio Code의 Azure Functions 확장을 사용하여 새 Azure Functions 프로젝트를 만들고 *host.json*에서 MCP 서버 설정을 구성합니다. 확장은 통합 디버깅을 위한 *.vscode* 구성 파일을 생성하고 Python v2 프로그래밍 모델을 설정하는 등 프로젝트 구조를 스캐폴딩합니다.

1. 프로젝트 폴더(예: *mcp-server-functions*)를 만들고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택하여 Visual Studio Code에서 엽니다.

1. **보기(View) > 명령 팔레트(Command Palette)...**를 선택하여 명령 팔레트를 엽니다. **Azure Functions: Create Function...** 명령을 실행하고 메시지가 표시되면 다음 옵션을 선택합니다.

    | 옵션 | 작업 |
    |--|--|
    | Select the folder... | 이전 단계에서 연 폴더를 선택합니다. |
    | Select a project type | **Python**을 선택합니다. |
    | Select a Python interpreter... | **Skip virtual environment**(가상 환경 건너뛰기)를 선택합니다. |
    | Select a template... | **HTTP trigger**를 선택합니다. |
    | Function name | 기본값인 **http_trigger**를 그대로 사용합니다. |
    | Authorization level | **ANONYMOUS**를 선택합니다. |

    확장은 *function_app.py*, *host.json*, *local.settings.json*, *requirements.txt*, 그리고 *launch.json*, *tasks.json*, *extensions.json*이 포함된 *.vscode* 폴더를 비롯한 프로젝트 구조를 만듭니다. 스캐폴딩된 *function_app.py*의 HTTP 트리거 함수는 다음 섹션에서 교체합니다.

1. *host.json*을 열고 다음 코드로 내용을 바꾼 다음 변경 내용을 저장합니다. **mcpToolTrigger** 바인딩 형식은 안정적인 확장 번들에 포함되지 않은 미리 보기 기능이므로 **extensionBundle**은 **Preview** 번들을 사용해야 합니다. **mcpToolTrigger** 섹션은 MCP 클라이언트가 연결할 때 표시되는 MCP 서버 이름, 버전 및 지침을 정의합니다.

    ```json
    {
        "version": "2.0",
        "extensionBundle": {
            "id": "Microsoft.Azure.Functions.ExtensionBundle.Preview",
            "version": "[4.*, 5.0.0)"
        },
        "extensions": {
            "mcpToolTrigger": {
                "serverName": "document-tools",
                "serverVersion": "1.0.0",
                "serverInstructions": "Tools for document processing and classification"
            }
        }
    }
    ```

1. *local.settings.json*을 열고 다음 코드로 내용을 바꿉니다.

    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsSecretStorageType": "Files"
      }
    }
    ```

1. 프로젝트에 *.vscode/mcp.json* 파일을 만들어 로컬 MCP 엔드포인트를 Visual Studio Code에 등록합니다. 이 파일은 Visual Studio Code에 MCP 서버의 위치와 연결 방법을 알려줍니다. 다음 코드를 파일에 추가한 다음 변경 내용을 저장합니다.

    ```json
    {
        "servers": {
            "document-tools-local": {
                "type": "sse",
                "url": "http://localhost:7071/runtime/webhooks/mcp/sse"
            }
        }
    }
    ```

## MCP 도구 트리거 함수 정의

이 섹션에서는 MCP 클라이언트가 검색할 수 있는 두 개의 MCP 도구 트리거 함수를 정의합니다. 각 함수는 **mcpToolTrigger** 형식의 **@app.generic_trigger()** 데코레이터를 사용합니다. 트리거 구성에서 도구 이름, 설명 및 입력 속성을 정의하면 연결된 MCP 클라이언트의 도구 호출 요청을 함수가 받습니다.

1. Visual Studio Code 탐색기 사이드바에서 *function_app.py*를 열고 두 개의 MCP 도구 트리거 함수를 정의하는 다음 코드로 내용을 바꿉니다.

    ```python
    import azure.functions as func
    import json
    import logging

    # Initialize the FunctionApp instance that registers all trigger functions
    app = func.FunctionApp()

    # Define an MCP tool trigger that exposes "summarize_text" to MCP clients.
    # toolProperties defines the input schema: a single "text" string parameter.
    @app.generic_trigger(
        arg_name="context",
        type="mcpToolTrigger",
        toolName="summarize_text",
        description="Summarize a block of text into key points",
        toolProperties='[{"propertyName": "text", "propertyType": "string", "description": "The text to summarize"}]'
    )
    def summarize_text(context: str) -> str:
        # Log the raw payload for debugging
        logging.info(f"summarize_text raw context: {context}")
        # Parse the outer request envelope sent by the MCP client
        request = json.loads(context)
        logging.info(f"summarize_text parsed request: {request}")
        # Extract the tool arguments from the request
        arguments = request.get("arguments", {})
        # Retrieve the "text" property defined in toolProperties
        text = arguments.get("text", "")

        # In a real implementation, call an Azure AI service here
        summary = f"Summary of {len(text.split())} words: {text[:100]}..."

        # Return a JSON response; the "content" field is displayed to the MCP client
        return json.dumps({"content": summary})

    # Define a second MCP tool trigger that exposes "classify_document" to MCP clients.
    # toolProperties defines two input parameters: "text" and "categories".
    @app.generic_trigger(
        arg_name="context",
        type="mcpToolTrigger",
        toolName="classify_document",
        description="Classify a document into a category",
        toolProperties='[{"propertyName": "text", "propertyType": "string", "description": "The document text to classify"}, {"propertyName": "categories", "propertyType": "string", "description": "Comma-separated list of possible categories"}]'
    )
    def classify_document(context: str) -> str:
        # Log the raw payload for debugging
        logging.info(f"classify_document raw context: {context}")
        # Parse the outer request envelope sent by the MCP client
        request = json.loads(context)
        logging.info(f"classify_document parsed request: {request}")
        # Extract the tool arguments from the request
        arguments = request.get("arguments", {})
        # Retrieve the "text" and "categories" properties defined in toolProperties
        text = arguments.get("text", "")
        categories = arguments.get("categories", "general")

        # In a real implementation, call an Azure AI service here
        # Split the comma-separated categories string into a list
        category_list = [c.strip() for c in categories.split(",")]
        # Select the first category as the classification result
        selected_category = category_list[0] if category_list else "unknown"

        # Return a JSON response with the classification result
        return json.dumps({
            "content": f"Classification: {selected_category}",
            "category": selected_category
        })
    ```

1. 파일을 저장하고 잠시 코드를 검토합니다. 각 함수는 **mcpToolTrigger** 형식의 **@app.generic_trigger()** 데코레이터를 사용합니다. **toolName**은 MCP 클라이언트의 도구 목록에 표시되고, **description**은 언어 모델이 각 도구를 언제 사용할지 이해하는 데 도움이 됩니다. **toolProperties** 매개 변수는 속성 정의의 JSON 배열로 입력 스키마를 정의합니다.

## Python 환경 구성

이 섹션에서는 Python 가상 환경을 만들고 활성화하여 프로젝트 종속성을 설치한 다음, Visual Studio Code가 해당 가상 환경을 사용하도록 구성합니다.

1. Visual Studio Code에서 **터미널(Terminal) > 새 터미널(New Terminal)**을 선택하여 프로젝트 디렉터리에서 통합 터미널을 엽니다.

1. 다음 명령을 VS Code 터미널에서 실행하여 Python 환경을 만듭니다.

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

1. 다음 명령을 VS Code 터미널에서 실행하여 종속성을 설치합니다.

    ```
    pip install -r requirements.txt
    ```

1. **보기(View) > 명령 팔레트(Command Palette)...**를 선택하여 명령 팔레트를 열고 **Python: Select Interpreter** 명령을 실행합니다. 프로젝트 디렉터리의 *.venv* 폴더에 있는 인터프리터를 선택합니다. 이렇게 하면 **F5** 키로 Functions 런타임을 시작할 때 디버거가 올바른 환경을 사용합니다.

## MCP 서버를 로컬로 테스트

이 섹션에서는 로컬 Functions 런타임을 시작한 다음, 에이전트 모드의 GitHub Copilot에서 MCP 서버에 연결하여 도구를 검색할 수 있고 예상한 결과를 반환하는지 확인합니다.

1. Visual Studio Code에서 **계정(Accounts)** 아이콘을 선택하고 GitHub Copilot을 사용할 수 있는 계정으로 GitHub에 로그인되어 있는지 확인합니다. 로그인되어 있지 않으면 계속하기 전에 안내에 따라 로그인합니다.

1. **F5**를 눌러 디버거가 연결된 상태로 Functions 런타임을 시작합니다. 필요한 스토리지 계정에 대한 경고가 표시되면 **Skip for now**(지금 건너뛰기)를 선택합니다. Visual Studio Code가 Core Tools를 시작하고 디버거를 연결한 다음, 함수 엔드포인트가 표시된 터미널 패널을 엽니다.

    >**참고:** 통합 터미널에서 `func start`를 실행하면 디버거 없이 런타임을 시작할 수도 있습니다.

    터미널 출력에는 등록된 MCP 도구 트리거 함수가 표시됩니다. 다음과 비슷한 출력이 있는지 확인합니다.

    ```
    Functions:
        classify_document: mcpToolTrigger
        summarize_text: mcpToolTrigger
    ```

    두 함수가 모두 표시되면 MCP 서버가 실행 중이며 연결할 준비가 된 것입니다.

    >참고: 사용 중인 Azure Functions Core Tools 버전에 따라 터미널에 경고가 표시될 수 있습니다. 상태 확인에 관한 이러한 경고는 무시해도 됩니다.

1. Visual Studio Code는 앞에서 만든 *.vscode/mcp.json* 파일을 감지하고 MCP 서버에 연결합니다. GitHub Copilot 채팅을 열고 채팅 창 아래쪽의 도구 아이콘을 선택합니다. *.vscode/mcp.json*의 서버 키 이름과 일치하는 **document-tools-local** 그룹을 찾습니다. 해당 그룹 아래에 설명과 함께 **summarize_text**와 **classify_document**가 모두 표시되는지 확인합니다.

### 명시적 프롬프트로 테스트

도구 이름을 직접 지정하는 명시적 프롬프트는 MCP 도구를 호출하게 하는 가장 신뢰할 수 있는 방법입니다. 모델은 대개 도구를 호출하지만 응답에서 도구의 원시 출력을 다시 표현하거나 요약할 수도 있습니다. 도구가 호출되지 않으면 터미널 출력을 확인한 다음 프롬프트를 다시 제출합니다.

1. Copilot 채팅에 다음 프롬프트를 입력하여 **classify_document** 도구를 테스트합니다. **참고:** Copilot이 MCP 도구를 처음 호출할 때 권한 프롬프트가 표시될 수 있습니다. Copilot이 도구를 호출하도록 **Allow in this Session**(이 세션에서 허용)을 선택합니다.

    <!--
    ```
    Use the classify_document tool to classify this text: 'This agreement is entered into by Party A and Party B'  with categories: contract, invoice, memo
    ```
    -->
    ```prompt
    Use the classify_document tool to classify this text: 'This agreement is entered into by Party A and Party B'  with categories: contract, invoice, memo
    ```

    ```prompt
    classify_document 도구를 사용하여 다음 텍스트를 분류합니다: 'This agreement is entered into by Party A and Party B'  분류 범주는 contract, invoice, memo입니다.
    ```

    Copilot이 도구를 호출하고 응답을 반환합니다. 결과에 **contract** 분류가 포함되어 있는지 확인합니다. 스텁 구현은 쉼표로 구분된 목록의 첫 번째 범주를 선택하므로, 결과는 프롬프트에서 제공한 첫 번째 범주와 일치합니다. 터미널 출력에서 함수 호출 로그 항목을 확인합니다.

1. Copilot 채팅에 다음 프롬프트를 입력하여 **summarize_text** 도구를 테스트합니다.

    <!--
    ```
    Use the summarize_text tool to summarize this text: 'Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure.'
    ```
    -->
    ```prompt
    Use the summarize_text tool to summarize this text: 'Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure.'
    ```

    ```prompt
    summarize_text 도구를 사용하여 다음 텍스트를 요약합니다: 'Azure Functions is a serverless compute service that lets you run event-triggered code without having to explicitly provision or manage infrastructure.'
    ```

    결과가 **Summary of**로 시작하고 단어 수와 입력 텍스트의 일부 미리 보기가 뒤따르는 요약 문자열을 포함하는지 확인합니다.

### 자연어 프롬프트로 테스트

모델이 도구의 관련성을 스스로 판단해야 하므로 자연어 프롬프트는 도구를 호출하지 않고 바로 답변할 가능성이 더 높습니다. 실제 도구가 호출되었는지 확인하려면 터미널 출력의 로그 항목을 확인합니다. 호출되지 않았다면 프롬프트를 바꾸거나 도구 이름을 명시적으로 지정합니다.

1. Copilot 채팅에 다음 프롬프트를 입력합니다.

    <!--
    ```
    Is the following text an invoice, contract, or memo?
    'Invoice B1234 for services rendered in January 2026. Total amount due: $5,000.'
    ```
    -->
    ```prompt
    Is the following text an invoice, contract, or memo?
    'Invoice B1234 for services rendered in January 2026. Total amount due: $5,000.'
    ```

    ```prompt
    다음 텍스트는 송장, 계약서 또는 메모 중 무엇인가요?
    'Invoice B1234 for services rendered in January 2026. Total amount due: $5,000.'
    ```

    Copilot은 **classify_document** 도구가 이 요청에 적합하다고 판단하여 자동으로 호출해야 합니다. 결과가 분류를 반환하는지 확인합니다. 터미널 출력에서 함수가 호출되었는지 확인합니다.

1. **summarize_text** 도구의 자연어 검색을 테스트하려면 다음 프롬프트를 입력합니다.

    <!--
    ```
    Give me a brief summary of this text: 'Machine learning models require large datasets for training. The quality of the training data directly impacts model accuracy. Data preprocessing steps include cleaning, normalization, and feature extraction.'
    ```
    -->
    ```prompt
    Give me a brief summary of this text: 'Machine learning models require large datasets for training. The quality of the training data directly impacts model accuracy. Data preprocessing steps include cleaning, normalization, and feature extraction.'
    ```

    ```prompt
    다음 텍스트를 간단히 요약해 주세요: 'Machine learning models require large datasets for training. The quality of the training data directly impacts model accuracy. Data preprocessing steps include cleaning, normalization, and feature extraction.'
    ```

    Copilot은 **summarize_text** 도구를 호출하고 요약을 반환해야 합니다. 터미널 출력에 함수 호출이 표시되는지 확인합니다.

1. **Shift+F5**를 눌러 디버거를 중지하고 Functions 런타임을 종료합니다.

## 다음 단계

프로덕션 시나리오에서는 Flex Consumption 계획을 사용하여 함수 앱을 Azure에 배포하고, **mcp_extension** 시스템 키로 MCP 클라이언트 연결을 인증하며, 각 도구 함수의 자리 표시자 로직을 **DefaultAzureCredential** 및 함수 앱의 관리 ID를 사용하여 Azure AI 서비스를 호출하는 코드로 바꿉니다. 자세한 내용은 [Azure Functions MCP 확장 설명서](/azure/azure-functions/functions-bindings-mcp)를 참조하세요.

## 문제 해결

연습을 진행하는 동안 문제가 발생하면 다음 문제 해결 단계를 시도합니다.

**Azure Functions Core Tools가 시작되지 않음**
- 터미널에서 **func --version**을 실행하여 Azure Functions Core Tools v4 이상이 설치되어 있는지 확인합니다.
- 포트 7071을 다른 프로세스가 사용 중인지 확인합니다.
- 프로젝트 루트에 *local.settings.json*이 있는지 확인합니다. Azure Functions 확장이 프로젝트를 만들 때 이 파일을 생성합니다.

**Copilot에 MCP 도구가 표시되지 않음**
- *.vscode/mcp.json*이 저장되어 있고 URL이 로컬 엔드포인트(`http://localhost:7071/runtime/webhooks/mcp/sse`)와 일치하는지 확인합니다.
- Functions 런타임이 실행 중이고 터미널 출력에 두 도구 트리거 함수가 모두 표시되는지 확인합니다.
- 파일을 저장한 후에도 MCP 서버 구성이 감지되지 않으면 Visual Studio Code를 다시 시작해 봅니다.

**함수 호출에서 오류가 반환됨**
- 터미널 출력에서 Python 예외 또는 스택 추적을 확인합니다.
- *function_app.py*의 들여쓰기가 올바르고 표시된 대로 모든 코드를 입력했는지 확인합니다.
- 가상 환경이 활성화되어 있고 *requirements.txt*의 모든 종속성이 설치되어 있는지 확인합니다.

**Python 환경 및 종속성 확인**
- **Python: Select Interpreter** 명령을 실행하여 Visual Studio Code가 *.venv* 폴더의 Python 인터프리터를 사용하는지 확인합니다.
- 통합 터미널에서 **pip list**를 실행하여 *requirements.txt*의 모든 패키지가 성공적으로 설치되었는지 확인합니다.
