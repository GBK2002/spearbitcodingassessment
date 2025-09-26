import os
from services.github import resolve_repo, fetch_repo_files
from services.llm import analyze_with_llm


SCAN_MAX_FILES = int(os.environ.get("SCAN_MAX_FILES", 400))
SCAN_MAX_TOTAL_BYTES = int(os.environ.get("SCAN_MAX_TOTAL_BYTES", 8_000_000))
SCAN_MAX_FILE_BYTES = int(os.environ.get("SCAN_MAX_FILE_BYTES", 1_000_000))


def run_scan(repo_url: str):
    ref = resolve_repo(repo_url)
    files = fetch_repo_files(ref, max_files=SCAN_MAX_FILES, max_total_bytes=SCAN_MAX_TOTAL_BYTES, max_file_bytes=SCAN_MAX_FILE_BYTES)
    findings = analyze_with_llm(files, repo={"owner": ref["owner"], "name": ref["name"]})
    return {"repo": ref, "files": files, "issues": findings}