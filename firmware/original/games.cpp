// Original PicoConsole games and procedural art, 2026-10-11.
// SPDX-License-Identifier: GPL-3.0-only
#include "../console.h"
#include <algorithm>
#include <array>

namespace fresh {
constexpr u16 white=0xffff,cyan=0x07ff,yellow=0xffe0,red=0xf800,blue=0x229f;
void box(int x,int y,int w,int h,u16 c){DrawRect(x+40,y,w,h,c);}
void frame(int x,int y,int w,int h,u16 c){DrawFrame(x+40,y,w,h,c);}
void label(int x,int y,const char* s,u16 c=white){DrawText(s,x+40,y,c);}
void header(const char* s){DrawClear();SelFont8x16();label(4,2,s,cyan);}
void cursor(int x,int y,int n,u16 c=yellow){frame(x,y,n,n,c);frame(x+1,y+1,n-2,n-2,c);}
void move(u8 k,int& x,int& y,int n){if(k==KEY_LEFT)x=(x+n-1)%n;if(k==KEY_RIGHT)x=(x+1)%n;if(k==KEY_UP)y=(y+n-1)%n;if(k==KEY_DOWN)y=(y+1)%n;}
void present(){DispUpdate();WaitMs(18);}
}

namespace original_minefield {
void run(){using namespace fresh;
 std::array<bool,81> mine{},open{},flag{};std::array<int,81> nearby{};
 int x=4,y=4;bool started=false,over=false,won=false;
 for(;;){u8 k=KeyGet();move(k,x,y,9);int at=y*9+x;
  if(k==KEY_X){mine.fill(false);open.fill(false);flag.fill(false);nearby.fill(0);started=over=won=false;}
  if(k==KEY_B&&!over)flag[at]=!flag[at];
  if(k==KEY_A&&!over&&!flag[at]){
   if(!started){int placed=0;while(placed<10){int p=RandU32()%81;if(!mine[p]&&(abs(p%9-x)>1||abs(p/9-y)>1)){mine[p]=true;++placed;}}
    for(int p=0;p<81;++p)for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx){int xx=p%9+dx,yy=p/9+dy;if(xx>=0&&xx<9&&yy>=0&&yy<9&&mine[yy*9+xx])++nearby[p];}started=true;}
   open[at]=true;if(mine[at])over=true;
   else {bool changed=true;while(changed){changed=false;for(int p=0;p<81;++p)if(open[p]&&!nearby[p])for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx){int xx=p%9+dx,yy=p/9+dy;if(xx>=0&&xx<9&&yy>=0&&yy<9){int q=yy*9+xx;if(!mine[q]&&!open[q]&&!flag[q]){open[q]=true;changed=true;}}}}
    won=true;for(int p=0;p<81;++p)if(!mine[p]&&!open[p])won=false;if(won)over=true;}
  }
  header(won?"CLEARED! X NEW":over?"BOOM! X NEW":"MINEFIELD 10 MINES");
  for(int p=0;p<81;++p){int xx=21+(p%9)*22,yy=24+(p/9)*22;box(xx,yy,21,21,open[p]?0x18c3:blue);
   if(mine[p]&&over)label(xx+6,yy+2,"*",red);else if(flag[p])label(xx+6,yy+2,"F",yellow);else if(open[p]&&nearby[p]){char t[2]={char('0'+nearby[p]),0};label(xx+6,yy+2,t);}}
  cursor(21+x*22,24+y*22,22);label(4,224,"A OPEN B FLAG X NEW");present();
 }
}}

namespace original_reversi {
using Board=std::array<int,64>;
int turn(Board& b,int at,int who,bool apply){if(b[at])return 0;int total=0;
 for(int dy=-1;dy<=1;++dy)for(int dx=-1;dx<=1;++dx)if(dx||dy){int x=at%8+dx,y=at/8+dy,n=0;
  while(x>=0&&x<8&&y>=0&&y<8&&b[y*8+x]==-who){++n;x+=dx;y+=dy;}
  if(n&&x>=0&&x<8&&y>=0&&y<8&&b[y*8+x]==who){total+=n;if(apply){x=at%8+dx;y=at/8+dy;while(n--){b[y*8+x]=who;x+=dx;y+=dy;}}}}
 if(total&&apply)b[at]=who;return total;
}
void reset(Board& b){b.fill(0);b[27]=b[36]=-1;b[28]=b[35]=1;}
void run(){using namespace fresh;Board b{};reset(b);int x=3,y=2;bool over=false;
 for(;;){u8 k=KeyGet();move(k,x,y,8);if(k==KEY_X){reset(b);over=false;}
  bool moved=k==KEY_A&&turn(b,y*8+x,1,true)>0;
  bool human=false;for(int p=0;p<64;++p)human|=turn(b,p,1,false)>0;
  while(!over&&(moved||!human)){int best=-1,value=0;for(int p=0;p<64;++p){int n=turn(b,p,-1,false);if(n>value){best=p;value=n;}}
   if(best>=0)turn(b,best,-1,true);human=false;for(int p=0;p<64;++p)human|=turn(b,p,1,false)>0;
   if(!human&&best<0)over=true;moved=false;if(human)break;}
  int us=std::count(b.begin(),b.end(),1),cpu=std::count(b.begin(),b.end(),-1);char title[30];snprintf(title,sizeof(title),"YOU %d CPU %d",us,cpu);header(title);
  for(int p=0;p<64;++p){int xx=24+p%8*24,yy=26+p/8*24;frame(xx,yy,24,24,blue);
   if(b[p]){box(xx+5,yy+5,14,14,b[p]==1?white:yellow);frame(xx+3,yy+3,18,18,b[p]==1?white:yellow);}else if(turn(b,p,1,false))box(xx+10,yy+10,4,4,cyan);}
  cursor(24+x*24,26+y*24,24);label(4,224,over?(us>cpu?"YOU WIN! X NEW":us==cpu?"DRAW! X NEW":"CPU WINS! X NEW"):"A PLACE X NEW Y MENU");present();
 }
}}

namespace original_memory {
void run(){using namespace fresh;std::array<int,16> cards{};std::array<bool,16> done{};int x=0,y=0,first=-1,second=-1,moves=0;bool reset=true;
 for(;;){u8 k=KeyGet();move(k,x,y,4);if(k==KEY_X)reset=true;
  if(reset){for(int i=0;i<16;++i)cards[i]=i/2;for(int i=15;i>0;--i)std::swap(cards[i],cards[RandU32()%(i+1)]);done.fill(false);first=second=-1;moves=0;reset=false;}
  if(k==KEY_A&&!done[y*4+x]&&first!=y*4+x){if(first<0)first=y*4+x;else{second=y*4+x;++moves;if(cards[first]==cards[second])done[first]=done[second]=true;}}
  char title[30];snprintf(title,sizeof(title),"PAIRS MOVES %d",moves);header(title);
  for(int p=0;p<16;++p){int xx=20+p%4*50,yy=26+p/4*48;box(xx,yy,46,44,done[p]?0x0320:blue);
   if(done[p]||p==first||p==second){char t[2]={char('1'+cards[p]),0};label(xx+18,yy+14,t,white);}else label(xx+18,yy+14,"?",white);}
  cursor(20+x*50,26+y*48,46);label(4,224,std::all_of(done.begin(),done.end(),[](bool d){return d;})?"ALL MATCHED! X NEW":"A REVEAL X NEW Y MENU");present();
  if(second>=0){if(!done[second])WaitMs(750);first=second=-1;}
 }
}}

namespace original_simon {
void draw(int lit,const char* title){using namespace fresh;header(title);const u16 colors[]={red,blue,yellow,0x07e0};const char* words[]={"UP","RIGHT","DOWN","LEFT"};
 for(int i=0;i<4;++i){int x=20+(i%2)*104,y=32+(i/2)*90;box(x,y,96,82,lit==i?white:colors[i]);label(x+26,y+32,words[i],lit==i?0:0);if(lit==i)cursor(x,y,82,cyan);}label(4,224,"A START Y MENU");DispUpdate();}
void run(){std::array<int,64> seq{};int length=0,at=0;bool playing=false,show=false;
 for(;;){u8 k=KeyGet();if(k==KEY_A||k==KEY_X){length=1;at=0;playing=true;seq[0]=RandU32()%4;show=true;}
  if(show){draw(-1,"WATCH");WaitMs(300);for(int i=0;i<length;++i){draw(seq[i],"WATCH");WaitMs(350);draw(-1,"WATCH");WaitMs(160);}KeyFlush();show=false;at=0;}
  int choice=k==KEY_UP?0:k==KEY_RIGHT?1:k==KEY_DOWN?2:k==KEY_LEFT?3:-1;
  if(playing&&choice>=0){draw(choice,"YOUR TURN");WaitMs(150);if(choice!=seq[at]){playing=false;draw(-1,"MISSED! A RETRY");}
   else if(++at==length){if(length==64){playing=false;draw(-1,"PERFECT! A RETRY");}else{seq[length++]=RandU32()%4;show=true;}}}
  char title[25];snprintf(title,sizeof(title),"%s ROUND %d",playing?"REPEAT":"SIMON",length);if(playing||length==0)draw(-1,title);WaitMs(20);
 }
}}
