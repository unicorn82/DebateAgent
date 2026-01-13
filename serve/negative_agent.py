import os
from typing import Tuple, Optional, List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from ConfigService import ConfigService
from llm_service import LLMService
from agent_service import DebateAgentService

# Load environment variables
load_dotenv()

class NegativeAgent:
    """Agent responsible for generating negative team statements and arguments"""
    
    def __init__(self):
        self.system_prompt = (
            "You are a skilled debater on the negative team. "
            "Provide strong, logical arguments that oppose the given position. "
            "Be analytical, critical, and structured in identifying flaws and counterpoints. "
            "Focus on evidence-based reasoning and logical fallacies in opposing arguments. "
            "Stance: Negative (Con) "
            "Role: Negative Team Member "
            "Task: Generate a strong, persuasive argument opposing the given topic. "
            "The statement should: "
            "- Be clear and well-structured "
            "- Include logical reasoning and evidence "
            "- Identify potential problems or flaws with the affirmative position "
            "- Present alternative viewpoints or solutions "
            "- Be compelling and persuasive "
            "- Stay focused on opposing the topic "
        )
        # Default provider configuration
        self.default_temperature: float = 0.7
        
        self.config_service = ConfigService()
        self.role = 'negative'
        self.stance = 'Negative (oppose the topic)'
        self.llm_service = DebateAgentService(user_role=self.role)
        self.topic_prompt_template = self.llm_service.read_prompt_template('topic_prompt_template.txt')
        self.prompt_template = self.llm_service.read_prompt_template('negative_prompt_template.txt')
        self.summary_prompt_template = self.llm_service.read_prompt_template('summarize_prompt_template.txt')

   


    # function to format prompt template
    def format_prompt_template(self, topic: str, neg_options: str, affirmative_statements: list[str], negative_statements: list[str]) -> str:
        return self.prompt_template.format(
            topic=topic,
            neg_options=neg_options,
            affirmative_statements='\n'.join(affirmative_statements),
            negative_statements='\n'.join(negative_statements)
        )

    def format_prompt_topic(self, topic: str) -> str:
        """Generate prompt for team options"""
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

    def generate_negative_statement(
        self, 
        topic: str,
        neg_options: str,
        affirmative_statements: list[str],
        negative_statements: list[str],
        context: str = "",
        provider_id: Optional[int] = None,
        token_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """Generate a negative team statement
        
        Args:
            topic: The debate topic
            neg_options: The negative team options
            affirmative_statements: The affirmative team statements
            negative_statements: The negative team statements
            context: Additional context or team strategy
            
        Returns:
            Tuple of (generated_statement, status_message)
        """
        if not topic or not topic.strip():
            return "", "Enter a topic first."

        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature

        try:
            # Generate negative statement
            llm_service = DebateAgentService(user_role=self.role, provider_id=provider_id, token_id=token_id)
            statement, request_count = llm_service.run_workflow(
               self.format_prompt_template(topic, neg_options, affirmative_statements, negative_statements),
               system_message=self.system_prompt,
               temperature=use_temperature
            )
            
            status = "Negative statement generated successfully."
            return statement, status, request_count
            
        except Exception as e:
            return "", f"Error generating negative statement: {e}", None

    def generate_rebuttal(
        self,
        topic: str,
        opponent_argument: str,
        team_position: str,
        token_id: Optional[str] = None
    ) -> Tuple[str, str, Optional[int]]:
        """Generate a rebuttal against the affirmative team
        
        Args:
            topic: The debate topic
            opponent_argument: The affirmative team's argument to rebut
            team_position: Current negative team position/strategy
            
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

    def format_summary_prompt_template(self, topic: str, team_options: str, team_statements: list[str], opponent_statements: list[str]) -> str:
        return self.summary_prompt_template.format(
            topic=topic,
            aff_options=team_options,
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

        closing_prompt = self.format_summary_prompt_template(topic, neg_options, team_statements, opponent_statements)
       
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

    def analyze_opponent_weakness(
        self,
        topic: str,
        opponent_arguments: List[str],
        token_id: Optional[str] = None
    ) -> Tuple[str, str]:
        """Analyze opponent's arguments to identify weaknesses
        
        Args:
            topic: The debate topic
            opponent_arguments: List of affirmative team arguments to analyze
            
        Returns:
            Tuple of (analysis_result, status_message)
        """
        if not topic.strip() or not opponent_arguments:
            return "", "Topic and opponent arguments are required."

        # Get configuration from ConfigService
        use_temperature = self.config_service.get_temperature() if self.config_service.get_temperature() is not None else self.default_temperature

        # Build context from opponent arguments
        opponent_context = "\n".join([f"- {arg}" for arg in opponent_arguments if arg.strip()])

        analysis_prompt = f"""Topic: "{topic}"
Role: Negative Team - Strategic Analysis

Opponent's arguments to analyze:
{opponent_context}

Task: Analyze the opponent's arguments and identify:
- Logical fallacies or weak reasoning
- Lack of evidence or questionable sources
- Contradictions within their position
- Unaddressed consequences or risks
- Alternative interpretations of their evidence
- Strategic vulnerabilities to exploit

Provide your strategic analysis:"""

        try:
            # Generate analysis
            llm_service = DebateAgentService(user_role=self.role, token_id=token_id)
            analysis = llm_service.run_workflow(
                analysis_prompt,
                system_message=self.system_prompt,
                temperature=use_temperature
            )
            
            status = "Opponent analysis completed successfully."
            return analysis, status
            
        except Exception as e:
            return "", f"Error analyzing opponent arguments: {e}"