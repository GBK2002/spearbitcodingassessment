import base64
import requests
API = "https://api.github.com"
class GitHubError(Exception):
    pass


def parse_repo_url(url: str):
# Accept forms: https://github.com/owner/repo or .../owner/repo.git
    import re
    m = re.search(r"github\.com/([^/]+)/([^/]+)", url)
    if not m:
        raise GitHubError("Invalid GitHub URL")
    owner, name = m.group(1), m.group(2).replace('.git','')
    return owner, name


def resolve_repo(url: str):
    owner, name = parse_repo_url(url)
    r = requests.get(f"{API}/repos/{owner}/{name}")
    if r.status_code != 200:
        raise GitHubError(f"GitHub repo not found: {owner}/{name}")
    data = r.json()
    return {"owner": owner, "name": name, "defaultBranch": data.get("default_branch", "main")}


def fetch_repo_files(ref: dict, *, max_files: int, max_total_bytes: int, max_file_bytes: int):
    owner, name, branch = ref["owner"], ref["name"], ref["defaultBranch"]
    # get tree recursively
    tr = requests.get(f"{API}/repos/{owner}/{name}/git/trees/{branch}?recursive=1")
    if tr.status_code != 200:
        raise GitHubError("Failed to fetch repo tree")
    tree = tr.json().get("tree", [])


    files_meta = [
        {"path": n.get("path"), "size": n.get("size", 0)}
        for n in tree
        if n.get("type") == "blob" and isinstance(n.get("path"), str)
    ]
    # Filter obvious heavy/vendor dirs
    import re
    deny = re.compile(r"^(\.git|node_modules|dist|build|out|.next|venv|env|target)/")
    files_meta = [f for f in files_meta if not deny.match(f["path"] or "")]


    total = 0
    picked = []
    for f in files_meta[:max_files]:
        size = int(f["size"] or 0)
        if size > max_file_bytes:
            continue
        if total + size > max_total_bytes:
            break
        cr = requests.get(f"{API}/repos/{owner}/{name}/contents/{f['path']}")
        if cr.status_code != 200:
            continue
        data = cr.json()
        if isinstance(data, dict) and data.get("type") == "file" and data.get("content"):
            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
            picked.append({"path": f["path"], "size": size, "content": content})
            total += size
    return picked