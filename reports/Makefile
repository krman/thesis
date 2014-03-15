TITLE = title.tex ../images/UQ.jpg
ABSTRACT = abstract.tex
ACKNOWLEDGEMENTS = ack.tex
INTRODUCTION = intro.tex

FILES = $(TITLE) $(ACKNOWLEDGEMENTS) $(ABSTRACT) $(INTRODUCTION)
FILES += $(LITERATURE)

all: main proposal clean

main: main.tex $(FILES)
	pdflatex -jobname=Thesis $@
	bibtex Thesis.aux
	pdflatex -jobname=Thesis $@
	pdflatex -jobname=Thesis $@

proposal: proposal.tex
	pdflatex -jobname=Proposal $@
	bibtex Proposal.aux
	pdflatex -jobname=Proposal $@
	pdflatex -jobname=Proposal $@

.PHONY clean:
	rm -f *.aux *.log *.bbl *.blg *.glo *.ist *.lof *.lot *.toc
