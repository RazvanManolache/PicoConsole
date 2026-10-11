"""Adapt a few small GPL3 Pocket Gamer games into the remaining flash."""
from pathlib import Path
import json,re,shutil
root=Path(__file__).resolve().parents[1];src=root/'upstream/pocket-gamer/src';dst=root/'firmware/pocket';dst.mkdir(exist_ok=True);(dst/'games').mkdir(exist_ok=True)
def put(p,s):
 if not p.exists() or p.read_text()!=s:p.write_text(s)
for name in ['mainLoop.h','gpu.h','interface.h','gameshared.h','gameshared.c','textures.c','textures.h']:
 s=(src/name).read_text().replace('16*1024','2048')
 if name=='gpu.h':s=s.replace('RGB(0,0,255)','RGB(0,128,255)').replace('RGB(64,64,64)','RGB(160,160,160)').replace('RGB(128,128,128)','RGB(208,208,208)').replace('RGB(192,192,192)','RGB(255,255,255)')
 if name=='gpu.h':s=re.sub(r'^#define RGB\(r, g, b\).*$', '#define RGB(r,g,b) ((uint16_t)((((r)&0xf8)<<8)|(((g)&0xfc)<<3)|(((b)&0xf8)>>3)))',s,flags=re.M)
 put(dst/name,s)
selected=[(3,'LIGHTS OUT'),(7,'CONNECT FOUR'),(9,'2048'),(11,'SNAKE'),(13,'PONG'),(14,'BREAKOUT'),(6,'3D LABYRINTH'),(1,'TIC TAC TOE CPU'),(2,'TIC TAC TOE 2P'),(4,'MATH CHALLENGE'),(5,'TETRAMINO'),(8,'CONNECT FOUR 2P')]
for n,title in selected:
 s=(src/'games'/f'game{n:02d}.c').read_text()
 if n==9:
  s=s.replace('const FontDescription * f = &fontDescription[2];','const FontDescription * f = &fontDescription[3];').replace('char text[5];','char text[16];')
  s=s.replace('#define BLOCK_SIZE ( (GPU_X/2 < GPU_Y) ? (GPU_X/8) : (GPU_Y/4) )','#define BLOCK_SIZE 52').replace('#define START_X ( (GPU_X/2 - 4*BLOCK_SIZE)/2 )','#define START_X 56').replace('#define START_Y ( (GPU_Y - 4*BLOCK_SIZE)/2 )','#define START_Y 30')
  a=s.index('    // Draw second screen',s.index('static void G_Draw'));b=s.index('\n}\n',a)
  s=s[:a]+'    char text[24]; int len=snprintf(text,sizeof(text),"Score %lu",(unsigned long)memory->_score);\n    GPU_DrawText(C_WHITE,font_l,56,4,text,len);'+s[b:]
 if n in (7,8):
  # A full column returns -1; keep it signed in the AI's temporary moves.
  s=s.replace('static uint8_t Drop(', 'static int Drop(').replace('uint8_t row = Drop(', 'int row = Drop(')
  a=s.index('static void G_Draw(void)');b=s.index('static void G_Deinit',a)
  s=s[:a]+"""static void G_Draw(void) {
    GPU_ClearFramebuffers();
    GPU_Color turn=memory->_playerNext==C4_PLAYER_1?C_RED:C_YELLOW;
    const char* label=memory->_playerNext==memory->_playerAI?"CPU TURN":"YOUR TURN";
    if(mainMemory._gameState==GS_DONE) {C4Enum winner=CheckWinner();label=winner==C4_PLAYER_DRAW?"DRAW":winner==memory->_playerAI?"CPU WINS":"YOU WIN";}
    GPU_DrawText(C_WHITE,&fontDescription[2],56,2,label,strlen(label));
    GPU_DrawFilledCircle(turn,70+memory->_choicePosition*30,30,6);
    for(int x=0;x<7;++x)for(int y=0;y<6;++y) {
      GPU_DrawEmptySquare(C_WHITE,55+x*30,42+y*30,30,30);
      if(memory->_field[x][y]!=C4_EMPTY)GPU_DrawFilledCircle(memory->_field[x][y]==C4_PLAYER_1?C_RED:C_YELLOW,70+x*30,57+y*30,12);
    }
    if(mainMemory._gameState==GS_DONE)GPU_DrawText(C_WHITE,&fontDescription[2],56,224,"B RESTART",9);
}

"""+s[b:]
  if n==8:s=s.replace('memory->_playerNext==memory->_playerAI?"CPU TURN":"YOUR TURN"','memory->_playerNext==C4_PLAYER_1?"RED TURN":"YELLOW TURN"').replace('winner==memory->_playerAI?"CPU WINS":"YOU WIN"','winner==C4_PLAYER_1?"RED WINS":"YELLOW WINS"')
 if n in (1,2):
  s=s.replace('#define START_X GPU_BORDER_X','#define START_X 55').replace('#define END_X (GPU_X/2-GPU_BORDER_X)','#define END_X 265').replace('#define START_Y GPU_BORDER_Y','#define START_Y 28').replace('#define END_Y (GPU_Y-GPU_BORDER_Y)','#define END_Y 238')
  a=s.index('static void G_Draw(void)');b=s.index('static void G_Deinit',a)
  turn='memory->_nextPlayer==memory->_aiPlayer?"CPU TURN":"YOUR TURN"' if n==1 else 'memory->_nextPlayer==TTTP_PLAYER_1?"X TURN":"O TURN"'
  s=s[:a]+'''static void G_Draw(void) {
    GPU_ClearFramebuffers(); const char* label='''+turn+''';
    if(mainMemory._gameState==GS_DONE)label=memory->_finalState==TTTGS_DRAW?"DRAW B RESTART":memory->_finalState==TTTGS_PLAYER1_WIN?"X WINS B RESTART":"O WINS B RESTART";
    GPU_DrawText(C_WHITE,&fontDescription[1],55,2,label,strlen(label));
    for(int x=0;x<3;++x)for(int y=0;y<3;++y) {
      GPU_DrawEmptySquare(C_WHITE,55+x*70,28+y*70,70,70);
      if(memory->_boardState[x][y]!=TTT_EMPTY)GPU_DrawLetter(memory->_boardState[x][y]==TTT_PLAYER_1?C_YELLOW:C_BLUE,&fontDescription[3],82+x*70,47+y*70,memory->_boardState[x][y]==TTT_PLAYER_1?'X':'O');
    }
}

'''+s[b:]
 if n==4:
  s=s.replace('#define BOX_W ((GPU_X/2)/4)','#define BOX_W 52').replace('#define BOX_H (GPU_Y/4)','#define BOX_H 45')
  s=s.replace('mainMemory.touch_X >= GPU_X/2 && mainMemory.touch_X <= GPU_X && mainMemory.touch_Y >= 0 && mainMemory.touch_Y <= GPU_Y','mainMemory.touch_X >= 56 && mainMemory.touch_X < 264 && mainMemory.touch_Y >= 52 && mainMemory.touch_Y < 232').replace('(mainMemory.touch_X - GPU_X/2)/BOX_W','(mainMemory.touch_X - 56)/BOX_W').replace('mainMemory.touch_Y/BOX_H','(mainMemory.touch_Y-52)/BOX_H')
  a=s.index('static void G_Draw(void)');b=s.index('static void G_Deinit',a)
  s=s[:a]+'''static void G_Draw(void) {
    GPU_ClearFramebuffers();char text[40];const char symbols[]="+-*/";
    int len=snprintf(text,sizeof(text),"%d %c %d = ?",memory->_x,symbols[memory->_arithmeticOperation],memory->_y);
    GPU_DrawText(C_WHITE,&fontDescription[1],56,2,text,len);
    len=snprintf(text,sizeof(text),"%lu / %lu correct",(unsigned long)memory->_guessesCorrect,(unsigned long)memory->_guessesTotal);
    GPU_DrawText(memory->_lastGuess==GR_WRONG?C_YELLOW:C_WHITE,&fontDescription[1],56,26,text,len);
    for(int y=0;y<4;++y)for(int x=0;x<4;++x) {
      GPU_DrawEmptySquare(C_WHITE,56+x*52,52+y*45,52,45);
      len=snprintf(text,sizeof(text),"%d",4*y+x);
      GPU_DrawText(C_WHITE,&fontDescription[3],56+x*52+26-len*8,58+y*45,text,len);
    }
}

'''+s[b:]
 if n==5:
  a=s.index('static void G_Draw(void)');b=s.index('static void G_Deinit',a)
  s=s[:a]+'''static void G_Draw(void) {
    GPU_ClearFramebuffers();GPU_DrawText(C_WHITE,&fontDescription[1],56,2,"TETRAMINO",9);
    for(int y=0;y<20;++y)for(int x=0;x<10;++x) {
      if(memory->_field[y][x]==TF_FULL)GPU_DrawFilledSquare(C_WHITE,66+x*10,26+y*10,9,9);
      else GPU_DrawEmptySquare(C_BLUE,66+x*10,26+y*10,10,10);
    }
    for(int x=0;x<memory->_activeWH;++x)for(int y=0;y<memory->_activeWH;++y)
      if(memory->_activeTetramino[x][y]==TF_OBJECT && y+memory->_activeY>=0)GPU_DrawFilledSquare(C_YELLOW,66+10*(x+memory->_activeX),26+10*(y+memory->_activeY),9,9);
    GPU_DrawText(C_WHITE,&fontDescription[1],178,28,"NEXT",4);
    for(int x=0;x<memory->_nextWH;++x)for(int y=0;y<memory->_nextWH;++y)if(memory->_nextTetramino[y][x]==TF_OBJECT)GPU_DrawFilledSquare(C_YELLOW,178+x*16,52+y*16,15,15);
    char text[20];int len=snprintf(text,sizeof(text),"%lu",(unsigned long)memory->_score);
    GPU_DrawText(C_WHITE,&fontDescription[1],178,130,"SCORE",5);GPU_DrawText(C_WHITE,&fontDescription[1],178,152,text,len);
    if(mainMemory._gameState==GS_DONE)GPU_DrawText(C_WHITE,&fontDescription[1],178,184,"GAME OVER",9);
    GPU_DrawText(C_WHITE,&fontDescription[1],56,224,"A TURN B NEW Y MENU",18);
}

'''+s[b:]
 put(dst/'games'/f'game{n:02d}.c','// PicoConsole input/display/layout modifications, 2026-10-11. Original program: Grgo Mariani, GPLv3.\n'+s)
shutil.copyfile(root/'upstream/pocket-gamer/LICENSE',dst/'LICENSE')
p=root/'tools/native_catalog.json';games=json.loads(p.read_text());games=[g for g in games if g['group']!='POCKET']
for n,title in selected:games.append(dict(id='pocket_'+str(n),folder=f'game{n:02d}.c',group='POCKET',title=title,rotate=0,controls='STICK+A / B RESET'))
p.write_text(json.dumps(games,indent=2)+'\n')
put(dst/'sources.cmake','file(GLOB POCKET_SOURCES "${CMAKE_CURRENT_LIST_DIR}/games/*.c")\nlist(APPEND POCKET_SOURCES pocket/gameshared.c pocket/textures.c pocket/bridge.cpp)\n')
put(dst/'entries.inc','\n'.join('namespace pocket_'+str(n)+' { void run() { pocket::run(&pocket::G'+str(n)+'_Callbacks); } }' for n,t in selected)+'\n')
print('Prepared',len(selected),'Pocket Gamer titles.')
