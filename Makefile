PY = venv/Scripts/python

run:
	$(PY) -m uvicorn tsuki.main:app --reload
