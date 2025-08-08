import tempfile
import subprocess
import os
import textwrap

def run_code_in_docker(code: str, timeout: int = 60) -> str:
    # Step 1: Write the code to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmpfile:
        # Dedent the code to remove unintended indentation
        clean_code = textwrap.dedent(code)
        tmpfile.write(clean_code.encode('utf-8'))
        tmpfile_path = tmpfile.name

    container_code_path = "/app/code.py"
    
    try:
        print("Testing Docker access...")
        docker_test = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        print(f"Docker version: {docker_test.stdout.strip()}")

        print("Testing image access...")
        image_test = subprocess.run(
            ["docker", "inspect", "py-runtime"], 
            capture_output=True, text=True
        )
        if image_test.returncode != 0:
            return f"❌ Image 'py-runtime' not found or not accessible: {image_test.stderr}"
        
        print("Running Docker container...")
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "bridge",
            "--cpus", "2.0",
            "--memory", "2048m",
            "--env-file", ".env",
            "-v", f"{tmpfile_path}:{container_code_path}:ro",
            "py-runtime",
            "python3", container_code_path
        ]

        print(f"Docker command: {' '.join(docker_cmd)}")
        
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            error_msg = f"❌ Docker container failed (exit code {result.returncode})\n"
            error_msg += f"STDOUT: {result.stdout}\n"
            error_msg += f"STDERR: {result.stderr}"
            return error_msg

        output = result.stdout.strip() or result.stderr.strip()
        return output if output else "✅ Code executed successfully (no output)"

    except subprocess.TimeoutExpired:
        return "❌ Execution timed out"
    except FileNotFoundError as e:
        return f"❌ Docker not found. Is Docker installed? Error: {str(e)}"
    except PermissionError as e:
        return f"❌ Permission denied. Try: sudo usermod -aG docker $USER\nError: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"
    finally:
        if os.path.exists(tmpfile_path):
            os.unlink(tmpfile_path)


# Use raw triple-quoted string
complex_code = """
paragraph = ""

file_path = "sample_paragraph.txt"

with open(file_path, "w", encoding="utf-8") as f:
    f.write(paragraph)

print(f"✅ Paragraph written to {file_path}")
"""

print("=== Testing with complex code (ML libraries) ===")
output = run_code_in_docker(complex_code)
print(output)
