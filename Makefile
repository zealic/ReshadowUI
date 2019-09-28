#!/bin/bash
TARGET_DIR=./target
INTERFACE_DIR=$(TARGET_DIR)/Interface/AddOns
UPLOAD_HOST?=RZ-DSM:5005
UPLOAD_URL=http://$(UPLOAD_HOST)/build/ReshadowUI
GENERAL_FILE=ReshadowUI-latest.zip
CLASSIC_FILE=ReshadowUI-Classic-latest.zip

build-classic: clean
	@python do_get.py ./addons-classic.json
	@ls *.zip | xargs -I{} unzip -d $(INTERFACE_DIR) {}
	@(cd target; zip -r $(CLASSIC_FILE) Interface)

build-general: clean
	@python do_get.py ./addons-general.json
	@ls *.zip | xargs -I{} unzip -d $(INTERFACE_DIR) {}
	@(cd target; zip -r $(GENERAL_FILE) Interface)

upload-general:
	@echo Uploading $(GENERAL_FILE) ...
	@curl --fail -sS -u anonymous: -T "$(TARGET_DIR)/$(GENERAL_FILE)" "$(UPLOAD_URL)/$(GENERAL_FILE)"
	@echo Upload successful.

upload-classic:
	@echo Uploading $(CLASSIC_FILE) ...
	@curl --fail -sS -u anonymous: -T "$(TARGET_DIR)/$(CLASSIC_FILE)" "$(UPLOAD_URL)/$(CLASSIC_FILE)"
	@echo Upload successful.

clean:
	@rm -rf *.zip
	@rm -rf $(INTERFACE_DIR)
	@mkdir -p $(INTERFACE_DIR) 2> /dev/null

.PHONY: clean
