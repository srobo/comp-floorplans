all: floor-0.pdf floor-2.pdf layout.pdf

%.pdf: %.svg teams.txt Makefile
	python add-teams.py $(shell pwd)/$<
	inkscape -A $(shell pwd)/$@ $(shell pwd)/$<-with-teams.svg

.PHONY: clean

clean:
	-rm -f *.pdf
