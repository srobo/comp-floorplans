BUILD_DIR=build

PDFS=floor-0.pdf floor-2.pdf venue-map.pdf shepherding-layout.pdf
BUILD_PDFS=$(patsubst %,$(BUILD_DIR)/%,$(PDFS))

all: $(BUILD_PDFS)

$(BUILD_DIR):
	mkdir build

$(BUILD_DIR)/%.pdf: %.svg teams.txt Makefile | $(BUILD_DIR)
	python add-teams.py $(shell pwd)/$<
	inkscape -A $(shell pwd)/$@ $(shell pwd)/$<-with-teams.svg

venue-map.svg: layout.svg Makefile
	sed '/inkscape:label="Shepherding"/!b; N; s/display:inline/display:none/' $< > $@

shepherding-layout.svg: layout.svg Makefile
	sed '/inkscape:label="Shepherding"/!b; N; s/display:none/display:inline/' $< > $@

.PHONY: clean

clean:
	-rm -rf *.pdf venue-map.svg shepherding-layout.svg *-with-teams.svg build
