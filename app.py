import streamlit as st

st.set_page_config(page_title="Pythonオセロ", page_icon="⚫", layout="centered")

SIZE = 8
EMPTY, BLACK, WHITE = 0, 1, 2
NAMES = {BLACK: "黒", WHITE: "白"}
SYMBOLS = {EMPTY: "　", BLACK: "⚫", WHITE: "⚪"}
DIRECTIONS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]

def new_board():
    b = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    b[3][3], b[3][4] = WHITE, BLACK
    b[4][3], b[4][4] = BLACK, WHITE
    return b

def flips_for(board, r, c, player):
    if board[r][c] != EMPTY:
        return []
    opponent = WHITE if player == BLACK else BLACK
    flips = []
    for dr, dc in DIRECTIONS:
        line = []
        rr, cc = r + dr, c + dc
        while 0 <= rr < SIZE and 0 <= cc < SIZE and board[rr][cc] == opponent:
            line.append((rr, cc))
            rr += dr
            cc += dc
        if line and 0 <= rr < SIZE and 0 <= cc < SIZE and board[rr][cc] == player:
            flips.extend(line)
    return flips

def legal_moves(board, player):
    return [(r, c) for r in range(SIZE) for c in range(SIZE)
            if flips_for(board, r, c, player)]

def play(board, r, c, player):
    flips = flips_for(board, r, c, player)
    if not flips:
        return False
    board[r][c] = player
    for rr, cc in flips:
        board[rr][cc] = player
    return True

def count(board):
    return sum(cell == BLACK for row in board for cell in row), sum(cell == WHITE for row in board for cell in row)

def reset():
    st.session_state.board = new_board()
    st.session_state.turn = BLACK
    st.session_state.message = "黒の番です"
    st.session_state.finished = False

if "board" not in st.session_state:
    reset()

st.title("⚫ Pythonオセロ")
st.caption("黒からスタート。置けるマスをタップしてね。")

board = st.session_state.board
turn = st.session_state.turn
black_n, white_n = count(board)
moves = legal_moves(board, turn)

c1, c2, c3 = st.columns(3)
c1.metric("⚫ 黒", black_n)
c2.metric("⚪ 白", white_n)
c3.metric("手番", NAMES[turn] if not st.session_state.finished else "終了")

if not st.session_state.finished and not moves:
    other = WHITE if turn == BLACK else BLACK
    if legal_moves(board, other):
        st.session_state.turn = other
        st.session_state.message = f"{NAMES[turn]}は置ける場所がないためパス。{NAMES[other]}の番です"
        st.rerun()
    else:
        st.session_state.finished = True

if st.session_state.finished:
    black_n, white_n = count(board)
    if black_n > white_n:
        result = "黒の勝ち！"
    elif white_n > black_n:
        result = "白の勝ち！"
    else:
        result = "引き分け！"
    st.success(f"ゲーム終了 — {result}（黒 {black_n} 対 白 {white_n}）")
else:
    st.info(st.session_state.message)

# Build a compact, touch-friendly 8x8 board.
for r in range(SIZE):
    cols = st.columns(8, gap="small")
    for c in range(SIZE):
        with cols[c]:
            is_legal = (r, c) in moves
            label = "·" if is_legal else SYMBOLS[board[r][c]]
            disabled = st.session_state.finished or not is_legal
            if st.button(label, key=f"cell_{r}_{c}", disabled=disabled,
                         use_container_width=True, type="primary" if is_legal else "secondary"):
                play(board, r, c, turn)
                st.session_state.turn = WHITE if turn == BLACK else BLACK
                st.session_state.message = f"{NAMES[st.session_state.turn]}の番です"
                st.rerun()

st.button("🔄 最初からやり直す", on_click=reset, use_container_width=True)

with st.expander("遊び方"):
    st.write("・黒から交互に石を置きます。")
    st.write("・相手の石を自分の石で挟める場所にだけ置けます。")
    st.write("・挟んだ相手の石は自分の色に変わります。")
    st.write("・両者とも置けなくなったら終了。石が多い方の勝ちです。")
    st.write("・「·」は現在置けるマスです。")
