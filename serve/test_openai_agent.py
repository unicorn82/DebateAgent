import sys
import os
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

# Add the parent directory to sys.path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from serve.ConfigService import ConfigService
from serve.agent_service import DebateAgentService

def test_openai_agent():
    print("Testing OpenAI Agent Integration...")
    
    # 1. Configure the service
    config_service = ConfigService()
    
    # Debug: Print loaded providers
    print("Loaded providers:", config_service.providers)
    
    # We expect PROVIDER2 to be openai based on .env
    openai_provider_id = 2
    
    # Verify provider 2 exists and is openai
    if openai_provider_id not in config_service.providers:
        print(f"Error: Provider {openai_provider_id} not found. Please ensure .env has PROVIDER2 defined.")
        return

    provider_data = config_service.providers[openai_provider_id]
    if provider_data["provider"] != "openai":
        print(f"Warning: Provider {openai_provider_id} is {provider_data['provider']}, expected 'openai'.")

    # Set the role to use OpenAI
    test_role = "openai_tester"
    config_service.set_role_provider(test_role, openai_provider_id)
    print(f"Mapped role '{test_role}' to provider ID {openai_provider_id}")
    
    # 2. Initialize Agent
    try:
        agent = DebateAgentService(user_role=test_role)
        print(f"Agent initialized successfully.")
        print(f"  Provider: {agent.provider}")
        print(f"  Model: {agent.model_name}")
        
        if agent.provider != "openai":
            print("  WARNING: Agent is not using openai provider!")
            
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Run Workflow
    prompt = "Explain how AI works in a few words"
    print(f"\nRunning workflow with prompt: '{prompt}'")
    
    try:
        result = agent.run_workflow(prompt)
        print("\n" + "="*30)
        print("Workflow Result:")
        print(result)
        print("="*30)
        print("\nTest Passed!")
    except Exception as e:
        print(f"\nTest Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_agent()
