
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import json
from pydantic import BaseModel, Field
from models import *
from tools import *
load_dotenv()


from openai import OpenAI
client = OpenAI()




# Register the tools with OpenAI
assistant = client.beta.assistants.create(
    name="Stablecoin and Internet Search Assistant",
    instructions="You are an assistant that helps retrieve information about stablecoins, liquidity pools, and can perform internet searches. Do not assume or hallucinate and tell any on your own. Use the tools to get the information and answer the prompt.",
    tools=[{
        "type": "function",
        "function": {
            "name": "fetch_stable_coins_tool",
            "description": "Retrieve the top stablecoins by market cap.",
            "parameters": GetStableCoinsInput.model_json_schema()
        }
    }, {
        "type": "function",
        "function": {
            "name": "internet_search_tool",
            "description": '''Perform an internet search for any news or information using DuckDuckGo.
              Use this tool to search for information on the web from reliable and good sources.
              Only use proper and good sources realted to crypto to get the information.
              Also use this to fetch the price of any crypto coins''',
            "parameters": InternetSearchInput.model_json_schema()
        }
    }, {
        "type": "function",
        "function": {
            "name": "Get_Top_Pools_by_TVL",
            "description": "Retrieve the top liquidity pools by Total Value Locked (TVL).",
            "parameters": GetPoolsInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Get_Stable_Coins",
            "description": "Retrieve the top stablecoins by market cap.",
            "parameters": GetStableCoinsInput.model_json_schema()
        }
    },
    {
        "type": "function",
        "function": {
            "name": "Get_Stable_Coin_Prices",
            "description": "Retrieve the prices of stablecoins such as bitcoin, doge coin etc.",
            "parameters":  GetStableCoinsPriceInput.model_json_schema()
        }
    }],
    
    model="gpt-4o-mini",
)

def handle_message(message_text, thread_id):
    message = client.beta.threads.messages.create(
  thread_id=thread_id,
  role="user",
  content=message_text
)
    
    messagerun = client.beta.threads.runs.create_and_poll(
    thread_id=thread_id,
    assistant_id=assistant.id
)
    
    return messagerun



def handle_tool_execution(tool_name, parsed_arguments):
    """Executes the tool based on its name and returns the result or an error message."""
    try:
        if tool_name == "fetch_stable_coins_tool":
            top_m = parsed_arguments.get("top_m", 5)
            try:
                result = fetch_stable_coins(top_m)
                return result
            except Exception as e:
                return {"Error": f"Error executing fetch_stable_coins_tool: {e}"}

        elif tool_name == "internet_search_tool":
            query = parsed_arguments.get("query")
            region = parsed_arguments.get("region", "wt-wt")
            max_results = parsed_arguments.get("max_results", 5)
            try:
                result = internet_search(query, region, max_results)
                return result
            except Exception as e:
                return {"Error": f"Error executing internet_search_tool: {e}"}

        elif tool_name == "Get_Top_Pools_by_TVL":
            top_n = parsed_arguments.get("top_n", 5)
            try:
                result = get_and_display_top_pools_by_tvl(top_n)
                return result
            except Exception as e:
                return {"Error": f"Error executing Get_Top_Pools_by_TVL: {e}"}

        elif tool_name == "Get_Stable_Coins":
            top_m = parsed_arguments.get("top_m", 5)
            try:
                result = get_stable_coins(top_m)
                return result
            except Exception as e:
                return {"Error": f"Error executing Get_Stable_Coins: {e}"}

        elif tool_name == "Get_Stable_Coin_Prices":
            try:
                result = get_stable_coin_prices(True)
                return result
            except Exception as e:
                return {"Error": f"Error executing Get_Stable_Coin_Prices: {e}"}

        else:
            return {"Error": f"Tool '{tool_name}' is not recognized."}
    except Exception as overall_exception:
        # Log or handle the exception as needed
        return {"Error": f"An error occurred while handling the tool '{tool_name}': {overall_exception}"}


def submit_tool_outputs(thread_id, run_id, tool_outputs):
    """Submits the tool outputs back to the assistant and polls the result."""
    # Submit the tool outputs and poll for further updates
    client.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )


def handle_run_response(thread_id, run):
    """Handles the response of a run based on its status."""
    if run.status == 'completed':
        # Fetch the latest message in the thread if the run is completed
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        latest_message = messages.data[0]
        
        # Access the content of the latest message
        latest_message_content = latest_message.content[-1].text.value if latest_message.content else "No content available"
        return latest_message_content

    elif run.status == 'requires_action':
        required_action = run.required_action

        # Check if the required action contains tool calls
        if required_action and hasattr(required_action, "submit_tool_outputs"):
            tool_calls = required_action.submit_tool_outputs.tool_calls
            
            if tool_calls:
                tool_outputs = []
                # Process each tool call in the list of tool calls
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_arguments = tool_call.function.arguments
                    
                    # Parse the JSON arguments into a Python dictionary
                    parsed_arguments = json.loads(tool_arguments)
                    
                    try:
                        # Execute the tool and get the result
                        result = handle_tool_execution(tool_name, parsed_arguments)

                        # Convert Pydantic model result to a dictionary if needed
                        if isinstance(result, BaseModel):
                            result = result.model_dump()

                        # Append the tool call output to the list
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "output": json.dumps(result)  # Convert the result to a JSON string
                        })
                    
                    except ValueError as e:
                        print(f"Error during tool execution: {e}")
                        return {"Error": str(e)}

                # Submit all tool outputs together
                submit_tool_outputs(thread_id, run.id, tool_outputs)
                return tool_outputs
            else:
                print("No tool calls found in the required action.")
        else:
            print("No tool invocation required or recognized action.")
    else:
        print(f"Unhandled run status: {run.status}")

def chat_with_assistant(prompt, new, id_thread=None):
    if new == True:
        # Create a new thread
        thread = client.beta.threads.create()
        id = thread.id
    else:
        # Use the provided thread ID
        id = id_thread
        thread = None  # Initialize thread as None for the else case

    messagerun = handle_message(prompt, thread_id=id)
    print("hello")
    if messagerun.status == 'requires_action':
        response = handle_run_response(run=messagerun, thread_id=id)

        # Retrieve runInfo only if a thread object exists
        if thread:
            runInfo = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=messagerun.id)
            if runInfo.completed_at is None:
                client.beta.threads.runs.cancel(messagerun.id, thread_id=id)
        print("hi")
        messagerun_output = handle_message(
            '''Use the tool output and try to answer the prompt as a sentence. If the information is not available, tell it. Do not mention about the tools. 
            Imagine you are presnting the information to a user as a markdown. Mentions about the sources and url of any information at thge last of the sentance. 
            If the source and url not available, no need to mention it
           IMPORTANT:  Do not give it as a json or a list. It should be only a sentance.
            
            ''',
            thread_id=id,
        )
        response = handle_run_response(run=messagerun_output, thread_id=id)
    else:
        response = handle_run_response(run=messagerun, thread_id=id)

    return {"id": id, "response": response}