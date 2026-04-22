An AI-powered Sales Agent built using Large Language Models (LLMs) to automate and enhance customer interactions.
This system leverages a **Retrieval-Augmented Generation (RAG)** pipeline to provide accurate, context-aware responses, detect user intent, and capture lead information such as name and email.

Designed for real-world business applications, the agent supports scalable, stateful conversations and can act as a virtual sales assistant.

---

## Key Features

*  **RAG-Based Knowledge Retrieval**
  Uses a vector database to fetch relevant information and generate accurate responses.

*  **Conversational AI Agent**
  Engages users in natural, human-like conversations.

*  **Intent Detection**
  Identifies user goals such as product inquiry, support request, or lead generation.

* **Lead Capture System**
  Extracts and stores user details like name and email for follow-ups.

*  **Stateful Conversations**
  Maintains conversation context for better interaction flow.

*  **Scalable Design**
  Built to handle real-world business use cases.

---

##  Architecture

The system follows a RAG-based pipeline:

1. User Input
2. Intent Detection
3. Retrieval from Vector Database
4. Context Injection into LLM
5. Response Generation
6. Lead Information Extraction (if applicable)

---

##  Tech Stack

* Language: Python
* LLM: OpenAI GPT / Llama 3 / Mistral
* Vector Database: FAISS / Pinecone / Chroma
* Frameworks: LangChain / LlamaIndex (optional)

---

##  Core Functionalities

* Knowledge retrieval using embeddings
* Context-aware response generation
* Intent classification
* Lead data extraction (name, email)
* Multi-turn conversation handling

---

##  How It Works

1. User sends a query
2. System identifies intent
3. Relevant knowledge is retrieved
4. LLM generates a contextual response
5. Agent collects lead details when needed

---

##  Use Cases

* AI Sales Assistant
* Customer Support Automation
* Lead Generation Systems
* Website Chatbots

---

##  Future Improvements

* CRM integration
* Voice-based interaction
* Advanced analytics dashboard
* Multi-agent architecture


