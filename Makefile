# This makefile has been created to help developers perform common actions.
# Most actions assume it is operating in a virtual environment where the
# python command links to the appropriate virtual environment Python.

VENVS_DIR := $(HOME)/.venvs
VENV_DIR := $(VENVS_DIR)/ronto

# Do not remove this block. It is used by the 'help' rule when
# constructing the help output.
# help:
# help: ronto Makefile help
# help:

# help: help                           - display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: venv                           - create a virtual environment for development
.PHONY: venv
venv:
	@test -d "$(VENVS_DIR)" || mkdir -p "$(VENVS_DIR)"
	@rm -Rf "$(VENV_DIR)"
	@python3 -m venv "$(VENV_DIR)"
	@/bin/bash -c "source $(VENV_DIR)/bin/activate && pip install pip --upgrade && pip install -r requirements.dev.txt && pip install -e ."
	@echo "Enter virtual environment using:\n\n\t$ source $(VENV_DIR)/bin/activate\n"


# help: clean                          - clean all files using .gitignore rules
.PHONY: clean
clean:
	@git clean -X -f -d


# help: scrub                          - clean all files, even untracked files
.PHONY: scrub
scrub:
	git clean -x -f -d


# help: test                           - run tests
.PHONY: test
test:
	@# run unit tests
	@py.test tests
	@# run component tests
	@behave


# help: test-verbose                   - run tests [verbosely]
.PHONY: test-verbose
test-verbose:
	@# run unit tests verbosely
	@py.test -v tests
	@# run component tests verbosely
	@behave -v



# help: style                          - perform code format compliance check
.PHONY: style
style:
	@black src/ronto tests



# help: check-types                    - check type hint annotations
.PHONY: check-types
check-types:
	@cd src; MYPYPATH=$(VENV_DIR)/lib/python*/site-packages mypy -p ronto --ignore-missing-imports


# help: docs                           - generate project documentation
.PHONY: docs
docs:
	@cd docs; make html


# help: check-docs                     - quick check docs consistency
.PHONY: check-docs
check-docs:
	@cd docs; make dummy


# help: serve-docs                     - serve project html documentation
.PHONY: serve-docs
serve-docs:
	@cd docs/build; python -m http.server --bind 127.0.0.1


# help: dist                           - create a wheel distribution package
.PHONY: dist
dist:
	@python setup.py bdist_wheel


# help: dist-test                      - test a whell distribution package
.PHONY: dist-test
dist-test: dist
	@cd dist && ../tests/test-dist.bash ./ronto-*-py3-none-any.whl


# help: dist-upload                    - upload a wheel distribution package
.PHONY: dist-upload
dist-upload:
	@twine upload dist/ronto-*-py3-none-any.whl


# Keep these lines at the end of the file to retain nice help
# output formatting.
# help:
