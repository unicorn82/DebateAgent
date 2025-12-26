def main():
    print("Hello from debateagent!")
    import os
    from dotenv import load_dotenv
    import debate_ui

    # Load environment variables from .env if present
    try:
        load_dotenv()
    except Exception:
        pass

    # Launch the Gradio UI defined in debate_ui
    debate_ui.demo.launch()


# Entry point for CLI execution
if __name__ == "__main__":
    main()
