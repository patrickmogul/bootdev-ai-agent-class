import os
from google.genai import types

def get_files_info(working_directory, directory="."):
    # Normalize paths to handle relative paths and prevent traversal
    working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, directory))
    
    # Check if full_path is within working_directory
    if not full_path.startswith(working_directory):
        error_msg = f"Directory '{directory}' is outside the working directory '{working_directory}'"
        print(f"Error: {error_msg}")
        return {"success": False, "data": error_msg}
    
    if not os.path.exists(full_path):
        error_msg = f"Directory '{full_path}' does not exist"
        print(f"Error: {error_msg}")
        return {"success": False, "data": error_msg}
    
    if not os.path.isdir(full_path):
        error_msg = f"'{full_path}' is not a directory"
        print(f"Error: {error_msg}")
        return {"success": False, "data": error_msg}
    
    contents = []
    try:
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            is_dir = os.path.isdir(item_path)
            file_size = os.path.getsize(item_path)  # Get size for files and directories
            contents.append({
                "name": item,
                "is_dir": is_dir,
                "file_size": file_size
            })
    except OSError as e:
        error_msg = f"Error accessing directory: {str(e)}"
        print(f"Error: {error_msg}")
        return {"success": False, "data": error_msg}
    
    # Print contents in the desired format
    print(f"Result for '{directory}':")
    for item in contents:
        print(f" - {item['name']}: file_size={item['file_size']} bytes, is_dir={item['is_dir']}")
    
    return {"success": True, "data": contents}

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)