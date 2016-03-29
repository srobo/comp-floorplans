all: floor-0.pdf floor-2.pdf layout.pdf

%.pdf: %.svg teams.txt Makefile
	inkscape -A $(shell pwd)/$@ $(shell pwd)/$<

.PHONY: clean

clean:
	-rm -f *.pdf

