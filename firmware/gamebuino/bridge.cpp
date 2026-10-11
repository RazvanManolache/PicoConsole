// SPDX-License-Identifier: GPL-3.0-only
#include "../console.h"
#include "runtime.h"
extern "C" {extern int tetScore,tetLevel,tetNextCells[4][4];extern bool tetIsOver,tetIsPaused;}
static void gamebuino_run(int index){
 gamebuino_select(index);
 while(true){uint32_t deadline=time_us_32()+16667;console_service();unsigned k=0;
  if(KeyPressed(KEY_UP))k|=1;if(KeyPressed(KEY_DOWN))k|=2;if(KeyPressed(KEY_LEFT))k|=4;if(KeyPressed(KEY_RIGHT))k|=8;
  if(KeyPressed(KEY_A)||KeyPressed(3))k|=16;if(KeyPressed(KEY_B))k|=32;if(KeyPressed(KEY_X))k|=64;
  gamebuino_input(k);gamebuino_update();gamebuino_render(FrameBuf,WIDTH);SelFont6x8();
  if(gamebuino_is_portrait()){
   char s[16];DrawText2("SCORE",44,12,COL_WHITE);snprintf(s,sizeof(s),"%d",tetScore);DrawText2(s,44,34,COL_YELLOW);
   DrawText2("LEVEL",44,76,COL_WHITE);snprintf(s,sizeof(s),"%d",tetLevel);DrawText2(s,44,98,COL_YELLOW);
   DrawText2("NEXT",220,12,COL_WHITE);for(int y=0;y<4;++y)for(int x=0;x<4;++x)if(tetNextCells[y][x])DrawRect(224+x*10,38+y*10,9,9,COL_CYAN);
   DrawText2("A",232,100,COL_WHITE);DrawText2("TURN",220,120,COL_CYAN);DrawText2("DOWN",220,160,COL_WHITE);DrawText2("DROP",220,180,COL_CYAN);DrawText2("Y MENU",208,218,COL_YELLOW);
   if(tetIsOver||tetIsPaused){DrawRect(116,96,88,44,COL_BLACK);DrawText2(tetIsOver?"GAME":"PAUSED",120,100,COL_YELLOW);if(tetIsOver)DrawText2("OVER",136,120,COL_YELLOW);}
  }
  else {DrawText2(gamebuino_game_title(index),44,4,COL_WHITE);DrawRect(44,30,232,2,COL_CYAN);DrawText2("A/B/X ACT Y MENU",44,216,COL_WHITE);}DispUpdate();
  int32_t remaining=deadline-time_us_32();if(remaining>0)WaitUs(remaining);
 }
}
#include "entries.inc"
