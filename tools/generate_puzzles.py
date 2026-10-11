"""Original Sokoban puzzles, GPL-3.0-only. No imported maps are used.

Start solved and walk/pull boxes backwards. Reversing that walk gives a
constructive solution, replayed below before accepting each puzzle.
"""
import json,random,re,hashlib
from pathlib import Path

def puzzles(count=128):
    rng=random.Random(2350318); result=[];seen=set()
    directions=[(1,0),(-1,0),(0,1),(0,-1)]
    while len(result)<count:
        n=9; floor={(x,y) for y in range(1,n-1) for x in range(1,n-1)}
        for _ in range(5):floor.discard((rng.randrange(2,7),rng.randrange(2,7)))
        goals=set(rng.sample(sorted(floor),2+len(result)%3));boxes=set(goals)
        player=rng.choice(sorted(floor-boxes));start=player;walk=[];pulls=0
        for _ in range(450):
            options=[]
            for dx,dy in directions:
                target=(player[0]+dx,player[1]+dy);behind=(player[0]-dx,player[1]-dy)
                if target in floor and target not in boxes:
                    options.append((dx,dy,False))
                    if behind in boxes:options.extend([(dx,dy,True)]*5)
            if not options:break
            dx,dy,pull=rng.choice(options)
            if pull:
                boxes.remove((player[0]-dx,player[1]-dy));boxes.add(player);pulls+=1
            player=(player[0]+dx,player[1]+dy);walk.append((dx,dy))
        if pulls<8 or len(boxes-goals)<2:continue
        rows=[]
        for y in range(n):
            row=''
            for x in range(n):
                p=(x,y)
                row+=('#' if p not in floor else '+' if p==player and p in goals else '@' if p==player else '*' if p in boxes and p in goals else '$' if p in boxes else '.' if p in goals else ' ')
            rows.append(row)
        board='!'.join(rows)+'!'
        if board in seen:continue
        # Replay the exact inverse walk with normal forward-push rules.
        check=set(boxes);pos=player;solution=''
        for dx,dy in reversed(walk):
            dx,dy=-dx,-dy;target=(pos[0]+dx,pos[1]+dy)
            assert target in floor
            if target in check:
                dest=(target[0]+dx,target[1]+dy);assert dest in floor and dest not in check
                check.remove(target);check.add(dest)
            pos=target;solution+={(1,0):'r',(-1,0):'l',(0,1):'d',(0,-1):'u'}[(dx,dy)]
        assert check==goals and pos==start
        seen.add(board);result.append((board,solution))
    return result

def level_definitions(original):
    data=puzzles()
    lines=['// Original PicoConsole puzzles, generated 2026-10-11. SPDX-License-Identifier: GPL-3.0-only',
           '// Deterministic reverse-pull generation; every stored solution is replay-verified.',
           '#include "../include.h"','const char* const CleanLevels[] = {']
    for board,solution in data:lines.extend([json.dumps(board)+',',json.dumps(solution)+','])
    lines.extend(['};','const sCollect CleanCollections[]={{"Fresh puzzles",CleanLevels,128}};',
                  'const sAuthor Author[]={{"PicoConsole",CleanCollections,1}};',
                  'const char* IntroLevel[]={'+json.dumps(data[0][0])+','+json.dumps(data[0][1])+'};'])
    lines.append(original[original.index('// selected level'):])
    report={'original_puzzles':len(data),'solutions_replayed':len(data),'imported_puzzles':0,
            'sha256':hashlib.sha256(json.dumps(data).encode()).hexdigest()}
    out=Path(__file__).resolve().parents[1]/'logs/puzzle-check.json';out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
    return '\n'.join(lines)

if __name__=='__main__':print(len(puzzles()),'original puzzles verified')
