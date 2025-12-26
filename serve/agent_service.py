

# from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import langchain.tools as tools
from langchain.tools import tool
# from langchain.agents.middleware import dynamic_prompt, ModelRequest
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from google import genai
from google.genai import types
from ConfigService import ConfigService


import os
from duckduckgo_search import DDGS
# from ddgs import DDGS

# Ensure environment variables are loaded
load_dotenv()


class GraphState(TypedDict):
    """
    Represents the state of our graph.
    
    Attributes:
        prompt: The original user prompt
        should_search: Whether to perform web search
        search_results: Raw search results from the web
        summary: Summary of search results
        final_statement: The generated final statement
        decision_reasoning: Explanation of the decision
    """
    prompt: str
    should_search: bool
    search_results: str
    summary: str
    final_statement: str
    decision_reasoning: str
    search_query: str
    role: str



class Context(TypedDict):
    user_role: str

class GeminiAdapter:
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.7):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, messages: list) -> object:
        # Convert LangChain messages to string content
        content = ""
        for msg in messages:
            if hasattr(msg, 'content'):
                content += msg.content + "\n"
            else:
                content += str(msg) + "\n"
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=content,
            config=types.GenerateContentConfig(
                temperature=self.temperature
            )
        )
        
        # Return object with content attribute to match LangChain interface
        class Response:
            def __init__(self, text):
                self.content = text
        
        return Response(response.text)

class DeepseekAdapter:
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    def invoke(self, messages: list) -> object:
        return self.llm.invoke(messages)

class OpenAIAdapter:
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key
        )

    def invoke(self, messages: list) -> object:
        return self.llm.invoke(messages)

class DebateAgentService:
    def __init__(self, user_role: str):
        self.config_service = ConfigService()
        provider_id = self.config_service.get_role_provider(user_role)
        print("find provider id: ", provider_id)
        self.provider = self.config_service.get_provider(provider_id)["provider"]
        self.model_name = self.config_service.get_provider(provider_id)["model"]
        self.api_key = self.config_service.get_provider(provider_id)["api_key"]
        print("find api key: ", self.api_key)
        self.user_role = user_role
        self.temperature = 0.7  # Default temperature
        self.llm = self._create_llm(self.temperature)

    def _create_llm(self, temperature: float):
        match self.provider:
            case "gemini":
                adapter_class = GeminiAdapter
            case "deepseek":
                adapter_class = DeepseekAdapter
            case _:
                adapter_class = OpenAIAdapter
        
        return adapter_class(
            model_name=self.model_name,
            api_key=self.api_key,
            temperature=temperature
        )

    def decision_node(self, state: GraphState) -> GraphState:
        """
        Node 1: Determine whether web search is needed.
        
        Analyzes the prompt and decides if external evidence is needed.
        """
        print("\n" + "="*80)
        print("NODE 1: DECISION - Determining if web search is needed...")
        print("="*80)
        
        decision_prompt = f"""Analyze the following prompt and determine if web search is needed to provide accurate, up-to-date information.

    Prompt: {state['prompt']}

    Consider:
    - Does this require current events, news, or recent data?
    - Would factual evidence from the web strengthen the response?
    - Is this about rapidly changing topics (technology, politics, sports, etc.)?
    - Does it ask for specific recent information?

    You are arguing for the {state['role']} side. Does this side need specific evidence?

    Respond with ONLY a JSON object in this format:
    {{
        "should_search": true/false,
        "search_query": "The specific query to search for (if needed, otherwise empty string)",
        "reasoning": "Brief explanation of your decision"
    }}"""
        
        response = self.llm.invoke([HumanMessage(content=decision_prompt)])
        
        # Parse the response
        import json
        try:
            # Clean up potential markdown code blocks if present
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            decision_data = json.loads(content)
            should_search = decision_data.get("should_search", False)
            search_query = decision_data.get("search_query", "")
            reasoning = decision_data.get("reasoning", "No reasoning provided")
        except:
            # Fallback parsing
            should_search = "true" in response.content.lower()
            search_query = ""
            reasoning = response.content
        
        print(f"\n🤔 Decision: {'SEARCH NEEDED' if should_search else 'NO SEARCH NEEDED'}")
        if should_search:
            print(f" Query: {search_query}")
        print(f"📝 Reasoning: {reasoning}")
        
        return {
            **state,
            "should_search": should_search,
            "search_query": search_query,
            "decision_reasoning": reasoning
        }

    def search_node(self, state: GraphState) -> GraphState:
        """
        Node 2a: Perform web search if needed.
        """
        print("\n" + "="*80)
        print("NODE 2: WEB SEARCH - Searching for information...")
        print("="*80)
        
        try:
            ddgs = DDGS()
            query = state.get('search_query')
            if not query:
                query = state['prompt']
                
            results = list(ddgs.text(query, max_results=5))
            
            if not results:
                search_results = "No search results found."
            else:
                formatted_results = []
                for i, result in enumerate(results, 1):
                    formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   URL: {result['href']}\n"
                    f"   Summary: {result['body']}\n"
                    )
                search_results = "\n".join(formatted_results)
            
            print(f"\n✅ Found {len(results)} search results")
            
        except Exception as e:
            search_results = f"Error during search: {str(e)}"
            print(f"\n❌ Search error: {e}")
        
        return {
            **state,
            "search_results": search_results
        }


    def summarize_node(self, state: GraphState) -> GraphState:
        """
        Node 2b: Summarize the search results.
        """
        print("\n" + "="*80)
        print("NODE 3: SUMMARIZE - Creating summary of search results...")
        print("="*80)
        
        summarize_prompt = f"""Summarize the following search results in relation to this prompt:

    Prompt: {state['prompt']}
    Role: {state['role']}

    Search Results:
    {state['search_results']}

    Provide a concise summary that:
    1. Extracts key facts and evidence
    2. Identifies main themes or findings
    3. Notes any contradictions or varying perspectives
    4. Highlights information that supports the {state['role']} position specifically

    Keep the summary clear and factual."""
        
        response = self.llm.invoke([HumanMessage(content=summarize_prompt)])
        summary = response.content
        
        print(f"\n📊 Summary created ({len(summary)} characters)")
        print(f"Preview: {summary[:200]}...")
        
        return {
            **state,
            "summary": summary
        }


    def generate_statement_node(self, state: GraphState) -> GraphState:
        """
        Node 3: Generate final statement based on results and summary.
        """
        print("\n" + "="*80)
        print("NODE 4: GENERATE - Creating final statement...")
        print("="*80)
        
        if state['should_search']:
            generation_prompt = f"""Based on the web search results and summary, generate a comprehensive statement addressing this prompt:

    Prompt: {state['prompt']}
    Role: {state['role']}

    Summary of Evidence:
    {state['summary']}

    Generate a well-structured statement that:
    1. Directly addresses the prompt
    2. Incorporates key findings from the search
    3. Provides specific examples and evidence
    4. Is clear, accurate, and informative
    5. Strongly supports the {state['role']} position
    6. Cites general sources when appropriate (e.g., "according to recent reports")

    Make the statement authoritative and well-supported."""
        else:
            generation_prompt = f"""Generate a comprehensive statement addressing this prompt:

    Prompt: {state['prompt']}
    Role: {state['role']}

    Note: No web search was needed for this prompt. Generate a statement based on your knowledge that:
    1. Directly addresses the prompt
    2. Is clear and informative
    3. Provides relevant context and explanation
    4. Is well-structured
    5. Persuasively argues for the {state['role']} position

    Generate a thorough response."""
        
        response = self.llm.invoke([HumanMessage(content=generation_prompt)])
        final_statement = response.content
        
        print(f"\n✍️ Final statement generated ({len(final_statement)} characters)")
        
        return {
            **state,
            "final_statement": final_statement
        }


    def skip_search_node(self, state: GraphState) -> GraphState:
        """
        Alternative path: Skip search and go directly to generation.
        """
        print("\n" + "="*80)
        print("SKIPPING SEARCH - Proceeding directly to generation...")
        print("="*80)
        
        return {
            **state,
            "search_results": "No search performed",
            "summary": "No search was needed for this prompt"
        }


    # ============================================================================
    # STEP 3: Define Routing Logic
    # ============================================================================

    def route_after_decision(self, state: GraphState) -> Literal["search", "skip_search"]:
        """
        Determines the next node based on the decision.
        """
        if state['should_search']:
            return "search"
        else:
            return "skip_search"

    # ============================================================================
    # STEP 4: Build the Graph
    # ============================================================================

    def create_workflow_graph(self):
        """
        Creates and compiles the LangGraph workflow.
        """
        # Initialize the graph
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("decision", self.decision_node)
        workflow.add_node("search", self.search_node)
        workflow.add_node("summarize", self.summarize_node)
        workflow.add_node("skip_search", self.skip_search_node)
        workflow.add_node("generate", self.generate_statement_node)
        
        # Set entry point
        workflow.set_entry_point("decision")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "decision",
            self.route_after_decision,
            {
                "search": "search",
                "skip_search": "skip_search"
            }
        )
        
        # Add edges for search path
        workflow.add_edge("search", "summarize")
        workflow.add_edge("summarize", "generate")
        
        # Add edge for skip path
        workflow.add_edge("skip_search", "generate")
        
        # Set finish point
        workflow.add_edge("generate", END)
        
        # Compile the graph
        app = workflow.compile()
        
        return app


    # ============================================================================
    # STEP 5: Main Execution
    # ============================================================================

    def run_workflow(self, prompt: str, system_message: Optional[str] = None, temperature: float = 0.7):
        """
        Execute the workflow with a given prompt.
        """
        # Store temperature for use in nodes
        self.temperature = temperature
        
        # Create the workflow
        app = self.create_workflow_graph()


        
        # Initial state
        initial_state = {
            "prompt": prompt,
            "role": self.user_role,
            "should_search": False,
            "search_results": "",
            "summary": "",
            "final_statement": "",
            "decision_reasoning": ""
        }
        
        print("\n" + "🚀" + "="*78 + "🚀")
        print(f"STARTING WORKFLOW")
        print(f"Prompt: {prompt}")
        print(f"Role: {self.user_role}")
        print("🚀" + "="*78 + "🚀")
        
        # Run the workflow
        result = app.invoke(initial_state)
        
        # Display final results
        print("\n" + "🎯" + "="*78 + "🎯")
        print("WORKFLOW COMPLETE - FINAL RESULTS")
        print("🎯" + "="*78 + "🎯")
        print(f"\n📝 Original Prompt:\n{result['prompt']}")
        print(f"\n🤔 Decision Made: {'Search Required' if result['should_search'] else 'No Search Needed'}")
        print(f"\n💭 Reasoning:\n{result['decision_reasoning']}")
        
        if result['should_search']:
            print(f"\n📊 Summary:\n{result['summary']}")
        
        print(f"\n✨ FINAL STATEMENT:\n{result['final_statement']}")
        print("\n" + "="*80 + "\n")
        
        return result['final_statement']

    def read_prompt_template(self, filename: str) -> str:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to prompts folder
        prompts_dir = os.path.join(script_dir, 'prompts')
        template_path = os.path.join(prompts_dir, filename)
        
        with open(template_path, 'r') as file:
            return file.read()




# Create the LangChain Tool
# search_tool = Tool(
#     name="web_search",
#     description=(
#         "Search the internet for current information, news, or facts. "
#         "Use this tool when you need up-to-date information that you don't have "
#         "in your training data, or when the user explicitly asks for a web search. "
#         "Input should be a search query string."
#     ),
#     func=search_internet
# )

@tool
def search(query: str) -> str:
    """Search for information."""
    return search_internet(query)







# Resolve API key and provider from environment
api_key = os.getenv("OPENAI_API_KEY") 
provider = "openai"
base_url = "https://api.deepseek.com" if provider == "deepseek" else None

# Resolve model name with sensible defaults
model_name = "gpt-4o-mini"

# agent = create_agent(
#     model=model_name,
#     tools=[search],
#     middleware=[user_role_prompt],
#     context_schema=Context
# )







# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "Do web search to support statement 'Python is a great programming language.'"}]},
#     context={"user_role": "expert"}
# )
# print(result["messages"])

debate_topic = "Should homework be banned in schools?"

# # Mock a state
# test_state = {
#     "prompt": debate_topic,
#     "should_search": False,
#     # ... other fields ...
# }

# # Call the function directly
# result_state = decision_node(test_state)

# print(result_state['should_search']) # Should be True

# # Mock a state where search is needed
# search_state = {
#     "prompt": debate_topic,
#     "should_search": True
# }

# # Call the function directly
# result_state = search_node(search_state)

# print(result_state['search_results'])

# debate_agent = DebateAgentService(user_role="affirmative team")
# debate_agent.run_workflow(debate_topic)
# debate_agent.run_workflow(debate_topic)


#generate test case to test agent_service with gemini provider







