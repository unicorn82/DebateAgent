"""
Debate Agent REST API

This module provides REST API endpoints for the debate agent system,
allowing clients to interact with affirmative agents, negative agents,
and referee agents through HTTP requests.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import debate agents
from affirmative_agent import AffirmativeAgent
from negative_agent import NegativeAgent
from referee_agent import RefereeAgent
from ConfigService import ConfigService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Debate Agent API",
    description="REST API for AI-powered debate system with affirmative, negative, and referee agents",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents (singleton pattern)
affirmative_agent = AffirmativeAgent()
negative_agent = NegativeAgent()
referee_agent = RefereeAgent()
config_service = ConfigService()


# ========================= Request/Response Models =========================

class TopicRequest(BaseModel):
    """Request model for topic-based operations"""
    topic: str = Field(..., description="The debate topic", min_length=1)


class GenerateStatementRequest(BaseModel):
    """Request model for generating debate statements"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    affirmative_statements: List[str] = Field(default=[], description="Previous affirmative statements")
    negative_statements: List[str] = Field(default=[], description="Previous negative statements")
    context: str = Field(default="", description="Additional context for the statement")


class GenerateRebuttalRequest(BaseModel):
    """Request model for generating rebuttals"""
    topic: str = Field(..., description="The debate topic")
    opponent_argument: str = Field(..., description="The opponent's argument to rebut")
    team_position: str = Field(..., description="Current team position/strategy")


class GenerateClosingRequest(BaseModel):
    """Request model for generating closing arguments"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    team_statements: List[str] = Field(default=[], description="Team's previous statements")
    opponent_statements: List[str] = Field(default=[], description="Opponent's previous statements")


class JudgeDebateRequest(BaseModel):
    """Request model for judging a debate"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    affirmative_statements: List[str] = Field(default=[], description="All affirmative statements")
    negative_statements: List[str] = Field(default=[], description="All negative statements")
    aff_final: str = Field(default="", description="Affirmative closing argument")
    neg_final: str = Field(default="", description="Negative closing argument")


class StatementResponse(BaseModel):
    """Response model for generated statements"""
    statement: str = Field(..., description="The generated statement")
    status: str = Field(default="success", description="Status of the operation")


class TopicsResponse(BaseModel):
    """Response model for generated topics"""
    affirmative_option: str = Field(..., description="Affirmative team option")
    negative_option: str = Field(..., description="Negative team option")
    status: str = Field(default="success", description="Status of the operation")


class JudgeResponse(BaseModel):
    """Response model for judge decision"""
    result: str = Field(..., description="The judge's decision and reasoning")
    status: str = Field(default="success", description="Status of the operation")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str
    version: str


# ========================= API Endpoints =========================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return HealthResponse(
        status="healthy",
        message="Debate Agent API is running",
        version="1.0.0"
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        version="1.0.0"
    )


# ========================= Topic Generation Endpoints =========================



@app.post("/api/topics/affirmative", response_model=StatementResponse)
async def generate_affirmative_option(request: TopicRequest):
    """
    Generate only the affirmative team option for a given topic.
    """
    logger.info(f"generate_affirmative_option request: {request.model_dump()}")
    try:
        aff_option = affirmative_agent.generate_topics_from_input(request.topic)
        return StatementResponse(
            statement=aff_option,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative option: {str(e)}")


@app.post("/api/topics/negative", response_model=StatementResponse)
async def generate_negative_option(request: TopicRequest):
    """
    Generate only the negative team option for a given topic.
    """
    logger.info(f"generate_negative_option request: {request.model_dump()}")
    try:
        neg_option = negative_agent.generate_topics_from_input(request.topic)
        return StatementResponse(
            statement=neg_option,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative option: {str(e)}")


# ========================= Affirmative Team Endpoints =========================

@app.post("/api/affirmative/statement", response_model=StatementResponse)
async def generate_affirmative_statement(request: GenerateStatementRequest):
    """
    Generate an affirmative team statement.
    
    This endpoint generates a new argument or statement for the affirmative team
    based on the topic, team options, and previous statements from both teams.
    """
    logger.info(f"generate_affirmative_statement request: {request.model_dump()}")
    try:
        statement, status = affirmative_agent.generate_affirmative_statement(
            topic=request.topic,
            aff_options=request.aff_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            context=request.context
        )
        return StatementResponse(
            statement=statement,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative statement: {str(e)}")


@app.post("/api/affirmative/rebuttal", response_model=StatementResponse)
async def generate_affirmative_rebuttal(request: GenerateRebuttalRequest):
    """
    Generate an affirmative team rebuttal.
    
    This endpoint generates a rebuttal from the affirmative team against
    a specific argument made by the negative team.
    """
    logger.info(f"generate_affirmative_rebuttal request: {request.model_dump()}")
    try:
        rebuttal, status = affirmative_agent.generate_rebuttal(
            topic=request.topic,
            opponent_argument=request.opponent_argument,
            team_position=request.team_position
        )
        return StatementResponse(
            statement=rebuttal,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative rebuttal: {str(e)}")


@app.post("/api/affirmative/closing", response_model=StatementResponse)
async def generate_affirmative_closing(request: GenerateClosingRequest):
    """
    Generate an affirmative team closing argument.
    
    This endpoint generates a comprehensive closing statement for the affirmative team,
    summarizing their position and addressing the negative team's arguments.
    """
    logger.info(f"generate_affirmative_closing request: {request.model_dump()}")
    try:
        closing, status = affirmative_agent.generate_closing_argument(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            team_statements=request.team_statements,
            opponent_statements=request.opponent_statements
        )
        return StatementResponse(
            statement=closing,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative closing: {str(e)}")


# ========================= Negative Team Endpoints =========================

@app.post("/api/negative/statement", response_model=StatementResponse)
async def generate_negative_statement(request: GenerateStatementRequest):
    """
    Generate a negative team statement.
    
    This endpoint generates a new argument or statement for the negative team
    based on the topic, team options, and previous statements from both teams.
    """
    logger.info(f"generate_negative_statement request: {request.model_dump()}")
    try:
        statement, status = negative_agent.generate_negative_statement(
            topic=request.topic,
            neg_options=request.neg_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            context=request.context
        )
        return StatementResponse(
            statement=statement,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative statement: {str(e)}")


@app.post("/api/negative/rebuttal", response_model=StatementResponse)
async def generate_negative_rebuttal(request: GenerateRebuttalRequest):
    """
    Generate a negative team rebuttal.
    
    This endpoint generates a rebuttal from the negative team against
    a specific argument made by the affirmative team.
    """
    logger.info(f"generate_negative_rebuttal request: {request.model_dump()}")
    try:
        rebuttal, status = negative_agent.generate_rebuttal(
            topic=request.topic,
            opponent_argument=request.opponent_argument,
            team_position=request.team_position
        )
        return StatementResponse(
            statement=rebuttal,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative rebuttal: {str(e)}")


@app.post("/api/negative/closing", response_model=StatementResponse)
async def generate_negative_closing(request: GenerateClosingRequest):
    """
    Generate a negative team closing argument.
    
    This endpoint generates a comprehensive closing statement for the negative team,
    summarizing their position and addressing the affirmative team's arguments.
    """
    logger.info(f"generate_negative_closing request: {request.model_dump()}")
    try:
        closing, status = negative_agent.generate_closing_argument(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            team_statements=request.team_statements,
            opponent_statements=request.opponent_statements
        )
        return StatementResponse(
            statement=closing,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative closing: {str(e)}")


# ========================= Referee/Judge Endpoints =========================



@app.post("/api/judge/debate", response_model=JudgeResponse)
async def judge_debate(request: JudgeDebateRequest):
    """
    Judge a complete debate.
    
    This endpoint evaluates the entire debate, considering all statements,
    arguments, and closing statements from both teams, and returns a
    decision with detailed reasoning.
    """
    logger.info(f"judge_debate request: {request.model_dump()}")
    try:
        result = referee_agent.judge_debate(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            aff_final=request.aff_final,
            neg_final=request.neg_final
        )
        return JudgeResponse(
            result=result,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to judge debate: {str(e)}")


# ========================= Configuration Endpoints =========================

@app.get("/api/config/temperature")
async def get_temperature():
    """Get the current temperature setting for AI generation"""
    try:
        temperature = config_service.get_temperature()
        return {"temperature": temperature if temperature is not None else 0.7}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get temperature: {str(e)}")


@app.post("/api/config/temperature")
async def set_temperature(temperature: float = Body(..., embed=True)):
    """Set the temperature for AI generation (0.0 to 2.0)"""
    logger.info(f"set_temperature request: {temperature}")
    try:
        if not 0.0 <= temperature <= 2.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 0.0 and 2.0")
        config_service.set_temperature(temperature)
        return {"message": "Temperature updated successfully", "temperature": temperature}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set temperature: {str(e)}")


# ========================= Main Entry Point =========================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", "8000"))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"Starting Debate Agent API on {host}:{port}")
    print(f"API Documentation available at http://{host}:{port}/docs")
    print(f"Alternative docs at http://{host}:{port}/redoc")
    
    uvicorn.run(
        "debate_api:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
