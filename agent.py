import os
import time
import operator
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, AnyMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from knowledge import KNOWLEDGE_BASE, SYSTEM_RULES
from tools import mock_lead_capture

# Define the State
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    intent: str | None
    name: str | None
    email: str | None
    platform: str | None
    lead_confirmed: bool
    lead_captured: bool

from langchain_groq import ChatGroq

# Initialize LLM with Groq (much friendlier free tier)
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2, max_retries=3)

class IntentOutput(BaseModel):
    intent: Literal["GREETING", "INFORMATIONAL", "HIGH_INTENT"]

class ExtractionOutput(BaseModel):
    name: str | None = Field(default=None, description="User's name if mentioned")
    email: str | None = Field(default=None, description="User's email if mentioned")
    platform: str | None = Field(default=None, description="User's platform (e.g. YouTube, Instagram) if mentioned")
    confirmed: bool = Field(default=False, description="True if the user just confirmed their details are correct")

def classify_intent(state: AgentState):
    latest_msg = state["messages"][-1].content
    
    prompt = f"""You are an intent classifier for AutoStream SaaS platform.
    Return ONLY ONE of these intents based on the user's latest message:
    1. GREETING: e.g. "Hi", "Hello", "Hey"
    2. INFORMATIONAL: e.g. "What is your pricing?", "Tell me about features"
    3. HIGH_INTENT: e.g. "I want to buy", "I want Pro plan", "How do I sign up?", "I want to try this"
    
    User Message: "{latest_msg}"
    """
    time.sleep(4) # Throttle to respect 15 RPM free tier limit
    structured_llm = llm.with_structured_output(IntentOutput)
    res = structured_llm.invoke(prompt)
    
    intent = res.intent if res else "INFORMATIONAL"
    
    # If we are already in HIGH_INTENT and haven't fully captured the lead,
    # force it to remain HIGH_INTENT so the conversation flow continues collecting data.
    if state.get("intent") == "HIGH_INTENT" and not state.get("lead_captured"):
        intent = "HIGH_INTENT"
        
    return {"intent": intent}


def greeting_node(state: AgentState):
    time.sleep(4)
    response = llm.invoke([
        {"role": "system", "content": "You are a helpful AutoStream AI agent. The user just greeted you. Respond politely and ask how you can help. Keep it brief. " + SYSTEM_RULES},
        state["messages"][-1]
    ])
    return {"messages": [AIMessage(content=response.content)]}


def informational_node(state: AgentState):
    # Retrieve from knowledge base (RAG)
    system_msg = f"{SYSTEM_RULES}\n\nKNOWLEDGE BASE:\n{KNOWLEDGE_BASE}"
    
    messages = [{"role": "system", "content": system_msg}] + state["messages"]
    
    time.sleep(4)
    response = llm.invoke(messages)
    return {"messages": [AIMessage(content=response.content)]}


def lead_collection_node(state: AgentState):
    latest_msg = state["messages"][-1].content
    history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in state["messages"][-3:]])
    
    extract_prompt = f"""
    Extract lead information from the recent conversation. 
    If a field is not mentioned, return null.
    Also detect if the user confirmed their details.
    
    Conversation History:
    {history_str}
    """
    time.sleep(4)
    structured_llm = llm.with_structured_output(ExtractionOutput)
    extracted = structured_llm.invoke(extract_prompt)
    
    # Update state
    current_name = state.get("name")
    current_email = state.get("email")
    current_platform = state.get("platform")
    
    if extracted:
        if extracted.name: current_name = extracted.name
        if extracted.email: current_email = extracted.email
        if extracted.platform: current_platform = extracted.platform
        
    # Check what is missing
    missing = []
    if not current_name: missing.append("name")
    if not current_email: missing.append("email")
    if not current_platform: missing.append("platform")
    
    # Construct response
    if missing:
        next_missing = missing[0]
        prompt = f"You are an AI agent collecting lead info: Name, Email, Platform.\nUser already provided: Name={current_name}, Email={current_email}, Platform={current_platform}.\nWe need: {next_missing}.\nAsk the user conversationally and naturally for their {next_missing}. Only ask ONE question. Do not ask for already provided info.\nRecent user message: {latest_msg}"
        time.sleep(4)
        response = llm.invoke([{"role": "user", "content": prompt}])
        return {
            "name": current_name, 
            "email": current_email, 
            "platform": current_platform,
            "messages": [AIMessage(content=response.content)]
        }
    else:
        # All info collected. Ask for confirmation if not confirmed
        confirmed = state.get("lead_confirmed", False) or (extracted and extracted.confirmed)
        
        if not confirmed:
            msg = f"Thanks {current_name}! Just confirming your details:\nEmail: {current_email}\nPlatform: {current_platform}\n\nIs this correct? Shall I proceed to create your account?"
            return {
                "name": current_name, 
                "email": current_email, 
                "platform": current_platform,
                "messages": [AIMessage(content=msg)],
                "lead_confirmed": False
            }
        else:
            # Execute tool!
            tool_msg = mock_lead_capture(current_name, current_email, current_platform)
            return {
                "name": current_name, 
                "email": current_email, 
                "platform": current_platform,
                "lead_confirmed": True,
                "lead_captured": True,
                "intent": "INFORMATIONAL", # Reset intent
                "messages": [AIMessage(content=f"{tool_msg} Your account is ready!")]
            }

def route_intent(state: AgentState):
    if state.get("intent") == "GREETING":
        return "greeting"
    elif state.get("intent") == "HIGH_INTENT":
        return "lead_collection"
    else:
        return "informational"

from langgraph.graph import StateGraph, START, END

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("classify", classify_intent)
builder.add_node("greeting", greeting_node)
builder.add_node("informational", informational_node)
builder.add_node("lead_collection", lead_collection_node)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route_intent)

builder.add_edge("greeting", END)
builder.add_edge("informational", END)
builder.add_edge("lead_collection", END)

# Use Checkpointer for memory if we want built-in memory, or just maintain state dictionary.
# We will use the simplest approach by passing the updated state back and forth in main.py.
graph = builder.compile()
