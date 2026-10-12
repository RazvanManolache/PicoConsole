// SPDX-License-Identifier: GPL-3.0-or-later
// Shared by the Pico launcher and desktop visual checks.
#include "library_screen.h"
#include "menu_previews.h"
#include <cstdio>
namespace library {
void draw_menu(uint16_t* pixels,int stride,const uint8_t* font,const Menu& menu,
               const char* (*title)(int),bool save_failed) {
    constexpr uint16_t white=0xffff,cyan=0x07ff,gold=0xfda0;
    auto fill=[&](int x,int y,int w,int h,uint16_t color){
        for(int yy=y;yy<y+h&&yy<240;++yy)for(int xx=x;xx<x+w&&xx<240;++xx)
            if(xx>=0&&yy>=0)pixels[yy*stride+xx]=color;
    };
    auto text=[&](int x,int y,const char* s,uint16_t color){
        for(;*s;++s,x+=12)for(int row=0;row<8;++row)for(int col=0;col<6;++col)
            if(font[row*256+uint8_t(*s)]&(0x80>>col))fill(x+col*2,y+row*2,2,2,color);
    };
    for(int i=0;i<stride*240;++i)pixels[i]=0x0863;
    int count=menu.size(),selected=menu.cursor(),top=selected/menu_rows*menu_rows;
    char label[32];snprintf(label,sizeof(label),"%s  %d/%d",menu.view_name(),count?selected+1:0,count);
    text(8,4,label,cyan);
    for(int row=0;row<menu_rows&&top+row<count;++row){
        int i=top+row,y=30+row*33,game=menu.game_at(i);
        fill(6,y,228,32,i==selected?0x19cc:0x10a5);
        if(game<menu.game_count())draw_preview(pixels,stride,game,y,i==selected);
        if(i==selected){fill(6,y,2,32,cyan);fill(6,y,228,1,cyan);fill(6,y+31,228,1,cyan);}
        const char* name=game==menu.game_count()?"DISPLAY / BUTTONS":title(game);
        text(23,y+8,name,0);text(25,y+8,name,0);text(24,y+7,name,0);text(24,y+9,name,0);
        text(8,y+8,menu.favorite(game)?"*":i==selected?">":" ",gold);
        text(24,y+8,name,white);
    }
    if(!count){
        text(8,64,menu.view()==View::Favorites?"NO FAVORITES":"NO RECENT GAMES",white);
        text(8,96,menu.view()==View::Favorites?"X STARS A GAME":"PLAY A GAME",white);
        text(8,120,"FROM ALL GAMES",white);
    }
    if(save_failed)fill(6,200,228,20,0x9800);
    text(8,202,save_failed?"SAVE FAILED":"B VIEWS  X STAR",save_failed?white:cyan);
    text(8,222,"L/R PAGE A PLAY",gold);
}
}
