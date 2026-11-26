import streamlit as st
import math

st.set_page_config(page_title="オセロ", page_icon="⚫", layout="centered")

# ---------- Game engine ----------
N = 8
DIRECTIONS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
WEIGHTS = [
    [100,-20,10,5,5,10,-20,100],
    [-20,-50,-2,-2,-2,-2,-50,-20],
    [10,-2,5,1,1,5,-2,10],
    [5,-2,1,0,0,1,-2,5],
    [5,-2,1,0,0,1,-2,5],
    [10,-2,5,1,1,5,-2,10],
    [-20,-50,-2,-2,-2,-2,-50,-20],
    [100,-20,10,5,5,10,-20,100],
]

def initial_board():
    b = [[0]*8 for _ in range(8)]
    b[3][3] = b[4][4] = 2
    b[3][4] = b[4][3] = 1
    return b

def flips_for(board, r, c, player):
    if board[r][c] != 0:
        return []
    other = 3-player
    flips = []
    for dr, dc in DIRECTIONS:
        line=[]; rr=r+dr; cc=c+dc
        while 0 <= rr < 8 and 0 <= cc < 8 and board[rr][cc] == other:
            line.append((rr,cc)); rr += dr; cc += dc
        if line and 0 <= rr < 8 and 0 <= cc < 8 and board[rr][cc] == player:
            flips.extend(line)
    return flips

def legal_moves(board, player):
    return [(r,c) for r in range(8) for c in range(8) if flips_for(board,r,c,player)]

def play(board, r, c, player):
    flips = flips_for(board,r,c,player)
    if not flips:
        return None
    b=[row[:] for row in board]
    b[r][c]=player
    for rr,cc in flips: b[rr][cc]=player
    return b

def counts(board):
    return sum(x==1 for row in board for x in row), sum(x==2 for row in board for x in row)

def is_over(board):
    return not legal_moves(board,1) and not legal_moves(board,2)

def evaluate(board, player):
    # Positional score, mobility, and disc difference (disc difference matters more late game).
    opp=3-player
    positional=sum(WEIGHTS[r][c] * (1 if board[r][c]==player else -1 if board[r][c]==opp else 0)
                   for r in range(8) for c in range(8))
    mobility=5*(len(legal_moves(board,player))-len(legal_moves(board,opp)))
    p,o=counts(board)
    diff=(p-o) if player==1 else (o-p)
    occupied=p+o
    return positional + mobility + diff*(2 if occupied>48 else 0.4)

def minimax(board, player, depth, alpha, beta, maximizing_player):
    moves=legal_moves(board,player)
    if depth==0 or is_over(board):
        return evaluate(board, maximizing_player), None
    if not moves:
        score,_=minimax(board,3-player,depth-1,alpha,beta,maximizing_player)
        return score,None
    if player==maximizing_player:
        best=-math.inf; best_move=moves[0]
        for r,c in moves:
            score,_=minimax(play(board,r,c,player),3-player,depth-1,alpha,beta,maximizing_player)
            if score>best: best,best_move=score,(r,c)
            alpha=max(alpha,best)
            if beta<=alpha: break
        return best,best_move
    best=math.inf; best_move=moves[0]
    for r,c in moves:
        score,_=minimax(play(board,r,c,player),3-player,depth-1,alpha,beta,maximizing_player)
        if score<best: best,best_move=score,(r,c)
        beta=min(beta,best)
        if beta<=alpha: break
    return best,best_move

def cpu_move(board, level):
    moves=legal_moves(board,2)
    if not moves: return None
    depth={"かんたん":1,"ふつう":3,"強い":4}[level]
    if level=="かんたん":
        # A simple but legal move, favoring corners and edges.
        return max(moves,key=lambda m: WEIGHTS[m[0]][m[1]])
    return minimax(board,2,depth,-math.inf,math.inf,2)[1]

# ---------- Session state ----------
if "board" not in st.session_state:
    st.session_state.board=initial_board()
    st.session_state.turn=1
    st.session_state.mode="CPUと対戦"
    st.session_state.level="ふつう"
    st.session_state.history=[]
    st.session_state.message="あなた（黒）の番です。"
    st.session_state.finished=False

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {max-width: 680px; padding-top: 1.2rem; padding-bottom: 2rem;}
.game-title {font-size: clamp(1.8rem, 6vw, 2.6rem); font-weight: 800; text-align:center; margin:.2rem 0 .2rem;}
.game-sub {text-align:center; color:#aeb8b1; margin-bottom:1rem;}
.score-wrap {display:flex; gap:10px; margin:12px 0;}
.score-card {flex:1; background:#202b24; border:1px solid #35513d; border-radius:14px; padding:10px 14px; text-align:center;}
.score-label {font-size:.9rem; opacity:.85;}
.score-num {font-size:2rem; font-weight:800; line-height:1.15;}
.turn-box {background:#203044; border-radius:12px; padding:12px 14px; text-align:center; margin:12px 0 14px; font-weight:650;}
.board-frame {background:#155b32; border:5px solid #104525; border-radius:10px; padding:5px;}
.stButton > button {border-radius:7px; min-height:0; padding:0; font-size:clamp(16px, 4.2vw, 28px); line-height:1; aspect-ratio:1 / 1; width:100%; border:1px solid #2d7745; background:#238447; color:white;}
.stButton > button:hover {border-color:#f5d76e; color:white; background:#2b9652;}
div[data-testid="stHorizontalBlock"] {gap:3px !important;}
div[data-testid="stHorizontalBlock"] > div {min-width:0 !important;}
div[data-testid="stButton"] {width:100%;}
div[data-testid="stButton"] button:focus {border:2px solid #f5d76e; color:white;}
@media (max-width:480px) { .block-container {padding-left:.45rem; padding-right:.45rem;} .stButton > button {font-size:18px;} }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="game-title">⚫ オセロ</div>', unsafe_allow_html=True)
st.markdown('<div class="game-sub">置けるマスをタップしてね</div>', unsafe_allow_html=True)

# Settings
with st.expander("⚙️ 対戦設定", expanded=False):
    mode = st.radio("対戦相手", ["CPUと対戦", "2人で対戦"], horizontal=True,
                    index=0 if st.session_state.mode=="CPUと対戦" else 1)
    level = st.select_slider("CPUの強さ", options=["かんたん","ふつう","強い"], value=st.session_state.level,
                             disabled=(mode!="CPUと対戦"))
    if mode != st.session_state.mode or level != st.session_state.level:
        st.session_state.mode=mode; st.session_state.level=level
        st.session_state.board=initial_board(); st.session_state.turn=1
        st.session_state.history=[]; st.session_state.message="あなた（黒）の番です。"; st.session_state.finished=False
        st.rerun()

b=st.session_state.board
black,white=counts(b)
a,bscore=black,white
st.markdown(f'''<div class="score-wrap">
<div class="score-card"><div class="score-label">⚫ 黒 {'（あなた）' if st.session_state.mode=='CPUと対戦' else ''}</div><div class="score-num">{a}</div></div>
<div class="score-card"><div class="score-label">⚪ 白 {'（CPU）' if st.session_state.mode=='CPUと対戦' else ''}</div><div class="score-num">{bscore}</div></div>
</div>''', unsafe_allow_html=True)

turn=st.session_state.turn
if not st.session_state.finished and not legal_moves(b,turn):
    if not legal_moves(b,3-turn):
        st.session_state.finished=True
    else:
        st.session_state.message=f"{'黒' if turn==1 else '白'}は置ける場所がないためパスです。"
        st.session_state.turn=3-turn
        st.rerun()

if st.session_state.finished or is_over(st.session_state.board):
    st.session_state.finished=True
    black,white=counts(st.session_state.board)
    if black>white: result="黒の勝ち！"
    elif white>black: result="白の勝ち！"
    else: result="引き分け！"
    st.markdown(f'<div class="turn-box">🏁 {result}　最終結果：黒 {black} − 白 {white}</div>',unsafe_allow_html=True)
else:
    player=st.session_state.turn
    if st.session_state.mode=="CPUと対戦":
        turn_text="あなた（黒）の番" if player==1 else "CPU（白）が考えています…"
    else:
        turn_text="黒の番" if player==1 else "白の番"
    st.markdown(f'<div class="turn-box">{turn_text}</div>',unsafe_allow_html=True)

# Board buttons
valid=set(legal_moves(st.session_state.board,st.session_state.turn))
for r in range(8):
    cols=st.columns(8, gap="small")
    for c in range(8):
        val=st.session_state.board[r][c]
        if val==1: label="⚫"
        elif val==2: label="⚪"
        elif (r,c) in valid: label="·"
        else: label=" "
        disabled=(st.session_state.finished or (r,c) not in valid or
                  (st.session_state.mode=="CPUと対戦" and st.session_state.turn==2))
        if cols[c].button(label,key=f"cell_{r}_{c}",disabled=disabled,use_container_width=True):
            st.session_state.history.append(([row[:] for row in st.session_state.board], st.session_state.turn))
            st.session_state.board=play(st.session_state.board,r,c,st.session_state.turn)
            st.session_state.turn=3-st.session_state.turn
            st.session_state.message=""
            st.rerun()

# CPU plays after user's turn
if (not st.session_state.finished and st.session_state.mode=="CPUと対戦" and st.session_state.turn==2
    and legal_moves(st.session_state.board,2)):
    move=cpu_move(st.session_state.board,st.session_state.level)
    if move:
        st.session_state.history.append(([row[:] for row in st.session_state.board], st.session_state.turn))
        st.session_state.board=play(st.session_state.board,*move,2)
    st.session_state.turn=1
    st.rerun()

if st.session_state.message and not st.session_state.finished:
    st.caption(st.session_state.message)

c1,c2=st.columns(2)
with c1:
    if st.button("↶ 一手戻す",use_container_width=True,disabled=(len(st.session_state.history)==0)):
        st.session_state.board,st.session_state.turn=st.session_state.history.pop()
        st.session_state.finished=False; st.rerun()
with c2:
    if st.button("🔄 最初から",use_container_width=True):
        st.session_state.board=initial_board(); st.session_state.turn=1
        st.session_state.history=[]; st.session_state.message="あなた（黒）の番です。"; st.session_state.finished=False
        st.rerun()

with st.expander("📖 遊び方"):
    st.markdown("""
- 黒が先手、白が後手です。
- 相手の石を自分の石ではさむと、はさんだ石が自分の色に変わります。
- 置ける場所がないときは自動でパスします。
- 盤面が埋まるか、両者とも置けなくなると終了です。
- CPU対戦ではあなたが黒、CPUが白です。
""")
