/*
Implements RouletteWheel Selection

Copyright (C) 2010 Michael O'Neill
This software is distributed under the terms of the GNU General Public License.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

import java.util.*;
import java.io.*;

/**
 * This is the class to perform Roulette wheel selection
 * @author Michael O'Neill
 */
public class RouletteWheel {

    protected Random rng;   /* variable storing the initialised pseudo random number generator object*/


    /**
     * RouletteWheel constructor method
     */
    public RouletteWheel(int seed) {
	/* initialise Java's built-in pseudo random number generator*/
	Random generator = new Random(seed);
	this.rng = generator;
    }


    /**
     * Selects Individuals from the list "operands"
     * @param operands contains the fitness values of the individuals to be chosen from
     **/
    protected int spinRoulette(List<Double> operands) {
        double prob;
	double accumulatedFitnessSum = 0.0;

	prob = rng.nextDouble();

	Iterator<Double> itI = operands.iterator();
	int cnt = 0;        
	while(itI.hasNext() && cnt < operands.size() && accumulatedFitnessSum < prob) {
	    accumulatedFitnessSum += itI.next().doubleValue();
	    cnt++;
	}
	return cnt;
    }



    /**
     * Let's run RouletteWheel selection :-)
     * @param You must specify 
     *        (0) the number of parents to select
     *        (1) the List of fitness values stored in a file
     *        (2) an integer seed for Java's pseudo random number generator
     */

    public static void main(String[] args) {

	int numberOfParents = 0;
	File fileName = null;
	int seed = 0;
	List<Double> populationFitnessValues = new ArrayList<Double>();

	System.out.println("Running RouletteWheel v1.0...\n");

	/**
	 * parse the command line arguments
	 */
	if(args.length<3) System.out.println("Usage: java RouletteWheel numberOfParents  fileName seed)");
	else{
	    try {
		numberOfParents = Integer.parseInt(args[0]);
	    } catch (NumberFormatException e) {
		System.err.println("First argument must be an integer");
		System.exit(1);
	    }	
	    fileName = new File(args[1]);
	    if (fileName == null) {
		System.out.println ("Default: populationFitnessValues.txt");
		fileName = new File ("populationFitnessValues.txt");
	    }
	    try{
		FileReader inFile = new FileReader (fileName);
		BufferedReader bufferFile = new BufferedReader (inFile);
		do {
		    String line = bufferFile.readLine ();
		    if (line == null) break;
		    populationFitnessValues.add(Double.parseDouble(line));
		} while (true);
		bufferFile.close ();
		System.out.println("fitnessvalues: "+populationFitnessValues);
	    }
	    catch (IOException e) {
		System.out.println ("IO exception = " + e );
	    }
	    try {
		seed = Integer.parseInt(args[2]);
	    } catch (NumberFormatException e) {
		System.err.println("Third argument must be an integer");
		System.exit(1);
	    }


	    /**
	     * instantiate the RouletteWheel object 
	     */
	    RouletteWheel rWheel = new RouletteWheel(seed);
	    int selectedIndividual = 0;  /* variable to store the index of the selected individual */

	    /**
	     * Rank the population from lowest to highest fitness values 
	     */
	    Collections.sort(populationFitnessValues);
	    
	    /**
	     * select N parents from the population 
	     */
	    for(int i=0;i<numberOfParents;i++){
		selectedIndividual = rWheel.spinRoulette(populationFitnessValues);
		System.out.println("selectedIndividual: "+selectedIndividual);
	    }

        System.out.println("best fitness: "+Collections.max(populationFitnessValues));
        System.out.println("average fitness: "+Collections.max(populationFitnessValues));
        System.out.println("worst fitness: "+Collections.min(populationFitnessValues));

	}
	System.out.println("\n ...RouletteWheel Finished.");
    }
}
