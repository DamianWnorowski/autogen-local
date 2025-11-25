"""CLI entry point for AutoGen Local."""
import argparse
import sys
from local_bridge import ollama
from config import config


def cmd_status(args):
    """Check system status."""
    print("Checking Ollama connection...")
    if ollama.is_healthy():
        print("Ollama: OK")
        models = ollama.list_models()
        print(f"Available models: {', '.join(models[:5])}..." if len(models) > 5 else f"Available models: {', '.join(models)}")
    else:
        print("Ollama: NOT RUNNING")
        print("Start Ollama with: ollama serve")
        return 1
    return 0


def cmd_crew(args):
    """Run multi-agent crew."""
    from agents.crew import Crew
    crew = Crew()
    result = crew.run(args.task)
    print(result)


def cmd_review(args):
    """Run code review."""
    from workflows.code_review import CodeReviewer
    reviewer = CodeReviewer()
    findings = reviewer.review_path(args.path)
    for f in findings:
        print(f"{f['severity']}: {f['file']}:{f['line']} - {f['message']}")


def cmd_research(args):
    """Run research pipeline."""
    from workflows.research import ResearchPipeline
    pipeline = ResearchPipeline()
    result = pipeline.research(args.question)
    print(result)


def cmd_chat(args):
    """Interactive chat."""
    from local_bridge import Message
    messages = []
    print("Chat mode. Type 'quit' to exit.")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ('quit', 'exit', 'q'):
                break
            messages.append(Message(role="user", content=user_input))
            response = ollama.chat(messages)
            print(f"AI: {response}")
            messages.append(Message(role="assistant", content=response))
        except KeyboardInterrupt:
            break
    print("Bye!")


def cmd_playground(args):
    """Launch REPL playground."""
    from tools.playground import start_repl
    start_repl()


def cmd_dashboard(args):
    """Launch web dashboard."""
    from tools.dashboard import run_dashboard
    run_dashboard(host=args.host, port=args.port)


def main():
    parser = argparse.ArgumentParser(description="AutoGen Local CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status
    subparsers.add_parser("status", help="Check system status")
    
    # crew
    crew_parser = subparsers.add_parser("crew", help="Run multi-agent crew")
    crew_parser.add_argument("task", help="Task description")
    
    # review
    review_parser = subparsers.add_parser("review", help="Code review")
    review_parser.add_argument("path", help="Path to review")
    
    # research
    research_parser = subparsers.add_parser("research", help="Research question")
    research_parser.add_argument("question", help="Research question")
    
    # chat
    subparsers.add_parser("chat", help="Interactive chat")
    
    # playground
    subparsers.add_parser("playground", help="REPL playground")
    
    # dashboard
    dash_parser = subparsers.add_parser("dashboard", help="Web dashboard")
    dash_parser.add_argument("--host", default="127.0.0.1")
    dash_parser.add_argument("--port", type=int, default=8080)
    
    args = parser.parse_args()
    
    commands = {
        "status": cmd_status,
        "crew": cmd_crew,
        "review": cmd_review,
        "research": cmd_research,
        "chat": cmd_chat,
        "playground": cmd_playground,
        "dashboard": cmd_dashboard,
    }
    
    if args.command in commands:
        sys.exit(commands[args.command](args) or 0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
