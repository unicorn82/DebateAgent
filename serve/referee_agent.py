import os
from re import U
from typing import Tuple, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from ConfigService import ConfigService
from llm_service import LLMService
from agent_service import DebateAgentService

# Load environment variables
load_dotenv()

class RefereeAgent:
    """Agent responsible for generating debate topics and managing debate flow"""
    
    def __init__(self):
        self.system_prompt = (
            "You are a debate coach. Produce concise, practical guidance with clear bullets."
        )
        # Default provider configuration
        self.default_temperature: float = 0.7
        self.config_service = ConfigService()
        self.role = 'referee'
        self.llm_service = DebateAgentService(user_role=self.role)
        self.judge_prompt_template = self.llm_service.read_prompt_template('judge_prompt_template.txt')
        
    

    
    def format_judge_prompt_template(self, topic: str, aff_options: str, neg_options: str, affirmative_statements: list[str], negative_statements: list[str], aff_final: str, neg_final: str) -> str:
        print("format_judge_prompt_template")
        print(self.judge_prompt_template)
        
        try:
            # Ensure parameters are not None and convert to strings
            topic = topic or ""
            aff_options = aff_options or ""
            neg_options = neg_options or ""
            aff_final = aff_final or ""
            neg_final = neg_final or ""
            
            # Ensure statements are lists and contain strings
            if not isinstance(affirmative_statements, list):
                affirmative_statements = []
            if not isinstance(negative_statements, list):
                negative_statements = []
                
            # Convert all items to strings and filter out None/empty
            aff_stmts = [str(stmt) for stmt in affirmative_statements if stmt]
            neg_stmts = [str(stmt) for stmt in negative_statements if stmt]
            
            return self.judge_prompt_template.format(
                topic=topic,
                affirmative_opinion=aff_options,
                negative_opinion=neg_options,
                affirmative_statements='\n'.join(aff_stmts),
                negative_statements='\n'.join(neg_stmts),
                affirmative_summary=aff_final,
                negative_summary=neg_final
            )
        except (KeyError, ValueError, AttributeError) as e:
            print(f"Error formatting judge prompt template: {e}")
            return f"Error formatting prompt: {str(e)}"
    
    

    def judge_debate(
        self, 
        topic: str,
        aff_options: str,
        neg_options: str,
        affirmative_statements: list[str],
        negative_statements: list[str],
        aff_final: str,
        neg_final: str,
        provider_id: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Tuple[str, Optional[int]]:
        """Judge the debate and return the result"""
        try:
            use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature
            judge_prompt = self.format_judge_prompt_template(topic, aff_options, neg_options, affirmative_statements, negative_statements, aff_final, neg_final)
            
            print("judge_prompt")
            print(judge_prompt)
            llm_service = DebateAgentService(user_role=self.role, provider_id=provider_id, token_id=token_id)
            judge_response, request_count = llm_service.run_workflow(
                judge_prompt,
                system_message=self.system_prompt,
                temperature=use_temperature
            )
            print(judge_response)
            return judge_response, request_count
            
        except Exception as e:
            # Return a properly formatted JSON error response
            error_response = {
                "winner": "ERROR",
                "reason": f"Failed to judge debate due to LLM service error: {str(e)}",
                "affirmative_score": 0,
                "negative_score": 0
            }
            return json.dumps(error_response), None
    
    def parse_judge_response(self, judge_response: str) -> dict:
        """Parse the judge response into a JSON object"""
        return json.loads(judge_response)