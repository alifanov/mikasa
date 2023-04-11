install-reqs:
	pip install -r requirements/package.txt

install-dev-reqs:
	pip install -r requirements/package.txt -r requirements/dev.txt

pip-compile:
	pip-compile  --no-emit-index-url -v --generate-hashes --allow-unsafe requirements/package.txt
	pip-compile  --no-emit-index-url -v --generate-hashes --allow-unsafe requirements/dev.txt

install-git-hooks:
	pre-commit install -t pre-commit -t commit-msg

version:
	cz bump --pr rc --changelog
