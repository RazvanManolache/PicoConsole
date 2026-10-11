#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include "pico/stdlib.h"

using u8 = uint8_t; using s8 = int8_t;
using u16 = uint16_t; using s16 = int16_t; using u32 = uint32_t;
using s32 = int32_t; using u64 = uint64_t; using s64 = int64_t;
using Bool = uint8_t;
constexpr bool True=true,False=false;
void console_service();
constexpr float PI=3.14159265358979323846f;
constexpr float PI2=PI*2;
inline void sincosf(float a,float* s,float* c) { *s=sinf(a); *c=cosf(a); }
constexpr int SNDFORM_PCM=0;
constexpr int SNDFORM_ADPCM=1;
#define ALIGNED __attribute__((aligned(4)))
#define MemPrint snprintf
#define StrLen strlen
inline int f2i(float f) { return int(f); }
#define BIT(n) (1u<<(n))
inline u32 Mask(u32 n) { n |= n>>1; n |= n>>2; n |= n>>4; n |= n>>8; return n | (n>>16); }
#define COLOR(r,g,b) (u16((((r)&0xf8)<<8)|(((g)&0xfc)<<3)|(((b)&0xf8)>>3)))
#define PLAYSOUND(...) ((void)0)
#define PLAYSOUNDREP(...) ((void)0)
#define DISP_STRIP_NUM 1
constexpr int NOKEY=0,DECNUMBUF_SIZE=32;
inline char DecNumBuf[DECNUMBUF_SIZE];
inline int DecNum(char* p,s32 n,char) { return sprintf(p,"%ld",(long)n); }
inline int DecUNum(char* p,u32 n,char) { return sprintf(p,"%lu",(unsigned long)n); }
inline void VgaWaitVSync() { console_service(); }
struct pText { char data[512]; };
inline void TextInit(pText* p) { p->data[0]=0; }
inline void TextTerm(pText*) {}
inline void TextEmpty(pText* p) { p->data[0]=0; }
inline int TextLen(const pText* p) { return strlen(p->data); }
inline const char* TextPtr(const pText* p) { return p->data; }
inline void TextAddStr(pText* p,const char* s) { strncat(p->data,s,511-strlen(p->data)); }
inline void TextSetStr(pText* p,const char* s) { TextEmpty(p); TextAddStr(p,s); }
inline void TextAddCh(pText* p,char ch) { char s[]={ch,0}; TextAddStr(p,s); }
inline void TextAddSpc(pText* p) { TextAddCh(p,' '); }
inline void TextAddUInt(pText* p,u32 n,char=0) { char s[32]; sprintf(s,"%lu",(unsigned long)n); TextAddStr(p,s); }
inline void UsbPortTerm() {}
inline void UsbPortInit(int) {}
constexpr int USBPORT_CMD_QUIT=4;
constexpr int USBPORT_CMD_APP=8;
#define INLINE inline
#define NOFLASH(x) x
#define FASTCODE
constexpr u16 COL_BLACK=0,COL_WHITE=0xffff,COL_RED=0xf800,COL_GREEN=0x07e0,COL_BLUE=0x001f;
constexpr u16 COL_YELLOW=0xffe0,COL_CYAN=0x07ff,COL_MAGENTA=0xf81f,COL_ORANGE=0xfd20;
constexpr u16 COL_GRAY=0x8410,COL_LTGREEN=0x87f0,COL_LTGRAY=0xc618,COL_DKGRAY=0x4208;
constexpr u16 COL_AZURE=0x7dff,COL_DKBLUE=0x0010,COL_DKGREEN=0x0400,COL_LTBLUE=0x841f,COL_LTRED=0xfc10,COL_LTYELLOW=0xfff0;
inline bool IsPow2(unsigned n) { return n && !(n&(n-1)); }
#define B0 (1u<<0)
#define B1 (1u<<1)
#define B2 (1u<<2)
#define B3 (1u<<3)
#define B4 (1u<<4)
#define B5 (1u<<5)
#define B6 (1u<<6)
#define B7 (1u<<7)
#define B8 (1u<<8)
#define B9 (1u<<9)
#define B10 (1u<<10)
#define B11 (1u<<11)
#define B12 (1u<<12)
#define B13 (1u<<13)
#define B14 (1u<<14)
#define B15 (1u<<15)
#define COLTYPE u16
#define FRAMETYPE u16
#define WIDTHLEN WIDTH
#define COLBITS 16
#define USE_DRAW 1
#define USE_MAT2D 1
#define USE_INTERP 0
#define pDrawBuf FrameBuf
#define DispMinY 0
#define DispMaxY HEIGHT
#define FONTH 16
#define FONTW 8
#define COL_PRINT_DEF 0xffff
inline int float2int(float f) { return int(f); }
extern const u8 FontBold8x8[],FontBold8x14[],FontBold8x16[],FontCond6x8[],FontTiny5x8[];
constexpr int WIDTH=320, HEIGHT=240, KEY_NUM=9;
constexpr int BTN_UP_PIN=2, BTN_DOWN_PIN=18, BTN_LEFT_PIN=16, BTN_RIGHT_PIN=20;
constexpr int BTN_A_PIN=15, BTN_B_PIN=17, BTN_X_PIN=19, BTN_Y_PIN=21;
constexpr int KEY_Y=21, PWMSND_GPIO=25;
constexpr int KEY_UP=2,KEY_DOWN=18,KEY_LEFT=16,KEY_RIGHT=20,KEY_A=15,KEY_B=17,KEY_X=19,KEY_NONE=0;
constexpr int LED1=0,LED2=1;
inline void LedOn(int) {} inline void LedOff(int) {}
#define USE_SCREENSHOT 0
extern u16 FrameBuf[WIDTH*HEIGHT];
struct ConsoleConfig { int volume=0; };
extern ConsoleConfig Config;
struct ReturnToMenu {};
void console_service();
bool game_gpio_get(int pin);
void WaitMs(uint32_t ms);
void WaitUs(uint32_t us);
void DispUpdate();
void console_set_rotated(bool enabled);
void console_stats(int level,int lives);
u8 KeyGet();
void KeyFlush();
inline u32 Time() { console_service(); return time_us_32(); }
inline u64 Time64() { console_service(); return time_us_64(); }
inline u32 RandShift() { return (u32(rand())<<16)^u32(rand()); }
inline u8 RandU8() { return RandShift(); }
inline u16 RandU16() { return RandShift(); }
inline u32 RandU32() { return RandShift(); }
inline u8 RandU8Max(u8 n) { return RandShift()%(u32(n)+1); }
inline u16 RandU16Max(u16 n) { return RandShift()%(u32(n)+1); }
inline u8 RandU8MinMax(u8 a,u8 b) { return a+RandU8Max(b-a); }
inline u16 RandU16MinMax(u16 a,u16 b) { return a+RandU16Max(b-a); }
inline s8 RandS8MinMax(s8 a,s8 b) { return a+RandU8Max(b-a); }
inline s16 RandS16MinMax(s16 a,s16 b) { return a+RandU16Max(b-a); }
inline s16 RandS16Max(s16 n) { return RandS16MinMax(0,n); }
inline float RandFloat() { return float(RandShift())/4294967296.0f; }
inline float RandFloatMax(float n) { return RandFloat()*n; }
inline float RandFloatMinMax(float a,float b) { return a+(b-a)*RandFloat(); }
template<class... T> inline void PlaySoundChan(T...) {}
template<class... T> inline void PlaySound(T...) {}
template<class... T> inline void SetNextSound(T...) {}
template<class... T> inline void StopSoundChan(T...) {}
template<class... T> inline void SpeedSound(T...) {}
template<class... T> inline bool PlayingSoundChan(T...) { return false; }
inline void StopSound() {} inline void StopAllSound() {} inline bool PlayingSound() { return false; }
inline bool DispSetStripNext() { return false; }
inline void DispUpdateAll() { DispUpdate(); }
inline void DispDirtyRect(int,int,int,int) {}
inline void DispSetStripOff() {}
inline void DispDirtyPoint(int,int) {}
inline void DispDirtyAll() {}
inline bool KeyPressed(int pin) { return !game_gpio_get(pin); }
inline void ResetToBootLoader() { throw ReturnToMenu{}; }
#include "compat/lib_draw.h"
#include "games/registry.h"
