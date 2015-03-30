.PHONY: all clean

all:
	$(MAKE) -C 2014
	$(MAKE) -C 2015

clean:
	$(MAKE) -C 2014 clean
	$(MAKE) -C 2015 clean
