import ollama
import subprocess
import sys
import json

# Configuration
MODEL = "gemma4:e2b"

def run_command(command):
    print(f"\n[Gemma wants to run]: {command}")
    confirm = input("Confirm execution? (y/n): ")
    if confirm.lower() == 'y':
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            return output if output else "Command executed successfully (no output)."
        except Exception as e:
            return f"Error executing command: {str(e)}"
    else:
        return "Command cancelled by user."

def main():
    print(f"--- Gemma 4 Terminal Agent (Model: {MODEL}) ---")
    print("Type 'exit' to quit.")
    
    messages = [
        {
            'role': 'system',
            'content': (
                "You are a terminal agent with full control over the user's laptop. "
                "You can run shell commands using the 'run_command' tool. "
                "Always explain what you are about to do before running a command. "
                "Use the output of the commands to inform your next steps. "
                "Your goal is to help the user with their tasks effectively."
            )
        }
    ]

    # Define the tool for Gemma
    tools = [
        {
            'type': 'function',
            'function': {
                'name': 'run_command',
                'description': 'Run a shell command on the laptop and return the output.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'command': {
                            'type': 'string',
                            'description': 'The shell command to execute.',
                        },
                    },
                    'required': ['command'],
                },
            },
        }
    ]

    while True:
        user_input = input("\nUser> ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        messages.append({'role': 'user', 'content': user_input})
        
        # Initial call to get model response/tool call
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        
        messages.append(response['message'])
        
        # Check if the model wants to call a tool
        if response['message'].get('tool_calls'):
            for tool in response['message']['tool_calls']:
                if tool['function']['name'] == 'run_command':
                    command = tool['function']['arguments']['command']
                    output = run_command(command)
                    
                    # Add tool output back to conversation
                    messages.append({
                        'role': 'tool',
                        'content': output,
                    })
            
            # Get final response after tool execution
            final_response = ollama.chat(
                model=MODEL,
                messages=messages,
            )
            print(f"\nGemma> {final_response['message']['content']}")
            messages.append(final_response['message'])
        else:
            print(f"\nGemma> {response['message']['content']}")

if __name__ == "__main__":
    main()
