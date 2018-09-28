#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>


#define MYCSPORT     58049
#define US_NAME_SIZE 5
#define US_PASS_SIZE 8

extern int errno;
int  err;
char usName[US_NAME_SIZE+1], usPass[US_PASS_SIZE+1];


//============================== Funcoes Gerais ==============================
void verificaErr() {
  if (err == -1) {
    printf("Error: %s\n", strerror(errno));
    exit(1);
  }
}
//============================================================================


//===================== Funcoes dos Comandos da aplicacao =====================
void cmLogin() {
  int  i;

  err = scanf("%s %s", usName, usPass);
  verificaErr();

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

  //TODO--> ainda nao acabei
}
//=============================================================================

int main(int argc, char const *argv[]) {
  int  csPort, cmSize;
  char csName[128], command[8];

  void (*old_handler)(int);
  if ((old_handler = signal(SIGPIPE, SIG_IGN)) == SIG_ERR) {
    fprintf(stderr, "Erro ao proteger do SIGPIPE\n");
    exit(1);
  }


  //---------- Atribuicoes do Central Server e a sua porta de acesso ----------
  csPort = MYCSPORT;

  switch (argc) {
    case 1:
      err = gethostname(csName, 128);
      verificaErr();
      break;

    case 3:
      if (!strcmp(argv[1], "-n")) { strcpy(csName, argv[2]); }
      else if (!strcmp(argv[1], "-p")) {
        csPort = atoi(argv[2]);
        err    = gethostname(csName, 128);
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
    err = scanf("%s", command);
    verificaErr();

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
