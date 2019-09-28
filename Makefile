#!/bin/bash
INTERFACE_DIR=./target/Interface/AddOns


build-classic: clean
	@python do_get.py ./addons-classic.json
	@ls *.zip | xargs -I{} unzip -d $(INTERFACE_DIR) {}
	@(cd target; zip -r ReshadowUI-Classic-latest.zip Interface)

build-general: clean
	@python do_get.py ./addons.json
	@ls *.zip | xargs -I{} unzip -d $(INTERFACE_DIR) {}
	@(cd target; zip -r ReshadowUI-latest.zip Interface)

clean:
	@rm -rf *.zip
	@rm -rf ./target
	@mkdir -p $(INTERFACE_DIR) 2> /dev/null

.PHONY: clean
