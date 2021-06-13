# TODO: fill out makefile
# need commands for run, ?gh push?

# all of these commands that utilize python will specifically
# be run using `poetry run` to ensure poetry virtualenvs are 
# being used 😃

run:
	@poetry run uvicorn app.main:app --reload