import os
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.run_python_files import schema_run_python_file
from functions.write_file import schema_write_file
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_files import run_python_file
from functions.write_file import write_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. The working directory contains a 'pkg' subdirectory with the main code files. Always check the directory structure first if you're unsure about file locations.

Remember to explore the codebase by listing directories and reading relevant files before making changes or providing answers.
"""

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    args = function_call_part.args.copy()  # Copy to avoid modifying original
    args['working_directory'] = './calculator'  # Hardcode working directory
    
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    function_map = {
        'get_files_info': get_files_info,
        'get_file_content': get_file_content,
        'run_python_file': run_python_file,
        'write_file': write_file,
    }
    
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    function_result = function_map[function_name](**args)
    
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

def main():
    parser = argparse.ArgumentParser(description="Generate content using Gemini API.")
    parser.add_argument("user_prompt", type=str, help="The prompt to send to the model")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    messages = [
        types.Content(role="user", parts=[types.Part(text=args.user_prompt)]),
    ]
    
    max_iterations = 20
    for iteration in range(max_iterations):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-001', contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
            
            # Add the response content to messages
            for candidate in response.candidates:
                messages.append(candidate.content)
            
            # Check for function calls
            if response.function_calls:
                for function_call_part in response.function_calls:
                    function_call_result = call_function(function_call_part, args.verbose)
                    if not hasattr(function_call_result, 'parts') or not function_call_result.parts or not hasattr(function_call_result.parts[0], 'function_response'):
                        raise Exception("Invalid function call result structure")
                    if args.verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    # Add tool response as user message
                    messages.append(types.Content(
                        role="user",
                        parts=[function_call_result.parts[0]]
                    ))
            else:
                # If there's text response, print it and break
                if hasattr(response, 'text') and response.text:
                    print(response.text)
                    break
                else:
                    # Continue if no text but no function calls either
                    continue
        
        except Exception as e:
            print(f"Error during iteration {iteration + 1}: {e}")
            break
    
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Total iterations: {iteration + 1}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

client = genai.Client(api_key=api_key)

if __name__ == "__main__":
    main()
