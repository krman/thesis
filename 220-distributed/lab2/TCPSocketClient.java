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
    * The socket connected to the server.
    */
   public Socket toServer;

   public PrintWriter out;

   /**
    * Sets the client up with the server details.
    * @param the_serverHost the server host name.
    * @param the_serverPort the server port.
    */
   public TCPSocketClient(String the_serverHost, int the_serverPort) {
      my_serverHost = the_serverHost;
      my_serverPort = the_serverPort;
      try {
          toServer = new Socket(my_serverHost, my_serverPort);
      } catch (IOException ioe) {
          ioe.printStackTrace();
      } catch (SecurityException se) {
          se.printStackTrace();
      }

   }

    public void open() {
       try {
          toServer = new Socket(my_serverHost, my_serverPort);
          out = new PrintWriter(toServer.getOutputStream(), true);
      } catch (IOException ioe) {
          ioe.printStackTrace();
      } catch (SecurityException se) {
          se.printStackTrace();
      }
    }

        

   /**
    * Close the client and tidy up.
    */
   public void close() {
       try {
           toServer.close();
       } catch (IOException ioe) {
           ioe.printStackTrace();
       } 
   }

   /**
    * Creates a connection to the server and sends a message.
    * @param a_message the message to send to the server.
    */
   public void sendMessages(int num) {
      try {

          open();
          String message;

         for (int i=0; i<num; i++) {
             message = "Message #" + i;
             out.println(message);
         }

         close();
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
      int num = 0;

      // Check we have the right number of arguments and parse
      if (args.length == 3) {
         host = args[0];
         try {
            port = Integer.valueOf(args[1]);
         } catch (NumberFormatException nfe) {
            System.err.println("The value provided for the port is not an integer");
            nfe.printStackTrace();
         }
         num = Integer.valueOf(args[2]); //error check this

         // Create the client
         TCPSocketClient client = new TCPSocketClient(host, port);
         // Send num messages to the server
         client.sendMessages(num);
         // Close the client
         client.close();
      } else {
         System.out.println("Usage: java TCPSocketClient <host> <port> <message>");
      }

   }
} // end class

