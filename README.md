This repository contains my attempt at the Spearbit coding assessment.
The goal was to build a full-stack web application that scans a public GitHub repository, uses an LLM to identify potential bugs/code smells, and displays results in two views:

Issues List – like GitHub Issues

Pull Request Style Code View – highlighting affected lines of code

Current Status

✅ Core Flask + HTMX scaffolding in place

✅ GitHub API integration implemented

✅ OpenAI Responses API integrated for bug detection

✅ Templates for Issues list and Code visualization drafted

⚠️ Hosting on Render ran into deployment issues (could not finalize environment / runtime setup in time)

⚠️ Incomplete polish around error handling, persistence, and UI

At this stage, the project runs locally, but is not hosted on a public URL as required.

How to Run Locally
git clone https://github.com/your-username/spearbitcodingassessment.git
cd spearbitcodingassessment

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# add your OpenAI API key in .env

python app.py


The app will attempt to start on:
👉 http://localhost:8080

Known Issues

Render deploy failed due to environment/runtime mismatches.

No persistence layer — scans reset on restart.

Styling is minimal; code viewer lacks syntax highlighting.

GitHub API rate limits may cause blank results for large repos.

Lessons Learned

The assignment helped me practice connecting APIs (GitHub + OpenAI) and building two distinct UI views.

Even though hosting was not completed, I now understand what additional work is needed to finalize a production-ready version (e.g., persistence, improved error handling, a more deployment-friendly framework like Next.js).
