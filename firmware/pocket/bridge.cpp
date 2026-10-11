// PicoConsole display/input backend for GrgoMariani/Pocket Gamer (GPL3).
#include "../console.h"
#include <algorithm>
namespace pocket {
extern "C" {
#include "mainLoop.h"
#include "gpu.h"
#include "gameshared.h"
}
static uint16_t texture[64*64];
static const Callbacks* current_callbacks=nullptr;
extern "C" void ResetGame() { if(current_callbacks)current_callbacks->initCallback(); }
extern "C" const FontDescription fontDescription[4]={{nullptr,8,8},{nullptr,8,16},{nullptr,16,16},{nullptr,16,32}};
// Process return requests in the C++ outer loop, after C callbacks finish.
extern "C" uint32_t IF_GetCurrentTime() { return time_us_32(); }
extern "C" uint32_t IF_Random() { return RandU32(); }
extern "C" void GPU_ClearFramebuffers() { DrawClear(); }
extern "C" GPU_Color Texture_GetPixel(uint8_t x,uint8_t y) {return texture[(y%64)*64+x%64];}
extern "C" void Texture_CopyFrom(const uint16_t* data) { for(int i=0;i<4096;++i)texture[i]=(data[i]>>8)|(data[i]<<8); }
extern "C" void GPU_ClearTexture() { memset(texture,0,sizeof(texture)); }
extern "C" void GPU_DrawPixel(GPU_Color c,uint16_t x,uint16_t y) { DrawPoint(x,y,c); }
extern "C" void GPU_DrawFilledSquare(GPU_Color c,int16_t x,int16_t y,int16_t w,int16_t h) { DrawRect(x,y,w,h,c); }
extern "C" void GPU_DrawEmptySquare(GPU_Color c,int16_t x,int16_t y,int16_t w,int16_t h) { DrawFrame(x,y,w,h,c); }
static void letter(uint16_t* buf,int stride,int maxw,int maxh,GPU_Color c,const FontDescription* f,int x,int y,char ch) {
 for(int yy=0;yy<f->height;++yy) for(int xx=0;xx<f->width;++xx) {
  int dx=x+xx,dy=y+yy;
  if(dx>=0&&dx<maxw&&dy>=0&&dy<maxh && (FontBold8x16[(yy*16/f->height)*256+(u8)ch]&(0x80>>(xx*8/f->width))))buf[dy*stride+dx]=c;
 }
}
extern "C" void GPU_DrawText(GPU_Color c,const FontDescription* f,int16_t x,int16_t y,const char* s,uint16_t len) { for(unsigned i=0;i<len && s[i];++i)letter(FrameBuf,WIDTH,WIDTH,HEIGHT,c,f,x+i*f->width,y,s[i]); }
extern "C" void GPU_DrawLetter(GPU_Color c,const FontDescription* f,int16_t x,int16_t y,char ch) {letter(FrameBuf,WIDTH,WIDTH,HEIGHT,c,f,x,y,ch);}
extern "C" void Texture_DrawText(GPU_Color c,const FontDescription* f,int16_t x,int16_t y,const char* s,uint16_t len) { for(unsigned i=0;i<len && s[i];++i)letter(texture,64,64,64,c,f,x+i*f->width,y,s[i]); }
extern "C" void Texture_DrawEmptySquare(GPU_Color c,int16_t x,int16_t y,int16_t w,int16_t h) {
 for(int yy=0;yy<h;++yy) for(int xx=0;xx<w;++xx)if(xx==0||yy==0||xx==w-1||yy==h-1) {int dx=x+xx,dy=y+yy;if(dx>=0&&dx<64&&dy>=0&&dy<64)texture[dy*64+dx]=c;}
}
extern "C" void GPU_DrawRotatedTexture(int16_t x,int16_t y,float factor,float angle) {
 if(factor<=0)return;float co=cosf(angle)/factor,si=sinf(angle)/factor;int bound=int(ceilf(46*factor));
 for(int yy=-bound;yy<=bound;++yy) for(int xx=-bound;xx<=bound;++xx) {
  int sx=int(32+xx*co+yy*si),sy=int(32-xx*si+yy*co);
  if(sx>=0&&sx<64&&sy>=0&&sy<64) {u16 c=texture[sy*64+sx];if(c)DrawPoint(x+xx,y+yy,c);}
 }
}
extern "C" void GPU_DrawEmptyCircle(GPU_Color c,int16_t x,int16_t y,int16_t r) { for(int yy=-r;yy<=r;++yy)for(int xx=-r;xx<=r;++xx) {int d=xx*xx+yy*yy;if(d<=r*r&&d>=(r-1)*(r-1))DrawPoint(x+xx,y+yy,c);} }
extern "C" void GPU_DrawFilledCircle(GPU_Color c,int16_t x,int16_t y,int16_t r) { for(int yy=-r;yy<=r;++yy)for(int xx=-r;xx<=r;++xx)if(xx*xx+yy*yy<=r*r)DrawPoint(x+xx,y+yy,c); }
extern "C" void GPU_DrawLine(GPU_Color c,int16_t x,int16_t y,int16_t x2,int16_t y2) {
 int dx=abs(x2-x),sx=x<x2?1:-1,dy=-abs(y2-y),sy=y<y2?1:-1,e=dx+dy;
 while(true) {DrawPoint(x,y,c);if(x==x2&&y==y2)break;int e2=e*2;if(e2>=dy){e+=dy;x+=sx;}if(e2<=dx){e+=dx;y+=sy;} }
}
static void run(const Callbacks* cb) {
 current_callbacks=cb;memset(&mainMemory,0,sizeof(mainMemory));GPU_ClearTexture(); cb->initCallback();bool old_reset=false;uint32_t old_keys=0;int cursor_x=2,cursor_y=2;
 const int pins[]={BTN_UP_PIN,BTN_DOWN_PIN,BTN_LEFT_PIN,BTN_RIGHT_PIN};
 const KeyPressedEnum keys[]={KEY_UP,KEY_DOWN,KEY_LEFT,KEY_RIGHT};
 while(true) {
  console_service();uint32_t held=0;
  bool action=!game_gpio_get(BTN_A_PIN)||!game_gpio_get(3);
  for(int i=0;i<4;++i) {if(!game_gpio_get(pins[i]) || (i==1 && (cb==&G7_Callbacks||cb==&G8_Callbacks) && action) || (i==0 && cb==&G5_Callbacks && action)) {Key_Down(keys[i]);held|=1u<<i;}else Key_Up(keys[i]);}
  bool reset=!game_gpio_get(BTN_B_PIN)||!game_gpio_get(BTN_X_PIN);
  if(reset&&!old_reset)cb->initCallback();old_reset=reset;
  if(cb==&G3_Callbacks) {
   uint32_t edge=held&~old_keys;
   cursor_x=std::clamp(cursor_x+int(bool(edge&8))-int(bool(edge&4)),0,4);
   cursor_y=std::clamp(cursor_y+int(bool(edge&2))-int(bool(edge&1)),0,4);
   mainMemory.touchPressed=action;mainMemory.touch_X=cursor_x*48+24;mainMemory.touch_Y=cursor_y*48+24;
  } else if(cb==&G1_Callbacks||cb==&G2_Callbacks||cb==&G4_Callbacks) {
   uint32_t edge=held&~old_keys;int size=cb==&G4_Callbacks?4:3;
   cursor_x=std::clamp(cursor_x+int(bool(edge&8))-int(bool(edge&4)),0,size-1);
   cursor_y=std::clamp(cursor_y+int(bool(edge&2))-int(bool(edge&1)),0,size-1);
   mainMemory.touchPressed=action;
   mainMemory.touch_X=cb==&G4_Callbacks?56+cursor_x*52+26:55+cursor_x*70+35;
   mainMemory.touch_Y=cb==&G4_Callbacks?52+cursor_y*45+22:28+cursor_y*70+35;
  }
  old_keys=held;
  cb->updateCallback(); cb->drawCallback();
  if(cb==&G3_Callbacks) { DrawFrame(cursor_x*48+3,cursor_y*48+3,42,42,COL_CYAN); DrawFrame(cursor_x*48+4,cursor_y*48+4,40,40,C_WHITE); }
  if(cb==&G1_Callbacks||cb==&G2_Callbacks) {DrawFrame(56+cursor_x*70,29+cursor_y*70,68,68,COL_CYAN);DrawFrame(57+cursor_x*70,30+cursor_y*70,66,66,COL_CYAN);}
  if(cb==&G4_Callbacks) {DrawFrame(57+cursor_x*52,53+cursor_y*45,50,43,COL_CYAN);DrawFrame(58+cursor_x*52,54+cursor_y*45,48,41,COL_CYAN);}
  DispUpdate(); WaitMs(5);
 }
}
}
#include "entries.inc"
