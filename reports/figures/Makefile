all: figures clean
.PHONY: figures clean

figures:
	for entry in `ls *.tex`; do pdflatex -shell-escape $$entry; done

clean:
	rm -f *.aux *.log *.ps *-fig*.tex tmp.inputs

