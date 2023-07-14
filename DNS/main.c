#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
/*
  Use the `getaddrinfo` and `inet_ntop` functions to convert a string host and
  integer port into a string dotted ip address and port.
 */
int main(int argc, char* argv[]) {
  if (argc != 3) {
    printf("Invalid arguments - %s <host> <port>", argv[0]);
    return -1;
  }
  char* host = argv[1];
  long port = atoi(argv[2]);
  (void)port;
  struct addrinfo hints, *res;
  //Setting of hints is refered from Lab discusion session from Alex
  memset(&hints, 0, sizeof(hints));
  hints.ai_family = PF_UNSPEC;
  hints.ai_socktype = SOCK_STREAM;
  hints.ai_protocol = IPPROTO_TCP;
  hints.ai_flags = AI_PASSIVE;
  int error = getaddrinfo(host, "http", &hints, &res);
  (void)error;
  struct addrinfo* i;
  char buffer[200];
  for(i=res; i!=NULL; i=i->ai_next)
  {
	if (i->ai_addr->sa_family == AF_INET) { // IPv4 Address
  	struct sockaddr_in* ipaddr = (struct sockaddr_in*)i->ai_addr;
	inet_ntop(AF_INET, &(ipaddr->sin_addr), buffer, sizeof(buffer));
	printf("IPv4 %s\n",buffer);
	}
	else { //IPv6 Address
  	struct sockaddr_in6* ipaddr = (struct sockaddr_in6*)i->ai_addr;
	inet_ntop(AF_INET6, &(ipaddr->sin6_addr), buffer, sizeof(buffer));
	printf("IPv6 %s\n", buffer);
	}
  }

  return 0;
}
