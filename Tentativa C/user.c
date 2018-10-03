#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>


#define MYCSPORT     58049
#define US_NAME_SIZE 5
#define US_PASS_SIZE 8
#define STRING_MAX   128
#define COMMAND_SIZE 8
#define AUT_SZ       19
#define AUTR_SZ      8

extern int errno;
int  err, fd, csPort;
char usName[US_NAME_SIZE+1], usPass[US_PASS_SIZE+1], csName[STRING_MAX];
char aut[AUT_SZ+1];


//============================== Funcoes Gerais ==============================
void verificaErr() {
  if (err == -1) {
    printf("Error: %s\n", strerror(errno));
    exit(1);
  }
}

int connectServerTCP() {
  struct hostent *hostptr;
  struct sockaddr_in serveraddr;

  fd = socket(AF_INET, SOCK_STREAM, 0);
  if (fd == -1) {
    printf("error: %s\n", strerror(errno));
    return -1;
  }

  hostptr = gethostbyname(csName);
  if (hostptr == NULL) { return -1; }

  memset((void*)&serveraddr, (int)'\0', sizeof(serveraddr));
  serveraddr.sin_family = AF_INET;
  serveraddr.sin_addr.s_addr = ((struct in_addr*)(hostptr->h_addr_list[0]))->s_addr;
  serveraddr.sin_port = htons((u_short)csPort);


  if (connect(fd, (struct sockaddr*)&serveraddr, sizeof(serveraddr)) == -1) {
    printf("aqui\n");return -1;
  }

  return 0;
}


int sendMSG(char *msg, int msg_sz) {
  char *ptr;
  int  nleft, nwrite;

  ptr   = &msg[0];
  nleft = msg_sz;

  while (nleft > 0) {
    nwrite = write(fd, ptr, nleft);
    if (nwrite <= 0) {
      return -1;
    }

    nleft -= nwrite;
    ptr   += nwrite;
  }
  return 0;
}


int receiveMSG(char *buffer, int buff_sz) {
  char *ptr;
  int  nleft, nread;

  ptr   = &buffer[0];
  nleft = buff_sz;

  while (nleft > 0) {
    nread = read(fd, ptr, nleft);

    if (nread == -1)     { return -1; }
    else if (nread == 0) { break;     }

    nleft -= nread;
    ptr   += nread;
  }

  return 0;
}
//============================================================================


//===================== Funcoes dos Comandos da aplicacao =====================
void cmLogin() {
  int  i;
  char autR[AUTR_SZ+1];

  if (scanf("%s %s", usName, usPass) == -1) {
    printf("Erro ao ler username e pass\n");
    return;
  }

  // Zona de verificacao para ver se o input esta na forma correta
  for (i = 0; usName[i] != '\0'; i++) {
    if ( (usName[i] < '0') || (usName[i] > '9') || (i == US_NAME_SIZE) ) {
      /* Se nao e um numero ou se o usName ja e demasido grande */
      printf("User name tem de ser 5 digitos.\n");
      return;
    }
  }
  if (i < US_NAME_SIZE) {
    printf("User name tem de ser 5 digitos.\n");
    return;
  }

  for (i = 0; usPass[i] != '\0'; i++) {
    if (!(((usPass[i] >= '0') && (usPass[i] <= '9'))  ||
          ((usPass[i] >= 'A') && (usPass[i] <= 'Z'))  ||
          ((usPass[i] >= 'a') && (usPass[i] <= 'z'))) || (i == US_PASS_SIZE) ) {
      /* Se nao e um numero nem uma maiscula nem uma minuscula ou se ja e
         demasiado grande */
      printf("User pass tem de ser 8 caracteres (digitos e/ou letras).\n");
      return;
    }
  }
  if (i < US_PASS_SIZE) {
    printf("User pass tem de ser 8 caracteres (digitos e/ou letras).\n");
    return;
  }

  // Zona de conecao ao server
  if (connectServerTCP() == -1) {
    printf("Erro ao conectar-se com o servidor\n");
    return;
  }

  strcat(strcat(strcat(strcat(strcat(aut, "AUT "), usName), " "), usPass), "\n\0");
  if (sendMSG(aut, AUT_SZ) == -1) {
    printf("Erro ao enviar o pedido de autorizacao.\n");
    return;
  }

  if (receiveMSG(autR, AUTR_SZ) == -1) {
    printf("Erro ao receber autorizacao.\n");
    return;
  }
  autR[AUTR_SZ] = '\0';

  printf("%s\n", autR);
}
//=============================================================================

int main(int argc, char const *argv[]) {
  int  cmSize;
  char command[COMMAND_SIZE];

  void (*old_handler)(int);
  if ((old_handler = signal(SIGPIPE, SIG_IGN)) == SIG_ERR) {
    fprintf(stderr, "Erro ao proteger do SIGPIPE\n");
    exit(1);
  }


  //---------- Atribuicoes do Central Server e a sua porta de acesso ----------
  csPort = MYCSPORT;

  switch (argc) {
    case 1:
      err = gethostname(csName, STRING_MAX);
      verificaErr();
      break;

    case 3:
      if (!strcmp(argv[1], "-n")) { strcpy(csName, argv[2]); }
      else if (!strcmp(argv[1], "-p")) {
        csPort = atoi(argv[2]);
        err    = gethostname(csName, STRING_MAX);
        verificaErr();
        break;
      }

    case 5:
      if (!strcmp(argv[1], "-n"))      { strcpy(csName, argv[2]); }
      else if (!strcmp(argv[3], "-n")) { strcpy(csName, argv[4]); }
      else {
        fprintf(stderr, "Aplicação chamada erradamente.\n");
        fprintf(stderr, "Ex: ./user [-n CSname] [-p CSport]\n");
        exit(1);
      }

      if (!strcmp(argv[1], "-p"))      { csPort = atoi(argv[2]); }
      else if (!strcmp(argv[3], "-p")) { csPort = atoi(argv[4]); }
      else {
        fprintf(stderr, "Aplicação chamada erradamente.\n");
        fprintf(stderr, "Ex: ./user [-n CSname] [-p CSport]\n");
        exit(1);
      }
      break;

    default:
      fprintf(stderr, "Aplicação chamada erradamente.\n");
      fprintf(stderr, "Ex: ./user [-n CSname] [-p CSport]\n");
      exit(1);
  }
  //---------------------------------------------------------------------------


  //--------------------------- Ciclo da aplicacao ---------------------------
  while (1) {
    printf("> ");
    if (scanf("%s", command) != -1) {
      cmSize = strlen(command); // Serve para se ter que comparar o comando com
      switch (cmSize) {         // todas aspossibilidades.
        case 4:
          if (!strcmp(command, "exit")) { return 0; }
          else { printf("Comando inexistente\n"); }
          break;

        case 5:
          if (!strcmp(command, "login")) { cmLogin(); }
          else { printf("Comando inexistente\n"); }
          break;

        default:
          printf("Comando inexistente\n");
      }
    } else { printf("Erro ao ler o comando\n"); }

    /*if (login--5) {}
    else if (deluser--7) {}
    else if (backup--6) {}
    else if (restore--7) {}
    else if (dirlist--7) {}
    else if (filelist--8) {}
    else if (delete--6) {}
    else if (logout--6) {}*/

  }
  //---------------------------------------------------------------------------

  return 0;
}
