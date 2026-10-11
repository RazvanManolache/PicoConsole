// PicoConsole launcher and Waveshare Pico-LCD-1.3 adapter, GPL-3.0-or-later.
// ST7789 initialisation adapted from Waveshare Pico_code (GPLv3); see LICENSES.
#include "console.h"
#include "hardware/spi.h"
#include "hardware/pwm.h"
#include "pico/stdio_usb.h"
#include "pico/bootrom.h"
#include <algorithm>
#include <iterator>

u16 FrameBuf[WIDTH*HEIGHT];
ConsoleConfig Config;
static u16 panel[240];
static int panel_y=0;
static bool panel_game=false;
static void render_row(bool game,int y);
static const int pins[]={2,18,16,20,3,15,17,19,21};
static const char* names[]={"UP","DOWN","LEFT","RIGHT","OK","A","B","X","Y"};
struct GameSpec { const char* title; void (*run)(); bool tiny; int full; int rotate; const char* controls; };
static const GameSpec games[]={
#include "games/registry.inc"
};
static bool rotated=false;
static int game_level=1,game_lives=3;
void console_set_rotated(bool enabled) { rotated=enabled; }
void console_stats(int level,int lives) { game_level=level; game_lives=lives; }
static const u16 BG=0x0863, WHITE=0xffff, MUTED=0xffff, CYAN=0x07ff, GOLD=0xfda0;
static int active=-1, pending=-1, selected=0;
static bool quitting=false, in_service=false;
static uint32_t virtual_keys=0, virtual_until=0, seen=0, frames=0, menu_returns=0;
static uint32_t raw_keys=0, stable_keys=0, last_raw=0, change_at=0;
static uint32_t queued_keys=0,key_previous=0,key_repeat=0;
static char command[96];
static int command_len=0;
static bool shot_pending=false;
static uint32_t last_present_ms=0,shot_requested_ms=0;
static void emit_shot();

static uint32_t now_ms() { return to_ms_since_boot(get_absolute_time()); }
static uint32_t read_keys() {
    uint32_t result=0;
    for (int i=0;i<9;++i) if (!gpio_get(pins[i])) result|=1u<<i;
    seen |= result;
    if ((int32_t)(virtual_until-now_ms())>0) result|=virtual_keys;
    return result;
}
static void lcd_command(uint8_t cmd, const uint8_t* bytes=nullptr, size_t n=0) {
    gpio_put(8,0); gpio_put(9,0);
    spi_write_blocking(spi1,&cmd,1);
    gpio_put(9,1);
    if (n) { gpio_put(8,1); gpio_put(9,0); spi_write_blocking(spi1,bytes,n); gpio_put(9,1); }
}
static void lcd_init() {
    for (int pin : {8,9,12,13}) { gpio_init(pin); gpio_set_dir(pin,GPIO_OUT); gpio_put(pin,1); }
    gpio_put(13,0);
    spi_init(spi1,40000000); // 37.5 MHz at the stock 150 MHz system clock.
    gpio_set_function(10,GPIO_FUNC_SPI); gpio_set_function(11,GPIO_FUNC_SPI);
    gpio_put(12,1); sleep_ms(100); gpio_put(12,0); sleep_ms(100); gpio_put(12,1); sleep_ms(100);
    const uint8_t madctl=0x70, format=0x05;
    lcd_command(0x36,&madctl,1); lcd_command(0x3a,&format,1);
    const uint8_t porch[]={0x0c,0x0c,0,0x33,0x33}; lcd_command(0xb2,porch,5);
    const uint8_t pairs[][2]={{0xb7,0x35},{0xbb,0x19},{0xc0,0x2c},{0xc2,1},{0xc3,0x12},{0xc4,0x20},{0xc6,0x0f}};
    for (const auto& p:pairs) lcd_command(p[0],p+1,1);
    const uint8_t power[]={0xa4,0xa1}; lcd_command(0xd0,power,2);
    const uint8_t gamma1[]={0xd0,4,0x0d,0x11,0x13,0x2b,0x3f,0x54,0x4c,0x18,0x0d,0x0b,0x1f,0x23};
    const uint8_t gamma2[]={0xd0,4,0x0c,0x11,0x13,0x2c,0x3f,0x44,0x51,0x2f,0x1f,0x1f,0x20,0x23};
    lcd_command(0xe0,gamma1,14); lcd_command(0xe1,gamma2,14);
    lcd_command(0x21); lcd_command(0x11); sleep_ms(120); lcd_command(0x29); sleep_ms(20);
    // Show the first frame before turning on the backlight.
}
static void fill(u16* dest,int stride,int x,int y,int w,int h,u16 color) {
    if(dest==panel) { if(panel_y>=y && panel_y<y+h) for(int xx=std::max(x,0);xx<std::min(x+w,240);++xx) dest[xx]=color; return; }
    for (int yy=std::max(y,0);yy<std::min(y+h,240);++yy)
        for (int xx=std::max(x,0);xx<std::min(x+w,240);++xx) dest[yy*stride+xx]=color;
}
static void text(u16* dest,int stride,int x,int y,const char* s,u16 color,int scale=2) {
    if(dest==panel && (panel_y<y || panel_y>=y+8*scale)) return;
    const u8* font=FontCond6x8;
    for (;*s;++s,x+=6*scale) for (int row=0;row<8;++row) {
        uint8_t bits=font[row*256+(uint8_t)*s];
        for (int col=0;col<6;++col) if (bits & (0x80>>col)) fill(dest,stride,x+col*scale,y+row*scale,scale,scale,color);
    }
}
static void panel_send() {
    const uint8_t window[]={0,0,0,239};
    lcd_command(0x2a,window,4); lcd_command(0x2b,window,4); lcd_command(0x2c);
    gpio_put(8,1); gpio_put(9,0);
    uint8_t row[480];
    for (int y=0;y<240;++y) {
        render_row(panel_game,y);
        for (int x=0;x<240;++x) { u16 p=panel[x]; row[2*x]=p>>8; row[2*x+1]=p; }
        spi_write_blocking(spi1,row,480);
    }
    gpio_put(9,1); gpio_put(13,1); ++frames;
}
static void render_row(bool game,int y) {
    panel_y=y;
    if (!game) memcpy(panel,FrameBuf+y*WIDTH,480);
    else if(games[active].full) memcpy(panel,FrameBuf+y*WIDTH+(games[active].full==2?0:40),480);
    else {
        std::fill(std::begin(panel),std::end(panel),BG);
        text(panel,240,8,2,games[active].title,WHITE);
        if (games[active].rotate && rotated) {
            // Rotate the original left paddle to the bottom, retaining aspect ratio.
            const int vw=games[active].rotate==2?116:116, sw=games[active].rotate==2?116:114;
            if(y>=22 && y<230) for(int x=0;x<vw;++x)
                panel[x+(240-vw)/2]=FrameBuf[(48+x*128/vw)*WIDTH+32+(sw-1-(y-22)*sw/208)*2];
            text(panel,240,2,64,"LEFT",WHITE); text(panel,240,2,84,"RIGHT",WHITE);
            text(panel,240,2,108,games[active].rotate==2?"FLIP":"MOVE",CYAN);
            text(panel,240,186,64,"A/B",WHITE); text(panel,240,186,84,"BALL",CYAN);
            char hud[16]; snprintf(hud,sizeof(hud),"L%d",game_level); text(panel,240,188,130,hud,GOLD);
            snprintf(hud,sizeof(hud),"H%d",game_lives); text(panel,240,188,146,hud,GOLD);
            text(panel,240,2,220,"Y",GOLD);
        } else if (games[active].tiny) {
        fill(panel,240,12,32,216,2,CYAN);
        // Preserve all original 128x64 pixels. Source games draw 2x at (32,48).
        if(y>=54 && y<174) for (int x=0;x<240;++x)
            panel[x]=FrameBuf[(48+(y-54)*128/120)*WIDTH+32+x*256/240];
        text(panel,240,12,216,"A/B ACT   Y MENU",WHITE);
        } else {
            if(y>=22 && y<202) for(int x=0;x<240;++x)
                panel[x]=FrameBuf[((y-22)*4/3)*WIDTH+x*4/3];
            text(panel,240,8,216,"A/B/X ACT   Y MENU",WHITE);
        }
    }
}
static void present(bool game) { panel_game=game; panel_send(); last_present_ms=now_ms(); if(shot_pending)emit_shot(); }
static void emit_shot() {
    shot_pending=false;
    printf("FRAME 240 240 RGB565LE 115200\n");
    for(int y=0;y<240;++y) { render_row(panel_game,y); fwrite(panel,1,sizeof(panel),stdout); }
    fflush(stdout); puts("\nEND_FRAME");
}
static void send_status() {
    printf("{\"version\":\"native-0.3\",\"mode\":\"%s\",\"game\":%d,\"frames\":%lu,\"returns\":%lu,\"keys\":%lu,\"seen_physical\":%lu,\"uptime_ms\":%lu,\"count\":%d,\"selected\":%d,\"rotated\":%d}\n",
        active==-1?"menu":active==-2?"diagnostic":"game",active,
        (unsigned long)frames,(unsigned long)menu_returns,(unsigned long)read_keys(),(unsigned long)seen,(unsigned long)now_ms(),GAME_COUNT,selected,rotated);
}
static void dispatch(const char* line) {
    if (!strcmp(line,"status")) send_status();
    else if (!strcmp(line,"menu")) { quitting=true; pending=-1; puts("OK menu"); }
    else if (!strncmp(line,"launch ",7)) {
        int n=atoi(line+7);
        if (n>=0 && n<=GAME_COUNT) { pending=n; if(active!=-1) quitting=true; puts("OK launch"); }
        else puts("ERROR game index");
    } else if (!strcmp(line,"list")) {
        for (int i=0;i<GAME_COUNT;++i) printf("%d %s\n",i,games[i].title);
        puts("END_LIST");
    } else if (!strncmp(line,"press ",6)) {
        char key[12]={}; unsigned ms=0;
        if (sscanf(line+6,"%11s %u",key,&ms)==2 && ms<=5000) {
            virtual_keys=0;
            for (int i=0;i<9;++i) if (!strcmp(key,names[i])) virtual_keys|=1u<<i;
            virtual_until=now_ms()+ms;
            puts(virtual_keys?"OK press":"ERROR key");
        } else puts("ERROR press KEY milliseconds (0..5000)");
    } else if (!strcmp(line,"shot")) {
        if(active>=0 && now_ms()-last_present_ms<200) { shot_pending=true;shot_requested_ms=now_ms(); }
        else emit_shot();
    } else if (!strcmp(line,"boot")) { puts("OK boot"); stdio_flush(); reset_usb_boot(0,0); }
    else puts("ERROR commands: status, launch 0..2, menu, press KEY ms, shot, boot");
}
void console_service() {
    if (in_service) return;
    in_service=true;
    int c;
    while ((c=getchar_timeout_us(0))!=PICO_ERROR_TIMEOUT) {
        if (c=='\n' || c=='\r') {
            if (command_len) { command[command_len]=0; dispatch(command); command_len=0; }
        } else if (command_len<int(sizeof(command))-1) command[command_len++]=c;
        else command_len=0;
    }
    uint32_t t=now_ms(); raw_keys=read_keys();
    if (raw_keys!=last_raw) { last_raw=raw_keys; change_at=t; }
    if (t-change_at>=15) stable_keys=raw_keys;
    if (active!=-1 && (stable_keys & (1u<<8))) quitting=true;
    if(shot_pending && t-shot_requested_ms>250) emit_shot();
    in_service=false;
    if (active!=-1 && quitting) throw ReturnToMenu{};
}
bool game_gpio_get(int pin) {
    console_service();
    if (active>=0 && games[active].rotate && rotated) {
        if(pin==BTN_UP_PIN) pin=BTN_LEFT_PIN;
        else if(pin==BTN_DOWN_PIN) pin=BTN_RIGHT_PIN;
        else if(pin==BTN_LEFT_PIN) pin=BTN_DOWN_PIN;
        else if(pin==BTN_RIGHT_PIN) pin=BTN_UP_PIN;
    }
    for (int i=0;i<9;++i) if (pins[i]==pin) return !(raw_keys & (1u<<i));
    return true;
}
void KeyFlush() { console_service(); queued_keys=0; key_previous=stable_keys; key_repeat=now_ms()+350; }
u8 KeyGet() {
    console_service();
    queued_keys |= stable_keys & ~key_previous;
    if(stable_keys!=key_previous) key_repeat=now_ms()+350;
    else if(stable_keys && int32_t(now_ms()-key_repeat)>=0) { queued_keys|=stable_keys; key_repeat=now_ms()+100; }
    key_previous=stable_keys;
    for(int i=0;i<9;++i) if(queued_keys&(1u<<i)) { queued_keys&=~(1u<<i); return pins[i]==3?KEY_A:pins[i]; }
    return KEY_NONE;
}
void WaitMs(uint32_t ms) {
    uint32_t start=now_ms();
    do { console_service(); sleep_ms(1); } while (now_ms()-start<ms);
}
void WaitUs(uint32_t us) {
    uint64_t end=time_us_64()+us;
    do { console_service(); sleep_us(std::min<uint32_t>(us,1000)); } while(time_us_64()<end);
}
void DispUpdate() { console_service(); present(true); }

static void draw_menu() {
    std::fill(std::begin(FrameBuf),std::end(FrameBuf),BG);
    char label[32]; snprintf(label,sizeof(label),"%d GAMES  %d/%d",GAME_COUNT,selected+1,GAME_COUNT+1);
    text(FrameBuf,WIDTH,8,4,label,CYAN);
    int top=(selected/7)*7;
    for (int row=0;row<7 && top+row<=GAME_COUNT;++row) {
        int i=top+row,y=30+row*24;
        fill(FrameBuf,WIDTH,6,y,228,23,i==selected?0x2253:0x10a5);
        text(FrameBuf,WIDTH,8,y+4,i==selected?">":" ",CYAN);
        text(FrameBuf,WIDTH,24,y+4,i==GAME_COUNT?"DISPLAY / BUTTONS":games[i].title,WHITE);
    }
    text(FrameBuf,WIDTH,8,218,"L/R PAGE  A PLAY",GOLD);
    present(false);
}
static void diagnostics() {
    uint32_t previous=~0u;
    while (true) {
        console_service();
        if (previous!=raw_keys) {
            previous=raw_keys;
            std::fill(std::begin(FrameBuf),std::end(FrameBuf),BG);
            text(FrameBuf,WIDTH,8,12,"DISPLAY / BUTTONS",WHITE);
            fill(FrameBuf,WIDTH,8,32,72,24,0xf800);
            fill(FrameBuf,WIDTH,84,32,72,24,0x07e0);
            fill(FrameBuf,WIDTH,160,32,72,24,0x001f);
            text(FrameBuf,WIDTH,12,65,"RED   GREEN   BLUE",WHITE);
            for (int i=0;i<9;++i) {
                int x=8+(i%3)*78,y=88+(i/3)*36;
                fill(FrameBuf,WIDTH,x,y,72,28,(raw_keys&(1u<<i))?0x2c6a:0x18e7);
                text(FrameBuf,WIDTH,x+8,y+10,names[i],WHITE);
            }
            text(FrameBuf,WIDTH,8,207,"PICO 2 / 240 X 240",MUTED);
            text(FrameBuf,WIDTH,8,224,"Y  BACK TO GAMES",GOLD);
            present(false);
        }
        sleep_ms(5);
    }
}
int main() {
    stdio_init_all(); stdio_set_translate_crlf(&stdio_usb,false);
    for (int pin:pins) { gpio_init(pin); gpio_set_dir(pin,GPIO_IN); gpio_pull_up(pin); }
    lcd_init();
    uint32_t old=0,menu_repeat=0;
    draw_menu();
    while (true) {
        console_service();
        if (quitting) { quitting=false; draw_menu(); }
        uint32_t pressed=stable_keys & ~old;
        if(stable_keys!=old)menu_repeat=now_ms()+350;
        else if((stable_keys&15u) && int32_t(now_ms()-menu_repeat)>=0) { pressed|=stable_keys&15u;menu_repeat=now_ms()+100; }
        old=stable_keys;
        if (pressed&1u) { selected=(selected+GAME_COUNT)%(GAME_COUNT+1); draw_menu(); }
        if (pressed&2u) { selected=(selected+1)%(GAME_COUNT+1); draw_menu(); }
        if (pressed&4u) { selected=(selected+GAME_COUNT+1-7)%(GAME_COUNT+1); draw_menu(); }
        if (pressed&8u) { selected=(selected+7)%(GAME_COUNT+1); draw_menu(); }
        if (pressed&((1u<<4)|(1u<<5))) pending=selected;
        if (pending>=0) {
            selected=pending; pending=-1;
            // Consume the selection press, so it cannot skip the game's intro.
            while (read_keys()) { console_service(); sleep_ms(5); }
            stable_keys=last_raw=raw_keys=old=0;
            quitting=false;
            std::fill(std::begin(FrameBuf),std::end(FrameBuf),0);
            rotated=false;
            extern uint8_t __game_ram_start, __game_ram_end;
            memset(&__game_ram_start,0,&__game_ram_end-&__game_ram_start);
            SelFont8x16(); KeyFlush();
            active=selected==GAME_COUNT?-2:selected;
            try {
                if(active>=0) games[active].run();
                else diagnostics();
            } catch (const ReturnToMenu&) { ++menu_returns; }
            active=-1; quitting=false; virtual_keys=0;
            draw_menu();
            // Ignore a held Y after returning to the menu.
            while(read_keys()&(1u<<8)) { console_service(); sleep_ms(5); }
            stable_keys=last_raw=raw_keys=old=0;
        }
        sleep_ms(5);
    }
}
