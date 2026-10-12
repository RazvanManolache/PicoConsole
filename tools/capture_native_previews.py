"""Render curated C++ games on a desktop for preview artwork (no hardware test).
SPDX-License-Identifier: GPL-3.0-or-later
"""
from pathlib import Path
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--gxx',required=True);p.add_argument('--game');p.add_argument('--seconds',type=int,default=18);p.add_argument('--drop',action='store_true');a=p.parse_args()
out=ROOT/'logs/preview-native';out.mkdir(parents=True,exist_ok=True)
stub=out/'stubs/pico';stub.mkdir(parents=True,exist_ok=True)
(stub/'stdlib.h').write_text('''#pragma once
#include <cstdint>
#include <cstdlib>
inline long random(){return rand();}
template<class T,unsigned long long N> constexpr unsigned long long count_of(T (&)[N]){return N;}
uint64_t host_clock();
inline uint32_t time_us_32(){return host_clock();}
inline uint64_t time_us_64(){return host_clock();}
inline uint64_t get_absolute_time(){return host_clock();}
inline uint32_t to_ms_since_boot(uint64_t t){return t/1000;}
''')
games=[g for g in json.loads((ROOT/'tools/native_catalog.json').read_text()) if g['group'] in ('TINYGAME','GAME')]
host=r'''#include "console.h"
#include <string>
u16 FrameBuf[WIDTH*HEIGHT];ConsoleConfig Config;
static uint64_t ticks=0,next_shot=1000000;static unsigned old=0;static bool rotated=false;
static const char* output;
void console_set_rotated(bool x){rotated=x;}
void console_stats(int,int){}
static unsigned input(){
 unsigned ms=ticks/1000;
 // Repeated confirmations enter nested title/difficulty/level menus.
 if(ms<12000)return ms%600>=400?16:0;
 if(DROP)return ms%600<300?2:0;
 return ms%1800<1600?0:4;
}
static void shot(){char name[512];sprintf(name,"%s-%02u.rgb565",output,unsigned(next_shot/1000000));
 FILE* f=fopen(name,"wb");fwrite(FrameBuf,2,WIDTH*HEIGHT,f);fclose(f);
 FILE* r=fopen((std::string(name)+".json").c_str(),"w");fprintf(r,"{\"rotated\":%s}",rotated?"true":"false");fclose(r);
}
void console_service(){ticks+=100;if(ticks>=next_shot){shot();next_shot+=1000000;}if(ticks>=ENDTIME)throw ReturnToMenu{};}
uint64_t host_clock(){console_service();return ticks;}
bool game_gpio_get(int pin){console_service();int n=pin==KEY_UP?0:pin==KEY_DOWN?1:pin==KEY_LEFT?2:pin==KEY_RIGHT?3:pin==KEY_A?4:pin==KEY_B?5:6;return !(input()&(1u<<n));}
void WaitMs(uint32_t n){uint64_t end=ticks+uint64_t(n)*1000;while(ticks<end)console_service();}
void WaitUs(uint32_t n){uint64_t end=ticks+n;while(ticks<end)console_service();}
void DispUpdate(){console_service();}
void KeyFlush(){console_service();old=input();}
u8 KeyGet(){console_service();unsigned k=input(),p=k&~old;old=k;int keys[]={KEY_UP,KEY_DOWN,KEY_LEFT,KEY_RIGHT,KEY_A,KEY_B,KEY_X};for(int i=0;i<7;++i)if(p&(1u<<i))return keys[i];return 0;}
int main(int argc,char** argv){output=argv[1];srand(2350);try{GAME::run();}catch(ReturnToMenu&){}return 0;}
'''
sys.path.insert(0,str(ROOT/'tools/python-libs'));from PIL import Image
for g in games:
 if a.game and g['id']!=a.game:continue
 if (out/(g['id']+'-18.png')).exists() and not a.game:continue
 print(g['id'],flush=True)
 cpp=out/'host.cpp';cpp.write_text(host.replace('GAME::',g['id']+'::').replace('ENDTIME',str(a.seconds*1000000)).replace('DROP','true' if a.drop else 'false'))
 exe=out/'capture.exe';sources=sorted((ROOT/'firmware/games'/g['id']).glob('port_*.cpp'))
 cmd=[a.gxx,'-std=c++17','-O1','-w','-static','-fpermissive','-ffunction-sections','-fdata-sections','-Wl,--gc-sections','-I'+str(out/'stubs'),'-I'+str(ROOT/'firmware'),str(cpp),str(ROOT/'firmware/compat/draw.cpp'),str(ROOT/'firmware/compat/fonts.cpp'),*map(str,sources),'-o',str(exe)]
 with (out/(g['id']+'-compile.log')).open('w') as log:subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT)
 subprocess.run([str(exe),str(out/g['id'])],check=True,timeout=30)
 for raw in out.glob(g['id']+'-*.rgb565'):
  data=raw.read_bytes();rgb=[]
  for i in range(0,len(data),2):
   c=int.from_bytes(data[i:i+2],'little');rgb.append((((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31))
  im=Image.new('RGB',(320,240));im.putdata(rgb)
  rotation=json.loads(raw.with_suffix('.rgb565.json').read_text())['rotated']
  if g['group']=='TINYGAME':
   im=im.crop((32,48,288,176))
   if g.get('rotate') and rotation:im=im.rotate(90,expand=True)
  im.save(raw.with_suffix('.png'))
