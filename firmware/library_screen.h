// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "library.h"
namespace library {
void draw_menu(uint16_t* pixels,int stride,const uint8_t* font,const Menu& menu,
               const char* (*title)(int),bool save_failed);
}
