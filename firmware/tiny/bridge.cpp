// SPDX-License-Identifier: GPL-3.0-only
// PicoConsole joystick/display bridge, 2026-10-11.
#include "../console.h"
#include "runtime.h"
extern "C" {extern int trmoScore,trmoLevel,trmoLinesCleared,trmoNextPiece[16];}
static void label(const char* s,int x,int y,u16 c=COL_WHITE){DrawText2(s,x,y,c);}
static void tiny_run(int index) {
 tiny_select(index);
 while(true) {
  uint32_t deadline=time_us_32()+16667;
  console_service();unsigned k=0;
  if(KeyPressed(KEY_UP))k|=1;if(KeyPressed(KEY_DOWN))k|=2;
  if(KeyPressed(KEY_LEFT))k|=4;if(KeyPressed(KEY_RIGHT))k|=8;
  if(KeyPressed(KEY_A)||KeyPressed(3))k|=16;
  if(KeyPressed(KEY_B)||KeyPressed(KEY_X))k|=32;
  tiny_input(k);tiny_update();tiny_render(FrameBuf,WIDTH);SelFont6x8();
  if(tiny_is_tetromino()) {
   char s[16];label("SCORE",44,12);snprintf(s,sizeof(s),"%d",trmoScore);label(s,44,34,COL_YELLOW);
   label("LEVEL",44,76);snprintf(s,sizeof(s),"%d",trmoLevel);label(s,44,98,COL_YELLOW);
   label("LINES",44,140);snprintf(s,sizeof(s),"%d",trmoLinesCleared);label(s,44,162,COL_YELLOW);
   label("NEXT",220,12);for(int y=0;y<4;++y)for(int x=0;x<4;++x)if(trmoNextPiece[y*4+x])DrawRect(224+x*10,38+y*10,9,9,COL_CYAN);
   label("A",232,100);label("TURN",220,120,COL_CYAN);label("DOWN",220,160);label("DROP",220,180,COL_CYAN);label("Y MENU",208,218,COL_YELLOW);
  } else {label(tiny_game_title(index),44,6);DrawRect(44,30,232,2,COL_CYAN);label("A ACT B ALT Y MENU",44,216);}
  DispUpdate();
  int32_t remaining=deadline-time_us_32();if(remaining>0)WaitUs(remaining);
 }
}
#include "entries.inc"
