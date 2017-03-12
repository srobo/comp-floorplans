BUILD_DIR=build
MUNGER=./munge-svg.py

PDFS=floor-0-all.pdf floor-2-all.pdf venue-map.pdf shepherding-layout.pdf
BUILD_PDFS=$(patsubst %,$(BUILD_DIR)/%,$(PDFS))

SHELL=/bin/bash

all: $(BUILD_PDFS)

$(BUILD_DIR):
	mkdir build

$(BUILD_DIR)/floor-0-all.pdf: floor-0.svg teams.txt Makefile $(MUNGER) | $(BUILD_DIR)
	inkscape -A $@ <($(MUNGER) --show-layers ALL -- $<)

$(BUILD_DIR)/floor-2-all.pdf: floor-2.svg teams.txt Makefile $(MUNGER) | $(BUILD_DIR)
	inkscape -A $@ <($(MUNGER) --show-layers ALL -- $<)

$(BUILD_DIR)/venue-map.pdf: layout.svg Makefile $(MUNGER) | $(BUILD_DIR)
	inkscape -A $@ <($(MUNGER) --show-layers Layout -- $<)

$(BUILD_DIR)/shepherding-layout.pdf: layout.svg Makefile $(MUNGER) | $(BUILD_DIR)
	inkscape -A $@ <($(MUNGER) --show-layers Layout Shepherding -- $<)

.PHONY: clean

clean:
	-rm -rf *.pdf venue-map.svg shepherding-layout.svg *-with-teams.svg build
