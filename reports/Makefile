TITLE = title.tex ../images/UQ.jpg
ABSTRACT = abstract.tex

FILES = $(TITLE) $(ABSTRACT)

all: main lit clean

main: main.tex $(FILES)
	pdflatex -jobname=thesis $@
	bibtex thesis.aux
	pdflatex -jobname=thesis $@
	pdflatex -jobname=thesis $@

lit: lit.tex
	pdflatex -jobname=survey $@
	bibtex survey.aux
	pdflatex -jobname=survey $@
	pdflatex -jobname=survey $@

.PHONY clean:
	rm -f *.aux *.log *.bbl *.blg *.glo *.ist *.lof *.lot *.toc
