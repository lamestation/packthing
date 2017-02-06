PYTHON	:=	python
SETUP	:=	$(PYTHON) setup.py
MKDOCS	:=	mkdocs

.PHONY: all
all:
	@echo commands:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null \
		| awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
		| sort \
		| egrep -v -e '^[^[:alnum:]]' -e '^$@$$' \
		| xargs \
		| sed -e 's/ /\n  /g' -e 's/^/  /'

.PHONY: install 
install:
	$(SETUP) install

.PHONY: develop
develop:
	$(SETUP) develop

.PHONY: docs
docs:
	$(MKDOCS) build

.PHONY: serve
serve:
	$(MKDOCS) serve

.PHONY: clean
clean:
	rm -rf site/
