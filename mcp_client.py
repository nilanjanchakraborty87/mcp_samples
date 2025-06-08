import asyncio
import json
from typing import Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import OpenAI
import mcp.client.sse as _sse_mod
from httpx import AsyncClient as _BaseAsyncClient
from loguru import logger
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import asyncio
import os


from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

import httpx
_orig_request = httpx.AsyncClient.request

GROQ_API_KEY = "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"

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize the LLM model
model = ChatGroq(model="llama3-8b-8192", temperature=0)
# model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# def llm_client(message: str):
    
#     client = OpenAI()

#     completion = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an intelligent Assistant. You will execute tasks as instructed"},
#             {
#                 "role": "user",
#                 "content": message,
#             },
#         ],
#     )

#     result = completion.choices[0].message.content
#     return result



def get_prompt_to_identify_tool_and_arguements(query, tools):
    tools_description = "\n".join([f"{tool.name}: {tool.description}, {tool.inputSchema}" for tool in tools.tools])
    return  ("You are a helpful assistant with access to these tools:\n\n"
                f"{tools_description}\n"
                "Choose the appropriate tool based on the user's question. \n"
                f"User's Question: {query}\n"                
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: When you need to use a tool, you must ONLY respond with "                
                "the exact JSON object format below, nothing else:\n"
                "Keep the values in str "
                "{\n"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '        "argument-name": "value"\n'
                "    }\n"
                "}\n\n")
    


async def main(query:str):
    sse_url = "http://localhost:8100/sse"

    # 1) Open SSE → yields (in_stream, out_stream)
    async with sse_client(url=sse_url) as (in_stream, out_stream):
        # 2) Create an MCP session over those streams
        async with ClientSession(in_stream, out_stream) as session:
            # 3) Initialize
            info = await session.initialize()
            logger.info(f"Connected to {info.serverInfo.name} v{info.serverInfo.version}")

            # 4) List tools
            #tools = (await session.list_tools())
            #logger.info(tools)      

            tools = await load_mcp_tools(session)
            for tool in tools:
                logger.info(f"Loaded MCP tool: {tool.name}")
                logger.info(f"Description: {tool.description}")

            agent = create_react_agent(model, tools, prompt="You are a helpful assistant.")

            print("ReAct Agent Created.")

            print(f"Invoking agent with query: {query}")     
            response = await agent.ainvoke({ "messages": [{"role": "user", "content": query}] })
            
            print(response.get("messages", [])[-1].content)
                       

if __name__ == "__main__":
    
    queries = ["What is the time in Asia/Kolkata?", "What is the weather like right now in Dubai?"]
    for query in queries:
        asyncio.run(main(query))