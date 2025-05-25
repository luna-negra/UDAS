#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>


int count = 0;
const int ARR_LEN = 5;

void * count_up(void * arg)
{
    pthread_mutex_t * lock = (pthread_mutex_t *)arg;

    for (int i=0; i<10000; i++)
    {
        pthread_mutex_lock(lock);
        count++;
        pthread_mutex_unlock(lock);
    }

    return NULL;
}

int main (int argc, char * argv [])
{
    pthread_t thread_arr[ARR_LEN];
    pthread_mutex_t * lock = malloc(sizeof(pthread_mutex_t));
    int r = pthread_mutex_init(lock, NULL);

    // create and run thread.
    for (int i = 0; i < ARR_LEN; i++)
    {
        pthread_create(thread_arr + i, NULL, count_up, lock);
    }

    // maintain thread until the thread ends.
    for (int i = 0; i< ARR_LEN; i++)
    {
        pthread_join(thread_arr[i], NULL);
    }

    pthread_mutex_destroy(lock);
    free(lock);
    printf("%d\n", count);
    return 0;
}