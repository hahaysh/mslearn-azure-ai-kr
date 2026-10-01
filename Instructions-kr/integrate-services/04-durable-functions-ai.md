---
lab:
  topic: 백엔드 서비스 통합
  title: Azure Durable Functions로 지속성 있는 문서 처리 워크플로 빌드
  description: 병렬 작업, 재시도, 사람의 승인 및 실패 보상을 조정하는 지속성 있는 문서 처리 워크플로를 빌드하고 테스트하는 방법을 알아봅니다.
  level: 300
  duration: 35
  islab: true
  primarytopics:
    - Azure
    - Azure Functions
---

# Azure Durable Functions로 지속성 있는 문서 처리 워크플로 빌드

Durable Functions는 상태 저장 오케스트레이션을 통해 Azure Functions를 확장하므로 서버리스 앱이 체크포인트, 큐 또는 폴링 루프를 직접 관리하지 않고도 오래 실행되는 작업을 조정할 수 있습니다. 오케스트레이터 함수는 진행 상태를 기록하므로 워크플로가 중단 후 복구되고, 실패한 작업을 재시도하고, 외부 이벤트를 효율적으로 기다리고, 지속성 타이머를 통해 다시 시작할 수 있습니다.

이 연습에서는 클레임 문서를 병렬로 처리하는 Python Durable Functions 앱을 완성합니다. 멱등성 결과 저장, 활동 재시도, 실패 보상, 시간 제한이 있는 사람 승인 경로, 팬아웃/팬인 오케스트레이션 및 외부 이벤트 전달을 추가합니다. 그런 다음 Azurite를 사용하여 워크플로를 로컬로 실행하고 테스트합니다.

이 연습에서 수행하는 작업:

- 프로젝트 시작 파일 다운로드
- Function App에 지속성 워크플로 코드 추가
- 워크플로를 로컬로 실행하고 테스트

이 연습을 완료하는 데 약 **35**분이 걸립니다.

## 시작하기 전에

이 섹션에서는 연습에 필요한 도구와 액세스를 확인합니다.

연습을 완료하려면 다음이 필요합니다.

- [Visual Studio Code](https://code.visualstudio.com/) 및 [지원되는 플랫폼](https://code.visualstudio.com/docs/supporting/requirements#_platforms) 중 하나.
- [Python 3.12](https://www.python.org/downloads/) 이상.
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) v4 이상.
- Visual Studio Code용 [Azurite](https://marketplace.visualstudio.com/items?itemName=Azurite.azurite) 확장.
- **선택 사항:** Python 코드 서식 지정 및 린팅을 위한 Visual Studio Code용 [Ruff 확장](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff).

Durable Functions는 오케스트레이션 기록과 상태를 저장하기 위해 스토리지 공급자가 필요합니다. 이 연습에서는 로컬 스토리지 공급자로 Azurite를 사용합니다.

## 프로젝트 시작 파일 다운로드

이 섹션에서는 시작 프로젝트를 다운로드하고 Visual Studio Code에서 엽니다. 프로젝트에는 Functions 호스트 구성, 샘플 워크플로 요청, 로컬 테스트 실행기 및 일부가 완성된 Function App이 포함되어 있습니다.

1. 브라우저를 열고 다음 URL을 입력하여 시작 파일을 다운로드합니다. 파일은 기본 다운로드 위치에 저장됩니다.

    ```
    https://github.com/MicrosoftLearning/mslearn-azure-ai/raw/main/downloads/python/durable-functions-python.zip
    ```

1. 파일을 복사하거나 이동하여 프로젝트 작업에 사용할 시스템 위치에 둡니다. 그런 다음 파일의 압축을 폴더에 풉니다.

1. Visual Studio Code를 시작하고 메뉴에서 **파일(File) > 폴더 열기...(Open Folder...)**를 선택한 다음 프로젝트 파일이 들어 있는 폴더를 선택합니다.

1. 탐색기 사이드바에서 프로젝트 파일을 검토합니다.

    - *function_app.py*에는 HTTP 엔드포인트, 활동 함수 및 오케스트레이터 함수가 포함되어 있습니다.
    - *host.json*은 Durable Functions 확장 및 작업 허브를 구성합니다.
    - *local.settings.json*은 Functions 호스트가 로컬에서 Azurite를 사용하도록 구성합니다.
    - *requirements.txt*에는 고정된 Python 종속성이 포함되어 있습니다.
    - *samples* 폴더에는 일반 및 재시도 동작을 테스트하기 위한 JSON 요청 본문이 들어 있습니다.
    - *tests* 폴더에는 대화형 워크플로 테스트 실행기가 들어 있습니다.

## 앱 완성

이 섹션에서는 문서 처리를 조정하고, 재시도와 사람의 결정을 처리하며, 최종 결과를 저장하는 Durable Functions 코드를 추가합니다. 요청 유효성 검사, 시뮬레이션된 문서 활동, 스토리지 클라이언트 및 HTTP 기본 코드는 이미 제공되므로 지속성 워크플로 개념에 집중할 수 있습니다.

1. Visual Studio Code 탐색기 사이드바에서 *function_app.py*를 엽니다.

>**참고:** 각 코드 블록은 일치하는 BEGIN 및 END 주석 사이에 추가합니다. 일부 블록은 기존 함수 안에 있으므로 들여쓰기를 네 칸 유지해야 합니다.

### 멱등성 결과 저장 추가

이 섹션에서는 Blob Storage에 하나의 간결한 결과 레코드를 쓰는 활동 함수를 추가합니다. 호스트가 외부 쓰기 이후 활동 완료가 기록되기 전에 실패하면 Durable Functions가 활동을 다시 실행할 수 있으므로 외부에서 확인할 수 있는 쓰기는 멱등성이 있어야 합니다.

**persist_result()** 활동은 결정적 작업 ID를 Blob 이름으로 사용하고 **overwrite**를 false로 설정합니다. Blob이 이미 있으면 함수는 저장된 레코드를 읽고 중복으로 만들지 않고 **AlreadyExists**를 반환합니다. 또한 문서 ID를 확인하여 예상치 못한 작업 ID 충돌이 명시적으로 실패하도록 합니다.

1. **# BEGIN IDEMPOTENT RESULT PERSISTENCE** 주석을 찾아 그 아래에 다음 코드를 추가합니다.

    ```python
    @app.activity_trigger(input_name="request")
    def persist_result(request):
        container = _get_or_create_container(RESULTS_CONTAINER)
        # The operation ID is the idempotency key for this external write.
        blob = container.get_blob_client(f"{request['operation_id']}.json")
        serialized = json.dumps(request, sort_keys=True)

        try:
            blob.upload_blob(serialized, overwrite=False)
            write_status = "Created"
            stored_result = request
        except ResourceExistsError:
            # A replay returns the original result instead of writing a duplicate.
            stored_result = json.loads(blob.download_blob().readall())
            if stored_result.get("document_id") != request["document_id"]:
                raise RuntimeError(
                    f"Operation ID collision for '{request['operation_id']}'."
                )
            write_status = "AlreadyExists"

        return {
            **stored_result,
            "result_url": blob.url,
            "write_status": write_status,
        }
    ```

1. 변경 내용을 저장하고 잠시 코드를 검토합니다.

### 활동 재시도 및 실패 보상 추가

이 섹션에서는 문서별 오케스트레이터의 첫 부분을 추가합니다. 각 문서에는 결정적 작업 ID가 부여되고, 추출, 분류 및 요약 활동은 제한된 재시도 정책에 따라 순차적으로 실행됩니다.

**document_orchestrator()** 함수는 각 활동을 최대 세 번 시도하고 첫 재시도 간격을 2초로 설정하는 **RetryOptions**를 만듭니다. 각 활동은 이전 활동의 출력을 받습니다. 재시도 후에도 활동이 실패하면 오케스트레이터는 **compensate_document()**를 예약하고 예외를 다시 발생시켜 워크플로가 성공처럼 보이는 결과를 반환하지 않고 기술적 실패를 보고하게 합니다.

1. **# BEGIN ACTIVITY RETRY WORKFLOW** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드는 **document_orchestrator()** 함수 안에서 들여쓴 상태여야 합니다.

    ```python
        document = context.get_input()
        # new_uuid() remains deterministic when the orchestrator replays.
        operation_id = str(context.new_uuid())
        process_request = {**document, "operation_id": operation_id}
        retry_options = df.RetryOptions(2_000, 3)

        try:
            # Each activity can run up to three times before the workflow fails.
            extracted = yield context.call_activity_with_retry(
                "extract_text",
                retry_options,
                process_request,
            )
            classified = yield context.call_activity_with_retry(
                "classify_document",
                retry_options,
                extracted,
            )
            summarized = yield context.call_activity_with_retry(
                "generate_summary",
                retry_options,
                classified,
            )
        except Exception:
            # Compensate only after the activity exhausts its retry policy.
            yield context.call_activity(
                "compensate_document",
                {
                    "operation_id": operation_id,
                    "reason": "ProcessingFailed",
                },
            )
            raise
    ```

1. 변경 내용을 저장하고 잠시 코드를 검토합니다.

### 지속성 시간 제한을 적용한 사람 승인 추가

이 섹션에서는 함수 호출을 계속 실행 상태로 유지하지 않고 신뢰도가 낮은 문서를 사람의 결정으로 전달합니다. 신뢰도가 높은 문서는 자동으로 완료되고, 신뢰도가 낮은 문서는 외부 이벤트 또는 지속성 타이머를 기다립니다.

오케스트레이터는 **wait_for_external_event()**와 **create_timer()**를 사용하여 두 개의 지속성 작업을 만든 다음, **task_any()**를 호출하여 먼저 완료되는 작업에 맞춰 계속 진행합니다. 승인 이벤트가 오면 사용하지 않는 타이머를 취소합니다. 거부 또는 시간 초과가 발생하면 보상 작업을 예약하고 명시적인 최종 상태를 기록합니다.

1. **# BEGIN HUMAN APPROVAL WORKFLOW** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드는 **document_orchestrator()** 함수 안에서 들여쓴 상태여야 합니다.

    ```python
        # High-confidence documents do not require a human decision.
        if summarized["confidence"] >= APPROVAL_CONFIDENCE_THRESHOLD:
            final_status = "Completed"
        else:
            yield context.call_activity(
                "notify_approver",
                {
                    **summarized,
                    "instance_id": context.instance_id,
                },
            )

            # Race the external event against a durable timer without blocking a worker.
            approval = context.wait_for_external_event("ApprovalResponse")
            deadline = context.current_utc_datetime + timedelta(
                seconds=APPROVAL_TIMEOUT_SECONDS
            )
            timeout = context.create_timer(deadline)
            winner = yield context.task_any([approval, timeout])

            if winner == approval:
                # Cancel the timer so the orchestration has no outstanding work.
                if not timeout.is_completed:
                    timeout.cancel()
                approval_payload = approval.result
                if isinstance(approval_payload, str):
                    approval_payload = json.loads(approval_payload)
                final_status = approval_payload["decision"]
            else:
                final_status = "ApprovalTimedOut"

            # Rejection and timeout both require a compensating action.
            if final_status != "Approved":
                yield context.call_activity(
                    "compensate_document",
                    {
                        "operation_id": operation_id,
                        "reason": final_status,
                    },
                )
    ```

1. 변경 내용을 저장하고 잠시 코드를 검토합니다.

### 팬아웃 및 팬인 오케스트레이션 추가

이 섹션에서는 문서마다 하나의 하위 오케스트레이션을 시작하는 부모 오케스트레이터를 추가합니다. 기다리기 전에 하위 오케스트레이션을 예약하면 서로 독립적인 문서를 동시에 처리할 수 있습니다.

**document_workflow()** 함수는 부모 인스턴스 및 문서 ID를 기반으로 결정적인 자식 인스턴스 ID를 만듭니다. 각 문서에 대해 **call_sub_orchestrator()**를 호출한 다음, **task_all()**을 사용하여 모든 자식이 완료 상태에 도달할 때까지 기다리고 간결한 결과 모음을 반환합니다.

1. **# BEGIN FAN OUT FAN IN ORCHESTRATION** 주석을 찾아 그 아래에 다음 코드를 추가합니다.

    ```python
    @app.orchestration_trigger(context_name="context")
    def document_workflow(context: df.DurableOrchestrationContext):
        workflow_input = context.get_input()
        tasks = []

        # Schedule every child before yielding so documents run concurrently.
        for document in workflow_input["documents"]:
            child_instance_id = f"{context.instance_id}-{document['document_id']}"
            tasks.append(
                context.call_sub_orchestrator(
                    "document_orchestrator",
                    {
                        **document,
                        "batch_id": workflow_input["batch_id"],
                    },
                    child_instance_id,
                )
            )

        # Fan in after every child reaches a terminal state.
        results = yield context.task_all(tasks)
        return {
            "batch_id": workflow_input["batch_id"],
            "documents": results,
        }
    ```

1. 변경 내용을 저장하고 잠시 코드를 검토합니다.

### 승인 이벤트 전달 추가

이 섹션에서는 승인 HTTP 엔드포인트를 완성합니다. 미리 작성된 코드는 추가할 코드가 대기 중인 문서 하위 오케스트레이션으로 이벤트를 보내기 전에 이벤트 ID와 결정을 검증합니다.

**raise_event()** 메서드는 자식 인스턴스 ID를 대상으로 지정된 **ApprovalResponse** 이벤트를 보냅니다. 이벤트 데이터는 **document_orchestrator()** 안에서 대기 중인 작업의 결과가 되므로, 지속성 워크플로가 저장된 상태부터 다시 실행됩니다.

1. **# BEGIN APPROVAL EVENT DELIVERY** 주석을 찾아 그 아래에 다음 코드를 추가합니다. 코드는 **submit_approval()** 함수 안에서 들여쓴 상태여야 합니다.

    ```python
        instance_id = req.route_params["instance_id"]
        # Deliver the decision to the exact child waiting for this named event.
        await client.raise_event(
            instance_id,
            "ApprovalResponse",
            {
                "event_id": event_id,
                "decision": decision,
            },
        )
        return _json_response({"status": "Accepted"}, 202)
    ```

1. 변경 내용을 저장하고 잠시 코드를 검토합니다.

## Python 환경 구성

이 섹션에서는 Python 가상 환경을 만들고 Azure Functions, Durable Functions, Azure Identity 및 Blob Storage에 필요한 종속성을 설치합니다.

1. 다음 명령을 VS Code 터미널에서 실행하여 Python 환경을 만듭니다.

    ```
    python -m venv .venv
    ```

1. 다음 명령을 실행하여 Python 환경을 활성화합니다. Linux 또는 macOS에서는 Bash 명령을 사용하고 Windows에서는 PowerShell 명령을 사용합니다. Windows에서 Git Bash를 사용하는 경우 **source .venv/Scripts/activate**를 사용합니다.

    **Bash**
    ```bash
    source .venv/bin/activate
    ```

    **PowerShell**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

1. 다음 명령을 실행하여 프로젝트 종속성을 설치합니다.

    ```
    pip install -r requirements.txt
    ```

## 앱을 로컬로 실행

이 섹션에서는 Azurite와 로컬 Functions 호스트를 시작한 다음 자동 완료, 사람 승인, 재시도 및 시간 초과 동작을 테스트합니다.

1. Visual Studio Code에서 **보기(View) > 명령 팔레트(Command Palette)...**를 선택하고 **Azurite: Start** 명령을 실행합니다. Azurite 확장을 설치해도 로컬 스토리지 서비스가 자동으로 시작되지는 않습니다. Visual Studio Code 상태 표시줄에 **[Azurite Blob Service] Running on http://127.0.0.1:10000**이 표시되는지 확인합니다. Visual Studio Code 알림을 열어 Blob, Queue 및 Table 서비스 시작 메시지를 확인할 수도 있습니다.

1. 가상 환경이 활성화된 터미널에서 다음 명령을 실행하여 로컬 Functions 호스트를 시작합니다.

    ```
    func start
    ```

    호스트에는 활동 및 오케스트레이션 트리거와 함께 **start_workflow** 및 **submit_approval** HTTP 엔드포인트가 표시됩니다.

1. Visual Studio Code에서 두 번째 터미널을 열고 이전 섹션의 적절한 명령을 사용하여 가상 환경을 활성화합니다.

1. 다음 명령을 실행하여 대화형 워크플로 테스트 메뉴를 시작합니다.

    ```
    python tests/run_workflow_tests.py
    ```

1. **1**을 입력하여 신뢰도가 서로 다른 문서가 포함된 워크플로를 시작합니다. 테스트는 자동으로 완료되는 신뢰도 높은 문서 하나와 외부 승인 이벤트를 기다리는 신뢰도 낮은 문서 하나를 제출합니다. 테스트에 표시되는 부모 및 자식 오케스트레이션 ID를 기록합니다.

1. **2**를 입력하여 활성 워크플로 상태를 확인합니다. **Runtime status**가 **Running**인지 확인합니다. **Documents** 목록에서 승인을 기다리는 동안 **claim-001**의 상태가 **Completed**이고 **claim-002**의 상태가 **Pending**인지 확인합니다.

    ```
    Instance ID: <ID for instance>
    Runtime status: Running
    Created: 2026-09-01T19:52:57Z
    Last updated: 2026-09-01T19:52:57Z
    Documents:
      - id=claim-001, orchestration=Completed, status=Completed
      - id=claim-002, orchestration=Running, status=Pending

    Press Enter to return to the menu...
    ```

1. **3**을 입력하여 신뢰도가 낮은 문서인 **claim-002**를 승인합니다. 테스트는 대기 중인 자식 오케스트레이션으로 **ApprovalResponse** 외부 이벤트를 보냅니다.

1. 몇 초 기다린 다음 **2**를 다시 입력합니다. **Runtime status**가 **Completed**인지 확인합니다. **Documents** 목록에서 **claim-001**의 상태가 **Completed**이고 **claim-002**의 상태가 **Approved**인지 확인합니다.

1. **1**을 입력하여 새 워크플로를 시작한 다음 **4**를 입력하여 **claim-002**를 거부합니다. 몇 초 기다렸다가 **2**를 입력합니다. **claim-001**의 상태가 **Completed**이고 **claim-002**의 상태가 **Rejected**인지 확인합니다. 거부 상태는 워크플로가 보상 경로를 따랐음을 확인해 줍니다.

1. **5**를 입력하여 재시도 시나리오를 실행합니다. 출력에 **claim-003-retry**의 **status=Completed** 및 **retry_occurred=True**가 표시되는지 확인합니다. 또한 테스트가 **claim-003-retry**가 시뮬레이션된 일시적 실패 한 번 이후 복구되었다고 보고하고 **PASS: retry scenario**를 표시하는지 확인합니다.

1. **6**을 입력하여 시간 초과 시나리오를 실행합니다. 승인 타이머가 만료될 때까지 테스트는 약 30초 동안 기다립니다.

1. 출력에 **claim-002**의 **ApprovalTimedOut** 상태가 표시되고 테스트가 **PASS: timeout scenario**를 보고하는지 확인합니다. 시간 초과 상태는 워크플로가 보상 경로를 따랐음을 확인해 줍니다.

1. **7**을 입력하여 테스트 메뉴를 종료합니다. Functions 호스트 터미널로 돌아가 **Ctrl+C**를 눌러 호스트를 중지합니다. 그런 다음 Visual Studio Code 명령 팔레트에서 **Azurite: Close**를 실행하여 로컬 스토리지 서비스를 중지합니다.

## 문제 해결

이 섹션에서는 로컬 테스트 중 발생할 수 있는 일반적인 문제를 살펴봅니다.

**Azurite 또는 Functions 호스트가 시작되지 않음**
- **func --version**을 실행하여 Azure Functions Core Tools v4 이상이 설치되어 있는지 확인합니다.
- **func start**를 실행하기 전에 **Azurite: Start**를 실행합니다. Azurite 확장을 설치하는 것만으로는 충분하지 않습니다. Durable Functions가 로컬 오케스트레이션 상태를 위해 Blob, Queue 및 Table 서비스를 실행해야 합니다.
- Visual Studio Code 상태 표시줄에 **[Azurite Blob Service] Running on http://127.0.0.1:10000**이 표시되는지 확인하고 Visual Studio Code 알림에서 Blob, Queue 및 Table 서비스 시작 메시지를 검토합니다. 확장의 디버그 로깅 설정을 사용하도록 설정한 경우에만 **보기(View) > 출력(Output)** 아래에 **Azurite** 채널이 표시됩니다.
- **127.0.0.1:10000**에 대한 연결 거부 오류는 Azurite Blob 서비스가 실행 중이 아님을 의미합니다.
- *local.settings.json*의 **AzureWebJobsStorage** 값이 **UseDevelopmentStorage=true**인지 확인합니다.
- 이전 Azurite 프로세스가 포트 10000, 10001 또는 10002를 계속 사용 중이면 **Azurite: Close**를 실행한 다음 다시 시작합니다.

**코드 완성도 및 들여쓰기 확인**
- *function_app.py*에서 다섯 개 코드 블록을 각각 일치하는 BEGIN 및 END 주석 사이에 추가했는지 확인합니다.
- 활동 재시도, 사람 승인 및 승인 이벤트 전달 블록은 기존 함수 내부에 있으며 네 칸 들여써야 합니다.
- 지정된 섹션 밖의 미리 작성된 코드를 제거하거나 수정하지 않았는지 확인합니다.

**워크플로가 계속 Running 상태임**
- 신뢰도가 낮은 문서는 의도적으로 최대 30초 동안 승인을 기다립니다. 승인 이벤트를 보내거나 지속성 타이머가 만료될 때까지 기다립니다.
- 승인 URL에 부모 인스턴스 ID 뒤에 **-claim-002**가 포함되어 있는지 확인합니다.
- Functions 호스트 터미널에서 자식 오케스트레이션 ID와 활동 오류를 검토합니다.
