#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int connect_smtp(const char* host, int port);
void send_smtp(int sock, const char* msg, char* resp, size_t len);

/*
  Use the provided 'connect_smtp' and 'send_smtp' functions
  to connect to the "lunar.open.sice.indian.edu" smtp relay
  and send the commands to write emails as described in the
  assignment wiki.
 */
int main(int argc, char* argv[]) {
  if (argc != 3) {
    printf("Invalid arguments - %s <email-to> <email-filepath>", argv[0]);
    return -1;
  }

  char* host = "lunar.open.sice.indiana.edu";
  int port = 25;
  char initiate[4096];
  char response[4096];
  char mail_from[4096];
  char rcpt_to[4096];
  char data[4096];
  char* rcpt = argv[1];
  char* filepath = argv[2];
  char mail_message[4096];
  char *line = NULL;
  size_t len = 0;
  ssize_t read;
 
  FILE* file = fopen(filepath, "r");
  if (file == NULL) {
        printf("\n Can't open the file, error occured");
        exit(1);
    }
  while ((read = getline(&line, &len, file)) != -1) {
      strcat(mail_message, line);
  }
  fclose(file);
  strcat(mail_message,"\r\n.\r\n");
  
  int socket = connect_smtp(host, port);
  
  strcat(initiate,"HELO client.example.com\n");
  puts(initiate);
  send_smtp(socket, initiate, response, 4096);
  printf("%s\n", response);
  
  //Mail From
  sprintf(mail_from, "MAIL FROM:%s\n", rcpt);
  puts(mail_from);
  send_smtp(socket, mail_from, response, 4096);
  printf("%s\n",response);
  
  //Recipient
  sprintf(rcpt_to, "RCPT TO:%s\n", rcpt);
  puts(rcpt_to);
  send_smtp(socket, rcpt_to, response, 4096);
  printf("%s\n",response);
  
  //Data for Mail
  strcat(data,"DATA\n");
  puts(data);
  send_smtp(socket, data, response, 4096);
  printf("%s\n",response);
  send_smtp(socket, mail_message, response, 4096);
  printf("%s\n",response);
 
  //Quit
  printf("QUIT\n");
  send_smtp(socket, "QUIT\n", response, 4096);
  printf("%s\n",response);
  return 0;
}
