import hide
from hide import model
from hide.toolkit import Toolkit

hc = hide.Client()

project = hc.create_project(
    repository=model.Repository(
        url="https://github.com/artmoskvin/tiny-math-service.git"
    )
)

result = hc.run_task(project_id=project.id, alias="test")

print(result.stdout)
# ============================= test session starts ==============================
# platform linux -- Python 3.12.5, pytest-8.0.1, pluggy-1.4.0
# rootdir: /workspace
# plugins: anyio-4.3.0
# collected 3 items
#
# tests/test_api.py ...                                                    [100%]
# ======================== 3 passed, 5 warnings in 0.05s =========================

result = hc.run_task(project_id=project.id, command="pwd")

print(result.stdout)
# /workspace

file = hc.get_file(project_id=project.id, path="my_tiny_service/api/routers/maths.py")

print(file)
#  1 | """Endpoint examples with input/output models and error handling."""
#  2 | import logging
#  3 |
#  4 | import fastapi
#  5 | import pydantic
#  6 | import starlette.status
#  7 |
#  8 | router = fastapi.APIRouter()
# ... | ...
# 112 |         raise fastapi.HTTPException(
# 113 |             status_code=starlette.status.HTTP_400_BAD_REQUEST,
# 114 |             detail="Division by zero is not allowed",
# 115 |         ) from e

patch = """\
--- a/my_tiny_service/api/routers/maths.py
+++ b/my_tiny_service/api/routers/maths.py
@@ -113,3 +113,17 @@
             status_code=starlette.status.HTTP_400_BAD_REQUEST,
             detail="Division by zero is not allowed",
         ) from e
+
+
+@router.post(
+    "/exp",
+    summary="Calculate the exponent of two numbers",
+    response_model=MathsResult,
+)
+def exp(maths_input: MathsIn) -> MathsResult:
+    \"\"\"Calculates the exponent of two whole numbers.\"\"\"
+    return MathsResult(
+        **maths_input.dict(),
+        operation="exp",
+        result=maths_input.number1 ** maths_input.number,
+    )
"""

file = hc.update_file(
    project_id=project.id,
    path="my_tiny_service/api/routers/maths.py",
    update=model.UdiffUpdate(patch=patch),
)

print(file)
#  1 | """Endpoint examples with input/output models and error handling."""
#  2 | import logging
#  3 |
#  4 | import fastapi
#  5 | import pydantic
#  6 | import starlette.status
#  7 |
#  8 | router = fastapi.APIRouter()
# ... | ...
# 123 | def exp(maths_input: MathsIn) -> MathsResult:
# 124 |     """Calculates the exponent of two whole numbers."""
# 125 |     return MathsResult(
# 126 |         **maths_input.dict(),
# 127 |         operation="exp",
# 128 |         result=maths_input.number1 ** maths_input.number,
#                                                         ^^^^^^ Error: Cannot access attribute "number" for class "MathsIn"
#   Attribute "number" is unknown
#
# 129 |     )

from hide.toolkit import Toolkit

toolkit = Toolkit(project=project, client=hc)
lc_toolkit = toolkit.as_langchain()

for tool in lc_toolkit.get_tools():
    print("Name:", tool.name)
    print("Description:", tool.description)
    print("Args:", tool.args)
    print("")

# Name: append_lines
# Description: append_lines(path: str, content: str) -> str - Append lines to a file in the project.
# Args: {'path': {'title': 'Path', 'type': 'string'}, 'content': {'title': 'Content', 'type': 'string'}}
#
# ...
#
# Name: run_task
# Description: run_task(command: Optional[str] = None, alias: Optional[str] = None) -> str - Run a task in the project. Provide either command or alias. Command will be executed in the shell.
#         For the list of available tasks and their aliases, use the `get_tasks` tool.
# Args: {'command': {'title': 'Command', 'type': 'string'}, 'alias': {'title': 'Alias', 'type': 'string'}}

import os

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", seed=128)
prompt = hub.pull("hwchase17/openai-tools-agent")
tools = lc_toolkit.get_tools()

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

prompt = """\
I created the new exponentiation endpoint in the `my_tiny_service/api/routers/maths.py` file. Could you add the tests for it in the `tests/test_api.py` file?
Run the tests and make sure they pass. If the tests fail, fix them until they pass.
"""

response = agent_executor.invoke({"input": prompt})

print(response["output"])
# > Entering new AgentExecutor chain...
#
# Invoking: `get_file` with `{'path': 'my_tiny_service/api/routers/maths.py'}`
#
# ...
#
# > Finished chain.
#
# All tests have passed successfully, including the new test for the exponentiation endpoint.
