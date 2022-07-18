PY = venv/Scripts/python

run:
	$(PY) -m uvicorn tsuki.main:app --reload

reqs:
	$(PY) -m poetry export -f requirements.txt --output requirements.txt --without-hashes

git:
	git add .
	git commit -m "$(msg)"
	git push
	git push heroku
