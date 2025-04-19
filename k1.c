#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>
#include <time.h>

// gcc k1.c -o k1.o -lm -O3

int main(int argc, char* argv[]) {
    if (argc != 3) {
        printf("Użycie: %s <dolny_zakres> <gorny_zakres>\n", argv[0]);
        return 1;
    }

    int m = atoi(argv[1]);
    int n = atoi(argv[2]);

    if (m > n || m < 2) {
        printf("Zakres nieprawidłowy. Upewnij się, że m >= 2 i m <= n.\n");
        return 1;
    }

    clock_t start = clock();

    int range = n - m + 1;
    bool* result = (bool*)malloc(range * sizeof(bool));
    memset(result, true, range * sizeof(bool));

    int sqrt_n = (int)sqrt(n) + 1;
    bool* primeArray = (bool*)malloc(sqrt_n * sizeof(bool));
    memset(primeArray, true, sqrt_n * sizeof(bool));

    for (int i = 2; i * i <= n; i++) {
        for (int j = 2; j * j <= i; j++) {
            if (primeArray[j] && i % j == 0) {
                primeArray[i] = false;
                break;
            }
        }
    }

    for (int i = m; i <= n; i++) {
        for (int j = 2; j * j <= i; j++) {
            if (primeArray[j] && i % j == 0) {
                result[i - m] = false;
                break;
            }
        }
    }

    printf("Liczby pierwsze w zakresie [%d, %d]:\n", m, n);
    for (int i = 0; i < range; i++) {
        if (result[i]) {
            printf("%d ", i + m);
        }
    }
    printf("\n");

    clock_t end = clock();
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    printf("Czas przetwarzania: %.6f sekund\n", time_spent);

    free(result);
    free(primeArray);

    return 0;
}
