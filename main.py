import os
from dotenv import load_dotenv

# Load env variables first to get GOOGLE_API_KEY
load_dotenv()

from langchain_core.messages import HumanMessage
from agent import graph

def main():
    print("AutoStream AI Agent Initialized")
    print("Type 'exit' or 'quit' to stop.\n")
    
    # Initialize State
    config = {"configurable": {"thread_id": "1"}} # Usually used if checkpointer is enabled
    
    state = {
        "messages": [],
        "intent": None,
        "name": None,
        "email": None,
        "platform": None,
        "lead_confirmed": False,
        "lead_captured": False
    }
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        state["messages"].append(HumanMessage(content=user_input))
        
        try:
            state = graph.invoke(state, config)
        except Exception as e:
            print(f"\n[API Limits Hit] The API is exhausted ({e}).")
            print("We are on a strict free-tier! Wait 15 seconds, and then type your request again.\n")
            state["messages"].pop() # Remove the message so it doesn't break history
            continue
        
        latest_msg = state["messages"][-1]
        print(f"Agent: {latest_msg.content}\n")

if __name__ == "__main__":
    main()
