from google.adk.tools.tool_context import ToolContext
# ToolContext is used to manage the state transfers in bwetween the and control the data parsing between conversations

def get_stateful_temparature_report(city: str, toolContext: ToolContext) -> dict:
    '''
        get_stateful_weather_report tool provides the temparature report for a specific city. 
        Gets the city value as an argument and access the user_preferred_temparature_metric from the ToolContext
        and returns the procesign status and weatheer report in a dict format

        Args : 
            city : str
            toolContext : ToolContext 
        returns:
            dict : [str,str]
    '''
    preferred_unit = toolContext.state.get('user_preferred_temparature_metric','Celsius')
    # default the tempaarture unit to celcius
    city_normalized = city.lower().replace(" ","")

    # initialize the static data for etsting purpose
    mock_temparature_data = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_temparature_data:
        data = mock_temparature_data[city_normalized]
        temp = data["temp_c"]
        temp_metric = "*C"
        weather_condition = data["condition"]

        if preferred_unit=="Fahrenheit":
            temp = (temp*(9/5))+32 # Convert to fahrenheit metric
            temp_metric = "*F"
        result = f"the weather in the city : {city_normalized.capitalize()} is {weather_condition} with a temparature of {temp:.2f}{temp_metric}"
        response = {"status":'True','Result' : result}
        toolContext.state["Lats_City_Checked"]=city

    else:
        error_msg = f"could fidn teh weather report for the city : {city}"
        response = {'status':'False', 'Result': error_msg}

    return response