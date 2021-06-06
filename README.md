# UdpChat.py - William Liang (jl5825)

UdpChat.py is a program written in Python3 to implement UDP-based communication 
functionalities as indicated by the programming assignment 1 of CSEE4119. The program has
two modes of operation: server, and client. As a server, the program will act to 
keep track of the user information, activities, and store offline chat messages 
in case a recipient is offline. As a client, the program allows the user to 
send and receive messages from other clients, and manage the user's own online 
status. When sending messages, the clients communicate directly with each other 
using UDP instead of relying on the server.

## 💫 Quick Start

UdpChat.py is built entirely using tools that come with Python3.6 with no 
externally installed libraries to make the testing and running process easy. 
To run the program, simply follow the steps below. 

<strong> Server Mode </strong>

To run the program as a server, simply provide the port number in the field which you 
wish the server to be listening to. 

```bash
python3 UdpChat.py -s <port>
```
<strong> Client Mode </strong>

To run the program as a client, you will need to provide the nick-name, server-ip, server-port number,
and client-port number. 
<br>
```bash
 python3 UdpChat.py -c <nick-name> <server-ip> <server-port> <client-port>
 ```
<br>
If you need to know the server ip and server port of the current machine, simply run the server
first and check the server window. 

## ⚙ Client Mode️ Commands & Options  
### `reg`
Command for registering with the server to go online. This command is automatically issued when the 
client first starts the program and can be subsequently issued during operation to log back after
loggin off. 

### `dereg`
Command for de-registering with the server to go offline. After de-registering, all messages received 
while offline will be automatically saved to the server and will be retrieved once the client registers
again.

### `send`
Command for sending messages to other clients. You can also send a message to yourself by specifying your 
own username in the recipient field below. 
```bash
send <recepient-name> <message>
```


## 📖 Project Wiki
UdpChat.py has server features that make this program useful.

`Dynamic Client Table 🗂` The program supports a dynamic client table that is constantly 
being communicated between the server and the client. When a new user registers, the 
new user's information will be added to the table with no limit on the number of 
clients allowed to register. When a user goes offline, the server supports functionalities 
to check the status of the user to make sure it is consistent with the record in the table
and to broadcast the table to all connected clients when the information of the table changes. 

`Offline chatting 📲` The program also supports offline chatting. When a client tries to send 
messages to another client who is offline, the program will send the messages instead to the 
server which will create a designated file to store these messages until the intended client logs back.

`Error Checking 🩺` The program supports several types of error checking to provide helpful 
feedbacks to help the user recover from the error. The program supports checking to ensure
 uniqueness of registration names. The program supports recovery from invalid commands and will not
 break when the user makes a mistake in the command, in the required arguments, and in the spelling 
of recipient's names.

`Dynamic Logging 📈` The server mode of the program is implemented to support dynamic logging of evnets 
with helpful data and timestamps. When using the program, the user can refer to the window of the server 
to view a log of events as the clients issue commands.





 ### 🔧 Algorithms and Data Structures Used

* Object-Oriented:
The program is implemented using an object-oriented approach with the Server and the Client 
programmed explicitly as classes, respectively.  
  

* Multi-threaded: Multi-threading is used for both the Server and 
the Client. For example, the Server opens up a new thread each time it receives a new message 
from the client to process the message. Also, the Client uses a separate thread to listen 
to incoming messages while at the same time responds to the user inputs of commands. 


* Client Table: The client table is implemented as a dictionary of the form `{Name: [(IP, port), Boolean]}`. 
The table is programmed as an attribute of the Client object or the Server object. The boolean 
value indicates whether a client is online or offline. 


* Transmitting Table: When processing requests, the table 
can be transmitted between the server and the client as `json` objects. When updating the 
client table, the Server will first encode the client table as a `json string` which will then 
be decoded by the Client.


* Offline messages: The offline messages as stored as `<name>.txt` files in the same directory as the program 
to retain these messages in case that the server fails. When a client logs back, the Server will check 
  to see if the associated file exists in the same working directory. If it does, the Server will 
  send the chat record line by line to the Client before deleting the record.
  

* Ping Test: After receiving a SAVE-OFFLINE request from the client, the Server will perform a ping test 
to ensure that the intended recipient is indeed offline. The server performs the test by sending a 
  `PING` request to the intended recipient. If it is acknowledged, the Server will send an error message 
  to the original sender along with a copy of the client table for the original sender to update. 
  

##  💡 Extra Features 

If you ever forget the registration name or port number of the client you are running, maybe because 
you have too many windows open, you could check that information by issuing a `test` command on the 
client. You could also check this information of the connected Server by issuing `testserver` on the 
Client and view the Server window. 

Also, because I am a picky freak, I made a graceful exit for the client when the user Ctrl-C by catching 
the KeyboardInterrupt exception. I could also make the user automatically deregister when Ctrl-C to avoid 
quitting without deregistering but I decided to leave it out to make testing easier. 