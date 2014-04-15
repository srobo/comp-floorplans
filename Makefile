all: floor-0.pdf floor-2.pdf

%.pdf: %.svg
	inkscape -A $@ $<

.PHONY: clean

clean:
	-rm -f *.pdf

