all: floor-0.png floor-2.png

%.png: %.svg
	inkscape -e $@ $<

.PHONY: clean

clean:
	-rm -f *.png

