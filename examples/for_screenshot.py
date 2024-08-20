import hide
from hide.toolkit import Toolkit

hc = hide.Client()

project = hc.create_project(
    repository="https://github.com/your-org/your-repo.git",
)

toolkit = Toolkit(project=project, client=hc)

your_agent.with_tools(toolkit).run("Do stuff")
