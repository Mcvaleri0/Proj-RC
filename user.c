#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <signal.h>



#define MYCSPORT 58049

extern int errno;


void verificaErro(int err) {
  if (err == -1) {
    printf("Error: %s\n", strerror(errno));
    exit(1);
  }
}


int main(int argc, char *argv[]) {
  char csName[128];
  int err, csPort = MYCSPORT;

  void (*old_handler)(int);

  int fd, nb, nl, nw, nr;
  struct sockaddr_in serveraddr;
  struct hostent *hostptr;
  char *ptr, buffer[50];


  strcpy(csName, "tejo.tecnico.ulisboa.pt");
  csPort = 58011;


  if ((old_handler = signal(SIGPIPE, SIG_IGN)) == SIG_ERR) {
    printf("Erro ao proteger do SIGPIPE\n");
    exit(1);
  }

  fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd == -1) {
    printf("error: %s\n", strerror(errno));
    exit(1);
  }

  hostptr = gethostbyname(csName);
  if (hostptr == NULL) {
    printf("Erro ao encontrar o host.\n");
    exit(1);
  }

  memset((void*)&serveraddr, (int)'\0', sizeof(serveraddr));
  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = ((struct in_addr*)(hostptr->h_addr_list[0]))->s_addr;
  serveraddr.sin_port = htons((u_short)csPort);


  err = connect(fd, (struct sockaddr*)&serveraddr, sizeof(serveraddr));
  if (err == -1) {
    printf("Erro ao conectar\n");
    exit(1);
  }

  strcpy(buffer, "AUT 67890 aaaaaaaa\n");
  nl = strlen(buffer);
  ptr = &buffer[0];
  while (nl > 0) {
    nw = write(fd, ptr, nl);
    if (nw <= 0) {
      printf("Erro ao escrever mensagem\n");
      exit(1);
    }

    nl  -= nw;
    ptr += nw;
  }
  printf("mandei: %s\n", buffer);

  ptr = &buffer[0];
  nl  = 7;
  while (nl > 0) {
    nr = read(fd, ptr, nl);

    if (nr == -1) {
      printf("Erro ao receber mensagem\n");
      exit(1);
    } else if (nr == 0) { break; }

    nl  -= nr;
    ptr += nr;
  }
  buffer[7] = '\0';
  printf("recebi: %s\n", buffer);





  //---------- Atribuicoes do Central Server e a sua porta de acesso ----------
  /*if (argc == 1) {
    Se nao sao dados mais argumentos sao atribuidos os default
          CS --> e na minha maquina
    err = gethostname(csName, 128);
    verificaErro(err);
  }
  else if (argc == 3) {
    if (!strcmp(argv[1], "-n")) {
      strcpy(csName,argv[2]);
    }
    else if (!strcmp(argv[1], "-p")) {
      csPort = atoi(argv[2]);
      err = gethostname(csName, 128);
      verificaErro(err);}}
  else {
    printf("Chamada errada aplicação.\nEx: ./user [-n CSname] [-p CSport]\n");
    exit(1);
  }*/






  return 0;
}
