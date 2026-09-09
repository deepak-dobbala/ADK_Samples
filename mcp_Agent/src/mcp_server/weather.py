from typing import Any                  # Python Typing strings are used to generate custom responses
import httpx                            # httpx is used for the Async requests to the weeather API
from mcp.server.fastmcp import FastMCP  # This is used as a quick scaffolding to creaete the MCP server
#FastMCP  is an layered abstraction over the regualr mcp.server.Server which provides more granular control over the server streams

# Initialize FastMCP server - this creaetes the intial scaffolding for the MCP Server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# This function parses txhe url using the httpx module and returns the request back to the client
async def make_nws_request(url:str) -> dict[str,Any] | None:

    #prepare the headers for the connection request
    headers={
        "User-Agent" : USER_AGENT,
        "Accept" : "application/geo+json"
    }

    #the asyncClient() function splins up the Connection objection for Async Connectivity
    async with httpx.AsyncClient() as client:
        try :
            response = await client.get(url,headers=headers, timeout=30.0)
            response.raise_for_status()
            #if the Response ended in a 4XX type Error it will r eaise an exception for the request
            return response.json()
        except Exception:
            return None
    return None

#accesses the features from the reponse body and formats then for alerts
def format_alerts(features : dict) -> str:
    return f"""
        Event : {features["properties"].get("event","Unknown")}
        Area: {features["properties"].get('areaDesc', 'Unknown')}
        Severity: {features["properties"].get('severity', 'Unknown')}
        Description: {features["properties"].get('description', 'No description available')}
        Instructions: {features["properties"].get('instruction', 'No specific instructions provided')}
    """

@mcp.tool()
async def get_weather_alert(state : str) -> str:
    # Get the weather of a american state 
    # Args : state : two letter word for each state (eg : CA, NY)
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alerts(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude : float, longitude : float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
            {period['name']}:
            Temperature: {period['temperature']}°{period['temperatureUnit']}
            Wind: {period['windSpeed']} {period['windDirection']}
            Forecast: {period['detailedForecast']}
        """
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__=="__main__":
    mcp.run(transport="stdio")
    # as the server willbe used for local communication 
    # stdio comm  is used for low overhead transfport of messages
    #stdio should not be used with session logging as this may corrupt the STDIO  messages
