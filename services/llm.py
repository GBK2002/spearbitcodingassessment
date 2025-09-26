import os
import uuid
import json
import requests
from pydantic import BaseModel, Field, ValidationError
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")


class Finding(BaseModel):
    title: str
    severity: str = Field(pattern=r"^(low|medium|high)$")
    filePath: str
    lineStart: int
    lineEnd: int
    description: str
    suggestedFix: str | None = None


class Findings(BaseModel):
    __root__: list[Finding]

PROMPT_TMPL = (
    "You are a security static analyser. Given ONE source file from a public GitHub repo "
    "{owner}/{name}, find potential security bugs or code smells. Output ONLY JSON array of objects: "
    "{title, severity (low|medium|high), filePath, lineStart, lineEnd, description, suggestedFix}. "
    "Keep line ranges tight to implicated code. File path: {path}.\n\n"
    )


HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}" if OPENAI_API_KEY else "",
    "Content-Type": "application/json",
    }

def analyze_with_llm(files: list[dict], repo: dict) -> list[dict]:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")


    findings: list[dict] = []
    for file in files:
        prompt = PROMPT_TMPL.format(owner=repo["owner"], name=repo["name"], path=file["path"])
        body = {
            "model": OPENAI_MODEL,
            "input": [
                 {"role": "system", "content": "Return ONLY valid JSON for findings; no commentary."},
                 {"role": "user", "content": [
                     {"type": "text", "text": prompt},
                     {"type": "input_text", "text": file["content"]}
                 ]}
             ],
            "text_format": {
                "type": "json_schema",
                 "json_schema": {
                    "name": "Findings",
                    "schema": {
                        "type": "array",
                        "items": {
                             "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "severity": {"type": "string", "enum": ["low","medium","high"]},
                                    "filePath": {"type": "string"},
                                    "lineStart": {"type": "integer", "minimum": 1},
                                    "lineEnd": {"type": "integer", "minimum": 1},
                                    "description": {"type": "string"},
                                    "suggestedFix": {"type": "string"}
                                },
                                "required": ["title","severity","filePath","lineStart","lineEnd","description"]
                            }
                        },
                        "strict": False
                    }
                }
            }
        r = requests.post("https://api.openai.com/v1/responses", headers=HEADERS, data=json.dumps(body))
        if r.status_code != 200:
            raise RuntimeError(f"OpenAI error: {r.status_code} {r.text[:200]}")
        data = r.json()
            # Try both structured and plain text fallbacks
        text = (
            (data.get("output", [{}])[0].get("content", [{}])[0].get("text"))
            or data.get("output_text")
            or "[]"
        )
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = []
        try:
                model = Findings(__root__=parsed)
                for f in model.__root__:
                    d = f.dict()
                    d["id"] = str(uuid.uuid4())
                    findings.append(d)
        except ValidationError:
            #skip invalid file output, continue
            continue
    return findings