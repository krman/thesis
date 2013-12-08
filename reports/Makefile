TITLE = title.tex ../images/UQ.jpg
ABSTRACT = abstract.tex

FILES = $(TITLE) $(ABSTRACT)

all: thesis lit clean

thesis: main.tex $(FILES)
	pdflatex -jobname=thesis main.tex

lit: lit-survey.tex
	pdflatex -jobname=survey lit-survey.tex

#add in requirements for the title stuff as a variable

.PHONY clean:
	rm -f *.aux *.log
