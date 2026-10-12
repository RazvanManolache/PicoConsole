// SPDX-License-Identifier: GPL-3.0-or-later
// PicoConsole library navigation and saved profile, 2026-10-12.
#pragma once
#include <cstddef>
#include <cstdint>

namespace library {
constexpr int max_games=512, recent_limit=20, saved_bytes=8192;
enum class View { All, Favorites, Recent };
// Fixed schema stores stable game IDs, so reordered/extended catalogs retain
// favorites and history. One complete record fits in nine flash pages.
struct Record {
    uint32_t magic, schema, sequence, favorite_count, recent_count;
    uint32_t favorites[max_games], recent[recent_limit];
    uint8_t reserved[152];
    uint32_t checksum;
};
static_assert(sizeof(Record)==2304);
bool valid(const Record& record);
int newest(const Record* a,const Record* b);

class Menu {
public:
    Menu(const uint32_t* keys,int count): keys_(keys),count_(count) {}
    int game_count() const { return count_; }
    View view() const { return view_; }
    const char* view_name() const;
    int cursor() const { return cursor_[int(view_)]; }
    int size() const;
    int game_at(int row) const;
    int selected() const { return game_at(cursor()); }
    bool favorite(int game) const;
    int favorite_count() const;
    int recent_count() const { return recent_count_; }
    void move(int delta);
    void cycle();
    void all();
    void focus(int game);
    bool toggle();
    bool played(int game);
    void restore(const Record& record);
    void encode(Record& record,uint32_t sequence) const;
private:
    const uint32_t* keys_;
    int count_;
    uint8_t favorites_[(max_games+7)/8]{};
    uint16_t recent_[recent_limit]{};
    int recent_count_=0,cursor_[3]{};
    View view_=View::All;
    int index(uint32_t key) const;
    void clamp();
};
}
