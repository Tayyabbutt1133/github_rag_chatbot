from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain.tools.retriever import create_retriever_tool
from langchain import hub
from github import fetch_github_issues
from note import note_tool

load_dotenv()

# Initiating vector databases collection
def connect_to_vstore():
    embeddings = OpenAIEmbeddings()
    ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
    ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    desired_namespace = os.getenv("ASTRA_DB_KEYSPACE")

    if desired_namespace:
        ASTRA_DB_KEYSPACE = desired_namespace
    else:
        ASTRA_DB_KEYSPACE = None

    vstore = AstraDBVectorStore(
        embedding=embeddings,
        collection_name="github",
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace=ASTRA_DB_KEYSPACE,
    )
    return vstore






vstore = connect_to_vstore()
add_to_vectorstore = input("Do you want to update the issues? (y/N): ").lower() in [
    "yes",
    "y",
]

# adding data that we are fetching from github to vector store
if add_to_vectorstore:
    owner = "facebook"
    repo = "react"
    issues = fetch_github_issues(owner, repo)

    
    try:
        vstore.delete_collection()
    except:
        pass
# if in-case data-collection has been deleteed, we will connect/initialize vector databases again from start
    vstore = connect_to_vstore()
    vstore.add_documents(issues)


    

# creating a retriever
retriever = vstore.as_retriever(search_kwargs= {"k": 6})
retriever_tool = create_retriever_tool(
    retriever,
    "github_search",
    "Search for information about github issues. For any questions about github issues, you must use this tool!",
)



# using langchain hub agent for prompt
prompt = hub.pull("hwchase17/openai-functions-agent")

# initializing openai llm
llm = ChatOpenAI()

# creating retriever tool through agentExecutor
tools = [retriever_tool, note_tool]
agent = create_tool_calling_agent(prompt, tools, llm)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while (question := input("Ask a question about github issues (q to quit): ")) != "q":
    result = agent_executor.invoke({"input": question})
    print(result["output"])