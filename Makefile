PY = venv/Scripts/python

run:
	$(PY) -m uvicorn tsuki.main:app --reload

git:
	git add .
	git commit -m $(msg)
	git push
