install-reqs:
	pip install -r requirements/package.txt

install-dev-reqs:
	pip install -r requirements/package.txt -r requirements/dev.txt

pip-compile:
	pip-compile  --no-emit-index-url -v --generate-hashes --allow-unsafe requirements/package.in
	pip-compile  --no-emit-index-url -v --generate-hashes --allow-unsafe requirements/dev.in

install-git-hooks:
	pre-commit install -t pre-commit -t commit-msg

version:
	cz bump --changelog

tests:
	pytest \
	--cov=mikasa
	-v mikasa/tests

	coverage report

clean:
	rm -rf mikasa.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf **/.ruff_cache
