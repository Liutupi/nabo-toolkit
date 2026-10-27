#pragma once
#include "FreeRTOS.h"
typedef void *SemaphoreHandle_t;
static inline SemaphoreHandle_t xSemaphoreCreateMutex(void){static int token;return &token;}
static inline int xSemaphoreTake(SemaphoreHandle_t semaphore,unsigned ticks){(void)semaphore;(void)ticks;return pdTRUE;}
static inline int xSemaphoreGive(SemaphoreHandle_t semaphore){(void)semaphore;return pdTRUE;}
