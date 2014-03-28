
import java.io.*;
import java.net.*;
import java.util.*;

/**
* UDPSender
* Author: Mauro Dragone
**/
public class UDPSender {
    protected MulticastSocket socket = null; 
    protected InetAddress multicastAddress;
    protected int multiCastPort;

    public UDPSender(String multicastGroup,  int multiCastPort) {

	this.multiCastPort = multiCastPort;

	try {
	  multicastAddress = InetAddress.getByName(multicastGroup);
	}
	catch(Throwable t) {
	}


	try {
 	  socket = new MulticastSocket();
	  socket.joinGroup(multicastAddress); 
	}
	catch (java.net.SocketException e) {
	  System.out.println("Exception starting server: " + e.getMessage());
	}
	catch (IOException e) {     	 
	        e.printStackTrace();		
    	}	
	
    }

    public void send(String msg) {
    	try {					
		//byte[] buf = new byte[256];			
		byte[] buf = msg.getBytes();

		// create the packet to wrap the msg data
		DatagramPacket packet = new DatagramPacket(buf, buf.length, 			multicastAddress, multiCastPort);
	     
		socket.send(packet);
	}
	catch (IOException e) {     	 
	    e.printStackTrace();	
	    // TO-DO: improve by handling this exception	
    	}
    }

    
    public static void main(String[] args) {
	String multicastGroup = "230.0.0.1";
	String strMulticastPort = "4445";

	UDPSender sender = new UDPSender(multicastGroup, Integer.parseInt(strMulticastPort));

	int i = 1;
	while (true) {		
		String msg = "test message "+i; 
		System.out.println("Sending: "+msg);
		sender.send(msg);
		i++;
		
		try {
	    		Thread.sleep(500);
        	} catch (InterruptedException e) {}
	}	
    }


   



}