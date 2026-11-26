import streamlit as st

st.set_page_config(page_title="オセロ", page_icon="⚫", layout="centered", initial_sidebar_state="collapsed")

SIZE = 8
EMPTY, BLACK, WHITE = 0, 1, 2
NAMES = {BLACK: "黒", WHITE: "白"}
GLYPHS = {EMPTY: "", BLACK: "●", WHITE: "○"}
DIRECTIONS = [(dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0)]


def new_board():
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    board[3][3], board[3][4] = WHITE, BLACK
    board[4][3], board[4][4] = BLACK, WHITE
    return board


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
    return [(r, c) for r in range(SIZE) for c in range(SIZE) if flips_for(board, r, c, player)]


def count(board):
    return (sum(cell == BLACK for row in board for cell in row),
            sum(cell == WHITE for row in board for cell in row))


def reset():
    st.session_state.board = new_board()
    st.session_state.turn = BLACK
    st.session_state.message = "黒の番です。置ける場所（小さな点）を選んでね。"
    st.session_state.finished = False


def finish_or_pass():
    board = st.session_state.board
    turn = st.session_state.turn
    if legal_moves(board, turn):
        return
    other = WHITE if turn == BLACK else BLACK
    if legal_moves(board, other):
        st.session_state.turn = other
        st.session_state.message = f"{NAMES[turn]}は置ける場所がないのでパス。{NAMES[other]}の番です。"
    else:
        st.session_state.finished = True


if "board" not in st.session_state:
    reset()

# Keep the board readable on narrow phone screens.
st.markdown("""
<style>
    .block-container {max-width: 680px; padding: 1.2rem 0.65rem 2rem 0.65rem;}
    h1 {font-size: clamp(1.8rem, 7vw, 2.6rem) !important; margin-bottom: .2rem !important;}
    .st-key-board [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(8, minmax(0, 1fr)) !important;
        gap: 3px !important;
        width: 100% !important;
    }
    .st-key-board [data-testid="column"] {
        width: auto !important; min-width: 0 !important; flex: none !important;
    }
    .st-key-board [data-testid="stButton"] {width: 100%;}
    .st-key-board [data-testid="stButton"] button {
        width: 100%; min-width: 0; height: clamp(36px, 10.4vw, 66px);
        padding: 0 !important; border-radius: 4px !important;
        border: 1px solid #174d2b !important; background: #238b45 !important;
        color: #ffffff !important; font-size: clamp(19px, 6.5vw, 36px) !important;
        line-height: 1 !important; box-shadow: none !important;
    }
    .st-key-board [data-testid="stButton"] button:disabled {
        opacity: 1 !important; color: #ffffff !important; background: #238b45 !important;
    }
    .st-key-board [data-testid="stButton"] button:hover {border-color: #f4d35e !important;}
    div[data-testid="stMetric"] {padding: .35rem .5rem; background: rgba(128,128,128,.08); border-radius: 10px;}
    .turn-banner {padding: .75rem 1rem; border-radius: 12px; background: rgba(60,130,220,.15); font-weight: 600;}
</style>
""", unsafe_allow_html=True)

st.title("⚫ オセロ")
st.caption("黒からスタート。緑の盤面の点が置ける場所だよ。")

board = st.session_state.board
turn = st.session_state.turn
moves = legal_moves(board, turn)

if not st.session_state.finished and not moves:
    finish_or_pass()
    st.rerun()

black_n, white_n = count(board)
score_cols = st.columns(2)
score_cols[0].metric("⚫ 黒", black_n)
score_cols[1].metric("⚪ 白", white_n)

if st.session_state.finished:
    if black_n > white_n:
        result = "黒の勝ち！"
    elif white_n > black_n:
        result = "白の勝ち！"
    else:
        result = "引き分け！"
    st.success(f"{result}　黒 {black_n} 対 白 {white_n}")
else:
    st.markdown(f'<div class="turn-banner">手番：{NAMES[turn]}　｜　{st.session_state.message}</div>', unsafe_allow_html=True)

with st.container(key="board"):
    for r in range(SIZE):
        row_cols = st.columns(8, gap=None)
        for c in range(SIZE):
            is_legal = (r, c) in moves
            value = board[r][c]
            label = "·" if is_legal else GLYPHS[value]
            if not label:
                label = "　"
            with row_cols[c]:
                if st.button(label, key=f"cell_{r}_{c}", disabled=(st.session_state.finished or not is_legal), use_container_width=True):
                    flips = flips_for(st.session_state.board, r, c, st.session_state.turn)
                    if flips:
                        st.session_state.board[r][c] = st.session_state.turn
                        for rr, cc in flips:
                            st.session_state.board[rr][cc] = st.session_state.turn
                        st.session_state.turn = WHITE if st.session_state.turn == BLACK else BLACK
                        st.session_state.message = f"{NAMES[st.session_state.turn]}の番です。"
                        finish_or_pass()
                    st.rerun()

st.button("↻ 最初からやり直す", on_click=reset, use_container_width=True)
with st.expander("遊び方"):
    st.write("・黒と白が交互に打ちます。")
    st.write("・相手の石を自分の石で挟める場所に置けます。")
    st.write("・挟んだ石は自分の色に変わります。")
    st.write("・「·」が置ける場所です。置けないときは自動でパスします。")
    st.write("・両者とも置けなくなったら終了。石が多い方の勝ちです。")
