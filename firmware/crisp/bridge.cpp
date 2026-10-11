// Native PicoConsole backend for Crisp Game Lib (MIT).
#include "../console.h"
#include <algorithm>
#include "lib/cglp.h"
#include "lib/menu.h"
static float view_scale=2.0f;
static int view_w=100,view_h=100,view_x=60,view_y=20;
static bool initialized=false;
static u16 rgb(unsigned char r,unsigned char g,unsigned char b) { return COLOR(r,g,b); }
extern "C" void md_initView(int w,int h) {
    view_w=w; view_h=h; view_scale=std::min(240.0f/w,240.0f/h);
    view_x=int(40+(240-w*view_scale)/2); view_y=int((240-h*view_scale)/2);
}
extern "C" void md_drawRect(float x,float y,float w,float h,unsigned char r,unsigned char g,unsigned char b) {
    int x1=std::max(view_x,int(view_x+x*view_scale)),y1=std::max(view_y,int(view_y+y*view_scale));
    int x2=std::min(view_x+int(view_w*view_scale),int(ceilf(view_x+(x+w)*view_scale)));
    int y2=std::min(view_y+int(view_h*view_scale),int(ceilf(view_y+(y+h)*view_scale)));
    if(x2>x1 && y2>y1) DrawRect(x1,y1,x2-x1,y2-y1,rgb(r,g,b));
}
extern "C" void md_drawCharacter(unsigned char grid[6][6][3],float x,float y,int) {
    for(int yy=0;yy<6;++yy) for(int xx=0;xx<6;++xx) {
        auto* p=grid[yy][xx];
        if(p[0]||p[1]||p[2]) md_drawRect(x+xx,y+yy,1,1,p[0],p[1],p[2]);
    }
}
extern "C" void md_clearView(unsigned char r,unsigned char g,unsigned char b) { DrawRect(view_x,view_y,int(view_w*view_scale),int(view_h*view_scale),rgb(r,g,b)); }
extern "C" void md_clearScreen(unsigned char r,unsigned char g,unsigned char b) { DrawClearCol(rgb(r,g,b)); }
extern "C" void md_playTone(float,float,float) {}
extern "C" void md_stopTone() {}
extern "C" float md_getAudioTime() { return time_us_64()/1000000.0f; }
extern "C" void md_consoleLog(char*) {}
static void crisp_run(int index) {
    if(!initialized) { initGame(); disableSound(); initialized=true; }
    restartGame(index);
    float mouse_x=view_w/2.0f,mouse_y=view_h/2.0f;
    uint64_t next=time_us_64();
    while(true) {
        console_service();
        bool left=!game_gpio_get(BTN_LEFT_PIN),right=!game_gpio_get(BTN_RIGHT_PIN);
        bool up=!game_gpio_get(BTN_UP_PIN),down=!game_gpio_get(BTN_DOWN_PIN);
        bool a=!game_gpio_get(BTN_A_PIN)||!game_gpio_get(BTN_B_PIN)||!game_gpio_get(3);
        bool b=!game_gpio_get(BTN_X_PIN);
        mouse_x=std::clamp(mouse_x+(right-left)*1.5f,0.0f,float(view_w-1));
        mouse_y=std::clamp(mouse_y+(down-up)*1.5f,0.0f,float(view_h-1));
        setMousePos(mouse_x,mouse_y);
        setButtonState(left,right,up,down,b,a);
        updateFrame(); DispUpdate();
        next+=16667;
        while(time_us_64()<next) { console_service(); sleep_us(200); }
        if(time_us_64()>next+33334) next=time_us_64();
    }
}
#include "entries.inc"
