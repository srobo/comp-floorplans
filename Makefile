all: floor-0.pdf floor-2.pdf team-map.pdf

%.pdf: %.svg
	inkscape -A $@ $<

.PHONY: clean

clean:
	-rm -f *.pdf

