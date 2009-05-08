###############################################
#      Makefile for single target projects    #
#                Andreas Gölzer               #
#                 version 0.31                 #
#        2006, last update 2008-03-05         #
###############################################

name := readesm
headers = $(wildcard *.h)
objects = $(headers:.h=.o)
extrafiles = $(name).doxygen EC_PK.bin batchall.sh license_sha1.txt COPYING README images.tar.bz2  $(name)-wrap-kde.sh
run_args = 
sources = $(name).cpp $(filter $(wildcard *.cpp), $(objects:.o=.cpp)) $(filter $(wildcard *.h), $(objects:.o=.h))

distribution = $(sources) $(extrafiles) Makefile
uploadtarget=www.goelzer.de@ssh.strato.de:andreas/wordpress/download
uploader=scp -p

SHELL=/bin/bash
TEX=latex
CFLAGS=-Wall -pipe  -Werror
# CXX=i586-mingw32msvc-g++
# LD=i586-mingw32msvc-ld

LIBRARIES=
CXXFLAGS=$(CFLAGS)
LDFLAGS=-s -lgmp -lgmpxx -lboost_program_options

all: $(name)

$(name) : $(patsubst %.cpp, %.o, $(filter $(wildcard *.cpp), $(objects:.o=.cpp)))
$(name).o: $(filter $(wildcard *.h), $(objects:.o=.h))


.PHONY:all clean distclean doc dist backup depend run zip links upload runall install uninstall package

run: $(name)
	./$(name) $(run_args)

install: $(name)
	install -d /usr/local/share/readesm
	install -m 755 $(name) /usr/local/bin
	install -m 755 $(name)-wrap-kde.sh /usr/local/bin
	install -m 644 images.tar.bz2 /usr/local/share/readesm
	install -m 644 EC_PK.bin /usr/local/share/readesm

package: $(name)
	checkinstall -y --maintainer "Andreas Goelzer \<andreas@goelzer.de\>" --pkgsource "http://andreas.goelzer.de/download/$(name).tar.bz2" --pkggroup text --requires "libgmpxx4ldbl, libgmp3c2, libboost-program-options1.34.1" --install=no --fstrans
uninstall:
	rm /usr/local/bin/$(name)
	rm /usr/local/share/images.tar.bz2

profiling: $(name)
	valgrind --tool=callgrind ./$(name) $(run_args)

depend: 
	@echo Makedepend is pretty insane, and will report lots of warnings about missing iostream and
	@echo similar standard headers. That is okay, or more precisely can hardly be prevented.
	makedepend -Y $(sources)


clean:
	-$(RM) $(RMFLAGS) $(name) $(objects) $(name).o

distclean: clean
	-rm -r html/ latex/
	-rm *~
	@echo Directory should be clean now, except for the .tar.bz2 files which
	@echo are created by \"make dist\" and \"make backup\". Remove them yourself
	@echo if you have to.
	@echo The following files in this directory would normally not be included in the
	@echo distribution:
	@ls -hl $(addprefix -I ,$(distribution))

dist: $(name).tar.bz2
$(name).tar.bz2: $(distribution)
	@echo Creating $(name).tar.bz2 ...
	@tar -C .. -chvjf $(name).tar.bz2 $(addprefix $(name)/,$(distribution))

upload: dist
	$(uploader) $(name).tar.bz2 $(uploadtarget)

backup: dist
	@echo Copying $(name).tar.bz2 to $(name)-backup-`date +%Y%m%d-%H%M`.tar.bz2
	@cp $(name).tar.bz2 $(name)-backup-`date +%Y%m%d-%H%M`.tar.bz2

doc: html/index.html
html/index.html: $(sources) $(name).doxygen
	doxygen $(name).doxygen

#-- additional implicit rules --

%.pdf : %.eps
	epstopdf $<
%.pdf : %.tex
	pdflatex $<
