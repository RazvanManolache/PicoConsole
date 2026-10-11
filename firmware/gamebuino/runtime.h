// SPDX-License-Identifier: GPL-3.0-only
#pragma once
#ifdef __cplusplus
extern "C" {
#endif
void gamebuino_select(int index);
void gamebuino_update(void);
void gamebuino_reset(void);
void gamebuino_set_layout(int layout);
int gamebuino_is_portrait(void);
void gamebuino_input(unsigned keys);
void gamebuino_render(unsigned short* frame,int stride);
int gamebuino_game_count(void);
const char* gamebuino_game_title(int index);
#ifdef __cplusplus
}
#endif
