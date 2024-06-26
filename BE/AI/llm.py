import torch
from BE.AI.prompts import general_prompt, coding_prompt
from BE.Services.Pdf_service.query_data import pdf_ai
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent
from langchain_community.utilities import WikipediaAPIWrapper, StackExchangeAPIWrapper
from langchain_community.tools import YouTubeSearchTool, DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_experimental.utilities import PythonREPL
import requests
from BE.Database.chromadb.chroma_database import query_email_collection
#Apple Silicon Chip uses: mps
#https://pytorch.org/get-started/locally/
torch.set_default_device('mps')

llama3 = Ollama(model="llama3:instruct", request_timeout=100.0)
codellama = Ollama(model="codellama:13b", request_timeout=50.0)
sqlcoder = Ollama(model="sqlcoder:latest", request_timeout=50.0)


wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
you_tube = YouTubeSearchTool()
duckduckgo = DuckDuckGoSearchRun()
python_execute = PythonREPL()
# StackOverflow
stackoverflow = StackExchangeAPIWrapper()


def chromadb_emails(query_texts, n_results, name):
    return query_email_collection(query_texts, n_results, name)
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
    description="A tool for loading and querying video urls from Youtube. Make sure to forward the urls to "
                "the user as they are with some text around."
)

stackexchange_tool = FunctionTool.from_defaults(
    stackexchange,
    name="StackOverflow",
    description="A tool for loading and querying Results from Stackoverflow. Takes Error Message as Input"
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

vektor_based_emaildb = FunctionTool.from_defaults(
    query_email_collection,
    name="get E-mails from User",
    description="""
    Query the email collection in the vector database to retrieve the most relevant results based on query texts.

    Parameters:
    query_texts (list of str): A list of text queries for which the most relevant documents are to be retrieved.
    n_results (int): The number of top relevant results to return for each query.
    name (str): The name of the collection to query within the vector database.

    Returns:
    dict: A dictionary containing the query results, with keys corresponding to the query texts and values being lists of the top relevant documents."""

)


general_tools = [
    vektor_based_emaildb,
    wikipedia_tool,
    youtube_tool,
    duckduckgo_search_tool
]


general_agent = ReActAgent.from_tools(tools=general_tools, llm=llama3, verbose=True, context=general_prompt, max_iterations=30)

coding_tools = [
    perform_code_task,
    perform_sql_task,
    python_repl_tool,
    get_repository_tool
]

coding_agent = ReActAgent.from_tools(tools=coding_tools, llm=codellama, verbose=True, context=coding_prompt, max_iterations=30)

def get_agent(agent_name: str):
    if agent_name == "coding":
        return coding_agent
    elif agent_name == "psychology":
        return pdf_ai
    elif agent_name == "sql":
        return coding_agent
    else:
        return general_agent

