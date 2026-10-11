// SPDX-License-Identifier: GPL-3.0-only
// Original PicoConsole platform; no SDL, disk files or audio output.
#include "runtime.h"
#include "core/machineDependent.h"
#include <stdint.h>
#include <string.h>
static uint8_t pixels[84*6],gray[84*6],eeprom[1024];
static unsigned keys;static int frame,held[7],layout;
void gamebuino_set_layout(int l){layout=l;}
extern int tetState;
int gamebuino_is_portrait(void){return layout==1&&tetState==1;}
extern void gbBegin(void);extern void gbSetEngineFrameRate(int);
void gamebuino_reset(void){memset(pixels,0,sizeof(pixels));memset(gray,0,sizeof(gray));memset(eeprom,255,sizeof(eeprom));memset(held,0,sizeof(held));keys=0;frame=0;gbSetEngineFrameRate(60);gbBegin();}
void gamebuino_input(unsigned k){
 if(gamebuino_is_portrait()){unsigned n=k&~15u;if(k&4)n|=1;if(k&8)n|=2;if(k&2)n|=4;if(k&1)n|=8;k=n;}
 keys=k;++frame;for(int i=0;i<7;++i)held[i]=(keys&(1u<<i))?held[i]+1:0;
}
void gamebuino_render(unsigned short* fb,int stride){
 for(int y=0;y<240;++y)for(int x=40;x<280;++x)fb[y*stride+x]=0;
 if(gamebuino_is_portrait()){
  // Original falling-block game is sideways: rotate counterclockwise.
  // Crop the 68x32 board before rotation; draw a readable HUD separately.
  for(int y=0;y<204;++y)for(int x=0;x<96;++x){int sx=67-y/3,sy=x/3,o=(sy/8)*84+sx,b=1u<<(sy%8);fb[(18+y)*stride+112+x]=(pixels[o]&b)?0xffff:(gray[o]&b)?(((x/2+y/2)&1)?0xffff:0):0;}
  return;
 }
 for(int y=0;y<137;++y)for(int x=0;x<240;++x){int sx=x*84/240,sy=y*48/137,o=(sy/8)*84+sx,b=1u<<(sy%8);fb[(48+y)*stride+40+x]=(pixels[o]&b)?0xffff:(gray[o]&b)?(((x/2+y/2)&1)?0xffff:0):0;}
}
void gb_md_beginFrame(void){memset(pixels,0,sizeof(pixels));memset(gray,0,sizeof(gray));}
void gb_md_drawColumn(int x,int p,int v){if(x>=0&&x<84&&p>=0&&p<6)pixels[p*84+x]=(uint8_t)v;}
void gb_md_drawColumnGray(int x,int p,int v){if(x>=0&&x<84&&p>=0&&p<6)gray[p*84+x]=(uint8_t)v;}
bool gb_md_inputUp(void){return (keys&1)!=0;}bool gb_md_inputDown(void){return (keys&2)!=0;}
bool gb_md_inputLeft(void){return (keys&4)!=0;}bool gb_md_inputRight(void){return (keys&8)!=0;}
bool gb_md_inputA(void){return (keys&16)!=0;}bool gb_md_inputB(void){return (keys&32)!=0;}bool gb_md_inputC(void){return (keys&64)!=0;}
bool gb_md_inputStart(void){return false;}bool gb_md_inputR(void){return false;}
int gb_md_inputUpFrames(void){return held[0];}int gb_md_inputDownFrames(void){return held[1];}int gb_md_inputLeftFrames(void){return held[2];}int gb_md_inputRightFrames(void){return held[3];}int gb_md_inputAFrames(void){return held[4];}
int gb_md_getFrameCounter(void){return frame;}void gb_md_armInputAGate(void){}
void gb_md_playTone(float f,float d){(void)f;(void)d;}void gb_md_stopTone(void){}void gb_md_updateAudio(void){}
int gb_md_trackerVoiceStart(float f,float v){(void)f;(void)v;return -1;}void gb_md_trackerVoiceRetune(int c,float f,float v){(void)c;(void)f;(void)v;}void gb_md_trackerVoiceStop(int c){(void)c;}
void gb_eepromSelectGame(char* t){(void)t;memset(eeprom,255,sizeof(eeprom));}
int gb_eeprom_read_byte(int a){return a>=0&&a<(int)sizeof(eeprom)?eeprom[a]:255;}void gb_eeprom_write_byte(int a,int v){if(a>=0&&a<(int)sizeof(eeprom))eeprom[a]=(uint8_t)v;}void gb_eeprom_update_byte(int a,int v){gb_eeprom_write_byte(a,v);}
int gb_eeprom_read_word(int a){return gb_eeprom_read_byte(a)|(gb_eeprom_read_byte(a+1)<<8);}void gb_eeprom_write_word(int a,int v){gb_eeprom_write_byte(a,v);gb_eeprom_write_byte(a+1,v>>8);}
int gb_eeprom_read_dword(int a){return (int)((uint32_t)gb_eeprom_read_word(a)|((uint32_t)gb_eeprom_read_word(a+2)<<16));}void gb_eeprom_write_dword(int a,int v){gb_eeprom_write_word(a,v);gb_eeprom_write_word(a+2,(unsigned)v>>16);}
void gb_eeprom_read_block(void* p,int a,int n){for(int i=0;i<n;++i)((uint8_t*)p)[i]=(uint8_t)gb_eeprom_read_byte(a+i);}void gb_eeprom_write_block(void* p,int a,int n){for(int i=0;i<n;++i)gb_eeprom_write_byte(a+i,((uint8_t*)p)[i]);}void gb_eeprom_busy_wait(void){}
