import os
from google.genai import types

def write_file(working_directory, file_path, content):
    # Normalize paths to handle relative paths and prevent traversal
    working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    # Check if full_path is within working_directory
    if not full_path.startswith(working_directory):
        error_msg = f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        print(error_msg)
        return error_msg
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # Write the content to the file
        with open(full_path, 'w') as file:
            file.write(content)
    except OSError as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return error_msg
    
    success_msg = f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    print(success_msg)
    return success_msg

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites the contents of a file, constrained to the working directory. Creates the file if it doesn't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)