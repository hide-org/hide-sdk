import os

from hide.client.hide_client import HideClient
from hide.langchain.toolkit import HideToolkit
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = "ENTER YOUR KEY"
HIDE_BASE_URL = "http://localhost:8080"
PROJECT_GIT_URL = "https://github.com/artmoskvin/tiny-math-service.git"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

hide_client = HideClient(base_url=HIDE_BASE_URL)
project = hide_client.create_project(url=PROJECT_GIT_URL)
toolkit = HideToolkit(project_id=project.id, hide_client=hide_client)

print(f"Project ID: {project.id}")

llm = ChatOpenAI(model="gpt-4-turbo")
prompt = hub.pull("hwchase17/openai-tools-agent")
tools = toolkit.get_tools()

for tool in tools:
    print("Name:", tool.name)
    print("Description:", tool.description)
    print("Args:", tool.args)
    print("")

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

response = agent_executor.invoke({"input": "Run tests"})
print()
print(response["output"])
