import os

from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

import hide
from hide.model import Repository
from hide.toolkit import Toolkit

OPENAI_API_KEY = "ENTER YOUR KEY"
HIDE_BASE_URL = "http://localhost:8080"
PROJECT_GIT_URL = "https://github.com/artmoskvin/tiny-math-service.git"

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


hide_client = hide.Client(base_url=HIDE_BASE_URL)

project = hide_client.create_project(
    repository=Repository(url=PROJECT_GIT_URL),
)

toolkit = Toolkit(project=project, client=hide_client)

print(f"Project ID: {project.id}")

llm = ChatOpenAI(model="gpt-4-turbo")
prompt = hub.pull("hwchase17/openai-tools-agent")
tools = toolkit.as_langchain().get_tools()

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
