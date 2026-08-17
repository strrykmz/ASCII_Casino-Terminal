# ♠️ ASCII Casino — Texas Hold'em No-Limit

Game poker Texas Hold'em No-Limit yang berjalan **100% di terminal**, satu file Python,
tanpa dependency eksternal. Kamu melawan hingga 7 bot AI dengan kepribadian & gaya
bermain yang berbeda-beda, lengkap dengan kartu bergaya ASCII/pixel-art, side-pot
engine yang benar, dan evaluator tangan 7-kartu.

> A single-file, zero-dependency Texas Hold'em No-Limit poker game that runs entirely
> in your terminal — play against up to 7 AI bots, each with a distinct personality,
> rendered with hand-drawn pixel-art ASCII cards.

## Pratinjau / Preview

```
╔════════════════════════════════════════════════════════════════════════╗
║  ♠♥  A S C I I   C A S I N O — TEXAS HOLD'EM NO-LIMIT  ♦♣    Hand #1   ║
╚════════════════════════════════════════════════════════════════════════╝
  ◉ Blinds: $100/$200   │  Street: FLOP   │  Pot: $10,500   │  Pemain tersisa: 7

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
  ★ Kamu                               Lawan-lawan:
  Satya                                The Bluffer [BTN]    The Rock
  chips:$50,000  bet:$0                chips:$50.0k         chips:$50.0k
  ╔═════════════╗ ╔═════════════╗      ┌───┐ ┌───┐          ┌───┐ ┌───┐
  ║J  ♦         ║ ║A  ♠         ║      │▓▓▓│ │▓▓▓│          │▓▓▓│ │▓▓▓│
  ║      █      ║ ║      █      ║      └───┘ └───┘          └───┘ └───┘
  ...
```

*(Di terminal sungguhan tampilannya berwarna — merah untuk ♥/♦, putih/bold untuk ♠/♣.)*

## Fitur

- **Aturan poker standar** — Texas Hold'em No-Limit lengkap: blind, preflop/flop/turn/river,
  all-in, side-pot bertingkat (multi-way all-in dihitung dengan benar), showdown.
- **7 kepribadian bot AI** yang benar-benar berbeda gaya bermainnya (lihat tabel di
  bawah), dipilih acak tiap sesi — bukan sekadar bot acak, tiap bot punya profil
  keketatan (VPIP), agresivitas, kecenderungan bluff, dan fold-to-raise sendiri.
- **AI adaptif**: preflop pakai Chen Formula, postflop pakai simulasi Monte Carlo
  (equity estimation) untuk menilai kekuatan tangan relatif terhadap jumlah lawan.
- **Evaluator tangan 7-kartu** yang benar (mencari kombinasi 5 kartu terbaik dari 7,
  termasuk kasus straight roda A-2-3-4-5).
- **Kartu ASCII/pixel-art** — tiap kartu digambar sebagai bitmap blok kecil yang
  menyerupai bentuk asli spade/heart/diamond/club, proporsinya disesuaikan dengan
  rasio kartu remi sungguhan (2.5:3.5).
- **Kartu lawan tertutup** selama tangan berjalan (dan tetap tertutup selamanya kalau
  fold, sesuai aturan mucking di poker sungguhan) — baru terbuka versi kecil saat
  showdown.
- **Modal sama rata**: kamu dan semua bot mulai dengan $50,000, blind naik otomatis
  tiap 5 tangan.
- **Dua bahasa** — Bahasa Indonesia & English, dipilih saat game dimulai. Semua
  teks penjelasan/prompt/pesan ikut berubah; istilah aksi inti (Check/Call/Raise/
  Fold/All-in) tetap bahasa Inggris di kedua pilihan karena itu istilah universal.
- **Zero dependency** — cuma pakai Python standard library (`random`, `os`, `re`,
  `time`, `itertools`, `collections`). Tidak perlu `pip install` apa pun.

## Kepribadian Bot

| Bot | Gaya bermain |
|---|---|
| **The Rock** | Sangat selektif, jarang bermain kecuali tangan kuat. Nyaris tidak pernah bluff. |
| **The Maniac** | Longgar dan agresif — bertaruh besar dan sering bluff. Bahaya kalau dianggap enteng. |
| **The Shark** | Seimbang dan kalkulatif, mendekati gaya bermain optimal. |
| **The Calling Station** | Suka memanggil (call) hampir apa saja, jarang fold atau raise. |
| **The Bluffer** | Sering menggertak tanpa memandang kekuatan tangan sebenarnya. |
| **The Mathematician** | Bermain sangat dekat dengan pot odds & ekuitas murni, minim emosi. |
| **The Wildcard** | Tidak dapat diprediksi — gayanya berubah-ubah dari tangan ke tangan. |

## Cara Menjalankan

Butuh Python 3.8+ dan terminal yang mendukung UTF-8 + warna ANSI (Terminal.app,
iTerm2, Windows Terminal, GNOME Terminal, dll — Command Prompt lawas mungkin perlu
`chcp 65001` dulu utk UTF-8).

```bash
git clone https://github.com/<username>/<nama-repo>.git
cd <nama-repo>
python3 poker_game.py
```

Tidak ada langkah instalasi lain — satu file, langsung jalan. Begitu dijalankan, kamu
akan diminta memilih bahasa (Indonesia/English) dulu sebelum masuk ke intro.

## Kontrol

| Tombol | Aksi |
|---|---|
| `K` | Check |
| `C` | Call |
| `R` | Raise (akan diminta memasukkan jumlahnya) |
| `A` | All-in |
| `F` | Fold |
| `Q` | Keluar dari game |

## Struktur Kode

Semuanya ada di satu file `poker_game.py` (~1000 baris), dibagi jadi beberapa bagian:

- **Kartu & Deck** — `Card`, `build_deck()`.
- **ASCII Art Kartu** — `card_art_lines()`, `SUIT_BITMAP`, kartu mini (`mini_card_lines()`).
- **Evaluator Tangan** — `evaluate_5()`, `evaluate_best()`, `hand_name()`.
- **AI Bot** — `chen_score()`, `estimate_equity()`, `bot_decide()`, `PERSONALITIES`.
- **`PokerGame`** — mesin permainan: rendering meja, ronde taruhan, side-pot
  (`compute_pots()`), showdown, dan loop turnamen.

## Kontribusi

Pull request & issue dipersilakan — beberapa ide pengembangan lanjutan:

- Simpan/lanjutkan sesi (save & resume).
- Statistik/riwayat tangan.
- Opsi variasi permainan lain (Omaha, Short Deck, dll).
- Dukungan multiplayer via socket/terminal bersama.

## Lisensi

[MIT License](LICENSE) — bebas dipakai, dicopy, dimodifikasi, bahkan dipakai untuk
proyek komersial oleh siapa saja, selama tetap mencantumkan notice hak cipta aslinya
(sudah ada di file `LICENSE`). Kamu tetap pemegang hak cipta atas kode ini.
