#pragma once
#include "tk_probe_model.h"
bool tk_probe_ui_open(void);
void tk_probe_ui_draw(const tk_probe_t *m, const char *status, unsigned heap, unsigned largest, unsigned sent, unsigned failed, int comparison);
