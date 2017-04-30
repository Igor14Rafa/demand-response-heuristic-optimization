#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>

#define NLA 5                  /* número de linhas na matriz A*/
#define NCA 5                  /* número de colunas na matriz A */
#define NCB 5                  /* number of colunas na matriz B */
#define MASTER 0               /* ID do processador 0*/
#define FROM_MASTER 1          /* tipo de mensagem enviada do processador 0 (mestre) */
#define FROM_WORKER 2          /* tipo de mensagem enviada do processador >0 (escravo) */

int main (int argc, char *argv[])
{
	int	numtasks,              /* número total de processadores */
		taskid,                /* ID do processador (rank)*/
		numworkers,            /* número de processadores, fora o processador mestre */
		source,                /* processador que manda a mensagem (0) */
		dest,                  /* Processador que irá receber a mensagem */
		mtype,                 /* tipo de mensagem */
		rows,                  /* Linhas da matriz A enviadas para cada processador */
		average_quant_row, extra, offset, /* quantidade de linhas enviadas para cada processador*/
		i, j, k;           
	double	a[NLA][NCA],           /* matriz A */
			b[NCA][NCB],           /* matriz B */
			c[NLA][NCB];           /* matriz C resultante*/
	MPI_Status status;

	MPI_Init(&argc, &argv);
	MPI_Comm_rank(MPI_COMM_WORLD, &taskid);
	MPI_Comm_size(MPI_COMM_WORLD, &numtasks);

	numworkers = numtasks - 1; /*Exclui o processador 0 do número de processadores
								 que irão realizar os cálculos */


	/**************************** processador 0 (mestre) ************************************/
	if (taskid == MASTER)
		{
			printf("Iniciando com %d processadores.\n", numtasks);
			printf("Inicializando matrizes...\n");
			printf("Matriz A:\n");
			for (i = 0; i < NLA; i++){
				printf("\n");
				for (j = 0; j < NCA; j++){
					a[i][j] = i + j;
					printf("%6.2f", a[i][j]);
				}
			}
			printf("\n");
			printf("Matriz B:\n");
			for (i = 0; i < NCA; i++){
				printf("\n");
				for (j = 0; j < NCB; j++){
					b[i][j] = i * j;
					printf("%6.2f", b[i][j]);
				}
			}
			printf("\n");
			/* Envio dos valores das matrizes para os outros processadores */
			average_quant_row = NLA / numworkers; /*Número médio de linhas que cada procssador vai receber */
			extra = NLA % numworkers; /* Número extra de linhas que serão distribuídas a alguns processadores*/
			offset = 0; /* Deslocamento em relação ao ínicio */
			mtype = FROM_MASTER; 
			for (dest = 1; dest <= numworkers; dest++)
				{
					rows = (dest <= extra) ? average_quant_row + 1 : average_quant_row; 
					printf("Enviando %d linhas ao processador %d; deslocamento = %d\n", rows, dest, offset);
					MPI_Send(&offset, 1, MPI_INT, dest, mtype, MPI_COMM_WORLD);
					MPI_Send(&rows, 1, MPI_INT, dest, mtype, MPI_COMM_WORLD);
					MPI_Send(&a[offset][0], rows * NCA, MPI_DOUBLE, dest, mtype,
							 MPI_COMM_WORLD);
					MPI_Send(&b, NCA * NCB, MPI_DOUBLE, dest, mtype, MPI_COMM_WORLD);
					offset = offset + rows;
				}

			/* Receive results from worker tasks */
			mtype = FROM_WORKER;
			for (i = 1; i <= numworkers; i++)
				{
					source = i;
					MPI_Recv(&offset, 1, MPI_INT, source, mtype, MPI_COMM_WORLD, &status);
					MPI_Recv(&rows, 1, MPI_INT, source, mtype, MPI_COMM_WORLD, &status);
					MPI_Recv(&c[offset][0], rows * NCB, MPI_DOUBLE, source, mtype,
							 MPI_COMM_WORLD, &status);
					printf("Resposta do calculo do processador %d recebida\n", source);
				}

			/* Print results */
			printf("******************************************************\n");
			printf("Matriz c resultante:\n");
			for (i = 0; i < NLA; i++)
				{
					printf("\n");
					for (j = 0; j < NCB; j++)
						printf("%6.2f   ", c[i][j]);
				}
			printf("\n******************************************************\n");
			printf ("\n");
		}


	/**************************** Processadores auxiliares (escravos) ************************************/
	if (taskid > MASTER)
		{
			mtype = FROM_MASTER;
			MPI_Recv(&offset, 1, MPI_INT, MASTER, mtype, MPI_COMM_WORLD, &status);
			MPI_Recv(&rows, 1, MPI_INT, MASTER, mtype, MPI_COMM_WORLD, &status);
			MPI_Recv(&a, rows * NCA, MPI_DOUBLE, MASTER, mtype, MPI_COMM_WORLD, &status);
			MPI_Recv(&b, NCA * NCB, MPI_DOUBLE, MASTER, mtype, MPI_COMM_WORLD, &status);

			for (k = 0; k < NCB; k++)
				for (i = 0; i < rows; i++)
					{
						c[i][k] = 0.0;
						for (j = 0; j < NCA; j++)
							c[i][k] = c[i][k] + a[i][j] * b[j][k];
					}
			mtype = FROM_WORKER;
			MPI_Send(&offset, 1, MPI_INT, MASTER, mtype, MPI_COMM_WORLD);
			MPI_Send(&rows, 1, MPI_INT, MASTER, mtype, MPI_COMM_WORLD);
			MPI_Send(&c, rows * NCB, MPI_DOUBLE, MASTER, mtype, MPI_COMM_WORLD);
		}
	MPI_Finalize();
}
