import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=[]):
    # Normalize paths to handle relative paths and prevent traversal
    working_directory = os.path.abspath(working_directory)
    full_path = os.path.abspath(os.path.join(working_directory, file_path))

    # Check if full_path is within working_directory
    if not full_path.startswith(working_directory):
        error_msg = f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        print(error_msg)
        return error_msg

    if not os.path.exists(full_path):
        error_msg = f'Error: File "{file_path}" not found.'
        print(error_msg)
        return error_msg

    if not file_path.endswith('.py'):
        error_msg = f'Error: "{file_path}" is not a Python file.'
        print(error_msg)
        return error_msg

    try:
        # Run the Python file
        cmd = ['python3', full_path] + args
        result = subprocess.run(
            cmd,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Format output
        output_parts = []
        if result.stdout:
            output_parts.append(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            output_parts.append(f"STDERR: {result.stderr.strip()}")
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")

        if not output_parts:
            output = "No output produced."
        else:
            output = "\n".join(output_parts)

        print(output)
        return output

    except subprocess.TimeoutExpired:
        error_msg = "Error: executing Python file: Process timed out after 30 seconds"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error: executing Python file: {e}"
        print(error_msg)
        return error_msg

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file with optional arguments, constrained to the working directory. Has a 30-second timeout.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional list of arguments to pass to the Python script.",
            ),
        },
        required=["file_path"],
    ),
)