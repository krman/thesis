TITLE = title.tex ../files/UQ.jpg
ABSTRACT = abstract.tex
ACKNOWLEDGEMENTS = ack.tex
INTRODUCTION = intro.tex

FILES = $(TITLE) $(ACKNOWLEDGEMENTS) $(ABSTRACT) $(INTRODUCTION)
FILES += $(LITERATURE)

all: main clean
.PHONY: figures clean

figures:
	make -C figures

main: main.tex $(FILES)
	pdflatex -jobname=Thesis main.tex
	bibtex Thesis.aux
	pdflatex -jobname=Thesis main.tex
	pdflatex -jobname=Thesis main.tex

proposal: proposal.tex
	pdflatex -jobname=Proposal $@
	bibtex Proposal.aux
	pdflatex -jobname=Proposal $@
	pdflatex -jobname=Proposal $@

clean:
	rm -f *.aux *.log *.bbl *.blg *.glo *.ist *.lof *.lot *.toc *.lol *.out
