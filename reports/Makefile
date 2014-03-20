TITLE = title.tex ../files/UQ.jpg
ABSTRACT = abstract.tex
ACKNOWLEDGEMENTS = ack.tex
INTRODUCTION = intro.tex

FILES = $(TITLE) $(ACKNOWLEDGEMENTS) $(ABSTRACT) $(INTRODUCTION)
FILES += $(LITERATURE)

all: main proposal clean
.PHONY: figures clean

figures:
	make -C figures

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

clean:
	rm -f *.aux *.log *.bbl *.blg *.glo *.ist *.lof *.lot *.toc
