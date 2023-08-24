PYTHON ?= $(shell command -v python)
MAKEFILE =$(abspath $(MAKEFILE_LIST))

.PHONY: help clean

# Usage:
#
#	make [rule]
#
# Rules:

help:
#	help 	- print this help message
	@grep '^#' $(MAKEFILE) | grep -v '^##' | sed -e 's:#::'  


clean:
#	clean	- remove generated files
	@rm -rf \
		./.coverage \
		./.mypy_cache \
		./.pytest_cache \
		./dist \
		./htmlcov
	@find ./virtbmc \
		-type d \
		-name "__pycache__" \
		-exec rm -r {} +
	@find ./virtbmc \
		-type d \
		-name "*.egg-info" \
		-exec rm -r {} +
