.PHONY: all clean deploy compile
SHELL := /bin/bash

OUTDIR := dist

MODULES := $(wildcard *.py)
JUSTCOPY=boot.py main.py
COMMON_REQUIREMENTS=config configuration.py ./util/remove-debug.sh

COMPILED_MODULES := $(filter-out $(JUSTCOPY),$(MODULES))
MPY_MODULES := $(patsubst %.py,%.mpy,$(COMPILED_MODULES))
MPY_MODULE_TARGETS := $(patsubst %,$(OUTDIR)/%,$(MPY_MODULES))

default: compile deploy

compile: $(MPY_MODULE_TARGETS)

clean:
	rm -rf $(OUTDIR)

$(MPY_MODULE_TARGETS): | config $(OUTDIR)

$(OUTDIR)/%.mpy : %.py $(COMMON_REQUIREMENTS)
	source config && envsubst < $< > $(OUTDIR)/$<
	./util/remove-debug.sh $(OUTDIR)/$<
	python -m py_compile $(OUTDIR)/$<
	mpy-cross -march=xtensa -O3 -o $@ $(OUTDIR)/$<

config:
	./util/init-config.sh

$(OUTDIR):
	mkdir $(OUTDIR)

deploy:
	./util/deploy.sh

