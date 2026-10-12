// SPDX-License-Identifier: GPL-3.0-or-later
#include "library.h"
#include <cstring>

namespace library {
static uint32_t crc(const Record& r) {
    uint32_t c=~0u;
    auto p=reinterpret_cast<const uint8_t*>(&r);
    for(size_t i=0;i<offsetof(Record,checksum);++i) {
        c^=p[i];for(int b=0;b<8;++b)c=(c>>1)^(0xedb88320u&uint32_t(-int(c&1)));
    }
    return ~c;
}
bool valid(const Record& r) {
    return r.magic==0x50434c42 && r.schema==1 && r.favorite_count<=max_games &&
           r.recent_count<=recent_limit && r.checksum==crc(r);
}
int newest(const Record* a,const Record* b) {
    bool av=a&&valid(*a),bv=b&&valid(*b);
    if(!av)return bv?1:-1;
    return bv&&int32_t(b->sequence-a->sequence)>0?1:0;
}
const char* Menu::view_name() const {
    return view_==View::All?"ALL":view_==View::Favorites?"FAVORITES":"RECENT";
}
bool Menu::favorite(int game) const {
    return game>=0&&game<count_&&(favorites_[game/8]&(1u<<(game%8)));
}
int Menu::favorite_count() const {
    int n=0;for(int i=0;i<count_;++i)n+=favorite(i);return n;
}
int Menu::size() const {
    return view_==View::All?count_+1:view_==View::Favorites?favorite_count():recent_count_;
}
int Menu::game_at(int row) const {
    if(row<0)return -1;
    if(view_==View::All)return row<=count_?row:-1; // Last row is diagnostics.
    if(view_==View::Recent)return row<recent_count_?recent_[row]:-1;
    for(int i=0;i<count_;++i)if(favorite(i)&&row--==0)return i;
    return -1;
}
void Menu::clamp() {
    int n=size();int& c=cursor_[int(view_)];if(c>=n)c=n?n-1:0;
}
void Menu::move(int delta) {
    int n=size();if(!n)return;
    int& c=cursor_[int(view_)];c=((c+delta)%n+n)%n;
}
void Menu::cycle() {view_=View((int(view_)+1)%3);clamp();}
void Menu::all() {view_=View::All;clamp();}
void Menu::focus(int game) {
    for(int i=0;i<size();++i)if(game_at(i)==game){cursor_[int(view_)]=i;return;}
    all();if(game>=0&&game<=count_)cursor_[0]=game;
}
bool Menu::toggle() {
    int game=selected();if(game<0||game>=count_)return false;
    favorites_[game/8]^=uint8_t(1u<<(game%8));clamp();return true;
}
bool Menu::played(int game) {
    if(game<0||game>=count_ || (recent_count_&&recent_[0]==game))return false;
    int old=0;while(old<recent_count_&&recent_[old]!=game)++old;
    if(old==recent_count_&&recent_count_<recent_limit)++recent_count_;
    if(old>=recent_limit)old=recent_limit-1;
    for(int i=old;i>0;--i)recent_[i]=recent_[i-1];recent_[0]=uint16_t(game);
    if(view_==View::Recent)cursor_[2]=0;
    return true;
}
int Menu::index(uint32_t key) const {
    for(int i=0;i<count_;++i)if(keys_[i]==key)return i;return -1;
}
void Menu::restore(const Record& r) {
    if(!valid(r))return;
    memset(favorites_,0,sizeof(favorites_));recent_count_=0;
    for(uint32_t i=0;i<r.favorite_count;++i){int g=index(r.favorites[i]);if(g>=0)favorites_[g/8]|=uint8_t(1u<<(g%8));}
    for(uint32_t i=0;i<r.recent_count;++i){
        int g=index(r.recent[i]);if(g<0)continue;
        bool duplicate=false;for(int j=0;j<recent_count_;++j)duplicate|=recent_[j]==g;
        if(!duplicate)recent_[recent_count_++]=uint16_t(g);
    }
    view_=View::All;memset(cursor_,0,sizeof(cursor_));
}
void Menu::encode(Record& r,uint32_t sequence) const {
    memset(&r,255,sizeof(r));r.magic=0x50434c42;r.schema=1;r.sequence=sequence;
    r.favorite_count=0;r.recent_count=recent_count_;
    for(int i=0;i<count_;++i)if(favorite(i))r.favorites[r.favorite_count++]=keys_[i];
    for(int i=0;i<recent_count_;++i)r.recent[i]=keys_[recent_[i]];
    r.checksum=crc(r);
}
}
