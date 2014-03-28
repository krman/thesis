import java.io.*;
import java.net.*;
import java.util.*;

/**
* UDPReceiver
* Author: Mauro Dragone
*/

public class UDPReceiver {
    protected MulticastSocket socket = null; 
    protected InetAddress multicastAddress;

    public UDPReceiver(String multicastGroup,  int multiCastPort) {

	try {
	  multicastAddress = InetAddress.getByName(multicastGroup);
	}
	catch(Throwable t) {
	  System.out.println("Exception getting inetaddress for group:"+ multicastGroup);
	}

	try {
	  // creates the multicast socket
 	  socket = new MulticastSocket(multiCastPort); 
	  socket.joinGroup(multicastAddress);	 
	}
	catch (java.net.SocketException e) {
	  System.out.println("Exception creating multicast socket and joining group: " + e.getMessage());
	}
	catch (IOException e) {     	 
	        e.printStackTrace();		
    	}	

	// Keep reading for ever
	while (true) {
		try  {
                byte[] buf = new byte[1024]; 
		    // HINT: TRY WHAT HAPPENS WHEN THE STRING RECEIVED IS BIGGER THAN THE BUFFER
                // receive packet
                DatagramPacket packet = new DatagramPacket(buf, buf.length);
                socket.receive(packet);
		
		    // I know it is a string...
		    String strCmd = new String(packet.getData()).trim();
		    int port = packet.getPort();
		
		    System.out.println("Received " + strCmd);
	

         } catch (IOException e) {
                e.printStackTrace();		
         }
	}
	

    }
    
    public static void main(String[] args) {
	String multicastGroup = "230.0.0.1";
	String strMulticastPort = "4445";

	new UDPReceiver(multicastGroup, Integer.parseInt(strMulticastPort));
    }



}