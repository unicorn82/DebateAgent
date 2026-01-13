"""
Debate Agent REST API

This module provides REST API endpoints for the debate agent system,
allowing clients to interact with affirmative agents, negative agents,
and referee agents through HTTP requests.
"""

from fastapi import FastAPI, HTTPException, Body, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from mangum import Mangum
import os
import logging
from typing import Optional
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
from DatabaseService import DatabaseService

db_service = DatabaseService()

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Debate Agent API",
    description="REST API for AI-powered debate system with affirmative, negative, and referee agents",
    version="1.0.0"
)
# handler = Mangum(app)
handler = Mangum(app, api_gateway_base_path="/default/debate-agent-backend")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://debate.weseekshop.com",
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of agents to speed up Lambda cold starts
_agents = {}

def get_agents():
    if not _agents:
        logger.info("Initializing agents (lazy load)...")
        _agents['affirmative'] = AffirmativeAgent()
        _agents['negative'] = NegativeAgent()
        _agents['referee'] = RefereeAgent()
        _agents['config'] = ConfigService()
    return _agents['affirmative'], _agents['negative'], _agents['referee'], _agents['config']


# ========================= Request/Response Models =========================

class TopicRequest(BaseModel):
    """Request model for topic-based operations"""
    topic: str = Field(..., description="The debate topic", min_length=1)
    provider_id: Optional[int] = Field(default=None, description="Optional provider ID")
    token: Optional[str] = Field(default=None, description="Access token")


class GenerateStatementRequest(BaseModel):
    """Request model for generating debate statements"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    affirmative_statements: List[str] = Field(default=[], description="Previous affirmative statements")
    negative_statements: List[str] = Field(default=[], description="Previous negative statements")
    context: str = Field(default="", description="Additional context for the statement")
    provider_id: Optional[int] = Field(default=None, description="Optional provider ID")
    token: Optional[str] = Field(default=None, description="Access token")


class GenerateRebuttalRequest(BaseModel):
    """Request model for generating rebuttals"""
    topic: str = Field(..., description="The debate topic")
    opponent_argument: str = Field(..., description="The opponent's argument to rebut")
    team_position: str = Field(..., description="Current team position/strategy")
    token: Optional[str] = Field(default=None, description="Access token")


class GenerateClosingRequest(BaseModel):
    """Request model for generating closing arguments"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    team_statements: List[str] = Field(default=[], description="Team's previous statements")
    opponent_statements: List[str] = Field(default=[], description="Opponent's previous statements")
    provider_id: Optional[int] = Field(default=None, description="Optional provider ID")
    token: Optional[str] = Field(default=None, description="Access token")


class JudgeDebateRequest(BaseModel):
    """Request model for judging a debate"""
    topic: str = Field(..., description="The debate topic")
    aff_options: str = Field(default="", description="Affirmative team options/position")
    neg_options: str = Field(default="", description="Negative team options/position")
    affirmative_statements: List[str] = Field(default=[], description="All affirmative statements")
    negative_statements: List[str] = Field(default=[], description="All negative statements")
    aff_final: str = Field(default="", description="Affirmative closing argument")
    neg_final: str = Field(default="", description="Negative closing argument")
    provider_id: Optional[int] = Field(default=None, description="Optional provider ID")
    token: Optional[str] = Field(default=None, description="Access token")


class StatementResponse(BaseModel):
    """Response model for generated statements"""
    statement: str = Field(..., description="The generated statement")
    status: str = Field(default="success", description="Status of the operation")
    request_count: Optional[int] = Field(default=None, description="Remaining request count")


class TopicsResponse(BaseModel):
    """Response model for generated topics"""
    affirmative_option: str = Field(..., description="Affirmative team option")
    negative_option: str = Field(..., description="Negative team option")
    status: str = Field(default="success", description="Status of the operation")


class JudgeResponse(BaseModel):
    """Response model for judge decision"""
    result: str = Field(..., description="The judge's decision and reasoning")
    status: str = Field(default="success", description="Status of the operation")
    request_count: Optional[int] = Field(default=None, description="Remaining request count")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    message: str
    version: str


# ========================= Helper Functions =========================

def validate_access_token(token: str = None, authorization: str = Header(None)) -> str:
    """Validate the access token against the database and return it"""
    # Try to get token from Authorization header if not in body
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Access token is required")

    if not db_service.validate_token(token):
        logger.warning(f"Invalid token attempt: {token}")
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    
    return token

# ========================= API Endpoints =========================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - API health check"""
    return HealthResponse(
        status="healthy",
        message="Debate Agent API is running",
        version="1.0.0"
    )


@app.get("/api/token/info")
async def get_token_info(token: str = None, authorization: str = Header(None)):
    """Get information about the access token, including remaining request count"""
    # Try to get token from Authorization header if not in body
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()
    elif token:
        token = token.strip()

    if not token:
        raise HTTPException(status_code=401, detail="Access token is required")

    token_data = db_service.get_token_data(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    
    # Convert Decimal to int/float for JSON serialization if needed
    # DynamoDB returns Decimal for numbers
    request_count = token_data.get("REQUEST_COUNT")
    if request_count is not None:
        request_count = int(request_count)

    return {
        "token_id": token_data.get("TOKEN_ID"),
        "status": token_data.get("STATUS"),
        "request_count": request_count,
        "email": token_data.get("EMAIL"),
        "created_at": token_data.get("CREATED_AT"),
        "ttl": int(token_data.get("TTL")) if token_data.get("TTL") else None
    }


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
async def generate_affirmative_option(request: TopicRequest, authorization: str = Header(None)):
    """Generate affirmative team options/position"""
    logger.info(f"generate_affirmative_option request: {request.topic}")
    token = validate_access_token(request.token, authorization)
    affirmative_agent, _, _, _ = get_agents()
    try:
        statement, request_count = affirmative_agent.generate_topics_from_input(request.topic, provider_id=request.provider_id, token_id=token)
        return StatementResponse(statement=statement, request_count=request_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative option: {str(e)}")


@app.post("/api/topics/negative", response_model=StatementResponse)
async def generate_negative_option(request: TopicRequest, authorization: str = Header(None)):
    """Generate negative team options/position"""
    logger.info(f"generate_negative_option request: {request.topic}")
    token = validate_access_token(request.token, authorization)
    _, negative_agent, _, _ = get_agents()
    try:
        statement, request_count = negative_agent.generate_topics_from_input(request.topic, provider_id=request.provider_id, token_id=token)
        return StatementResponse(statement=statement, request_count=request_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative option: {str(e)}")


# ========================= Affirmative Team Endpoints =========================

@app.post("/api/affirmative/statement", response_model=StatementResponse)
async def generate_affirmative_statement(request: GenerateStatementRequest, authorization: str = Header(None)):
    """
    Generate an affirmative team statement.
    
    This endpoint generates a new argument or statement for the affirmative team
    based on the topic, team options, and previous statements from both teams.
    """
    logger.info(f"generate_affirmative_statement request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    affirmative_agent, _, _, _ = get_agents()
    try:
        statement, status, request_count = affirmative_agent.generate_affirmative_statement(
            topic=request.topic,
            aff_options=request.aff_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            context=request.context,
            provider_id=request.provider_id,
            token_id=token
        )
        return StatementResponse(
            statement=statement,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative statement: {str(e)}")


@app.post("/api/affirmative/rebuttal", response_model=StatementResponse)
async def generate_affirmative_rebuttal(request: GenerateRebuttalRequest, authorization: str = Header(None)):
    """
    Generate an affirmative team rebuttal.
    
    This endpoint generates a rebuttal from the affirmative team against
    a specific argument made by the negative team.
    """
    logger.info(f"generate_affirmative_rebuttal request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    affirmative_agent, _, _, _ = get_agents()
    try:
        rebuttal, status, request_count = affirmative_agent.generate_rebuttal(
            topic=request.topic,
            opponent_argument=request.opponent_argument,
            team_position=request.team_position,
            token_id=token
        )
        return StatementResponse(
            statement=rebuttal,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative rebuttal: {str(e)}")


@app.post("/api/affirmative/closing", response_model=StatementResponse)
async def generate_affirmative_closing(request: GenerateClosingRequest, authorization: str = Header(None)):
    """
    Generate an affirmative team closing argument.
    
    This endpoint generates a comprehensive closing statement for the affirmative team,
    summarizing their position and addressing the negative team's arguments.
    """
    logger.info(f"generate_affirmative_closing request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    affirmative_agent, _, _, _ = get_agents()
    try:
        closing, status, request_count = affirmative_agent.generate_closing_argument(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            team_statements=request.team_statements,
            opponent_statements=request.opponent_statements,
            provider_id=request.provider_id,
            token_id=token
        )
        return StatementResponse(
            statement=closing,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate affirmative closing: {str(e)}")


# ========================= Negative Team Endpoints =========================

@app.post("/api/negative/statement", response_model=StatementResponse)
async def generate_negative_statement(request: GenerateStatementRequest, authorization: str = Header(None)):
    """
    Generate a negative team statement.
    
    This endpoint generates a new argument or statement for the negative team
    based on the topic, team options, and previous statements from both teams.
    """
    logger.info(f"generate_negative_statement request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    _, negative_agent, _, _ = get_agents()
    try:
        statement, status, request_count = negative_agent.generate_negative_statement(
            topic=request.topic,
            neg_options=request.neg_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            context=request.context,
            provider_id=request.provider_id,
            token_id=token
        )
        return StatementResponse(
            statement=statement,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative statement: {str(e)}")


@app.post("/api/negative/rebuttal", response_model=StatementResponse)
async def generate_negative_rebuttal(request: GenerateRebuttalRequest, authorization: str = Header(None)):
    """
    Generate a negative team rebuttal.
    
    This endpoint generates a rebuttal from the negative team against
    a specific argument made by the affirmative team.
    """
    logger.info(f"generate_negative_rebuttal request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    _, negative_agent, _, _ = get_agents()
    try:
        rebuttal, status, request_count = negative_agent.generate_rebuttal(
            topic=request.topic,
            opponent_argument=request.opponent_argument,
            team_position=request.team_position,
            token_id=token
        )
        return StatementResponse(
            statement=rebuttal,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative rebuttal: {str(e)}")


@app.post("/api/negative/closing", response_model=StatementResponse)
async def generate_negative_closing(request: GenerateClosingRequest, authorization: str = Header(None)):
    """
    Generate a negative team closing argument.
    
    This endpoint generates a comprehensive closing statement for the negative team,
    summarizing their position and addressing the affirmative team's arguments.
    """
    logger.info(f"generate_negative_closing request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    _, negative_agent, _, _ = get_agents()
    try:
        closing, status, request_count = negative_agent.generate_closing_argument(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            team_statements=request.team_statements,
            opponent_statements=request.opponent_statements,
            provider_id=request.provider_id,
            token_id=token
        )
        return StatementResponse(
            statement=closing,
            status=status,
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate negative closing: {str(e)}")


# ========================= Referee/Judge Endpoints =========================



@app.post("/api/judge/debate", response_model=JudgeResponse)
async def judge_debate(request: JudgeDebateRequest, authorization: str = Header(None)):
    """
    Judge a complete debate.
    
    This endpoint evaluates the entire debate, considering all statements,
    arguments, and closing statements from both teams, and returns a
    decision with detailed reasoning.
    """
    logger.info(f"judge_debate request: {request.model_dump()}")
    token = validate_access_token(request.token, authorization)
    _, _, referee_agent, _ = get_agents()
    try:
        result, request_count = referee_agent.judge_debate(
            topic=request.topic,
            aff_options=request.aff_options,
            neg_options=request.neg_options,
            affirmative_statements=request.affirmative_statements,
            negative_statements=request.negative_statements,
            aff_final=request.aff_final,
            neg_final=request.neg_final,
            provider_id=request.provider_id,
            token_id=token
        )
        return JudgeResponse(
            result=result,
            status="success",
            request_count=request_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to judge debate: {str(e)}")


# ========================= Configuration Endpoints =========================

@app.get("/api/config/temperature")
async def get_temperature():
    """Get the current temperature setting for AI generation"""
    _, _, _, config_service = get_agents()
    try:
        temperature = config_service.get_temperature()
        return {"temperature": temperature if temperature is not None else 0.7}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get temperature: {str(e)}")


@app.post("/api/config/temperature")
async def set_temperature(temperature: float = Body(..., embed=True)):
    """Set the temperature for AI generation (0.0 to 2.0)"""
    logger.info(f"set_temperature request: {temperature}")
    _, _, _, config_service = get_agents()
    try:
        if not 0.0 <= temperature <= 2.0:
            raise HTTPException(status_code=400, detail="Temperature must be between 0.0 and 2.0")
        config_service.set_temperature(temperature)
        return {"message": "Temperature updated successfully", "temperature": temperature}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set temperature: {str(e)}")


@app.get("/api/config/providers")
async def get_providers():
    """Get all available providers and models sorted by index"""
    _, _, _, config_service = get_agents()
    try:
        providers = config_service.list_providers()
        return {"providers": providers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list providers: {str(e)}")


# ========================= Main Entry Point =========================

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", "9000"))
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
