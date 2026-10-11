// SPDX-License-Identifier: GPL-3.0-only
// Original PicoConsole platform. No SDL, audio, storage or desktop dependencies.
#include "runtime.h"
#include "core/machineDependent.h"
#include <string.h>
#include <stdint.h>
static uint8_t oled[128*8], eeprom[1024];
static unsigned keys;
static int frame, held[6],layout;
extern int trmoState,npMode;
extern void tinyCoreReset(void);
void tiny_reset(void) {
 memset(oled,0,sizeof(oled));memset(eeprom,255,sizeof(eeprom));
 keys=0;frame=0;memset(held,0,sizeof(held));tinyCoreReset();
}
void tiny_input(unsigned k) {
 if(layout==1)k=(k&48)|((k&4)?2:0)|((k&8)?1:0)|((k&2)?4:0)|((k&1)?16:0);
 keys=k;++frame;
 for(int i=0;i<6;++i)held[i]=(keys&(1u<<i))?held[i]+1:0;
}
void tiny_render(unsigned short* fb,int stride) {
 for(int y=0;y<240;++y)for(int x=40;x<280;++x)fb[y*stride+x]=0;
 if(tiny_is_tetromino()) {
  // Clockwise board rotation: gravity now points down. 3x pixels, upright HUD.
  for(int y=0;y<222;++y)for(int x=0;x<96;++x) {
   int sx=30+y/3,sy=31-x/3;
   fb[(10+y)*stride+112+x]=(oled[(sy/8)*128+sx]&(1u<<(sy%8)))?0xffff:0;
  }
 } else if(layout==2&&npMode==2) {
  // 9x9 board gets 168 square pixels; tools retain a separate 2x side panel.
  for(int y=0;y<168;++y)for(int x=0;x<168;++x) {
   int sx=28+x*64/168,sy=y*64/168;
   fb[(36+y)*stride+44+x]=(oled[(sy/8)*128+sx]&(1u<<(sy%8)))?0xffff:0;
  }
  for(int y=0;y<128;++y)for(int x=0;x<64;++x) {
   int sx=96+x/2,sy=y/2;
   fb[(54+y)*stride+212+x]=(oled[(sy/8)*128+sx]&(1u<<(sy%8)))?0xffff:0;
  }
 } else for(int y=0;y<120;++y)for(int x=0;x<240;++x) {
  int sx=x*128/240,sy=y*64/120;
  fb[(54+y)*stride+40+x]=(oled[(sy/8)*128+sx]&(1u<<(sy%8)))?0xffff:0;
 }
}
void tiny_set_layout(int value){layout=value;}
int tiny_is_tetromino(void){return layout==1&&trmoState==1;}
void tj_md_beginFrame(void){memset(oled,0,sizeof(oled));}
void tj_md_drawColumn(int x,int p,int value){if(x>=0&&x<128&&p>=0&&p<8)oled[p*128+x]=(uint8_t)value;}
void tj_md_endFrame(void){}
bool tj_md_inputUp(void){return (keys&1)!=0;}
bool tj_md_inputDown(void){return (keys&2)!=0;}
bool tj_md_inputLeft(void){return (keys&4)!=0;}
bool tj_md_inputRight(void){return (keys&8)!=0;}
bool tj_md_inputFire(void){return (keys&16)!=0;}
bool tj_md_inputFire2(void){return (keys&32)!=0;}
bool tj_md_inputStart(void){return false;}
int tj_md_inputUpFrames(void){return held[0];}
int tj_md_inputDownFrames(void){return held[1];}
int tj_md_inputLeftFrames(void){return held[2];}
int tj_md_inputRightFrames(void){return held[3];}
int tj_md_inputFireFrames(void){return held[4];}
int tj_md_getFrameCounter(void){return frame;}
void tj_md_armInputFireGate(void){}
void tj_md_playTone(float frequency,float duration){(void)frequency;(void)duration;}
void tj_md_stopTone(void){}
void tj_md_updateAudio(void){}
void tj_md_initAudio(void){}
void eepromSelectGame(char* title){(void)title;memset(eeprom,255,sizeof(eeprom));}
int eeprom_read_byte(int a){return a>=0&&a<(int)sizeof(eeprom)?eeprom[a]:255;}
void eeprom_write_byte(int a,int v){if(a>=0&&a<(int)sizeof(eeprom))eeprom[a]=(uint8_t)v;}
void eeprom_update_byte(int a,int v){eeprom_write_byte(a,v);}
int eeprom_read_word(int a){return eeprom_read_byte(a)|(eeprom_read_byte(a+1)<<8);}
void eeprom_write_word(int a,int v){eeprom_write_byte(a,v);eeprom_write_byte(a+1,v>>8);}
int eeprom_read_dword(int a){return (int)((uint32_t)eeprom_read_word(a)|((uint32_t)eeprom_read_word(a+2)<<16));}
void eeprom_write_dword(int a,int v){eeprom_write_word(a,v);eeprom_write_word(a+2,(unsigned)v>>16);}
void eeprom_read_block(void* p,int a,int n){for(int i=0;i<n;++i)((uint8_t*)p)[i]=(uint8_t)eeprom_read_byte(a+i);}
void eeprom_write_block(void* p,int a,int n){for(int i=0;i<n;++i)eeprom_write_byte(a+i,((uint8_t*)p)[i]);}
void eeprom_busy_wait(void){}
