import os
import json
import tempfile
from typing import List, Dict, Tuple
from dotenv import load_dotenv

import gradio as gr
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from referee_agent import RefereeAgent
from ConfigService import ConfigService
from affirmative_agent import AffirmativeAgent
from negative_agent import NegativeAgent




# ----------------------------- Prompts -----------------------------


def prompt_judge(topic: str, aff_points: str, neg_points: str, aff_rounds: List[str], neg_rounds: List[str],
                 aff_summary: str, neg_summary: str) -> str:
    transcript = []
    transcript.append(f"TOPIC: {topic}\n")
    transcript.append("=== AFFIRMATIVE: TEAM OPTIONS ===\n" + aff_points.strip())
    transcript.append("=== NEGATIVE: TEAM OPTIONS ===\n" + neg_points.strip())

    def _group_rounds(rounds: List[str], side: str):
        for i, text in enumerate(rounds, start=1):
            transcript.append(f"--- {side} Round {i} ---\n{text.strip() if text else ''}")

    # rounds list comes as [m1r1, m2r1, m3r1, m1r2, m2r2, m3r2, m1r3, m2r3, m3r3]
    def _to_round_chunks(lst: List[str]) -> List[str]:
        out = []
        for round_i in range(3):
            base = round_i * 3
            r = []
            for m in range(3):
                label = f"Member {m+1}"
                r.append(f"{label}: {lst[base + m].strip() if base + m < len(lst) and lst[base+m] else ''}")
            out.append("\n".join(r))
        return out

    aff_chunks = _to_round_chunks(aff_rounds)
    neg_chunks = _to_round_chunks(neg_rounds)

    _group_rounds(aff_chunks, "AFFIRMATIVE")
    _group_rounds(neg_chunks, "NEGATIVE")

    transcript.append("=== AFFIRMATIVE FINAL SUMMARY ===\n" + (aff_summary or "").strip())
    transcript.append("=== NEGATIVE FINAL SUMMARY ===\n" + (neg_summary or "").strip())

    joined = "\n\n".join(transcript)

    return f"""Act as an impartial debate judge for a formal, civil debate.

Criteria (score holistically):
- Clarity & structure
- Use of evidence / reasoning
- Rebuttal quality and engagement with the other side
- Cohesion across team members
- Final summary strength

Return STRICT JSON ONLY with this schema (no extra text):
{{
  "winner": "affirmative" | "negative" | "tie",
  "reason": "<=150 words explaining your decision>",
  "scores": {{
    "affirmative": {{"argument": 0-10, "rebuttal": 0-10, "evidence": 0-10, "organization": 0-10}},
    "negative": {{"argument": 0-10, "rebuttal": 0-10, "evidence": 0-10, "organization": 0-10}}
  }},
  "suggestions": {{
    "affirmative": "one short paragraph to improve",
    "negative": "one short paragraph to improve"
  }}
}}

Transcript:
{joined}
"""



# Add this function after the on_judge function (around line 230)
def on_generate_topics(topic: str):
    """Generate debate topics using RefereeAgent"""
    if not topic.strip():
        return "", "", "⚠️ Please enter a debate topic first."
    
    try:
        # Configure the referee agent with default settings
       
        
        # Generate topics using RefereeAgent
        aff_result, neg_result, status = referee_agent.generate_topics_from_input(topic)
        
        return aff_result, neg_result, f"✅ {status}"
        
    except Exception as e:
        error_msg = f"❌ Error generating topics: {str(e)}"
        return "", "", error_msg

def on_judge(topic: str, aff_options: str, neg_options: str,
            aff_final: str, neg_final: str, current_state: dict):
    """Judge the debate and generate results."""
    if not topic.strip():
        return "⚠️ Please enter a debate topic first."

    print("on judge")

    
    affirmative_statements = []
    for textbox_id_key, value in current_state.items():
        if textbox_id_key.startswith('a') and value and value.strip():
            affirmative_statements.append(value)
    
    # collect all negative statements
    negative_statements = []
    for textbox_id_key, value in current_state.items():
        if textbox_id_key.startswith('n') and value and value.strip():
            negative_statements.append(value)
        
    try:
        # judge_response = referee_agent.judge_debate(topic, aff_options, neg_options, affirmative_statements, negative_statements, aff_final, neg_final)
        judge_response = """{    
  "winner": "NEGATIVE",
  "reason": "The negative's meta-analysis (Cooper et al., 2006) provides robust evidence for homework's academic benefits, outweighing the affirmative's stress claims which the negative successfully refuted as non-unique through Fernández-Alonso et al. (2015). On inequality, the negative's voter demonstrating homework programs improve scores by 12% in low-income schools (Kraft & Monti-Nussbaum, 2021) turns the affirmative's equity argument, showing banning homework harms disadvantaged students. The negative's impacts of irreversible academic decay and worsened inequality outweigh the affirmative's solvable stress concerns.",
  "affirmative_score": 18,
  "negative_score": 22
}"""
        
       
        # Clean the response to handle potential formatting issues
        cleaned_response = judge_response.strip()
        
        # Try to extract JSON from the response if it contains extra text
        import re
        json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if json_match:
            json_str = json_match.group()
        else:
            json_str = cleaned_response
        
        # Parse the JSON with better error handling
        try:
            result = json.loads(json_str)
        except json.JSONDecodeError as json_error:
            # If JSON parsing fails, try to fix common issues
            # Replace problematic quotes and escape sequences
            fixed_json = json_str.replace('\\"', '"').replace('\'', '"')
            try:
                result = json.loads(fixed_json)
            except json.JSONDecodeError:
                return f"❌ Error parsing judge response: {str(json_error)}\n\nRaw response: {judge_response}"
        
        winner = result.get("winner", "unknown")
        reason = result.get("reason", "No reason provided")
        aff_score = result.get("affirmative_score", "N/A")
        neg_score = result.get("negative_score", "N/A")
        print(winner)
        print(reason)
        print(aff_score)
        print(neg_score)
        
        # Format winner display with celebration
        winner_text = f"🏆 {winner.upper()} TEAM WINS! 🎉"
        
        # Format scores
        aff_score_text = f"{aff_score}/25"
        neg_score_text = f"{neg_score}/25"
        
        # Create transcript file
        transcript_content = f"""DEBATE TRANSCRIPT
=================

Topic: {topic}

Affirmative Team Options:
{aff_options}

Negative Team Options:
{neg_options}

Affirmative Statements:
{chr(10).join(f"{i+1}. {stmt}" for i, stmt in enumerate(affirmative_statements))}

Negative Statements:
{chr(10).join(f"{i+1}. {stmt}" for i, stmt in enumerate(negative_statements))}

Affirmative Final Summary:
{aff_final}

Negative Final Summary:
{neg_final}

JUDGE DECISION:
Winner: {winner}
Affirmative Score: {aff_score}/25
Negative Score: {neg_score}/25
Reason: {reason}
"""
        
        # Save transcript to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(transcript_content)
            temp_file_path = f.name
        
        return winner_text, aff_score_text, neg_score_text, reason, temp_file_path
        
    except Exception as e:
        error_msg = f"❌ Error during judging: {str(e)}"
        return error_msg, "0", "0", "An error occurred during judging.", None



# ----------------------------- UI Layout -----------------------------


# Load environment variables from .env file
load_dotenv()

# Create service instances
referee_agent = RefereeAgent()
config_service = ConfigService()
affirmative_agent = AffirmativeAgent()
negative_agent = NegativeAgent()



# Add at the top of your Blocks context
with gr.Blocks(title="Debate App", theme=gr.themes.Soft()) as demo:
    # Create a state to store current textbox values
    textbox_state = gr.State({})
    
    gr.Markdown("# 🗣️ Debate App n"
                "Enter a topic, auto-generate team options, run 3 rounds (3 members per team), "
                "write final summaries, then have an AI judge pick a winner.")

    with gr.Row():
        temperature = gr.Slider(0.0, 1.2, value=0.7, step=0.1, label="Temperature")
        num_rounds = gr.Dropdown([1, 2, 3], value=3, label="Number of Rounds")

    with gr.Row():
        # topic = gr.Textbox(label="Debate Topic", placeholder="e.g., Should homework be banned in middle schools?", lines=3)
        topic = gr.Textbox(label="Debate Topic", placeholder="e.g., Should homework be banned in middle schools?", lines=3, value="")
    # with gr.Row():
    #     generate_topic_btn = gr.Button("🎯 Generate Topics", variant="secondary")
  
        
    tip_box = gr.Markdown()

    with gr.Row():
        generate_topic_btn = gr.Button("✨ Generate Team Options (AI)", variant="primary")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## ✅ Affirmative Team")
            aff_options = gr.Textbox(lines=8, label="Affirmative Team Options (AI-generated, editable)")
        with gr.Column():
            gr.Markdown("## ❌ Negative Team")
            neg_options = gr.Textbox(lines=8, label="Negative Team Options (AI-generated, editable)")

    gr.Markdown("---")
    
    # Store textboxes and buttons for dynamic access
    round_textboxes = {}
    ai_buttons = {}
    
    # Round 1 (always visible)
    gr.Markdown("### 🔁 Round 1")
    with gr.Row():
        with gr.Column():
            gr.Markdown("**Affirmative Team**")
            # Member 1
            with gr.Row():
                gr.Markdown("Member 1")
                ai_buttons['a_m1_r1'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
            round_textboxes['a_m1_r1'] = gr.Textbox(lines=4, show_label=False)
            
            
        with gr.Column():
            gr.Markdown("**Negative Team**")
            # Member 1
            with gr.Row():
                gr.Markdown("Member 1")
                ai_buttons['n_m1_r1'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
            round_textboxes['n_m1_r1'] = gr.Textbox(lines=4, show_label=False)

    # Round 2 (conditionally visible)
    with gr.Group(visible=True) as round2_group:
        gr.Markdown("### 🔁 Round 2")
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Affirmative Team**")
                # Member 1
                with gr.Row():
                    gr.Markdown("Member 1")
                    ai_buttons['a_m1_r2'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
                round_textboxes['a_m1_r2'] = gr.Textbox(lines=4, show_label=False)
                
            
                
            with gr.Column():
                gr.Markdown("**Negative Team**")
                # Member 1
                with gr.Row():
                    gr.Markdown("Member 1")
                    ai_buttons['n_m1_r2'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
                round_textboxes['n_m1_r2'] = gr.Textbox(lines=4, show_label=False)
                
                

    # Round 3 (conditionally visible)
    with gr.Group(visible=True) as round3_group:
        gr.Markdown("### 🔁 Round 3")
        with gr.Row():
            with gr.Column():
                gr.Markdown("**Affirmative Team**")
                # Member 1
                with gr.Row():
                    gr.Markdown("Member 1")
                    ai_buttons['a_m1_r3'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
                round_textboxes['a_m1_r3'] = gr.Textbox(lines=4, show_label=False)
                
                
            with gr.Column():
                gr.Markdown("**Negative Team**")
                # Member 1
                with gr.Row():
                    gr.Markdown("Member 1")
                    ai_buttons['n_m1_r3'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
                round_textboxes['n_m1_r3'] = gr.Textbox(lines=4, show_label=False)
                

    gr.Markdown("---")
    gr.Markdown("### 🧾 Final Team Summaries")
    with gr.Row():
        with gr.Column():
            with gr.Row():
                gr.Markdown("**Affirmative — Final Team Summary**")
                ai_buttons['aff_final'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
            aff_final = gr.Textbox(lines=5, show_label=False)
        with gr.Column():
            with gr.Row():
                gr.Markdown("**Negative — Final Team Summary**")
                ai_buttons['neg_final'] = gr.Button("🤖 AI", variant="secondary", size="sm", scale=0)
            neg_final = gr.Textbox(lines=5, show_label=False)

    gr.Markdown("---")
    with gr.Row():
        judge_btn = gr.Button("🧑‍⚖️ Judge Winner (AI)", variant="primary")
    
    # Judge Results Section - Well-designed layout
    gr.Markdown("### 🏆 Judge Results")
    
    # Winner Display - Prominent section
    with gr.Row():
        winner_display = gr.Textbox(
            label="🎯 Winner",
            lines=1,
            max_lines=1,
            interactive=False,
            placeholder="Winner will be announced here...",
            elem_classes=["winner-display"]
        )
    
    # Scores Section - Side by side
    with gr.Row():
        with gr.Column():
            aff_score_display = gr.Textbox(
                label="✅ Affirmative Score",
                lines=1,
                max_lines=1,
                interactive=False,
                placeholder="--/25"
            )
        with gr.Column():
            neg_score_display = gr.Textbox(
                label="❌ Negative Score",
                lines=1,
                max_lines=1,
                interactive=False,
                placeholder="--/25"
            )
    
    # Reasoning Section - Larger area for detailed explanation
    with gr.Row():
        reason_display = gr.Textbox(
            label="📝 Judge's Reasoning",
            lines=6,
            max_lines=15,
            interactive=False,
            placeholder="Detailed reasoning will appear here after judging..."
        )
    
    # Optional: Download transcript
    with gr.Row():
        dl_file = gr.File(label="📄 Download Transcript", visible=False)

    # Add results textbox
    with gr.Row():
        results_textbox = gr.Textbox(
            label="📋 Judge Results", 
            lines=8, 
            max_lines=20,
            interactive=False,
            placeholder="Judge results will appear here after clicking 'Judge Winner'..."
        )

    # Wire actions
    def _update_rounds_visibility(num_rounds):
        """Update visibility of round groups based on selected number of rounds"""
        return {
            round2_group: gr.update(visible=num_rounds >= 2),
            round3_group: gr.update(visible=num_rounds >= 3)
        }

    num_rounds.change(_update_rounds_visibility, inputs=num_rounds, outputs=[round2_group, round3_group])

    # Add this event handler after the judge_btn.click handler
    generate_topic_btn.click(
        on_generate_topics,
        inputs=[topic],
        outputs=[aff_options, neg_options, tip_box],
    )

    judge_btn.click(
        on_judge,
        inputs=[
            topic,
            aff_options, neg_options,
            aff_final, neg_final,
            textbox_state
        ],
        outputs=[winner_display, aff_score_display, neg_score_display, reason_display, dl_file]
    )

    # Update the config update to only handle temperature and num_rounds
    for component, param in [(temperature, 'temperature'), (num_rounds, 'num_rounds')]:
        component.change(
            lambda *args, p=param: config_service.update_config(**{p: args[0]}),
            inputs=component
        )

    # Set up AI generation event handlers for all buttons (MOVE INSIDE BLOCKS CONTEXT)
    def update_textbox_state(state_dict, *textbox_values):
        textbox_keys = list(round_textboxes.keys())
        updated_state = dict(zip(textbox_keys, textbox_values))
        return updated_state
    
    # Set up change handlers for all textboxes
    for textbox in round_textboxes.values():
        textbox.change(
            update_textbox_state,
            inputs=[textbox_state] + list(round_textboxes.values()),
            outputs=textbox_state
        )
    
   

    def on_ai_generate_statement(textbox_id: str, topic: str, aff_options: str, neg_options: str, current_state: dict) -> str:
        """Generate AI content for a specific member based on textbox ID
        
        Args:
            textbox_id: Format like 'a_m1_r1' (affirmative_member1_round1) or 'n_m2_r3' (negative_member2_round3)
            topic: The debate topic
            aff_options: Affirmative team options
            neg_options: Negative team options
            temperature: AI temperature setting
        
        Returns:
            Generated content for the specific member
        """
    
        print(aff_options)
        print(neg_options)
        print(topic)
    
        if not topic.strip():
            return "⚠️ Please enter a debate topic first."
        
        affirmative_statements = []
        for textbox_id_key, value in current_state.items():
            if textbox_id_key.startswith('a') and value and value.strip():
                affirmative_statements.append(value)
        
        # collect all negative statements
        negative_statements = []
        for textbox_id_key, value in current_state.items():
            if textbox_id_key.startswith('n') and value and value.strip():
                negative_statements.append(value)
        
        # check textbox_id is affirmative or negative
        try: 
            if textbox_id.startswith('a'):
                return affirmative_agent.generate_affirmative_statement(topic, aff_options , affirmative_statements, negative_statements)
            else:
                return negative_agent.generate_negative_statement(topic, neg_options, affirmative_statements, negative_statements)
        except Exception as e:
            print(e)
            return "❌ Error generating content"

        

    # Wire AI buttons for round textboxes to call on_ai_generate_statement
    for textbox_id, button in ai_buttons.items():
        # Skip final summary buttons - they have separate handlers
        if textbox_id in ['aff_final', 'neg_final']:
            continue
            
        button.click(
            fn=lambda topic_val, aff_val, neg_val, temp_val, state, tb_id=textbox_id: 
                on_ai_generate_statement(tb_id, topic_val, aff_val, neg_val, state),
            inputs=[topic, aff_options, neg_options, temperature, textbox_state],
            outputs=round_textboxes[textbox_id]
        )

    # Add event handlers for final summary AI buttons
    def on_ai_generate_final_summary(team: str, topic: str, aff_options: str, neg_options: str, current_state: dict) -> str:
        """Generate AI final summary for affirmative or negative team"""
        if not topic.strip():
            return "⚠️ Please enter a debate topic first."
        
        # Collect team arguments from current state
        affirmative_statements = []
        for textbox_id_key, value in current_state.items():
            if textbox_id_key.startswith('a') and value and value.strip():
                affirmative_statements.append(value)
        
        # collect all negative statements
        negative_statements = []
        for textbox_id_key, value in current_state.items():
            if textbox_id_key.startswith('n') and value and value.strip():
                negative_statements.append(value)

        print(topic)
        print(aff_options)
        print(neg_options)


        print(affirmative_statements)
        print(negative_statements)  
        
        
        
        try:
            if team == 'affirmative':
                result, status = affirmative_agent.generate_closing_argument(topic, aff_options, neg_options, affirmative_statements, negative_statements)
            else:
                result, status = negative_agent.generate_closing_argument(topic, aff_options, neg_options, negative_statements, affirmative_statements)
            return result
        except Exception as e:
            return f"❌ Error generating {team} final summary: {e}"
    
    # Wire the final summary buttons separately
    ai_buttons['aff_final'].click(
        fn=lambda topic_val, aff_val, neg_val, temp_val, state: 
            on_ai_generate_final_summary('affirmative', topic_val, aff_val, neg_val, state),
        inputs=[topic, aff_options, neg_options, temperature, textbox_state],
        outputs=aff_final
    )
    
    ai_buttons['neg_final'].click(
        fn=lambda topic_val, aff_val, neg_val, temp_val, state: 
            on_ai_generate_final_summary('negative', topic_val, aff_val, neg_val, state),
        inputs=[topic, aff_options, neg_options, temperature, textbox_state],
        outputs=neg_final
    )

if __name__ == "__main__":
    demo.launch()