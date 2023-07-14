#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void send_http(char* host, char* msg, char* resp, size_t len);

/*
  Implement a program that takes a host, verb, and path and
  prints the contents of the response from the request
  represented by that request.
 */
int main(int argc, char* argv[]) {
  if (argc != 4) {
    printf("Invalid arguments - %s <host> <GET|POST> <path>\n", argv[0]);
    return -1;
  }
  char* host = argv[1];
  char* verb = argv[2];
  char* path = argv[3];
  char *msg = malloc(strlen(verb) + strlen(path) + 100);
  if ( msg != NULL){
     strcpy(msg, verb);
     strcat(msg, " ");
     strcat(msg, path);
     strcat(msg," HTTP/1.1\r\n");
  }
  char *fin = malloc(strlen(msg) * 500);
  if (fin != NULL){
     strcpy(fin,msg);
     strcat(fin, "Host:");
     strcat(fin, host);
     if (strcmp(verb,"GET")==0){
     	strcat(fin, "\r\n\r\n");
     }
     else if (strcmp(verb,"POST")==0){
	strcat(fin,"\r\nContent-Length:10\r\n\r\nThis is it\r\n\r\n");
     }
  } 
  char response[4096];
  send_http(host, fin, response, 4096);
  printf("%s\n", response);
  return 0;
}
