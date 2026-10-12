// SPDX-License-Identifier: GPL-3.0-or-later
// Two alternating sectors: a partial new write leaves the previous record valid.
#include "library_flash.h"
#include "hardware/flash.h"
#include "hardware/regs/addressmap.h"
#include "pico/flash.h"
#include "pico/stdlib.h"
#include <cstring>

static_assert(PICO_FLASH_SIZE_BYTES==4*1024*1024,"Profile layout expects Pico 2 flash");
static_assert(library::saved_bytes==2*FLASH_SECTOR_SIZE);
static_assert(sizeof(library::Record)%FLASH_PAGE_SIZE==0);
constexpr uint32_t offset=PICO_FLASH_SIZE_BYTES-library::saved_bytes;
static int current_slot=-1;
static uint32_t sequence=0;
static const library::Record* slot(int n) {
    return reinterpret_cast<const library::Record*>(XIP_BASE+offset+n*FLASH_SECTOR_SIZE);
}
void library_load(library::Menu& menu) {
    current_slot=library::newest(slot(0),slot(1));sequence=0;
    if(current_slot>=0){menu.restore(*slot(current_slot));sequence=slot(current_slot)->sequence;}
}
struct Write {uint32_t offset;const library::Record* record;};
static void write_record(void* data) {
    auto& w=*static_cast<Write*>(data);
    flash_range_erase(w.offset,FLASH_SECTOR_SIZE);
    flash_range_program(w.offset,reinterpret_cast<const uint8_t*>(w.record),sizeof(*w.record));
}
bool library_save(const library::Menu& menu) {
    library::Record record;menu.encode(record,sequence+1);
    int next=current_slot==0?1:0;
    Write w{offset+uint32_t(next)*FLASH_SECTOR_SIZE,&record};
    int result=flash_safe_execute(write_record,&w,1000);
    if(result!=PICO_OK||memcmp(slot(next),&record,sizeof(record))!=0||!library::valid(*slot(next)))return false;
    current_slot=next;sequence=record.sequence;return true;
}
