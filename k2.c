#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <omp.h>

// gcc k2.c -o k2.o -fopenmp -lm -O3

int main(int argc, char* argv[]) {
    if (argc < 3 || argc > 4) {
        printf("Użycie: %s <dolny_zakres> <gorny_zakres> [chunk_size]\n", argv[0]);
        return 1;
    }

    int m = atoi(argv[1]);
    int n = atoi(argv[2]);
    
    // Default chunk size is 2
    int chunk_size = 2;
    bool dynamic_schedule = false;
    
    // Process the third argument if provided
    if (argc == 4) {
        if (strcmp(argv[3], "dynamic") == 0) {
            dynamic_schedule = true;
        } else {
            chunk_size = atoi(argv[3]);
            if (chunk_size <= 0) {
                printf("Chunk size musi być liczbą dodatnią lub słowem 'dynamic'.\n");
                return 1;
            }
        }
    }

    if (m > n || m < 2) {
        printf("Zakres nieprawidłowy. Upewnij się, że m >= 2 i m <= n.\n");
        return 1;
    }

    double start_time = omp_get_wtime();

    bool* result = (bool*)malloc((n - m + 1) * sizeof(bool));
    memset(result, true, (n - m + 1) * sizeof(bool));

    bool* primeArray = (bool*)malloc((int)(sqrt(n) + 1) * sizeof(bool));
    memset(primeArray, true, (int)(sqrt(n) + 1) * sizeof(bool));

    for (int i = 2; i * i <= n; i++) {
        for (int j = 2; j * j <= i; j++) {
            if (primeArray[j] == true && i % j == 0) {
                primeArray[i] = false;
                break;
            }
        }
    }

    #pragma omp parallel
    {
        if (dynamic_schedule) {
            #pragma omp for schedule(dynamic)
            for (int i = m; i <= n; i++) {
                for (int j = 2; j * j <= i; j++) {
                    if (primeArray[j] == true && i % j == 0) {
                        result[i - m] = false;
                        break;
                    }
                }
            }
        } else {
            #pragma omp for schedule(static, chunk_size)
            for (int i = m; i <= n; i++) {
                for (int j = 2; j * j <= i; j++) {
                    if (primeArray[j] == true && i % j == 0) {
                        result[i - m] = false;
                        break;
                    }
                }
            }
        }
    }

    // printf("Liczby pierwsze w zakresie [%d, %d]:\n", m, n);
    // for (int i = 0; i <= n - m; i++) {
    //     if (result[i]) {
    //         printf("%d ", i + m);
    //     }
    // }
    // printf("\n");

    double end_time = omp_get_wtime();
    printf("Czas przetwarzania: %.6f sekund\n", end_time - start_time);
    
    if (dynamic_schedule) {
        printf("Użyto harmonogramu: dynamic\n");
    } else {
        printf("Użyto harmonogramu: static z rozmiarem bloku %d\n", chunk_size);
    }

    free(result);
    free(primeArray);

    return 0;
}