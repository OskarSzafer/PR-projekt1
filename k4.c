#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <time.h>
#include <omp.h>  

//gcc k4.c -o k4.o -lm -fopenmp -O3

int main(int argc, char* argv[]) {
    if (argc < 3 || argc > 4) {
        printf("Użycie: %s <dolny_zakres> <gorny_zakres> [chunk_size/dynamic]\n", argv[0]);
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

    int range = n - m + 1;
    bool* result = (bool*)malloc(range * sizeof(bool));
    memset(result, true, range * sizeof(bool));

    int sqrt_n = (int)sqrt(n) + 1;
    bool* primeArray = (bool*)malloc((n + 1) * sizeof(bool));
    memset(primeArray, true, (n + 1) * sizeof(bool));

    for (int i = 2; i * i * i * i <= n; i++) {
        if (primeArray[i]) {
            for (int j = i * i; j * j <= n; j += i) {
                primeArray[j] = false;
            }
        }
    }

    if (dynamic_schedule) {
        #pragma omp parallel for schedule(dynamic)
        for (int i = 2; i <= sqrt_n; i++) {
            if (primeArray[i]) {
                int firstMultiple = (m / i);
                if (firstMultiple <= 1) {
                    firstMultiple = i + i;
                } else if (m % i) {
                    firstMultiple = (firstMultiple * i) + i;
                } else {
                    firstMultiple = (firstMultiple * i);
                }

                for (int j = firstMultiple; j <= n; j += i) {
                    result[j - m] = false;
                }
            }
        }
    } else {
        #pragma omp parallel for schedule(static, chunk_size)
        for (int i = 2; i <= sqrt_n; i++) {
            if (primeArray[i]) {
                int firstMultiple = (m / i);
                if (firstMultiple <= 1) {
                    firstMultiple = i + i;
                } else if (m % i) {
                    firstMultiple = (firstMultiple * i) + i;
                } else {
                    firstMultiple = (firstMultiple * i);
                }

                for (int j = firstMultiple; j <= n; j += i) {
                    result[j - m] = false;
                }
            }
        }
    }

    // printf("Liczby pierwsze w zakresie [%d, %d]:\n", m, n);
    // for (int i = 0; i < range; i++) {
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