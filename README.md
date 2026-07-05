# Bet Intelligence AI

FastAPI + dashboard MVP for betting analysis.

## Render deploy
1. Upload these files to GitHub repo.
2. Render → New → Blueprint.
3. Select repo.
4. Add environment variable `FOOTYSTATS_API_KEY`.
5. Deploy.

## Local run
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Open http://127.0.0.1:8000
