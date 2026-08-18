#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=======================================================================================
  ASCII CASINO  —  TEXAS HOLD'EM NO-LIMIT
  Sebuah game poker kasino yang berjalan 100% lokal di terminal.
  A casino-style poker game that runs entirely in your terminal.
  Melawan 7 bot AI dengan kepribadian berbeda-beda. Modal awal: $50,000 masing-masing.
  7 AI bot opponents, each with a different style. $50,000 starting stack each.

  Cara main / How to run:
      python3 poker_game.py

  Bahasa/UI dipilih saat game dimulai (Indonesia/English).
  Language is chosen when the game starts (Indonesian/English).

  Kontrol saat giliranmu / Controls on your turn:
      [K] Check     [C] Call     [R] Raise     [A] All-in     [F] Fold     [Q] Quit
=======================================================================================
"""

import random
import os
import re
import sys
import time
import itertools
from collections import deque, Counter

# ---------------------------------------------------------------------------------
# BAHASA / LANGUAGE (i18n)
# ---------------------------------------------------------------------------------
# LANG dipilih lewat choose_language() di awal main() sebelum apa pun ditampilkan.
# Semua teks yg terlihat pemain (bkn komentar kode) diambil lewat t(key, **kwargs).
# Istilah aksi poker inti (Check/Call/Raise/Fold/All-in/Small Blind/Big Blind) sengaja
# dibiarkan bahasa Inggris di kedua bahasa — istilah ini universal & dipakai apa
# adanya oleh pemain poker Indonesia juga.
LANG = 'en'

STRINGS = {
    'id': {
        'subtitle': "7 lawan bot AI dengan gaya berbeda-beda. Modal $50,000. Winner takes all.",
        'controls_label': "Kontrol:",
        'ctrl_check': "check", 'ctrl_call': "call", 'ctrl_raise': "raise",
        'ctrl_allin': "all-in", 'ctrl_fold': "fold", 'ctrl_quit': "keluar",
        'meet_opponents': "Kenali lawanmu:",
        'name_prompt': "Masukkan nama kamu: ",
        'default_name': "Pemain",
        'you_label': "Kamu",
        'you_tag': " (Kamu)",
        'opponents_label': "Lawan-lawan:",
        'remaining_label': "Pemain tersisa:",
        'pause_prompt': "\n  (Tekan Enter untuk lanjut...)",
        'current_hand': "Tangan kamu saat ini:",
        'action_prompt': "{name}, aksi kamu: ",
        'opt_quit': "[Q] Keluar",
        'msg_free_check': "  Kamu bisa check gratis — tidak perlu fold. Pilih lagi.",
        'msg_not_enough_chips': "  Chip kamu tidak cukup untuk raise, coba All-in.",
        'prompt_raise_amount': "  Raise sebesar berapa (minimal {min})? $",
        'msg_invalid_input': "  Input tidak valid.",
        'msg_raise_positive': "  Jumlah raise harus positif.",
        'msg_min_raise': "  Raise minimal {min} (atau All-in).",
        'msg_unrecognized': "  Input tidak dikenali, coba lagi.",
        'note_all_in_runout': "Semua All-in — membuka sisa kartu papan...",
        'msg_win_by_fold': "{winner} menang {amount} (semua lawan fold)",
        'game_over_note': "{name} kehabisan chip. Game over.",
        'standings_header': "\n=== KLASEMEN AKHIR ===",
        'eliminated_tag': "TERSINGKIR",
        'thanks_playing': "\nTerima kasih sudah bermain!",
        'game_stopped': "\n\nGame dihentikan. Sampai jumpa!",
    },
    'en': {
        'subtitle': "7 AI bot opponents, each with a different style. $50,000 starting stack. Winner takes all.",
        'controls_label': "Controls:",
        'ctrl_check': "check", 'ctrl_call': "call", 'ctrl_raise': "raise",
        'ctrl_allin': "all-in", 'ctrl_fold': "fold", 'ctrl_quit': "quit",
        'meet_opponents': "Meet your opponents:",
        'name_prompt': "Enter your name: ",
        'default_name': "Player",
        'you_label': "You",
        'you_tag': " (You)",
        'opponents_label': "Opponents:",
        'remaining_label': "Players remaining:",
        'pause_prompt': "\n  (Press Enter to continue...)",
        'current_hand': "Your current hand:",
        'action_prompt': "{name}, your action: ",
        'opt_quit': "[Q] Quit",
        'msg_free_check': "  You can check for free — no need to fold. Choose again.",
        'msg_not_enough_chips': "  Not enough chips to raise — try All-in instead.",
        'prompt_raise_amount': "  Raise by how much (minimum {min})? $",
        'msg_invalid_input': "  Invalid input.",
        'msg_raise_positive': "  Raise amount must be positive.",
        'msg_min_raise': "  Minimum raise is {min} (or go All-in).",
        'msg_unrecognized': "  Input not recognized, try again.",
        'note_all_in_runout': "Everyone's All-in — revealing the rest of the board...",
        'msg_win_by_fold': "{winner} wins {amount} (all opponents folded)",
        'game_over_note': "{name} is out of chips. Game over.",
        'standings_header': "\n=== FINAL STANDINGS ===",
        'eliminated_tag': "ELIMINATED",
        'thanks_playing': "\nThanks for playing!",
        'game_stopped': "\n\nGame stopped. See you next time!",
    },
}


def t(key, **kwargs):
    """Ambil teks terjemahan sesuai LANG saat ini; format dgn kwargs kalau ada."""
    text = STRINGS[LANG][key]
    return text.format(**kwargs) if kwargs else text


# ---------------------------------------------------------------------------------
# WARNA TERMINAL (ANSI)
# ---------------------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    GREY = "\033[90m"
    RED_BOLD = "\033[1;31m"
    GOLD = "\033[1;33m"
    GREEN_BOLD = "\033[1;32m"


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def fmt(n):
    return f"${n:,.0f}" if isinstance(n, float) else f"${n:,}"


class QuitGame(Exception):
    """Dilempar saat pemain manusia memilih keluar dari game."""
    pass


# ---------------------------------------------------------------------------------
# KARTU & DECK
# ---------------------------------------------------------------------------------
SUITS = ['♠', '♥', '♦', '♣']
RED_SUITS = {'♥', '♦'}
RANK_ORDER = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANK_ORDER)}
RANK_NAME = {v: k for k, v in RANK_VALUE.items()}


class Card:
    __slots__ = ('rank', 'suit', 'value')

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = RANK_VALUE[rank]

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


def build_deck():
    return [Card(r, s) for s in SUITS for r in RANK_ORDER]


FULL_DECK_TEMPLATE = build_deck()


def color_for(card):
    return C.RED_BOLD if card.suit in RED_SUITS else C.BOLD


# ---- ASCII ART KARTU (gaya klasik/pixel — satu ikon bitmap besar per jenis kartu) --
# Terinspirasi deck pixel-art klasik: tiap kartu punya SATU ikon jenis kartu bergaya
# bitmap (bentuk siluet asli spade/heart/diamond/club, digambar blok demi blok) yang
# sama persis di semua rank — pembeda rank cuma indeks kecil di pojok kiri-atas &
# kanan-bawah (spt kartu asli). Lebih sederhana & konsisten drpd pola pip per-rank.
#
# Catatan proporsi: karakter terminal itu sendiri jauh lebih TINGGI drpd LEBAR (kira2
# rasio lebar:tinggi 1:2), jadi grid karakter yg dibuat *persegi* akan tampak memanjang
# ke atas di layar. Supaya kartu terlihat sedekat mungkin dgn rasio kartu remi asli
# (2.5:3.5 ≈ 0.71 lebar:tinggi), kartu ini dibuat LEBIH LEBAR drpd tinggi dlm hitungan
# kolom/baris karakter — setelah dikompensasi bentuk karakter yg tinggi, hasilnya baru
# terlihat proporsional 1:1 dgn bentuk kartu sungguhan.
CARD_INTERIOR_W = 13
CARD_BODY_ROWS = 7

# Bitmap 7x7 per jenis kartu ('#' = pixel terisi, '.' = kosong) — siluet sederhana tapi
# tetap terlihat bentuknya, gaya ikon pixel-art 8-bit.
SUIT_BITMAP = {
    '♥': [
        ".##.##.",
        "#######",
        "#######",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    '♦': [
        "...#...",
        "..###..",
        ".#####.",
        "#######",
        ".#####.",
        "..###..",
        "...#...",
    ],
    '♠': [
        "...#...",
        "..###..",
        ".#####.",
        "#######",
        "##.#.##",
        "...#...",
        "..###..",
    ],
    '♣': [
        "..###..",
        ".#####.",
        "###.###",
        "#######",
        ".#####.",
        "...#...",
        "..###..",
    ],
}


def _suit_icon_rows(suit, col):
    """Bangun CARD_BODY_ROWS baris interior berisi ikon bitmap besar suit, dipusatkan
    horizontal di dalam CARD_INTERIOR_W — dipakai sama utk semua rank kartu ini."""
    bitmap = SUIT_BITMAP[suit]
    bmp_w = len(bitmap[0])
    margin_l = (CARD_INTERIOR_W - bmp_w) // 2
    margin_r = CARD_INTERIOR_W - bmp_w - margin_l
    rows = []
    for line in bitmap:
        cells_txt = "".join((col + '█' + C.RESET) if ch == '#' else ' ' for ch in line)
        rows.append("║" + " " * margin_l + cells_txt + " " * margin_r + "║")
    return rows


def _back_pattern_row(width, offset):
    """Satu baris pola punggung kartu (checker belah ketupat), dibangun dinamis sesuai
    `width` supaya selalu pas berapa pun CARD_INTERIOR_W-nya."""
    cycle = "◆░◇░"
    return "".join(cycle[(i + offset) % len(cycle)] for i in range(width))


def card_art_lines(card=None, hidden=False):
    """Kembalikan baris-baris ASCII art kartu bergaya klasik/pixel."""
    top = "╔" + "═" * CARD_INTERIOR_W + "╗"
    bot = "╚" + "═" * CARD_INTERIOR_W + "╝"

    if hidden:
        col = C.BLUE
        rows = [top]
        for i in range(CARD_BODY_ROWS + 2):
            rows.append("║" + _back_pattern_row(CARD_INTERIOR_W, 0 if i % 2 == 0 else 2) + "║")
        rows.append(bot)
        return [col + r + C.RESET for r in rows]

    if card is None:
        col = C.GREY
        blank = "║" + " " * CARD_INTERIOR_W + "║"
        rows = [top] + [blank] * (CARD_BODY_ROWS + 2) + [bot]
        return [col + r + C.RESET for r in rows]

    col = color_for(card)
    rank, suit = card.rank, card.suit
    corner_top = "║" + col + f"{rank.ljust(2)} {suit}".ljust(CARD_INTERIOR_W) + C.RESET + "║"
    corner_bot = "║" + col + f"{suit} {rank.rjust(2)}".rjust(CARD_INTERIOR_W) + C.RESET + "║"

    body_rows = _suit_icon_rows(suit, col)

    lines = [col + top + C.RESET, corner_top] + body_rows + [corner_bot, col + bot + C.RESET]
    return lines


def render_row(cards, hidden_flags=None, spacing=1):
    if hidden_flags is None:
        hidden_flags = [False] * len(cards)
    arts = [card_art_lines(c, h) for c, h in zip(cards, hidden_flags)]
    if not arts:
        return ""
    height = len(arts[0])
    lines = []
    for i in range(height):
        lines.append((" " * spacing).join(art[i] for art in arts))
    return "\n".join(lines)


# ---- helper untuk layout kolom (grid) di terminal --------------------------------
ANSI_RE = re.compile(r'\033\[[0-9;]*m')


def visible_len(s):
    return len(ANSI_RE.sub('', s))


def pad(s, width):
    diff = width - visible_len(s)
    return s + (" " * diff if diff > 0 else "")


def fmt_short(n):
    """Format angka chip singkat untuk sel grid, mis. $50.0k / $1.2k / $850."""
    if abs(n) >= 1000:
        return f"${n / 1000:.1f}k"
    return f"${n:,}"


MINI_CARD_W = 3  # lebar interior kartu mini (grid lawan), muat "10"


def mini_card_lines(card=None, hidden=False):
    """Kartu mini bergaya sama (kotak bersudut, bkn cuma teks kode), dipakai di grid
    lawan: tertutup (punggung kartu) selama belum showdown, terbuka versi kecil saat
    showdown. 4 baris x 5 kolom."""
    top = "┌" + "─" * MINI_CARD_W + "┐"
    bot = "└" + "─" * MINI_CARD_W + "┘"
    if hidden or card is None:
        col = C.BLUE
        back = "│" + "▓" * MINI_CARD_W + "│"
        return [col + top + C.RESET, col + back + C.RESET, col + back + C.RESET, col + bot + C.RESET]
    col = color_for(card)
    row_rank = "│" + col + card.rank.ljust(MINI_CARD_W) + C.RESET + "│"
    row_suit = "│" + col + card.suit.center(MINI_CARD_W) + C.RESET + "│"
    return [col + top + C.RESET, row_rank, row_suit, col + bot + C.RESET]


def mini_render_row(cards, hidden_flags=None, spacing=1):
    """Sama seperti render_row(), tapi memakai template kartu mini; hasil sbg list baris."""
    if hidden_flags is None:
        hidden_flags = [False] * len(cards)
    arts = [mini_card_lines(c, h) for c, h in zip(cards, hidden_flags)]
    if not arts:
        return []
    height = len(arts[0])
    return [(" " * spacing).join(art[i] for art in arts) for i in range(height)]


def join_columns(left_lines, right_lines, left_width, gap=3):
    """Gabungkan dua blok teks multi-baris jadi dua kolom berdampingan."""
    total = max(len(left_lines), len(right_lines))
    out = []
    for i in range(total):
        l = pad(left_lines[i], left_width) if i < len(left_lines) else " " * left_width
        r = right_lines[i] if i < len(right_lines) else ""
        out.append(l + (" " * gap) + r)
    return out


def center_text(s, width):
    """Tengahkan teks (ANSI-aware) di dalam lebar tertentu, dipakai utk header blok showdown."""
    vis = visible_len(s)
    if vis >= width:
        return s
    total = width - vis
    left = total // 2
    right = total - left
    return (" " * left) + s + (" " * right)


# tata-letak grid pemain lain (di sebelah kanan)
LEFT_PANEL_WIDTH = 34
GRID_CELL_WIDTH = 27
GRID_CELL_GAP = 2
PANEL_GAP = 3
BOT_CELL_HEIGHT = 8  # nama, chip/bet, 4 baris kartu mini, status, aksi terakhir
GRID_ROWS_TARGET = 2  # jejerkan lawan maks 2 baris ke kanan (melebar), bukan menumpuk ke bawah

# tata-letak baris kartu showdown (kartu besar berjajar ke kanan per pemain)
SHOWDOWN_COLS = 3
SHOWDOWN_GAP = 4


def showdown_block_lines(player, hand_label, is_winner, is_button):
    """Satu blok showdown utk 1 pemain: nama+status di baris atas, kartu besar di bawahnya."""
    card_lines = render_row(player.hole, [False, False]).split("\n")
    block_width = max((visible_len(l) for l in card_lines), default=CARD_INTERIOR_W + 2)

    crown = (C.GOLD + " ♛ WINNER" + C.RESET) if is_winner else ""
    btn = (C.CYAN + " [BTN]" + C.RESET) if is_button else ""
    name_line = center_text(f"{C.BOLD}{player.name}{C.RESET}{btn}{crown}", block_width)
    status_line = center_text(f"{C.CYAN}{hand_label}{C.RESET}", block_width)

    return [name_line, status_line, ""] + card_lines


def showdown_layout_lines(blocks, cols=SHOWDOWN_COLS, gap=SHOWDOWN_GAP):
    """Susun blok-blok showdown_block_lines() berjajar ke kanan, membungkus tiap `cols` kolom."""
    if not blocks:
        return []
    height = len(blocks[0])
    lines = []
    for i in range(0, len(blocks), cols):
        row_blocks = blocks[i:i + cols]
        widths = [max(visible_len(l) for l in b) for b in row_blocks]
        for line_idx in range(height):
            row_line = (" " * gap).join(pad(b[line_idx], w) for b, w in zip(row_blocks, widths))
            lines.append(row_line)
        lines.append("")
    return lines


# ---------------------------------------------------------------------------------
# EVALUATOR TANGAN POKER (7 kartu -> tangan terbaik 5 kartu)
# ---------------------------------------------------------------------------------
def evaluate_5(cards):
    """cards: list 5 Card. Return (kategori, tuple_tiebreak) — makin besar makin bagus."""
    values = sorted((c.value for c in cards), reverse=True)
    suits = [c.suit for c in cards]
    is_flush = len(set(suits)) == 1

    unique_vals = sorted(set(values), reverse=True)
    is_straight = False
    straight_high = None
    if len(unique_vals) == 5:
        if unique_vals[0] - unique_vals[4] == 4:
            is_straight = True
            straight_high = unique_vals[0]
        elif unique_vals == [14, 5, 4, 3, 2]:
            is_straight = True
            straight_high = 5  # wheel: A-2-3-4-5

    counts = Counter(values)
    groups = sorted(counts.items(), key=lambda kv: (-kv[1], -kv[0]))
    pattern = tuple(g[1] for g in groups)
    ordered_values = [g[0] for g in groups]

    if is_straight and is_flush:
        return (8, (straight_high,))
    if pattern == (4, 1):
        return (7, (ordered_values[0], ordered_values[1]))
    if pattern == (3, 2):
        return (6, (ordered_values[0], ordered_values[1]))
    if is_flush:
        return (5, tuple(values))
    if is_straight:
        return (4, (straight_high,))
    if pattern == (3, 1, 1):
        return (3, (ordered_values[0], ordered_values[1], ordered_values[2]))
    if pattern == (2, 2, 1):
        return (2, (ordered_values[0], ordered_values[1], ordered_values[2]))
    if pattern == (2, 1, 1, 1):
        return (1, (ordered_values[0], ordered_values[1], ordered_values[2], ordered_values[3]))
    return (0, tuple(values))


def evaluate_best(cards7):
    """Cari kombinasi 5 kartu terbaik dari 7 (atau kurang) kartu."""
    best = None
    best_combo = None
    n = len(cards7)
    k = min(5, n)
    for combo in itertools.combinations(cards7, k):
        cc = list(combo)
        while len(cc) < 5:
            cc.append(cc[-1])  # jaga-jaga (tak seharusnya terjadi di gameplay normal)
        score = evaluate_5(cc)
        if best is None or score > best:
            best = score
            best_combo = combo
    return best, best_combo


HAND_CATEGORY_NAMES = {
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card",
}


def hand_name(score):
    cat, tb = score
    if cat == 8:
        if tb[0] == 14:
            return "Royal Flush"
        return f"Straight Flush, {RANK_NAME[tb[0]]}-high"
    if cat == 7:
        return f"Four of a Kind, {RANK_NAME[tb[0]]}s"
    if cat == 6:
        return f"Full House, {RANK_NAME[tb[0]]}s over {RANK_NAME[tb[1]]}s"
    if cat == 5:
        return f"Flush, {RANK_NAME[tb[0]]}-high"
    if cat == 4:
        return f"Straight, {RANK_NAME[tb[0]]}-high"
    if cat == 3:
        return f"Three of a Kind, {RANK_NAME[tb[0]]}s"
    if cat == 2:
        return f"Two Pair, {RANK_NAME[tb[0]]}s and {RANK_NAME[tb[1]]}s"
    if cat == 1:
        return f"Pair of {RANK_NAME[tb[0]]}s"
    return f"High Card, {RANK_NAME[tb[0]]}"


# ---------------------------------------------------------------------------------
# KEPRIBADIAN BOT
# ---------------------------------------------------------------------------------
PERSONALITIES = {
    "rock":     dict(label="The Rock",          vpip=0.16, aggression=0.25, bluff=0.03, fold_to_raise=0.75),
    "maniac":   dict(label="The Maniac",         vpip=0.65, aggression=0.85, bluff=0.35, fold_to_raise=0.15),
    "shark":    dict(label="The Shark",          vpip=0.28, aggression=0.60, bluff=0.12, fold_to_raise=0.40),
    "station":  dict(label="The Calling Station", vpip=0.55, aggression=0.15, bluff=0.05, fold_to_raise=0.10),
    "bluffer":  dict(label="The Bluffer",        vpip=0.35, aggression=0.55, bluff=0.45, fold_to_raise=0.35),
    "mathlete": dict(label="The Mathematician",  vpip=0.24, aggression=0.50, bluff=0.05, fold_to_raise=0.50),
    "wildcard": dict(label="The Wildcard",       vpip=0.40, aggression=0.50, bluff=0.25, fold_to_raise=0.30),
}

PERSONALITY_DESC = {
    'id': {
        "rock":     "Sangat selektif, jarang bermain kecuali tangan kuat. Nyaris tidak pernah bluff.",
        "maniac":   "Longgar dan agresif — bertaruh besar dan sering bluff. Bahaya kalau dianggap enteng.",
        "shark":    "Seimbang dan kalkulatif, mendekati gaya bermain optimal (GTO-ish).",
        "station":  "Suka memanggil (call) hampir apa saja, jarang melipat (fold) atau menaikkan (raise).",
        "bluffer":  "Sering menggertak tanpa memandang kekuatan tangan sebenarnya.",
        "mathlete": "Bermain sangat dekat dengan pot odds & ekuitas murni, minim emosi.",
        "wildcard": "Tidak dapat diprediksi — gayanya berubah-ubah dari tangan ke tangan.",
    },
    'en': {
        "rock":     "Extremely selective — rarely plays unless holding a strong hand. Almost never bluffs.",
        "maniac":   "Loose and aggressive — bets big and bluffs often. Dangerous if underestimated.",
        "shark":    "Balanced and calculating, close to an optimal (GTO-ish) playing style.",
        "station":  "Loves calling almost anything, rarely folds or raises.",
        "bluffer":  "Bluffs often, regardless of actual hand strength.",
        "mathlete": "Plays very close to pot odds and pure equity, with little emotion.",
        "wildcard": "Unpredictable — style shifts from hand to hand.",
    },
}

EQUITY_TRIALS = 60


def chen_score(hole):
    """Skor heuristik Chen Formula untuk kekuatan kartu pre-flop (0..~20)."""
    c1, c2 = hole
    high = max(c1.value, c2.value)
    low = min(c1.value, c2.value)
    base_points = {14: 10, 13: 8, 12: 7, 11: 6}
    score = base_points.get(high, high / 2.0)
    if c1.value == c2.value:
        score = max(score * 2, 5)
    if c1.suit == c2.suit:
        score += 2
    if c1.value != c2.value:
        gap = high - low - 1
        if gap == 1:
            score -= 1
        elif gap == 2:
            score -= 2
        elif gap == 3:
            score -= 4
        elif gap >= 4:
            score -= 5
        if gap <= 1 and high < 12:
            score += 1
    return max(score, 0)


def estimate_equity(hole, board, num_opponents, trials=EQUITY_TRIALS):
    """Estimasi probabilitas menang via simulasi Monte Carlo acak melawan N lawan."""
    known = set(hole) | set(board)
    deck = [c for c in FULL_DECK_TEMPLATE if c not in known]
    remaining_needed = 5 - len(board)
    need_per_trial = remaining_needed + 2 * num_opponents
    if need_per_trial > len(deck) or trials <= 0:
        return 0.5
    wins = 0.0
    for _ in range(trials):
        sample = random.sample(deck, need_per_trial)
        extra_board = sample[:remaining_needed]
        full_board = board + extra_board
        idx = remaining_needed
        opp_hands = []
        for _o in range(num_opponents):
            opp_hands.append([sample[idx], sample[idx + 1]])
            idx += 2
        my_score, _ = evaluate_best(hole + full_board)
        win = True
        tie = False
        for oh in opp_hands:
            osc, _ = evaluate_best(oh + full_board)
            if osc > my_score:
                win = False
                break
            elif osc == my_score:
                tie = True
        if win:
            wins += 0.5 if tie else 1.0
    return wins / trials


def raise_size(pot_ref, aggression, effective, min_raise):
    frac = 0.4 + aggression * 0.5 + (effective - 0.5) * 0.4
    frac = max(0.3, min(frac, 1.4))
    amount = int(pot_ref * frac)
    return max(amount, min_raise)


def bot_decide(player, to_call, min_raise, pot_now, strength):
    """Kembalikan (aksi, jumlah). aksi in {'fold','check','call','raise'}."""
    p = player.personality
    aggression = p['aggression']
    bluff_rate = p['bluff']
    tightness = 1 - p['vpip']

    is_bluff = random.random() < bluff_rate * (0.6 if to_call > 0 else 1.0)
    effective = random.uniform(0.65, 0.95) if is_bluff else strength

    if to_call <= 0:
        bet_prob = min(aggression * (0.3 + effective), 0.9)
        if effective > 0.75 or random.random() < bet_prob:
            amt = raise_size(pot_now, aggression, effective, min_raise)
            return ('raise', amt)
        return ('check', 0)
    else:
        pot_odds = to_call / (pot_now + to_call)
        required = pot_odds + tightness * 0.18 - aggression * 0.08
        required = max(0.03, min(required, 0.92))
        if effective < required:
            if to_call <= max(1, player.chips) * 0.05 and random.random() < (1 - tightness):
                return ('call', to_call)
            return ('fold', 0)
        raise_prob = aggression * (0.25 + effective * 0.5)
        if effective > 0.8 or random.random() < raise_prob:
            amt = raise_size(pot_now + to_call, aggression, effective, min_raise)
            return ('raise', amt)
        return ('call', to_call)


# ---------------------------------------------------------------------------------
# PEMAIN
# ---------------------------------------------------------------------------------
class Player:
    def __init__(self, name, chips, is_bot=False, personality=None):
        self.name = name
        self.chips = chips
        self.is_bot = is_bot
        self.personality = personality
        self.hole = []
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.total_bet_hand = 0
        self.eliminated = False
        self.last_action = ""

    def reset_for_hand(self):
        self.hole = []
        self.folded = False
        self.all_in = False
        self.current_bet = 0
        self.total_bet_hand = 0
        self.last_action = ""

    def reset_for_street(self):
        self.current_bet = 0

    def bet(self, amount):
        amount = max(0, min(amount, self.chips))
        self.chips -= amount
        self.current_bet += amount
        self.total_bet_hand += amount
        if self.chips == 0:
            self.all_in = True
        return amount


# ---------------------------------------------------------------------------------
# GAME ENGINE
# ---------------------------------------------------------------------------------
class PokerGame:
    def __init__(self, human_name, num_bots=7, starting_chips=50000, small_blind=100, big_blind=200):
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.hand_number = 0
        self.human = Player(human_name, starting_chips, is_bot=False)

        keys = list(PERSONALITIES.keys())
        random.shuffle(keys)
        keys = keys[:num_bots]
        self.bots = [Player(PERSONALITIES[k]['label'], starting_chips, is_bot=True,
                             personality=PERSONALITIES[k]) for k in keys]

        self.players = [self.human] + self.bots
        random.shuffle(self.players)
        self.button_player = None
        self.board = []
        self.deck = []

    # ---------- helper umum ----------
    def active_players(self):
        return [p for p in self.players if not p.eliminated]

    def pot_total(self):
        return sum(p.total_bet_hand for p in self.players)

    def count_not_folded(self, seat_order):
        return len([p for p in seat_order if not p.folded])

    def can_still_bet(self, seat_order):
        not_folded = [p for p in seat_order if not p.folded]
        if len(not_folded) <= 1:
            return False
        can_act = [p for p in not_folded if not p.all_in and p.chips > 0]
        return len(can_act) >= 2

    def deal_board(self, n):
        if self.deck:
            self.deck.pop()  # burn card
        for _ in range(n):
            self.board.append(self.deck.pop())

    def compute_pots(self, seat_order):
        contributions = [(p, p.total_bet_hand) for p in seat_order if p.total_bet_hand > 0]
        if not contributions:
            return []
        levels = sorted(set(c for _, c in contributions))
        pots = []
        prev_level = 0
        for level in levels:
            layer_contributors = [p for p, c in contributions if c >= level]
            layer_amount = (level - prev_level) * len(layer_contributors)
            eligible = [p for p in layer_contributors if not p.folded]
            if layer_amount > 0:
                pots.append((layer_amount, eligible))
            prev_level = level
        return pots

    # ---------- rendering ----------
    def _bot_cell_lines(self, p, reveal):
        """BOT_CELL_HEIGHT baris utk satu sel bot di grid: nama, chip/bet, kartu mini
        (tertutup selama belum showdown; terbuka versi kecil begitu showdown & tdk fold),
        status, aksi terakhir."""
        tag = C.CYAN + " [BTN]" + C.RESET if p is self.button_player else ""
        name_line = pad(f"{C.BOLD}{p.name[:20]}{C.RESET}{tag}", GRID_CELL_WIDTH)

        info_line = f"chips:{fmt_short(p.chips)}  bet:{fmt_short(p.current_bet)}"
        info_line = pad(info_line, GRID_CELL_WIDTH)

        hole = p.hole if p.hole else [None, None]
        # Kartu yg fold tetap tertutup selamanya (dibuang/mucked, spt aturan poker
        # sungguhan) — hanya kartu yg ikut showdown yg terbuka.
        hidden = not (reveal and not p.folded)
        card_lines = [pad(l, GRID_CELL_WIDTH) for l in mini_render_row(hole, [hidden, hidden])]

        status = ""
        if p.folded:
            status = C.GREY + "FOLD" + C.RESET
        elif p.all_in:
            status = C.MAGENTA + "ALL-IN" + C.RESET
        status_line = pad(status, GRID_CELL_WIDTH)

        action_txt = (p.last_action or "")[:20]
        action_line = pad(f"{C.DIM}{action_txt}{C.RESET}", GRID_CELL_WIDTH)

        return [name_line, info_line] + card_lines + [status_line, action_line]

    def _opponents_grid_lines(self, reveal):
        """Susun semua bot (bukan human) ke dalam grid, dikembalikan sbg list baris.
        Jumlah kolom dihitung otomatis supaya lawan selalu jejer maks GRID_ROWS_TARGET
        baris ke kanan (melebar), bukan menumpuk ke bawah jadi terlalu tinggi."""
        bots = [p for p in self.players if p is not self.human and not p.eliminated]
        lines = [f"{C.BOLD}{t('opponents_label')}{C.RESET}", ""]
        if not bots:
            return lines
        cols = -(-len(bots) // GRID_ROWS_TARGET)  # ceil(len(bots) / GRID_ROWS_TARGET)
        empty_cell = [" " * GRID_CELL_WIDTH] * BOT_CELL_HEIGHT
        for i in range(0, len(bots), cols):
            row_bots = bots[i:i + cols]
            cells = [self._bot_cell_lines(b, reveal) for b in row_bots]
            while len(cells) < cols:
                cells.append(empty_cell)
            for line_idx in range(BOT_CELL_HEIGHT):
                row_line = (" " * GRID_CELL_GAP).join(cells[c][line_idx] for c in range(cols))
                lines.append(row_line)
            lines.append("")  # spasi antar baris grid
        return lines

    def render_table(self, street, reveal=False, note=None, winners=None):
        clear_screen()
        W = 72
        title = f"♠♥  A S C I I   C A S I N O — TEXAS HOLD'EM NO-LIMIT  ♦♣    Hand #{self.hand_number}"
        print(C.GOLD + "╔" + "═" * W + "╗" + C.RESET)
        print(C.GOLD + "║" + pad("  " + title, W) + "║" + C.RESET)
        print(C.GOLD + "╚" + "═" * W + "╝" + C.RESET)
        remaining = len(self.active_players())
        chip_icon = C.YELLOW + "◉" + C.RESET
        print(f"  {chip_icon} Blinds: {C.BOLD}{fmt(self.small_blind)}/{fmt(self.big_blind)}{C.RESET}   "
              f"│  Street: {C.BOLD}{street.upper()}{C.RESET}   "
              f"│  Pot: {C.GREEN_BOLD}{fmt(self.pot_total())}{C.RESET}   "
              f"│  {t('remaining_label')} {C.BOLD}{remaining}{C.RESET}")
        print()
        print(f"  {C.BOLD}{C.YELLOW}♣ Community Cards ♦{C.RESET}")
        board_cards = self.board + [None] * (5 - len(self.board))
        print(render_row(board_cards, [False] * 5))
        print()
        print(C.GOLD + "─" * (W + 2) + C.RESET)

        # --- kolom kiri: kamu ---
        left_lines = [f"{C.BOLD}{C.YELLOW}★ {t('you_label')}{C.RESET}"]
        p = self.human
        if not p.eliminated:
            you_status = ""
            if p.folded:
                you_status = C.GREY + "FOLDED" + C.RESET
            elif p.all_in:
                you_status = C.MAGENTA + "ALL-IN" + C.RESET
            btn = C.CYAN + " [BTN]" + C.RESET if p is self.button_player else ""
            left_lines.append(f"{C.BOLD}{p.name}{C.RESET}{btn}")
            left_lines.append(f"chips:{fmt(p.chips)}  bet:{fmt(p.current_bet)}  {you_status}")
            left_lines.append(f"{C.DIM}{p.last_action}{C.RESET}")
            left_lines.append("")
            if p.hole:
                left_lines.extend(render_row(p.hole, [False, False]).split("\n"))

        # --- kolom kanan: grid lawan-lawan ---
        right_lines = self._opponents_grid_lines(reveal)

        for line in join_columns(left_lines, right_lines, LEFT_PANEL_WIDTH, PANEL_GAP):
            print("  " + line)

        print(C.GOLD + "─" * (W + 2) + C.RESET)
        if note:
            print(C.YELLOW + "  " + note + C.RESET)
        if winners:
            for line in winners:
                print(C.GREEN_BOLD + "  " + line + C.RESET)

    def pause_for_human(self):
        try:
            input(C.DIM + t('pause_prompt') + C.RESET)
        except EOFError:
            pass

    # ---------- aksi ----------
    def bot_strength(self, player, opponents):
        if not self.board:
            return min(chen_score(player.hole) / 20.0, 1.0)
        return estimate_equity(player.hole, self.board, max(opponents, 1))

    def human_action(self, player, to_call, min_raise, pot_now, current_bet):
        if self.board:
            score, _ = evaluate_best(player.hole + self.board)
            print(C.CYAN + f"  {t('current_hand')} {hand_name(score)}" + C.RESET)
        while True:
            opts = []
            if to_call == 0:
                opts.append("[K] Check")
            else:
                opts.append(f"[C] Call {fmt(min(to_call, player.chips))}")
            if player.chips > to_call:
                opts.append("[R] Raise")
            if player.chips > 0:
                opts.append("[A] All-in")
            if to_call > 0:
                opts.append("[F] Fold")
            opts.append(t('opt_quit'))
            print(C.YELLOW + "  " + "   ".join(opts) + C.RESET)
            try:
                raw = input(t('action_prompt', name=f"{C.BOLD}{player.name}{C.RESET}")).strip().lower()
            except EOFError:
                raise QuitGame()
            if raw in ('q', 'quit', 'exit', 'keluar'):
                raise QuitGame()
            if raw in ('k', 'check') and to_call == 0:
                return ('check', 0)
            if raw in ('c', 'call'):
                return ('check', 0) if to_call == 0 else ('call', to_call)
            if raw in ('f', 'fold'):
                if to_call == 0:
                    print(t('msg_free_check'))
                    continue
                return ('fold', 0)
            if raw in ('a', 'all-in', 'allin'):
                return ('raise', player.chips)
            if raw in ('r', 'raise'):
                if player.chips <= to_call:
                    print(t('msg_not_enough_chips'))
                    continue
                try:
                    amt_str = input(t('prompt_raise_amount', min=fmt(min_raise))).strip()
                    amt = int(amt_str.replace(',', ''))
                except (ValueError, EOFError):
                    print(t('msg_invalid_input'))
                    continue
                max_possible = player.chips - to_call
                if amt <= 0:
                    print(t('msg_raise_positive'))
                    continue
                if amt < min_raise and amt < max_possible:
                    print(t('msg_min_raise', min=fmt(min_raise)))
                    continue
                return ('raise', min(amt, max_possible))
            print(t('msg_unrecognized'))

    def get_action(self, player, to_call, min_raise, pot_now, current_bet, seat_order):
        if player.is_bot:
            opponents = len([p for p in seat_order if not p.folded and p is not player])
            strength = self.bot_strength(player, opponents)
            action, amt = bot_decide(player, to_call, min_raise, pot_now, strength)
            if to_call <= 0 and action == 'call':
                action = 'check'
            if to_call > 0 and action == 'check':
                action = 'call'
            return action, amt
        return self.human_action(player, to_call, min_raise, pot_now, current_bet)

    # ---------- ronde taruhan ----------
    def run_betting_street(self, street, seat_order, button_idx, bb_idx):
        n = len(seat_order)
        if street == 'preflop':
            first_idx = (bb_idx + 1) % n
        else:
            first_idx = (button_idx + 1) % n
        ordered = seat_order[first_idx:] + seat_order[:first_idx]
        to_act = deque([p for p in ordered if not p.folded and not p.all_in])
        current_bet = max((p.current_bet for p in seat_order if not p.folded), default=0)
        min_raise = self.big_blind

        while to_act:
            player = to_act.popleft()
            if player.folded or player.all_in:
                continue
            if self.count_not_folded(seat_order) <= 1:
                break
            to_call = current_bet - player.current_bet
            pot_now = self.pot_total()
            action, amt = self.get_action(player, to_call, min_raise, pot_now, current_bet, seat_order)

            if action == 'fold':
                player.folded = True
                player.last_action = "Fold"
            elif action == 'check':
                player.last_action = "Check"
            elif action == 'call':
                pay = min(to_call, player.chips)
                player.bet(pay)
                player.last_action = f"Call {fmt(pay)}" if pay > 0 else "Check"
            elif action == 'raise':
                raise_amt = max(amt, 1)
                target = current_bet + max(raise_amt, min_raise)
                need = target - player.current_bet
                pay = min(need, player.chips)
                player.bet(pay)
                actual_level = player.current_bet
                if actual_level > current_bet:
                    gained_raise = actual_level - current_bet
                    current_bet = actual_level
                    min_raise = max(min_raise, gained_raise)
                    player.last_action = (f"All-in {fmt(actual_level)}" if player.chips == 0
                                           else f"Raise to {fmt(actual_level)}")
                    to_act = deque([p for p in ordered if p is not player and not p.folded and not p.all_in])
                else:
                    player.last_action = (f"All-in {fmt(actual_level)}" if player.chips == 0
                                           else f"Call {fmt(pay)}")

            self.render_table(street, reveal=False)
            if player.is_bot:
                time.sleep(0.35)

    # ---------- satu tangan penuh ----------
    def play_hand(self):
        self.hand_number += 1
        seat_order = self.active_players()
        if len(seat_order) < 2:
            return False

        for p in seat_order:
            p.reset_for_hand()
        self.board = []
        self.deck = build_deck()
        random.shuffle(self.deck)

        if self.button_player is None or self.button_player.eliminated:
            self.button_player = seat_order[0]
        else:
            idx = self.players.index(self.button_player)
            i = (idx + 1) % len(self.players)
            guard = 0
            while self.players[i].eliminated and guard < len(self.players):
                i = (i + 1) % len(self.players)
                guard += 1
            self.button_player = self.players[i]

        n = len(seat_order)
        button_idx = seat_order.index(self.button_player)
        if n == 2:
            sb_idx, bb_idx = button_idx, (button_idx + 1) % n
        else:
            sb_idx = (button_idx + 1) % n
            bb_idx = (button_idx + 2) % n
        sb_player = seat_order[sb_idx]
        bb_player = seat_order[bb_idx]

        deal_order = seat_order[sb_idx:] + seat_order[:sb_idx]
        for _ in range(2):
            for p in deal_order:
                p.hole.append(self.deck.pop())

        sb_amt = sb_player.bet(min(self.small_blind, sb_player.chips))
        bb_amt = bb_player.bet(min(self.big_blind, bb_player.chips))
        sb_player.last_action = f"Small Blind {fmt(sb_amt)}"
        bb_player.last_action = f"Big Blind {fmt(bb_amt)}"

        self.render_table('preflop', reveal=False,
                           note=f"{sb_player.name} posts SB, {bb_player.name} posts BB.")
        if self.human in seat_order and not self.human.folded:
            self.pause_for_human()

        self.run_betting_street('preflop', seat_order, button_idx, bb_idx)

        for street, num_cards in (('flop', 3), ('turn', 1), ('river', 1)):
            if self.count_not_folded(seat_order) <= 1:
                break
            self.deal_board(num_cards)
            for p in seat_order:
                p.reset_for_street()
            if self.can_still_bet(seat_order):
                self.render_table(street, reveal=False)
                self.run_betting_street(street, seat_order, button_idx, bb_idx)
            else:
                self.render_table(street, reveal=False, note=t('note_all_in_runout'))
                time.sleep(0.6)

        while self.count_not_folded(seat_order) > 1 and len(self.board) < 5:
            self.deal_board(3 if len(self.board) == 0 else 1)

        self.showdown(seat_order)

        for p in seat_order:
            if p.chips <= 0:
                p.eliminated = True
                p.last_action = "ELIMINATED"
        return True

    # ---------- showdown ----------
    def showdown(self, seat_order):
        not_folded = [p for p in seat_order if not p.folded]
        result_lines = []
        if len(not_folded) == 1:
            winner = not_folded[0]
            amount = self.pot_total()
            winner.chips += amount
            for p in seat_order:
                p.total_bet_hand = 0
            result_lines.append(t('msg_win_by_fold', winner=winner.name, amount=fmt(amount)))
            self.render_table('showdown', reveal=False, winners=result_lines)
            self.pause_for_human()
            return

        pots = self.compute_pots(seat_order)
        scores, names = {}, {}
        for p in not_folded:
            score, _ = evaluate_best(p.hole + self.board)
            scores[p] = score
            names[p] = hand_name(score)

        winner_set = set()
        for amount, eligible in pots:
            eligible_in_hand = [p for p in eligible if p in not_folded]
            if not eligible_in_hand:
                continue
            best_score = max(scores[p] for p in eligible_in_hand)
            pot_winners = [p for p in eligible_in_hand if scores[p] == best_score]
            winner_set.update(pot_winners)
            share = amount // len(pot_winners)
            remainder = amount - share * len(pot_winners)
            for i, w in enumerate(pot_winners):
                w.chips += share + (1 if i < remainder else 0)
            wnames = ", ".join(f"{w.name} ({names[w]})" for w in pot_winners)
            result_lines.append(f"Pot {fmt(amount)} -> {wnames}")

        for p in seat_order:
            p.total_bet_hand = 0

        self.render_table('showdown', reveal=True, winners=result_lines)
        print()
        print(C.GOLD + "  " + "─" * 30 + f" {C.BOLD}SHOWDOWN{C.RESET}{C.GOLD} " + "─" * 30 + C.RESET)
        print()
        # tampilkan kartu tiap pemain yang masih hidup dalam ukuran besar & detail,
        # berjajar ke kanan (nama + status tangan di atas kartu masing-masing pemain)
        blocks = [
            showdown_block_lines(p, names[p], p in winner_set, p is self.button_player)
            for p in not_folded
        ]
        for line in showdown_layout_lines(blocks):
            print("  " + line)
        self.pause_for_human()

    # ---------- loop turnamen ----------
    def print_standings(self):
        ranked = sorted(self.players, key=lambda p: -p.chips)
        print(C.GOLD + t('standings_header') + C.RESET)
        for i, p in enumerate(ranked, 1):
            tag = t('you_tag') if p is self.human else ""
            status = t('eliminated_tag') if p.eliminated else fmt(p.chips)
            print(f"  {i}. {p.name}{tag}: {status}")

    def run(self):
        try:
            while True:
                active = self.active_players()
                if len(active) < 2:
                    break
                cont = self.play_hand()
                if not cont:
                    break
                if self.human.eliminated:
                    self.render_table('game over', reveal=False,
                                       note=t('game_over_note', name=self.human.name))
                    break
                if self.hand_number % 5 == 0:
                    self.small_blind = int(self.small_blind * 1.5)
                    self.big_blind = int(self.big_blind * 1.5)
        except QuitGame:
            print(C.YELLOW + t('thanks_playing') + C.RESET)
        self.print_standings()


# ---------------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------------
def print_intro():
    clear_screen()
    print(C.GOLD + C.BOLD)
    print(r"""
      ░███      ░██████     ░██████  ░██████░██████     ░██████                        ░██                      
     ░██░██    ░██   ░██   ░██   ░██   ░██    ░██      ░██   ░██                                                
    ░██  ░██  ░██         ░██          ░██    ░██     ░██         ░██████    ░███████  ░██░████████   ░███████  
   ░█████████  ░████████  ░██          ░██    ░██     ░██              ░██  ░██        ░██░██    ░██ ░██    ░██ 
   ░██    ░██         ░██ ░██          ░██    ░██     ░██         ░███████   ░███████  ░██░██    ░██ ░██    ░██ 
   ░██    ░██  ░██   ░██   ░██   ░██   ░██    ░██      ░██   ░██ ░██   ░██         ░██ ░██░██    ░██ ░██    ░██ 
   ░██    ░██   ░██████     ░██████  ░██████░██████     ░██████   ░█████░██  ░███████  ░██░██    ░██  ░███████  
                                                                                                                
                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              
    """)
    print(C.RESET)
    print(C.BOLD + "        ASCII CASINO — TEXAS HOLD'EM NO-LIMIT" + C.RESET)
    print(C.DIM + "        " + t('subtitle') + "\n" + C.RESET)
    print("  " + t('controls_label') + " " +
          C.YELLOW + "[K]" + C.RESET + t('ctrl_check') + "  " +
          C.YELLOW + "[C]" + C.RESET + t('ctrl_call') + "  " +
          C.YELLOW + "[R]" + C.RESET + t('ctrl_raise') + "  " +
          C.YELLOW + "[A]" + C.RESET + t('ctrl_allin') + "  " +
          C.YELLOW + "[F]" + C.RESET + t('ctrl_fold') + "  " +
          C.YELLOW + "[Q]" + C.RESET + t('ctrl_quit') + "\n")
    print(C.CYAN + "  " + t('meet_opponents') + C.RESET)
    for key, p in PERSONALITIES.items():
        print(f"   - {C.BOLD}{p['label']:<20}{C.RESET} {PERSONALITY_DESC[LANG][key]}")
    print()


def choose_language():
    """Tanyakan bahasa tampilan sebelum apa pun lain ditampilkan — istilah aksi inti
    (Check/Call/Raise/Fold/All-in) tetap bahasa Inggris di kedua pilihan, jadi kontrol
    dasar game tetap sama; yang berubah cuma teks penjelasan/prompt/pesannya."""
    global LANG
    print(C.GOLD + C.BOLD + "\n  Pilih bahasa / Choose language:" + C.RESET)
    print("   [1] Bahasa Indonesia")
    print("   [2] English (default)")
    try:
        raw = input("  > ").strip().lower()
    except EOFError:
        raw = ""
    if raw in ('1', 'id', 'indo', 'indonesia', 'bahasa indonesia', 'bahasa'):
        LANG = 'id'
    else:
        LANG = 'en'


def main():
    choose_language()
    print_intro()
    try:
        name = input(t('name_prompt')).strip()
    except EOFError:
        name = ""
    if not name:
        name = t('default_name')
    game = PokerGame(name, num_bots=7, starting_chips=50000, small_blind=100, big_blind=200)
    game.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(t('game_stopped'))
        sys.exit(0)
