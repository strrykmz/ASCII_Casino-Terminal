# ♠️ ASCII Casino — Texas Hold'em No-Limit

A single-file, zero-dependency Texas Hold'em No-Limit poker game that runs **100% in
your terminal**. Play against up to 7 AI bots, each with a distinct personality and
playstyle, rendered with hand-drawn pixel-art ASCII cards, a correct multi-way side-pot
engine, and a proper 7-card hand evaluator.

## Preview

```
╔════════════════════════════════════════════════════════════════════════╗
║  ♠♥  A S C I I   C A S I N O — TEXAS HOLD'EM NO-LIMIT  ♦♣    Hand #1   ║
╚════════════════════════════════════════════════════════════════════════╝
  ◉ Blinds: $100/$200   │  Street: FLOP   │  Pot: $10,500   │  Players remaining: 7

  ♣ Community Cards ♦
╔═════════════╗ ╔═════════════╗ ╔═════════════╗
║A  ♠         ║ ║K  ♦         ║ ║7  ♣         ║
║      █      ║ ║      █      ║ ║     ███     ║
║     ███     ║ ║     ███     ║ ║    █████    ║
║    █████    ║ ║    █████    ║ ║   ███ ███   ║
║   ███████   ║ ║   ███████   ║ ║   ███████   ║
║   ██ █ ██   ║ ║    █████    ║ ║    █████    ║
║      █      ║ ║     ███     ║ ║      █      ║
║     ███     ║ ║      █      ║ ║     ███     ║
║         ♠  A║ ║         ♦  K║ ║         ♣  7║
╚═════════════╝ ╚═════════════╝ ╚═════════════╝

──────────────────────────────────────────────────────────────────────────
  ★ You                                 Opponents:
  strrykmz                              The Bluffer [BTN]    The Rock
  chips:$50,000  bet:$0                 chips:$50.0k         chips:$50.0k
  ╔═════════════╗ ╔═════════════╗       ┌───┐ ┌───┐          ┌───┐ ┌───┐
  ║J  ♦         ║ ║A  ♠         ║       │▓▓▓│ │▓▓▓│          │▓▓▓│ │▓▓▓│
  ║      █      ║ ║      █      ║       └───┘ └───┘          └───┘ └───┘
  ...
```

*(Colors render in an actual terminal — red for ♥/♦, white/bold for ♠/♣.)*

## Features

- **Standard poker rules** — full Texas Hold'em No-Limit: blinds, preflop/flop/turn/
  river, all-in, multi-way side-pots (calculated correctly), showdown.
- **7 distinct AI bot personalities** (see table below), chosen at random each session
  — not just randomized bots, each one has its own tightness (VPIP), aggression,
  bluff tendency, and fold-to-raise profile.
- **Adaptive AI**: preflop uses the Chen Formula, postflop uses Monte Carlo simulation
  (equity estimation) to evaluate hand strength relative to the number of opponents.
- **Correct 7-card hand evaluator** (finds the best 5-card combination out of 7,
  including the A-2-3-4-5 wheel straight case).
- **ASCII/pixel-art cards** — each card is drawn as a small bitmap that resembles the
  real shape of a spade/heart/diamond/club, proportioned to match a real playing
  card's ratio (2.5:3.5).
- **Hidden opponent cards** while the hand is in progress (and permanently hidden if
  folded, following real poker mucking rules) — revealed as a smaller card at
  showdown.
- **Even starting stacks**: you and every bot start with $50,000, blinds increase
  automatically every 5 hands.
- **Two languages** — Indonesian & English, chosen when the game starts. All
  narration/prompt/message text switches accordingly; the core action terms
  (Check/Call/Raise/Fold/All-in) stay in English in both languages since those are
  universal poker terms.
- **Zero dependencies** — only uses the Python standard library (`random`, `os`, `re`,
  `time`, `itertools`, `collections`). No `pip install` required.

## Bot Personalities

| Bot | Playstyle |
|---|---|
| **The Rock** | Extremely selective, rarely plays unless the hand is strong. Almost never bluffs. |
| **The Maniac** | Loose and aggressive — bets big and bluffs often. Dangerous if underestimated. |
| **The Shark** | Balanced and calculating, close to optimal play. |
| **The Calling Station** | Loves to call almost anything, rarely folds or raises. |
| **The Bluffer** | Bluffs frequently regardless of actual hand strength. |
| **The Mathematician** | Plays very close to pure pot odds & equity, minimal emotion. |
| **The Wildcard** | Unpredictable — playstyle shifts from hand to hand. |

## How to Run

Requires Python 3.8+ and a terminal that supports UTF-8 + ANSI colors (Terminal.app,
iTerm2, Windows Terminal, GNOME Terminal, etc — older Command Prompt may need
`chcp 65001` first for UTF-8).

```bash
git clone https://github.com/<username>/<repo-name>.git
cd <repo-name>
python3 poker_game.py
```

No other installation steps — it's a single file, ready to run. Once launched, you'll
first be asked to choose a language (Indonesian/English) before the intro appears.

## Controls

| Key | Action |
|---|---|
| `K` | Check |
| `C` | Call |
| `R` | Raise (you'll be prompted for the amount) |
| `A` | All-in |
| `F` | Fold |
| `Q` | Quit the game |

## Code Structure

Everything lives in a single file, `poker_game.py` (~1000 lines), split into several
sections:

- **Cards & Deck** — `Card`, `build_deck()`.
- **Card ASCII Art** — `card_art_lines()`, `SUIT_BITMAP`, mini cards (`mini_card_lines()`).
- **Hand Evaluator** — `evaluate_5()`, `evaluate_best()`, `hand_name()`.
- **Bot AI** — `chen_score()`, `estimate_equity()`, `bot_decide()`, `PERSONALITIES`.
- **`PokerGame`** — the game engine: table rendering, betting rounds, side-pots
  (`compute_pots()`), showdown, and the tournament loop.

## Contributing

Pull requests & issues are welcome — a few ideas for future development:

- Save/resume a session.
- Hand history / statistics.
- Other game variants (Omaha, Short Deck, etc).
- Multiplayer support over sockets/shared terminal.

## License

[MIT License](LICENSE) — free to use, copy, modify, and even use commercially by
anyone, as long as the original copyright notice is kept (already included in the
`LICENSE` file). You remain the copyright holder of this code.
