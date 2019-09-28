#!/bin/bash
PACKAGES=$(wildcard *.zip)

build-classic: clean
	@mkdir -p ./target 2> /dev/null
	@python do_get.py ./addons-classic.json
	unzip 

clean: $(PACKAGES)
	@rm -rf ./target
