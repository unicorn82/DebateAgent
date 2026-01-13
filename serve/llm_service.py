import os
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from openai import OpenAI
from DatabaseService import DatabaseService

# Chains


# from langchain.agents import create_agent 

# Load environment variables
load_dotenv()

class LLMService:
    """Service for calling OpenAI and other LLM providers"""
    
    def __init__(self, role:str, token_id: Optional[str] = None):
       
        self.default_timeout = 60
        #convert role to uppercase
        self.role = role.upper()
        self.llm = None
        self.model = os.getenv(self.role + '_MODEL')
        self.provider = os.getenv(self.role + '_PROVIDER')
        self.api_key = os.getenv(self.role + '_API_KEY')
        self.token_id = token_id
        self.db = DatabaseService()

        print("role=" + self.role)

        # self.agent = create_agent(
        #     self.model
        #     # tools=tools
        # )

        # if ChatOpenAI is None:
        #     raise ImportError("LangChain ChatOpenAI integration is not installed. Please install 'langchain-openai' or 'langchain-community'.")

        # if self.provider not in ("openai", "deepseek"):
        #     raise ValueError(f"Provider {self.provider} not supported")

        # # Initialize a default client (temperature will be set per-call)
        # self.llm = self._make_chat_model(temperature=0.7)
    
    def run_agent(self, prompt: str) -> str:
        """Run the agent with the given prompt and return the result."""
        # The system prompt will be set dynamically based on context
        result = self.agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            context={"user_role": "expert"}
        )

        if self.token_id:
            self.db.decrement_request_count(self.token_id)

        return result
        

     # function to read prompt template from file
    def read_prompt_template(self, filename: str) -> str:
        with open(filename, 'r') as file:
            return file.read()

    def _make_chat_model(self, temperature: float):
        """Create a LangChain ChatOpenAI model instance for the configured provider."""
        # langchain_openai uses base_url; langchain_community uses openai_api_base & model_name
        if ChatOpenAI.__module__.startswith('langchain_openai'):
            if self.provider == 'deepseek':
                return ChatOpenAI(api_key=self.api_key, base_url="https://api.deepseek.com", model=self.model, temperature=temperature)
            else:  # openai
                return ChatOpenAI(api_key=self.api_key, model=self.model, temperature=temperature)
        else:
            if self.provider == 'deepseek':
                return ChatOpenAI(openai_api_key=self.api_key, openai_api_base="https://api.deepseek.com", model_name=self.model, temperature=temperature)
            else:  # openai
                return ChatOpenAI(openai_api_key=self.api_key, model_name=self.model, temperature=temperature)

    def call_llm(self, prompt, system_message: Optional[str] = None, temperature: float = 0.7) -> str:
        """Call LLM API with a prompt and return the result
        
        Args:
            prompt: The user prompt/message
            system_message: Optional system message to set context
            temperature: Sampling temperature (0.0 to 1.0)
        
        Returns:
            The generated text response from the model
        
        Raises:
            RuntimeError: If request fails
        """
        messages = []
        if system_message:
            messages.append(SystemMessage(content=system_message))
        messages.append(HumanMessage(content=prompt))

        chat = self._make_chat_model(temperature=temperature)
        result = chat.invoke(messages)

        if self.token_id:
            self.db.decrement_request_count(self.token_id)

        print(result.content)
        return result.content
    
if __name__ == "__main__":
    llm_service = LLMService("debate")
    llm_service.run_agent("你好")
           
