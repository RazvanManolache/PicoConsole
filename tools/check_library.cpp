// SPDX-License-Identifier: GPL-3.0-or-later
// Native behavior tests with simulated flash faults, using the actual profile
// writer and menu renderer. Hardware flash/USB/timing still require a Pico.
#include "library.h"
#include "library_flash.h"
#include "library_screen.h"
#include "menu_previews.h"
#include "hardware/flash.h"
#include "pico/stdlib.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>
#include "catalog.h"

uint8_t flash_image[PICO_FLASH_SIZE_BYTES];
static int fail_erase=-1,fail_program=-1,writes=0;
struct PowerLost {};
void flash_range_erase(uint32_t o,size_t n) {
    assert(o>=PICO_FLASH_SIZE_BYTES-8192&&o+n<=PICO_FLASH_SIZE_BYTES&&o%4096==0&&n==4096);
    size_t count=fail_erase>=0?size_t(fail_erase):n;
    memset(flash_image+o,255,count);if(fail_erase>=0)throw PowerLost{};
}
void flash_range_program(uint32_t o,const uint8_t* p,size_t n) {
    assert(o>=PICO_FLASH_SIZE_BYTES-8192&&o+n<=PICO_FLASH_SIZE_BYTES&&o%256==0&&n%256==0);
    size_t count=fail_program>=0?size_t(fail_program):n;
    for(size_t i=0;i<count;++i){assert((flash_image[o+i]&p[i])==p[i]);flash_image[o+i]&=p[i];}
    if(fail_program>=0)throw PowerLost{};
    ++writes;
}
int flash_safe_execute(void (*f)(void*),void* p,uint32_t) {
    try{f(p);return PICO_OK;}catch(const PowerLost&){return -1;}
}
using library::Menu;using library::Record;using library::View;
static uint32_t keys[40];
static int assertions=0;
#define CHECK(x) do{++assertions;assert(x);}while(0)
static const char* title(int game){return titles[game];}
static void capture(const std::string& out,const char* name,const Menu& menu,bool failed=false){
    std::vector<uint16_t> pixels(320*240,0xdead);
    library::draw_menu(pixels.data(),320,font,menu,title,failed);
    // The panel is 240px wide; the remaining canvas must stay background.
    bool clipped=true;for(int y=0;y<240;++y)for(int x=240;x<320;++x)clipped&=pixels[y*320+x]==0x0863;
    CHECK(clipped);
    std::ofstream f(out+"/"+name+".rgb565",std::ios::binary);
    for(int y=0;y<240;++y)f.write(reinterpret_cast<char*>(pixels.data()+y*320),480);
    CHECK(f.good());
}
int main(int argc,char** argv){
    CHECK(argc==2);for(int i=0;i<40;++i)keys[i]=100+i;
    CHECK(library::menu_rows==5);
    CHECK(library::preview_count()==int(sizeof(catalog_keys)/sizeof(*catalog_keys)));
    uint8_t thumbnail[library::preview_bytes];
    CHECK(!library::preview_bitmap(-1,thumbnail)&&!library::preview_bitmap(library::preview_count(),thumbnail));
    for(int i=0;i<library::preview_count();++i)CHECK(library::preview_bitmap(i,thumbnail));
    Menu m(keys,40);
    CHECK(m.size()==41&&m.selected()==0);
    m.move(-1);CHECK(m.selected()==40&&!m.toggle()&&!m.played(40));
    m.cycle();CHECK(m.view()==View::Favorites&&m.size()==0&&m.selected()==-1);
    m.move(-7);CHECK(m.selected()==-1&&!m.toggle());
    m.cycle();CHECK(m.view()==View::Recent&&m.size()==0);m.all();
    m.focus(3);CHECK(m.toggle());m.focus(9);CHECK(m.toggle());
    m.cycle();CHECK(m.size()==2&&m.selected()==3);
    m.move(1);CHECK(m.selected()==9);CHECK(m.toggle());CHECK(m.size()==1&&m.selected()==3);
    CHECK(m.toggle());CHECK(m.size()==0&&m.cursor()==0);
    m.all();m.focus(31);m.cycle();m.cycle();m.all();CHECK(m.selected()==31);
    m.move(library::menu_rows);CHECK(m.selected()==36);m.move(library::menu_rows);CHECK(m.selected()==0);
    for(int i=0;i<40;++i)CHECK(m.played(i));
    CHECK(m.recent_count()==20);m.all();m.cycle();m.cycle();CHECK(m.game_at(0)==39&&m.game_at(19)==20);
    m.move(7);CHECK(m.selected()==32);CHECK(m.played(32));CHECK(m.selected()==32&&m.game_at(1)==39);
    CHECK(!m.played(32)&&m.recent_count()==20);
    m.all();m.focus(5);CHECK(m.toggle());m.focus(9);CHECK(m.toggle());
    Record r;m.encode(r,123);CHECK(library::valid(r));
    Menu restored(keys,40);restored.restore(r);CHECK(restored.favorite(5)&&restored.favorite(9)&&restored.recent_count()==20);
    uint32_t reordered[]={109,999,105,132};Menu upgraded(reordered,4);upgraded.restore(r);
    CHECK(upgraded.favorite(0)&&upgraded.favorite(2)&&!upgraded.favorite(1));
    upgraded.cycle();upgraded.cycle();CHECK(upgraded.size()==1&&upgraded.selected()==3);
    for(size_t i=0;i<sizeof(r);++i){auto corrupt=r;reinterpret_cast<uint8_t*>(&corrupt)[i]^=1;CHECK(!library::valid(corrupt));}
    auto newer=r;restored.encode(newer,124);CHECK(library::newest(&r,&newer)==1);
    restored.encode(r,0xffffffff);restored.encode(newer,0);CHECK(library::newest(&r,&newer)==1);
    uint32_t many_keys[library::max_games];for(int i=0;i<library::max_games;++i)many_keys[i]=1000+i;
    Menu full(many_keys,library::max_games);
    for(int i=0;i<library::max_games;++i){full.focus(i);CHECK(full.toggle());}
    full.encode(r,1);CHECK(library::valid(r)&&r.favorite_count==library::max_games);
    Menu full_reload(many_keys,library::max_games);full_reload.restore(r);
    CHECK(full_reload.favorite_count()==library::max_games&&full_reload.favorite(library::max_games-1));
    memset(flash_image,255,sizeof(flash_image));Menu saved(keys,40);library_load(saved);
    CHECK(saved.favorite_count()==0&&saved.recent_count()==0);
    saved.focus(2);CHECK(saved.toggle());CHECK(saved.played(2));CHECK(library_save(saved));
    std::vector<uint8_t> old(flash_image+sizeof(flash_image)-8192,flash_image+sizeof(flash_image));
    int interruptions=0;
    for(int cut=0;cut<int(sizeof(Record));cut+=17){
        memcpy(flash_image+sizeof(flash_image)-8192,old.data(),8192);
        Menu edit(keys,40);library_load(edit);edit.focus(7);edit.toggle();edit.played(7);
        fail_program=cut;CHECK(!library_save(edit));fail_program=-1;++interruptions;
        Menu boot(keys,40);library_load(boot);CHECK(boot.favorite(2)&&!boot.favorite(7)&&boot.recent_count()==1);
        boot.cycle();boot.cycle();CHECK(boot.selected()==2);
    }
    for(int cut:{0,1,256,2048,4096}){
        memcpy(flash_image+sizeof(flash_image)-8192,old.data(),8192);
        Menu edit(keys,40);library_load(edit);edit.focus(7);edit.toggle();
        fail_erase=cut;CHECK(!library_save(edit));fail_erase=-1;++interruptions;
        Menu boot(keys,40);library_load(boot);CHECK(boot.favorite(2)&&!boot.favorite(7));
    }
    memcpy(flash_image+sizeof(flash_image)-8192,old.data(),8192);
    Menu edit(keys,40);library_load(edit);edit.focus(7);edit.toggle();edit.played(7);CHECK(library_save(edit));
    Menu reboot(keys,40);library_load(reboot);CHECK(reboot.favorite(2)&&reboot.favorite(7));
    CHECK(reboot.played(8)&&library_save(reboot)); // alternates back to sector 0
    Menu reboot2(keys,40);library_load(reboot2);reboot2.cycle();reboot2.cycle();CHECK(reboot2.selected()==8);
    // Render the actual catalog with the shared firmware drawing code.
    Menu visual(catalog_keys,int(sizeof(catalog_keys)/sizeof(*catalog_keys)));
    for(int game:{0,31,40,305,321,328,336,342,350}){visual.focus(game);visual.toggle();visual.played(game);}
    visual.all();visual.focus(31);capture(argv[1],"all",visual);
    visual.cycle();capture(argv[1],"favorites",visual);
    visual.cycle();capture(argv[1],"recent",visual);
    Menu empty(catalog_keys,int(sizeof(catalog_keys)/sizeof(*catalog_keys)));empty.cycle();capture(argv[1],"empty-favorites",empty);
    empty.cycle();capture(argv[1],"empty-recent",empty);capture(argv[1],"save-failed",visual,true);
    std::printf("PASS %d checks; %d interrupted saves recovered; %d completed flash writes\n",assertions,interruptions,writes);
}
