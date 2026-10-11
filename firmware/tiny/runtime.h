// SPDX-License-Identifier: GPL-3.0-only
// PicoConsole TinyJoypad platform, 2026-10-11.
#pragma once
#ifdef __cplusplus
extern "C" {
#endif
void tiny_select(int index);
void tiny_update(void);
void tiny_reset(void);
void tiny_input(unsigned keys);
void tiny_render(unsigned short* frame, int stride);
void tiny_set_layout(int layout);
int tiny_is_tetromino(void);
int tiny_game_count(void);
const char* tiny_game_title(int index);
#ifdef __cplusplus
}
#endif
