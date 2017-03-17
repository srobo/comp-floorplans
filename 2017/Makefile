all: floor-0.pdf floor-2.pdf plain-layout.pdf shepherding-layout.pdf

%.pdf: %.svg teams.txt Makefile
	python add-teams.py $(shell pwd)/$<
	inkscape -A $(shell pwd)/$@ $(shell pwd)/$<-with-teams.svg

plain-layout.svg: layout.svg Makefile
	sed '/inkscape:label="Shepherding"/!b; N; s/display:inline/display:none/' $< > $@

shepherding-layout.svg: layout.svg Makefile
	sed '/inkscape:label="Shepherding"/!b; N; s/display:none/display:inline/' $< > $@

.PHONY: clean

clean:
	-rm -f *.pdf plain-layout.svg shepherding-layout.svg *-with-teams.svg
