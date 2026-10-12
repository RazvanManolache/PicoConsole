// SPDX-License-Identifier: GPL-3.0-or-later
// Thumbnail pixels derive from the curated games; component notices apply.
#include "menu_previews.h"
#include <cstring>
#include "menu_previews.inc"
namespace library {
int preview_count(){return sizeof(preview_tints)/sizeof(*preview_tints);}
bool preview_bitmap(int game,uint8_t* out){
    if(game<0||game>=preview_count())return false;
    const uint8_t* p=preview_data+preview_offsets[game];
    const uint8_t* end=preview_data+preview_offsets[game+1];
    int used=0,mode=*p++;
    if(mode==0){if(end-p!=preview_bytes)return false;memcpy(out,p,preview_bytes);return true;}
    if(mode!=1)return false;
    while(p<end){
        int c=*p++,n=(c&128)?(c&127)+3:c+1;
        if(used+n>preview_bytes)return false;
        if(c&128){if(p==end)return false;memset(out+used,*p++,n);}
        else {if(end-p<n)return false;memcpy(out+used,p,n);p+=n;}
        used+=n;
    }
    return used==preview_bytes;
}
void draw_preview(uint16_t* pixels,int stride,int game,int y,bool selected){
    uint8_t bitmap[preview_bytes];if(!preview_bitmap(game,bitmap))return;
    uint16_t tint=preview_tints[game];
    int r=((tint>>11)&31)*255/31,g=((tint>>5)&63)*255/63,b=(tint&31)*255/31;
    int peak=r>g?r:g;if(b>peak)peak=b;if(!peak)peak=1;
    // Lift dark/saturated tints (especially blue) for the small LCD.
    r=120+r*135/peak;g=120+g*135/peak;b=120+b*135/peak;peak=255;
    int brightness=selected?180:145;
    for(int yy=0;yy<preview_height;++yy)for(int xx=0;xx<preview_width;++xx){
        if(!(bitmap[yy*(preview_width/8)+xx/8]&(128>>(xx%8))))continue;
        // Fade toward the text; the name also has a black outline.
        int fade=xx<24?xx:24;
        int rr=r*brightness*fade/(peak*24),gg=g*brightness*fade/(peak*24),bb=b*brightness*fade/(peak*24);
        int x=122+xx;if(y+yy<240)pixels[(y+yy)*stride+x]=uint16_t(((rr>>3)<<11)|((gg>>2)<<5)|(bb>>3));
    }
}
}
