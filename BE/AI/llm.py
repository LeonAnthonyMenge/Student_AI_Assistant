import torch
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from langchain_community.utilities import WikipediaAPIWrapper, StackExchangeAPIWrapper
from langchain_community.tools import YouTubeSearchTool, DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_experimental.utilities import PythonREPL
import requests
#Apple Silicon Chip uses: mps
#https://pytorch.org/get-started/locally/
torch.set_default_device('mps')

llama3 = Ollama(model="llama3:instruct", request_timeout=100.0)
codellama = Ollama(model="codellama:13b", request_timeout=50.0)
sqlcoder = Ollama(model="sqlcoder:latest", request_timeout=50.0)

context = """You are a Student Assistant. Your primary task is to help Students to get through their studies as easy as possible.
             In order to help the students with their general study questions you have access to a bunch of tools. You have to make
             sure to forward your findings from the tools to the user. If you are able to answer without further tools do so."""

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
you_tube = YouTubeSearchTool()
duckduckgo = DuckDuckGoSearchRun()
python_execute = PythonREPL()
# StackOverflow
stackoverflow = StackExchangeAPIWrapper()

def wikipedia(prompt):
    return wiki.run(prompt)

def youtube(prompt):
    return you_tube.run(prompt)

def duckduckgo_search(prompt):
    return duckduckgo.run(prompt)

def python_repl(python_code):
    return python_execute.run(python_code)

def stackexchange(prompt):
    return stackoverflow.run(prompt)

def coding_llm(user_prompt):
    return codellama.complete(user_prompt)

def sql_llm(user_prompt):
    return sqlcoder.complete(user_prompt)

def get_repository(username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to retrieve repository information")


perform_code_task = FunctionTool.from_defaults(
    fn=coding_llm,
    name="coding_llm",
    description="LLM specifically Trained to perform coding tasks. Takes the user prompt as input. Make sure to "
                "forward the answer as it is to the user"
)

perform_sql_task = FunctionTool.from_defaults(
    fn=sql_llm,
    name="sql_llm",
    description="LLM specifically Trained to perform sql tasks. Takes the user prompt as input. Make sure to "
                "forward the answer as it is to the user"
)


wikipedia_tool = FunctionTool.from_defaults(
    wikipedia,
    name="Wikipedia",
    description="A tool for loading and querying articles from Wikipedia"
)

youtube_tool = FunctionTool.from_defaults(
    youtube,
    name="YouTube",
    description="A tool for loading and querying video urls from Youtube. Make sure to forward this information to the user."
)

stackexchange_tool = FunctionTool.from_defaults(
    stackexchange,
    name="StackOverflow",
    description="A tool for loading and querying Results from Stackoverflow."
)

duckduckgo_search_tool = FunctionTool.from_defaults(
    duckduckgo_search,
    name="DuckDuckGo",
    description="A tool for querying Results from the search engine DuckDuckGo."
)

python_repl_tool = FunctionTool.from_defaults(
    python_repl,
    name="python_repl",
    description="A Python shell. Use this to execute python commands. Input should be a valid python command."
)

get_repository_tool = FunctionTool.from_defaults(
    get_repository,
    name="get GitHub Repository",
    description="A Function doing a get request via the github api. Takes username and repository_name (repo) as "
                "input and returns information about the repository."
)

tools = [
    perform_code_task,
    perform_sql_task,
    wikipedia_tool,
    #youtube_tool,
    #stackexchange,
    duckduckgo_search_tool,
    python_repl_tool,
    get_repository_tool
]


agent = ReActAgent.from_tools(tools, llm=llama3, verbose=True, context=context)

