import os
import config
from google.genai import types

def get_file_content(working_directory, file_path):
    # Normalize paths to handle relative paths and prevent traversal
    working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Check if full_path is within working_directory
    if not full_path.startswith(working_directory):
        error_msg = f"File '{file_path}' is outside the working directory '{working_directory}'"
        print(f"Error: {error_msg}")
        return f"Error: {error_msg}"
    
    if not os.path.exists(full_path):
        error_msg = f"File '{full_path}' does not exist"
        print(f"Error: {error_msg}")
        return f"Error: {error_msg}"
    
    if not os.path.isfile(full_path):
        error_msg = f"'{full_path}' is not a file"
        print(f"Error: {error_msg}")
        return f"Error: {error_msg}"
    
    try:
        with open(full_path, 'r') as file:
            content = file.read()
    except OSError as e:
        error_msg = f"Error reading file: {str(e)}"
        print(f"Error: {error_msg}")
        return f"Error: {error_msg}"
    
    if len(content) > config.MAX_FILE_SIZE:
        content = content[:config.MAX_FILE_SIZE] + f"\n...File \"{file_path}\" truncated at {config.MAX_FILE_SIZE} characters"
    
    print(f"Content of '{file_path}':")
    print(content)
    
    return content

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file, constrained to the working directory. Truncates files over 10,000 characters.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)