PYTHON		:=	python
SETUP		:=	$(PYTHON) setup.py
MKDOCS		:=	mkdocs
BUILD_DOCS 	:= $(PYTHON) build-docs.py
DIR_SCHEMA	:= packthing/schema
DIR_API		:= docs/config

SCHEMA_FILES := \
	main.yml \
	platforms.yml \
	sources.yml \
	builders.yml \
	files.yml \
	mimetypes.yml \
	packagers.yml

SCHEMA_FILES := $(patsubst %,$(DIR_SCHEMA)/%, $(SCHEMA_FILES))
API_FILES := $(patsubst $(DIR_SCHEMA)/%.yml, $(DIR_API)/%.md, $(SCHEMA_FILES))

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
docs: $(API_FILES)
	@echo $(SCHEMA_FILES)
	@echo $(API_FILES)
	$(MKDOCS) build

$(DIR_API)/%.md: $(DIR_SCHEMA)/%.yml
	if ! $(BUILD_DOCS) $< > $@ ; then \
		rm $@ ; \
		exit 1 ; \
	fi

.PHONY: serve
serve:
	$(MKDOCS) serve

.PHONY: clean
clean:
	rm -rf site/
	rm -f $(DIR_API)/*
