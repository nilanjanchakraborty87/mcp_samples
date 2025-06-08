import datetime
import os
from zoneinfo import ZoneInfo
from fastapi import FastAPI

import requests
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")


# Initialize the MCP server with your tools
mcp = FastMCP(name="mcp_server")


@mcp.tool()
def TimeTool(input_timezone):
    "Provides the current time for a given city's timezone like Asia/Kolkata, America/New_York etc. If no timezone is provided, it returns the local time."
    format = "%Y-%m-%d %H:%M:%S %Z%z"
    current_time = datetime.datetime.now()    
    if input_timezone:
        print("TimeZone", input_timezone)
        current_time =  current_time.astimezone(ZoneInfo(input_timezone))
    return f"The current time is {current_time}."

transport = SseServerTransport("/messages/")


@mcp.tool()
def get_weather(city: str) -> dict:
   """

   Fetch current weather for a given city using WeatherAPI.com.
   Returns a dictionary with city, temperature (C), and condition.
   """

   print(f"Server received weather request: {city}")
   url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
   response = requests.get(url)
   if response.status_code != 200:
       return {"error": f"Failed to fetch weather for {city}."}
   data = response.json()
   return {

       "city": data["location"]["name"],
       "region": data["location"]["region"],
       "country": data["location"]["country"],
       "temperature_C": data["current"]["temp_c"],
       "condition": data["current"]["condition"]["text"]
   }

async def handle_sse(request):
    # Prepare bidirectional streams over SSE
    async with transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (in_stream, out_stream):
        # Run the MCP server: read JSON-RPC from in_stream, write replies to out_stream
        await mcp._mcp_server.run(
            in_stream,
            out_stream,
            mcp._mcp_server.create_initialization_options()
        )


#Build a small Starlette app for the two MCP endpoints
sse_app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        # Note the trailing slash to avoid 307 redirects
        Mount("/messages/", app=transport.handle_post_message)
    ]
)


app = FastAPI()
app.mount("/", sse_app)

@app.get("/health")
def read_root():
    return {"message": "MCP SSE Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)