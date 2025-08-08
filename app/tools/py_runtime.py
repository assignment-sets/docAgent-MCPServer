from app.schemas import PyRuntimeInput
import tempfile
import subprocess
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PY_RUNTIME_TIMEOUT = int(os.getenv("PY_RUNTIME_TIMEOUT", "60"))
DOCKER_CONTAINER_NAME = os.getenv("DOCKER_CONTAINER_NAME", "py-runtime")


async def exec_py_runtime(
    input: PyRuntimeInput, timeout: int = PY_RUNTIME_TIMEOUT
) -> str:
    print(f"DEBUG: {input.code}")
    container_code_path = "/app/code.py"
    uploaded_urls = []

    try:
        # Step 1: Write the code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmpfile:
            tmpfile.write(input.code.encode("utf-8"))
            tmpfile_path = tmpfile.name
        logger.debug("Temporary file created at: %s", tmpfile_path)

        # Step 2: Verify Docker is accessible
        docker_test = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True
        )
        if docker_test.returncode != 0:
            logger.error("Docker not accessible: %s", docker_test.stderr)
            raise EnvironmentError("Docker is not installed or not accessible.")
        logger.info("Docker available: %s", docker_test.stdout.strip())

        # Step 3: Verify Docker image exists
        image_test = subprocess.run(
            ["docker", "inspect", DOCKER_CONTAINER_NAME], capture_output=True, text=True
        )
        if image_test.returncode != 0:
            logger.error(
                "Docker image '%s' not found: %s",
                DOCKER_CONTAINER_NAME,
                image_test.stderr,
            )
            raise ValueError(
                f"Image '{DOCKER_CONTAINER_NAME}' not found or inaccessible."
            )

        # Step 4: Build Docker run command
        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "bridge",
            "--cpus", "2.0",
            "--memory", "2048m",
            "--env-file", ".env",
            "-v", f"{tmpfile_path}:{container_code_path}:ro",
            DOCKER_CONTAINER_NAME,
        ]
        logger.debug("Running Docker with command: %s", " ".join(docker_cmd))

        result = subprocess.run(
            docker_cmd, capture_output=True, text=True, timeout=timeout
        )

        if result.returncode != 0:
            logger.error("Docker container failed. Exit code: %s", result.returncode)
            logger.debug("STDOUT: %s", result.stdout)
            logger.debug("STDERR: %s", result.stderr)
            raise RuntimeError(f"Docker failed: {result.stderr.strip()}")

        output = result.stdout.strip()
        logger.info("Execution successful. Output captured.")

        collecting = False
        for line in output.splitlines():
            if line.strip() == "=== Uploaded Files ===":
                collecting = True
                continue
            if collecting and line.strip().startswith("http"):
                uploaded_urls.append(line.strip())

        if not uploaded_urls:
            logger.warning("No URLs found in output.")

        return ", ".join(uploaded_urls)

    except subprocess.TimeoutExpired:
        logger.exception("Execution timed out after %s seconds.", timeout)
        raise TimeoutError("❌ Code execution timed out.")
    except FileNotFoundError as e:
        logger.exception("Docker not installed.")
        raise FileNotFoundError("❌ Docker not found. Please install Docker.") from e
    except PermissionError as e:
        logger.exception("Permission denied while accessing Docker.")
        raise PermissionError(
            "❌ Permission denied. Try: sudo usermod -aG docker $USER"
        ) from e
    except Exception as e:
        logger.exception("Unexpected error occurred during code execution.")
        raise RuntimeError(f"❌ Unexpected error: {str(e)}")
    finally:
        if "tmpfile_path" in locals() and os.path.exists(tmpfile_path):
            os.unlink(tmpfile_path)
            logger.debug("Temporary file cleaned up: %s", tmpfile_path)


if __name__ == '__main__':
    import asyncio
    
    complex_code = r"""
with open("translated_text.txt", "w") as f:
    f.write("hello sir")

"""
    
    async def test_py_runtime():
        artifacts = await exec_py_runtime(PyRuntimeInput(code=complex_code)) 
        print(artifacts)
    
    asyncio.run(test_py_runtime())
