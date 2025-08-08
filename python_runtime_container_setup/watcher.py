# watcher.py

import time
import boto3
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from uuid import uuid4
from datetime import datetime
from botocore.config import Config
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    config=Config(s3={"addressing_style": "virtual"}),
)


def get_unique_s3_obj_key(extension: str) -> str:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    uid = str(uuid4())
    return f"{now}_{uid}{extension}"


uploaded_files = set()
watch_path = "/app"
presigned_url_expiry = int(3*60*60) # for three hrs

# 🚫 Blacklisted filenames and extensions
IGNORED_FILES = {
    ".DS_Store",
    "Thumbs.db",
}

IGNORED_EXTENSIONS = {
    ".pyc",
    ".log",
    ".tmp",
}

IGNORED_PREFIXES = {
    "__pycache__",
    ".",
}


class UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or event.src_path.endswith(".done"):
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)
        _, ext = os.path.splitext(filename)

        # ✂️ Skip garbage files
        if (
            filename in IGNORED_FILES
            or ext.lower() in IGNORED_EXTENSIONS
            or any(filename.startswith(prefix) for prefix in IGNORED_PREFIXES)
        ):
            print(f"[Watcher] Skipping ignored file: {filename}")
            return

        key = get_unique_s3_obj_key(ext)
        print(f"[Watcher] New file created: {filepath}")
        try:
            print(f"[Watcher] Bucket: {BUCKET_NAME}")
            s3.upload_file(filepath, BUCKET_NAME, key)

            # Generate pre-signed URL valid for 60 seconds
            presigned_url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": BUCKET_NAME, "Key": key},
                ExpiresIn=presigned_url_expiry,
            )

            uploaded_files.add(presigned_url)
            print(f"[Watcher] Uploaded to S3: {presigned_url}")
        except Exception as e:
            print(f"[Watcher] Failed to upload {filepath}: {e}")


if __name__ == "__main__":
    print(f"[Watcher] Watching for files in: {watch_path}")
    event_handler = UploadHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()

    try:
        while True:
            if os.path.exists(os.path.join(watch_path, ".done")):
                print("[Watcher] Detected .done file, finishing up...")
                time.sleep(2)  # small buffer for final uploads
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.stop()
    observer.join()

    # Output all uploaded file URLs
    print("=== Uploaded Files ===")
    for url in uploaded_files:
        print(url)
