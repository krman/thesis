Answer Q.1 in Tutorial Session #1.
Answer Q.2 in Tutorial Session #2.
Answer Q.3 in Tutorial Session #3.

To complete Q.2 the following might help.....



To compile RouletteWheel.java open a terminal and enter:

	javac RouletteWheel.java

To execute RouletteWheel.class you need to pass arguments for
the number of parents to select, the file containing the fitness probabilities, and a seed for java's pseudo random number generator. For example, the statement below selects 2 parents from the probabilities contained in the file "populationFitnessValues.txt" using the seed value of 101:

	java RouletteWheel 2 populationFitnessValues.txt 101



After compiling and executing the above my terminal display looks like this....


miMac:tutorials mike$ javac RouletteWheel.java
miMac:tutorials mike$ java RouletteWheel 2 populationFitnessValues.txt 101
Running RouletteWheel v1.0...

fitnessvalues: [0.19, 0.01, 0.5, 0.2, 0.05, 0.05]
selectedIndividual: 6
selectedIndividual: 5

 ...RouletteWheel Finished.
miMac:tutorials mike$ 


