import os
from typing import Optional, List, Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class LLMService:
    """Service for calling OpenAI and other LLM providers"""
    
    def __init__(self, role:str):
       
        self.default_timeout = 60
        #convert role to uppercase
        self.role = role.upper()
        self.llm_client = None

        print("role="+self.role)

        if os.getenv(self.role+'_PROVIDER') == 'deepseek':
            self.llm_client = OpenAI(api_key=os.getenv(self.role+'_API_KEY'), base_url="https://api.deepseek.com")
        elif os.getenv(self.role+'_PROVIDER') == 'openai':
            self.llm_client = OpenAI(api_key=os.getenv(self.role+'_API_KEY'))
        else:
            raise ValueError(f"Provider {os.getenv(self.role+'_PROVIDER')} not supported")
        self.model = os.getenv(self.role+'_MODEL')

     # function to read prompt template from file
    def read_prompt_template(self, filename: str) -> str:
        with open(filename, 'r') as file:
            return file.read()


    def call_llm(self, prompt, system_message: Optional[str] = None, temperature: float = 0.7) -> str:
        """Call LLM API with a prompt and return the result
        
        Args:
            prompt: The user prompt/message
            system_message: Optional system message to set context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            api_key: Optional API key override
            timeout: Request timeout in seconds
            
        Returns:
            The generated text response from OpenAI
            
        Raises:
            RuntimeError: If API key is missing or request fails
        """
        
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})    
      

        stream = self.llm_client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
        
            temperature=temperature
        )

        print(stream.choices[0].message.content)

        return stream.choices[0].message.content
    
   
           
