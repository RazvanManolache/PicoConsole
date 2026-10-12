// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <cstdint>
namespace library {
constexpr int preview_width=112,preview_height=32,preview_bytes=448;
int preview_count();
bool preview_bitmap(int game,uint8_t* destination);
void draw_preview(uint16_t* pixels,int stride,int game,int y,bool selected);
}
