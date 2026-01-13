import os
from typing import Tuple, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from ConfigService import ConfigService
from llm_service import LLMService
from agent_service import DebateAgentService

# Load environment variables
load_dotenv()

class AffirmativeAgent:
    """Agent responsible for generating affirmative team statements and arguments"""
    
    def __init__(self):
        self.system_prompt = (
            "You are a skilled debater on the affirmative team. "
            "Provide strong, logical arguments that support the given position. "
            "Be persuasive, factual, and structured in your responses. "
            "Stance: Affirmative (Pro) "
            "Role: Affirmative Team Member "
            "Task: Generate a strong, persuasive argument supporting the affirmative position on this topic. "
            "The statement should: "
            "- Be clear and well-structured "
            "- Include logical reasoning and evidence "
            "- Address potential counterarguments "
            "- Be compelling and persuasive "
            "- Stay focused on supporting the affirmative stance "
        )
        # Default provider configuration
        self.default_temperature: float = 0.7
        self.config_service = ConfigService()
        self.role = 'affirmative'
        self.stance = 'Affirmative (support the topic)'
        
        self.llm_service = DebateAgentService(user_role=self.role)
        self.topic_prompt_template = self.llm_service.read_prompt_template('topic_prompt_template.txt')
        self.prompt_template = self.llm_service.read_prompt_template('affirmative_prompt_template.txt')
        self.summary_prompt_template = self.llm_service.read_prompt_template('summarize_prompt_template.txt')
    
    # function to format prompt template
    def format_prompt_template(self, topic: str, aff_options: str, affirmative_statements: list[str], negative_statements: list[str]) -> str:
        return self.prompt_template.format(
            topic=topic,
            aff_options=aff_options,
            affirmative_statements='\n'.join(affirmative_statements),
            negative_statements='\n'.join(negative_statements)
        )

    def format_prompt_topic(self, topic: str) -> str:
        return self.topic_prompt_template.format(
            topic=topic,
            stance=self.stance,
            role=self.role
        )
    
    
    def generate_topics_from_input(
        self, 
        topic: str,
        provider_id: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Tuple[str, Optional[int]]:
        """Generate affirmative and negative topics directly into team textboxes
        
        Args:
            topic: The debate topic
        """
        if not topic or not topic.strip():
            return "", "", "Enter a topic first."

        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature

        try:
            # Generate affirmative arguments
            llm_service = DebateAgentService(user_role=self.role, provider_id=provider_id, token_id=token_id)
            aff_topic, request_count = llm_service.run_workflow(
                self.format_prompt_topic(topic),
                system_message=self.system_prompt,
                temperature=use_temperature
            )

    
            
            return aff_topic, request_count
            
        except Exception as e:
            raise e



    def _prompt_rebuttal(self, topic: str, opponent_argument: str, team_position: str) -> str:
        """Generate prompt for rebuttal against negative team"""
        return f"""Topic: "{topic}"
Your Team Position: {team_position}
Opponent's Argument: "{opponent_argument}"

Task: Generate a strong rebuttal that:
- Directly addresses the opponent's key points
- Identifies weaknesses in their argument
- Reinforces your affirmative position
- Provides counter-evidence or reasoning
- Maintains a respectful but firm tone

Provide your rebuttal:"""

  

    def generate_affirmative_statement(
        self, 
        topic: str,
        aff_options: str,
        affirmative_statements: list[str],
        negative_statements: list[str],
        context: str = "",
        provider_id: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """Generate an affirmative team statement
        
        Args:
            topic: The debate topic
            aff_options: Affirmative team options
            affirmative_statements: List of existing affirmative statements
            negative_statements: List of existing negative statements
            context: Additional context or team strategy
            
        Returns:
            Tuple of (generated_statement, status_message)
        """
        if not topic or not topic.strip():
            return "", "Enter a topic first."
    
        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature
    
        try:
            # Generate affirmative statement - FIXED: Pass all required arguments
            llm_service = DebateAgentService(user_role=self.role, provider_id=provider_id, token_id=token_id)
            statement, request_count = llm_service.run_workflow(
                self.format_prompt_template(topic, aff_options, affirmative_statements, negative_statements),
                system_message=self.system_prompt,
                temperature=use_temperature
            )
            
            status = "Affirmative statement generated successfully."
            return statement, status, request_count
            
        except Exception as e:
            return "", f"Error generating affirmative statement: {e}", None

    

    def generate_rebuttal(
        self,
        topic: str,
        opponent_argument: str,
        team_position: str,
        token_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """Generate a rebuttal against the negative team
        
        Args:
            topic: The debate topic
            opponent_argument: The negative team's argument to rebut
            team_position: Current affirmative team position/strategy
            
        Returns:
            Tuple of (generated_rebuttal, status_message)
        """
        if not all([topic.strip(), opponent_argument.strip()]):
            return "", "Topic and opponent argument are required."

        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature

        try:
            # Generate rebuttal
            llm_service = DebateAgentService(user_role=self.role, token_id=token_id)
            rebuttal, request_count = llm_service.run_workflow(
                self._prompt_rebuttal(topic, opponent_argument, team_position),
                system_message=self.system_prompt,
                temperature=use_temperature
            )
            
            status = "Rebuttal generated successfully."
            return rebuttal, status, request_count
            
        except Exception as e:
            return "", f"Error generating rebuttal: {e}", None

    def format_summary_prompt_template(self, topic: str, team_option: str, team_statements: list[str], opponent_statements: list[str]) -> str:
        return self.summary_prompt_template.format(
            topic=topic,
            aff_options=team_option,
            team_statements='\n'.join(team_statements),
            opponent_statements='\n'.join(opponent_statements)
        )

    def generate_closing_argument(
        self,
        topic: str,
        aff_options: str,
        neg_options: str,
        team_statements: list[str],
        opponent_statements: list[str],
        provider_id: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """Generate a closing argument for the affirmative team
        
        Args:
            topic: The debate topic
            team_arguments: List of previous affirmative arguments
            opponent_arguments: List of negative team arguments (optional)
            
        Returns:
            Tuple of (generated_closing, status_message)
        """
        if not topic.strip() or not team_statements:
            return "", "Topic and team arguments are required."

        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature

        closing_prompt = self.format_summary_prompt_template(topic, aff_options, team_statements, opponent_statements)

        print(closing_prompt)
        
        try:
            # Generate closing argument
            llm_service = DebateAgentService(user_role=self.role, provider_id=provider_id, token_id=token_id)
            closing, request_count = llm_service.run_workflow(
                closing_prompt,
                system_message=self.system_prompt,
                temperature=use_temperature
            )
            
            status = "Closing argument generated successfully."
            return closing, status, request_count
            
        except Exception as e:
            return "", f"Error generating closing argument: {e}", None


    def main(self):
        topic = "Climate Change"
        import asyncio
        from autogen_agentchat.agents import AssistantAgent
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        async def main() -> None:
            model_client = OpenAIChatCompletionClient(model="gpt-4.1")
            agent = AssistantAgent("assistant", model_client=model_client)
            print(await agent.run(task="Say 'Hello World!'"))
            await model_client.close()

        asyncio.run(main())

if __name__ == "__main__":
    agent = AffirmativeAgent()
    agent.main()
