"""
Test client for Debate Agent REST API

This script demonstrates how to interact with the Debate Agent API
and run a complete debate programmatically.
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def check_api_health() -> bool:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Status: {data['status']}")
            print(f"✓ Version: {data['version']}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to connect to API: {e}")
        print(f"\nMake sure the API is running:")
        print(f"  cd serve")
        print(f"  python debate_api.py")
        return False


def generate_topics(topic: str) -> Dict[str, str]:
    """Generate affirmative and negative team options"""
    print(f"Generating team options for topic: '{topic}'")
    
    response = requests.post(
        f"{API_BASE}/api/topics/generate",
        json={"topic": topic}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✓ Affirmative Option:")
        print(f"  {data['affirmative_option']}\n")
        print(f"✓ Negative Option:")
        print(f"  {data['negative_option']}\n")
        return data
    else:
        print(f"✗ Failed to generate topics: {response.text}")
        return {}


def generate_statement(team: str, topic: str, aff_options: str, neg_options: str, 
                       aff_statements: list, neg_statements: list, context: str = "") -> str:
    """Generate a statement for a team"""
    endpoint = f"{API_BASE}/api/{team}/statement"
    
    payload = {
        "topic": topic,
        "aff_options": aff_options,
        "neg_options": neg_options,
        "affirmative_statements": aff_statements,
        "negative_statements": neg_statements,
        "context": context
    }
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()["statement"]
    else:
        print(f"✗ Failed to generate {team} statement: {response.text}")
        return ""


def generate_closing(team: str, topic: str, aff_options: str, neg_options: str,
                     team_statements: list, opponent_statements: list) -> str:
    """Generate a closing argument for a team"""
    endpoint = f"{API_BASE}/api/{team}/closing"
    
    payload = {
        "topic": topic,
        "aff_options": aff_options,
        "neg_options": neg_options,
        "team_statements": team_statements,
        "opponent_statements": opponent_statements
    }
    
    response = requests.post(endpoint, json=payload)
    
    if response.status_code == 200:
        return response.json()["statement"]
    else:
        print(f"✗ Failed to generate {team} closing: {response.text}")
        return ""


def judge_debate(topic: str, aff_options: str, neg_options: str,
                aff_statements: list, neg_statements: list,
                aff_final: str, neg_final: str) -> Dict[str, Any]:
    """Judge the debate and return the result"""
    payload = {
        "topic": topic,
        "aff_options": aff_options,
        "neg_options": neg_options,
        "affirmative_statements": aff_statements,
        "negative_statements": neg_statements,
        "aff_final": aff_final,
        "neg_final": neg_final
    }
    
    response = requests.post(f"{API_BASE}/api/judge/debate", json=payload)
    
    if response.status_code == 200:
        result = response.json()["result"]
        try:
            # Try to parse as JSON if it's a JSON string
            return json.loads(result)
        except:
            return {"result": result}
    else:
        print(f"✗ Failed to judge debate: {response.text}")
        return {}


def run_complete_debate(topic: str, num_rounds: int = 2):
    """Run a complete debate with multiple rounds"""
    
    print_section("DEBATE SETUP")
    
    # Generate team options
    topics = generate_topics(topic)
    if not topics:
        return
    
    aff_options = topics["affirmative_option"]
    neg_options = topics["negative_option"]
    
    # Storage for statements
    aff_statements = []
    neg_statements = []
    
    # Run debate rounds
    for round_num in range(1, num_rounds + 1):
        print_section(f"ROUND {round_num}")
        
        # Affirmative statement
        print(f"🔵 Affirmative Team - Round {round_num}:")
        context = f"Round {round_num} argument"
        aff_statement = generate_statement(
            "affirmative", topic, aff_options, neg_options,
            aff_statements, neg_statements, context
        )
        if aff_statement:
            print(f"  {aff_statement}\n")
            aff_statements.append(aff_statement)
        
        time.sleep(1)  # Brief pause between statements
        
        # Negative statement
        print(f"🔴 Negative Team - Round {round_num}:")
        neg_statement = generate_statement(
            "negative", topic, aff_options, neg_options,
            aff_statements, neg_statements, context
        )
        if neg_statement:
            print(f"  {neg_statement}\n")
            neg_statements.append(neg_statement)
        
        time.sleep(1)
    
    # Closing arguments
    print_section("CLOSING ARGUMENTS")
    
    print("🔵 Affirmative Team Closing:")
    aff_final = generate_closing(
        "affirmative", topic, aff_options, neg_options,
        aff_statements, neg_statements
    )
    if aff_final:
        print(f"  {aff_final}\n")
    
    time.sleep(1)
    
    print("🔴 Negative Team Closing:")
    neg_final = generate_closing(
        "negative", topic, aff_options, neg_options,
        neg_statements, aff_statements
    )
    if neg_final:
        print(f"  {neg_final}\n")
    
    # Judge the debate
    print_section("JUDGE'S DECISION")
    
    print("⚖️  Evaluating the debate...")
    result = judge_debate(
        topic, aff_options, neg_options,
        aff_statements, neg_statements,
        aff_final, neg_final
    )
    
    if result:
        print(f"\n{json.dumps(result, indent=2)}\n")
        
        # Try to extract winner if it's in the result
        if "winner" in result:
            winner = result["winner"]
            reason = result.get("reason", "No reason provided")
            print(f"🏆 Winner: {winner.upper()}")
            print(f"📝 Reason: {reason}")
            
            if "affirmative_score" in result and "negative_score" in result:
                print(f"\n📊 Scores:")
                print(f"   Affirmative: {result['affirmative_score']}")
                print(f"   Negative: {result['negative_score']}")


def main():
    """Main function to run the test client"""
    print_section("DEBATE AGENT API TEST CLIENT")
    
    # Check API health
    if not check_api_health():
        return
    
    # Example debate topics
    topics = [
        "Should artificial intelligence be regulated by governments?",
        "Is social media doing more harm than good?",
        "Should college education be free for all students?",
    ]
    
    print("\nAvailable debate topics:")
    for i, topic in enumerate(topics, 1):
        print(f"  {i}. {topic}")
    
    # For demo purposes, use the first topic
    selected_topic = topics[0]
    print(f"\n▶ Running debate on: '{selected_topic}'")
    
    # Run the complete debate
    run_complete_debate(selected_topic, num_rounds=2)
    
    print_section("DEBATE COMPLETE")
    print("Thank you for using the Debate Agent API!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDebate interrupted by user.")
    except Exception as e:
        print(f"\n\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
