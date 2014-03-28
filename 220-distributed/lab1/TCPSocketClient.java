import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;

/**
 * A simple class that opens a socket, sends a message to the server, and
 * terminates.
 * @author Graeme Stevenson (graeme.stevenson@ucd.ie)
 */
public class TCPSocketClient {

   /**
    * The server host name.
    */
   public String my_serverHost;

   /**
    * The server port.
    */
   public int my_serverPort;

   /**
    * Sets the client up with the server details.
    * @param the_serverHost the server host name.
    * @param the_serverPort the server port.
    */
   public TCPSocketClient(String the_serverHost, int the_serverPort) {
      my_serverHost = the_serverHost;
      my_serverPort = the_serverPort;
   }

   /**
    * Creates a connection to the server and sends a message.
    * @param a_message the message to send to the server.
    */
   public void sendMessage(String a_message) {
      try {
         // Create a connection to the server.
         Socket toServer = new Socket(my_serverHost, my_serverPort);

         // Wrap a PrintWriter round the socket output stream.
         // Read the javadoc to understand (1) the method arguments, and (2) why
         // we do this rather than writing to raw sockets.
         PrintWriter out = new PrintWriter(toServer.getOutputStream(), true);

         // Write the message to the socket.
         out.println(a_message);

         // EXERCISE: Extend this code to
         // 1. Read the response from the server.
         BufferedReader in = new BufferedReader(new InputStreamReader(toServer.getInputStream()));
         String reply = in.readLine();

         // 2. Print the response out to the console.
         System.out.println(reply);

         // tidy up
         in.close();
         out.close();
         toServer.close();
      } catch (IOException ioe) {
         ioe.printStackTrace();
      } catch (SecurityException se) {
         se.printStackTrace();
      }
   }

   /**
    * Parse the arguments to the program, create a socket, and send a message.
    * @param args the program arguments. Should take the form &lt;host&gt;
    *           &lt;port&gt; &lt;message&gt;
    */
   public static void main(String[] args) {

      String host = null;
      int port = 0;
      String msg = null;

      // Check we have the right number of arguments and parse
      if (args.length == 4) {
         host = args[0];
         try {
            port = Integer.valueOf(args[1]);
         } catch (NumberFormatException nfe) {
            System.err.println("The value provided for the port is not an integer");
            nfe.printStackTrace();
         }
         msg = String.format("%s %s", args[2], args[3]);

         // Create the client
         TCPSocketClient client = new TCPSocketClient(host, port);
         // Send a message using the client
         client.sendMessage(msg);
      } else {
         System.out.println("Usage: java TCPSocketClient <host> <port> <num> <denom>");
      }

   }
} // end class

