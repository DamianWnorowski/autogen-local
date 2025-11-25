"""Interactive playground for testing agents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from local_bridge import LocalBridge
from config import DEFAULT_MODEL


class Playground:
    """Interactive environment for agent experimentation."""
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.bridge = LocalBridge(model=model)
        self.history = []
        self.context = {}
    
    def chat(self, message: str) -> str:
        """Send a message and get response."""
        self.history.append({"role": "user", "content": message})
        response = self.bridge.chat(message)
        self.history.append({"role": "assistant", "content": response})
        return response
    
    def reset(self):
        """Clear conversation history."""
        self.history = []
        self.context = {}
    
    def set_system_prompt(self, prompt: str):
        """Set custom system prompt."""
        self.bridge.system_prompt = prompt
    
    def get_history(self) -> list:
        """Return conversation history."""
        return self.history.copy()
    
    def interactive_mode(self):
        """Run interactive REPL."""
        print("Playground active. Type 'quit' to exit, 'reset' to clear.")
        while True:
            try:
                user_input = input("\n> ").strip()
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'reset':
                    self.reset()
                    print("History cleared.")
                elif user_input:
                    response = self.chat(user_input)
                    print(f"\n{response}")
            except KeyboardInterrupt:
                print("\nExiting.")
                break


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Agent playground')
    parser.add_argument('--model', default=DEFAULT_MODEL, help='Model to use')
    args = parser.parse_args()
    
    playground = Playground(model=args.model)
    playground.interactive_mode()


if __name__ == '__main__':
    main()
