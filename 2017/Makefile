BUILD_DIR=build
MUNGER=./munge-svg.py

PDFS=$(patsubst %.diagram,$(BUILD_DIR)/%.pdf, $(wildcard *.diagram))
SVGS=$(wildcard *.svg)

SHELL=/bin/bash

all: $(PDFS)

$(BUILD_DIR):
	mkdir build

$(BUILD_DIR)/%.pdf: %.diagram teams.txt $(SVGS) | $(BUILD_DIR)
	inkscape -A $@ <($(MUNGER) @$<)

.PHONY: clean

clean:
	-rm -rf *.pdf venue-map.svg shepherding-layout.svg *-with-teams.svg build
