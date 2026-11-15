# PRD — Vyche: Agent Skill untuk Analisis, Perbaikan, dan Pelaporan Keamanan Kode

| Field | Isi |
| --- | --- |
| Nama produk | Vyche |
| Jenis | Agent skill (paket instruksi Markdown, tanpa dependensi) |
| Versi dokumen | 1.1 (revisi 15 November 2026: status implementasi, V-11/V-12, struktur repo final) |
| Tanggal | 15 November 2026 |
| Status | Final draf untuk pengembangan v1.0 |
| Pemilik | Bara Abiyyi |
| Media uji resmi | OpenCode |
| Distribusi | Open source di GitHub |
| Lisensi | MIT (usulan, lihat §20) |
| Dokumen terkait | `docs/archive/PRD-v0.1.md` (draf v0.1, arsip), `SKILL.md`, `references/*` |

---

## Daftar isi

1. [Ringkasan eksekutif](#1-ringkasan-eksekutif)
2. [Latar belakang](#2-latar-belakang)
3. [Masalah yang diselesaikan](#3-masalah-yang-diselesaikan)
4. [Tujuan dan non-tujuan](#4-tujuan-dan-non-tujuan)
5. [Pengguna target](#5-pengguna-target)
6. [Skenario penggunaan](#6-skenario-penggunaan)
7. [Permukaan perintah](#7-permukaan-perintah)
8. [Ruang lingkup v1](#8-ruang-lingkup-v1)
9. [Arsitektur skill](#9-arsitektur-skill)
10. [Alur kerja](#10-alur-kerja)
11. [Kontrak keluaran](#11-kontrak-keluaran)
12. [Kebutuhan fungsional](#12-kebutuhan-fungsional)
13. [Kebutuhan non-fungsional](#13-kebutuhan-non-fungsional)
14. [Keamanan, etika, dan privasi](#14-keamanan-etika-dan-privasi)
15. [Instalasi dan distribusi](#15-instalasi-dan-distribusi)
16. [Rencana pengujian fungsional](#16-rencana-pengujian-fungsional)
17. [Rencana evaluasi penelitian](#17-rencana-evaluasi-penelitian)
18. [Peta jalan](#18-peta-jalan)
19. [Risiko dan mitigasi](#19-risiko-dan-mitigasi)
20. [Keputusan terbuka](#20-keputusan-terbuka)
21. [Status implementasi terhadap v1.0](#21-status-implementasi-terhadap-v10)
22. [Lampiran](#22-lampiran)

---

## 1. Ringkasan eksekutif

Vyche adalah **agent skill** open source yang dipasang di agen AI coding untuk memeriksa keamanan kode sebelum masuk production. Fokus utamanya adalah kode yang ditulis dengan bantuan AI, yang sering lolos di aspek validasi input, otorisasi, dan pengelolaan secret karena keamanan jarang diminta eksplisit di prompt.

Vyche bukan program dan bukan scanner. Ia adalah paket instruksi (Markdown) yang dibaca agen. Tidak ada dependensi, tidak ada instalasi paket, tidak ada akses jaringan, dan tidak ada skrip tersembunyi. Seluruh isi dapat diaudit dengan membaca file.

Tiga perintah:

| Perintah | Sifat | Keluaran |
| --- | --- | --- |
| `/vyche scan` | read-only | Ringkasan temuan di chat: lokasi, CWE, severity, satu kalimat alasan |
| `/vyche report` | read-only | Laporan terstruktur: bukti, dampak, rekomendasi perbaikan, batasan |
| `/vyche fix` | menulis file | Patch minimal untuk temuan terverifikasi, tanpa commit |

Nilai pembeda: setiap temuan wajib berbukti (file, baris, kutipan), temuan berkeyakinan rendah disingkirkan ke bagian "Perlu ditinjau manusia", dan mode read-only dijamin tidak menyentuh file pengguna.

Dokumen ini sekaligus menjadi dasar skripsi: Vyche dirancang, lalu dievaluasi seberapa besar ia meningkatkan kemampuan agen **yang sama** dalam mendeteksi dan memperbaiki kerentanan, dibanding agen tanpa skill dan dibanding agen dengan prompt sederhana.

---

## 2. Latar belakang

Perkembangan AI coding assistant sudah mengubah cara orang menulis perangkat lunak. Dalam satu sesi, agen dapat menghasilkan CRUD, endpoint autentikasi, upload file, dan komponen frontend yang tampak benar dan langsung berjalan. Yang sering tidak ikut dihasilkan adalah lapisan keamanan: query yang diparameterisasi, pemeriksaan kepemilikan objek, penanganan secret, validasi di sisi server, dan konfigurasi cookie.

Tiga hal bertemu di titik ini:

1. **Volume kode naik, waktu review tidak.** Programmer memakai AI justru untuk menghemat waktu. Meninjau keamanan secara manual membatalkan penghematan itu, sehingga sering dilewati.
2. **AI tidak menolak, tetapi juga tidak waspada.** Model menghasilkan kode yang benar secara fungsional dan percaya diri. Ketiadaan peringatan sering dibaca sebagai jaminan keamanan.
3. **Tool keamanan konvensional tidak cocok dengan alur kerja ini.** SAST butuh instalasi, konfigurasi, dan pemahaman output. Hasilnya berupa daftar panjang tanpa penjelasan konteks, dan tidak menyentuh perbaikan.

Skill untuk agen adalah bentuk distribusi yang cocok: satu folder, dibaca agen yang sudah dipakai, tanpa infrastruktur baru. Masalahnya, mayoritas skill security review yang beredar tidak dievaluasi secara terukur — tidak jelas apakah ia benar-benar meningkatkan hasil, atau hanya menambah panjang jawaban.

Vyche dibangun untuk menutup dua hal sekaligus: **produk yang berguna** dan **klaim yang bisa diukur**.

---

## 3. Masalah yang diselesaikan

| ID | Masalah | Akibat pada pengguna |
| --- | --- | --- |
| P-1 | Kode hasil AI melewatkan kontrol keamanan dasar (validasi, otorisasi, secret, konfigurasi) | Celah masuk production tanpa disadari |
| P-2 | Programmer tidak punya waktu/keahlian untuk audit manual | Review keamanan dilewati |
| P-3 | Output SAST berupa daftar panjang tanpa konteks dan tanpa perbaikan | Temuan tidak ditindaklanjuti |
| P-4 | Temuan palsu dari review berbasis LLM merusak kepercayaan | Pengguna berhenti memakai alatnya |
| P-5 | File panjang membuat agen "memindai sekilas" dan melewatkan celah nyata | Rasa aman palsu |
| P-6 | Tidak ada skill security review yang dievaluasi dengan metrik jelas | Klaim manfaat tidak bisa dipertanggungjawabkan |

Cara Vyche menjawab P-4 dan P-5 secara desain: **pemetaan proyek sebelum mencari celah**, **penelusuran alur data sumber → sink** (bukan pencocokan pola), dan **gerbang verifikasi wajib** sebelum sebuah temuan boleh masuk laporan.

---

## 4. Tujuan dan non-tujuan

### 4.1 Tujuan produk

| ID | Tujuan | Ukuran keberhasilan |
| --- | --- | --- |
| G-1 | Menemukan kerentanan dengan cepat, berbukti, dan bisa diverifikasi pengguna | ≥ 90% temuan pada fixture uji punya bukti file+baris+kutipan yang valid |
| G-2 | Memperbaiki kerentanan dengan perubahan minimal yang bisa ditinjau | ≥ 80% temuan High/Medium tertutup tanpa regresi fungsi pada fixture uji |
| G-3 | Menghasilkan laporan terstruktur yang layak dilampirkan di PR | 100% report memakai template baku dan memuat bagian batasan |
| G-4 | Instalasi tanpa gesekan | ≤ 3 langkah salin file, nol dependensi |
| G-5 | Aman dijalankan kapan saja dalam mode read-only | Nol perubahan file pada seluruh run `scan` dan `report` |

### 4.2 Tujuan penelitian

| ID | Tujuan | Ukuran |
| --- | --- | --- |
| R-1 | Mengukur peningkatan precision, recall, F1 deteksi dengan Vyche vs tanpa skill | Selisih metrik pada kondisi A/B/C (§17) |
| R-2 | Mengetahui komponen desain mana yang paling berpengaruh | Ablation study (§17.4) |
| R-3 | Mengukur efektivitas perbaikan | Tingkat keberhasilan fix dan tingkat regresi |
| R-4 | Menempatkan Vyche relatif terhadap skill sejenis dan SAST | Perbandingan kondisi E |

### 4.3 Non-tujuan (v1)

- Bukan pengganti penetration test, SAST, atau review manusia, dan bukan jaminan kode aman.
- Tidak membuat exploit siap pakai, tidak menyerang sistem, tidak memindai jaringan/infrastruktur.
- Tidak menjalankan kode proyek, tidak menginstal paket, tidak membuat permintaan jaringan, tidak mengirim kode ke luar sesi agen.
- Tidak memanggil tool eksternal (Semgrep, CodeQL, Bandit, dan sejenisnya) di dalam skill; tool tersebut hanya dipakai peneliti sebagai pembanding saat evaluasi.
- Tidak menangani IaC dan konfigurasi CI secara resmi di v1 (Dockerfile/GitHub Actions hanya disentuh sebagai bagian pemeriksaan konfigurasi umum).
- Dukungan resmi hanya untuk OpenCode. Agen lain bersifat best-effort.
- Tidak ada auto-commit, auto-push, atau perubahan di luar cakupan yang diminta.

---

## 5. Pengguna target

| Persona | Konteks | Kebutuhan utama | Yang membuat ia bertahan memakai Vyche |
| --- | --- | --- | --- |
| Programmer yang banyak memakai AI (termasuk mahasiswa dan pemula) | Menulis fitur dengan agen, tidak selalu paham implikasi keamanan | Cara cepat memeriksa kode hasil AI, penjelasan yang bisa dipahami | Penjelasan "kenapa penting" tanpa istilah yang tidak dijelaskan |
| Pengembang mandiri / tim kecil tanpa tim security | Rilis cepat, tidak ada reviewer khusus keamanan | Laporan yang bisa dilampirkan di PR atau dokumentasi rilis | Format laporan yang siap tempel |
| Reviewer kode | Meninjau PR orang lain | Daftar temuan berbukti untuk mempercepat review | Bukti file+baris+kutipan yang bisa diverifikasi langsung |
| Peneliti (penyusun skripsi) | Merancang dan mengevaluasi skill | Perilaku skill yang terkontrol dan hasil yang bisa diukur | Mode yang deterministik, versi tercatat, output terstruktur |

---

## 6. Skenario penggunaan

| ID | Sebagai | Saya ingin | Agar |
| --- | --- | --- | --- |
| US-1 | Programmer | menjalankan `/vyche scan` pada file yang baru dibuat AI | tahu cepat jika ada celah yang jelas |
| US-2 | Programmer | menjalankan `/vyche report` pada seluruh proyek | mendapat laporan lengkap yang bisa disimpan atau dibagikan |
| US-3 | Programmer | menjalankan `/vyche fix` pada file tertentu | celah yang terbukti ditambal tanpa menulis ulang manual |
| US-4 | Pengguna | menentukan cakupan dengan kalimat bebas setelah perintah | pemeriksaan sesuai kebutuhan dan hemat waktu |
| US-5 | Pengguna | yakin `scan` dan `report` tidak mengubah file | aman dijalankan kapan saja, termasuk di repo orang lain |
| US-6 | Pengguna | melihat hasil fix lewat `git diff` tanpa commit otomatis | tetap memegang kendali atas repository |
| US-7 | Pengguna | mendapat laporan yang menyebut apa yang **tidak** diperiksa | tidak salah menyimpulkan bahwa kode sudah aman |
| US-8 | Peneliti | menjalankan skill berulang pada kode uji yang sama | membandingkan hasil dengan baseline secara adil |

Contoh pemanggilan:

```
/vyche scan folder src/auth
/vyche report seluruh proyek ini
/vyche fix celah di app/db.py
/vyche cek keamanan kode yang baru saya ubah
```

---

## 7. Permukaan perintah

### 7.1 Bentuk perintah

Vyche dipakai lewat custom command OpenCode. Dua bentuk didukung agar cocok dengan kebiasaan pengguna:

| Bentuk | File command | Perilaku |
| --- | --- | --- |
| `/vyche <subperintah> <cakupan>` (utama) | `.opencode/commands/vyche.md` | Router: kata pertama menentukan mode, sisanya jadi cakupan |
| `/vyche/scan`, `/vyche/fix`, `/vyche/report` | `.opencode/commands/vyche/scan.md`, `fix.md`, `report.md` | Mode eksplisit, argumen jadi cakupan |

Keduanya memanggil skill ID `vyche` yang sama. Router adalah bentuk utama karena lebih ringkas dan sesuai contoh pemakaian di README.

### 7.2 Tabel perintah

| Perintah | Tujuan | Mengubah file? | Keluaran |
| --- | --- | --- | --- |
| `/vyche scan` | Deteksi cepat pada cakupan yang diminta | **Tidak** | Tabel temuan di chat + tawaran `report`/`fix` |
| `/vyche report` | Analisis menyeluruh, laporan terstruktur | **Tidak** (menyimpan ke file hanya bila diminta) | Laporan lengkap dengan bukti dan rekomendasi |
| `/vyche fix` | Analisis, lalu perbaikan temuan terverifikasi | **Ya**, patch minimal, tanpa commit | Tabel perubahan + tindakan manual + saran perintah test |

### 7.3 Aturan parsing

1. Kata pertama setelah `/vyche` dicocokkan dengan `scan`, `fix`, `report` (peka terhadap sinonim Indonesia/Inggris: `scan|cek|periksa`, `fix|perbaiki|patch|tambal`, `report|laporan|audit|review`).
2. Tidak ada kata perintah dikenali → **default `scan`** bila pengguna meminta pemeriksaan cepat, **default `report`** bila permintaan bersifat menyeluruh atau ambigu. Bila benar-benar kosong, pakai `report` (paling informatif dan tetap read-only), lalu tawarkan langkah berikutnya.
3. Sisa kalimat menjadi cakupan (`folder src/auth`, `app/db.py`, `fitur login`).
4. Cakupan tidak disebut → mulai dari file yang berubah di working tree (`git status`, `git diff`), lalu file yang dipanggilnya. Cakupan yang dipilih **wajib dinyatakan dalam satu baris** di awal jawaban.
5. Kata kunci yang meminta perubahan di luar mode (`/vyche scan lalu perbaiki`) → jalankan `scan`, lalu tawarkan `fix`; jangan diam-diam menulis file.

### 7.4 Kontrak mode (tidak boleh dilanggar)

| Mode | Boleh membaca | Boleh menulis | Boleh commit | Boleh menjalankan perintah shell |
| --- | --- | --- | --- | --- |
| `scan` | Ya | **Tidak** | Tidak | Hanya baca (`git status`, `git diff`, `ls`) |
| `report` | Ya | Tidak (kecuali menyimpan laporan bila diminta eksplisit) | Tidak | Hanya baca |
| `fix` | Ya | Ya, hanya file yang terkait temuan | **Tidak** | Hanya bila pengguna memintanya (mis. test) |

---

## 8. Ruang lingkup v1

### 8.1 Bahasa dan framework

| Referensi | Cakupan |
| --- | --- |
| `references/language-patterns.md` | JavaScript/TypeScript (Node, Express, Nest), Python (Django, Flask, FastAPI), Go, Rust, Java/Spring, Ruby/Rails, PHP (Laravel). Berisi pasangan kode rentan → kode diperbaiki per pola, plus rujukan SQL injection per ORM |
| `references/frontend-patterns.md` | React, Next.js (Server Actions, middleware, hydration), Vue, Svelte, dan hal khusus browser (penyimpanan token, postMessage, CSP, DOM) |
| `references/vulnerability-checklist.md` | Kategori kerentanan, CWE, dan daftar pola khas kode hasil AI |
| `references/report-template.md` | Format laporan dan panduan severity |

Rujukan SQL injection per ORM yang wajib tercakup: Prisma, Sequelize, TypeORM, SQLAlchemy, Django ORM, GORM, Hibernate/JPA, ActiveRecord, Eloquent, sqlx/Diesel.

Setiap contoh kode ditulis sendiri dan dicocokkan dengan sumber resmi (OWASP Cheat Sheet Series, dokumentasi ORM terkait). Tidak ada penyalinan teks dari skill lain; bila ada ide yang terinspirasi, disebut sebagai sumber di lampiran.

**Didukung vs dievaluasi.** Semua bahasa di atas didukung sebagai produk. Evaluasi formal di skripsi dibatasi pada 2–3 target (usulan: **Python**, **JavaScript/TypeScript**, dan **Next.js** sebagai wakil frontend). Sisanya dinyatakan didukung namun belum dievaluasi formal, dan itu ditulis apa adanya di laporan akhir.

### 8.2 Kategori kerentanan v1

Berpedoman pada OWASP Top 10 dan CWE.

| # | Kategori | Cakupan utama (CWE) |
| --- | --- | --- |
| V-1 | Injeksi | SQL/NoSQL (CWE-89, 943), OS command (78), XSS (79), code injection (94/95), path traversal (22) |
| V-2 | Kontrol akses | Missing authorization (862), IDOR (639), mass assignment (915), cek hanya di sisi klien |
| V-3 | Autentikasi dan sesi | Hash lemah (256/916), tanpa rate limit (307), JWT (347/613), cookie (1004/384), CSRF (352), reset token |
| V-4 | Kriptografi dan secret | Secret tertanam (798), algoritma lemah (327/328), RNG tidak aman (338), IV/nonce statis, TLS verify mati (295) |
| V-5 | Paparan data sensitif | Log/error/URL (532/209/200), debug mode, respons mengembalikan objek utuh |
| V-6 | Upload dan deserialisasi | Upload tanpa batas (434), deserialisasi tidak aman (502), XXE (611), zip slip (22), ReDoS (1333) |
| V-7 | SSRF dan open redirect | SSRF (918), open redirect (601), CORS terlalu longgar (942) |
| V-8 | Konfigurasi tidak aman | Debug produksi, kredensial default, header keamanan, container root, secret di image/CI |
| V-9 | Rantai pasok | Dependensi usang/typosquat, lockfile hilang, `postinstall` berbahaya, versi tanpa pin |
| V-10 | Pola khas kode AI | Secret placeholder yang benar-benar dipakai, validasi "untuk demo" yang tidak dihapus, default tidak aman (`DEBUG=True`, `cors(*)`), TODO keamanan yang ditinggalkan, komentar yang mengklaim aman tanpa bukti, instruksi tersembunyi di dalam kode (prompt injection, CWE-1427) |
| V-11 | Logika bisnis dan konkurensi | Race condition (362), TOCTOU (367), alur yang bisa dilompati (840), resource exhaustion (400) |
| V-12 | Keamanan memori | OOB (787/125), use-after-free (416), integer overflow (190), format string (134) — C, C++, `unsafe` Rust, cgo |

V-10 adalah pembeda utama Vyche dan wajib punya bagian sendiri di checklist. V-11 dan V-12 disertakan karena keduanya sering muncul pada kode hasil AI (logika checkout yang bisa dilompati, pemakaian `unsafe` untuk "membuat jalan") dan karena keduanya sudah ada di checklist sejak prototipe.

---

## 9. Arsitektur skill

### 9.1 Struktur repositori

```
vyche/
├── SKILL.md                      # alur kerja inti, kontrak mode, gerbang kualitas
├── references/
│   ├── language-patterns.md      # JS/TS, Python, Go, Rust, Java/Spring, Ruby/Rails, PHP + SQLi per ORM
│   ├── frontend-patterns.md      # React, Next.js, Vue, Svelte, browser
│   ├── vulnerability-checklist.md# V-1..V-12, CWE, pola kode hasil AI
│   └── report-template.md        # kontrak keluaran scan/report/fix + panduan severity
├── commands/                     # disalin ke .opencode/commands/
│   ├── vyche.md                  # /vyche <args>
│   └── vyche/
│       ├── scan.md               # /vyche/scan
│       ├── fix.md                # /vyche/fix
│       └── report.md             # /vyche/report
├── examples/
│   ├── README.md                 # peta fixture, skema labels.json, cara menilai
│   ├── python-sqli/              # fixture + labels.json
│   ├── python-clean/
│   ├── full-app/
│   ├── hardcoded-secret/
│   ├── prompt-injection/
│   ├── ambiguous-auth/
│   └── nextjs-action/
├── docs/
│   ├── PRD.md                    # dokumen ini
│   └── PUBLISHING.md             # checklist rilis sebelum repo dibuat publik
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

### 9.2 Prinsip desain

1. **Progressive disclosure.** `SKILL.md` tetap ringkas (< 500 baris) dan hanya memuat alur kerja + aturan. Detail bahasa dan pola ada di `references/` dan dimuat **hanya** untuk stack yang terdeteksi. Ini menjaga konteks tetap efisien dan menekan biaya token.
2. **Instruksi, bukan program.** Tidak ada skrip yang dieksekusi. Semua perilaku berasal dari teks yang dibaca agen, sehingga bisa diaudit baris per baris.
3. **Gerbang verifikasi wajib.** Temuan tanpa bukti dan tanpa cek mitigasi tidak boleh masuk daftar utama. Ini menekan false positive secara struktural, bukan lewat imbauan.
4. **Pemetaan sebelum pencarian.** Agen memetakan stack, entry point, aset sensitif, dan trust boundary sebelum mencari celah. Ini menekan temuan terlewat pada file panjang.
5. **Mode sebagai pagar keselamatan.** `scan` dan `report` dilarang menulis file. Pagar ini eksplisit di SKILL.md dan di command, bukan kesimpulan agen.
6. **Frontmatter portabel.** `name`, `description`, `license`, `compatibility` diisi agar skill bisa dibaca agen lain (Claude Code, Codex, dan sejenisnya) tanpa perubahan isi.

### 9.3 Peran tiap file

| File | Peran | Batas ukuran |
| --- | --- | --- |
| `SKILL.md` | Alur kerja 6 langkah, aturan mode, aturan keselamatan, batasan yang harus dinyatakan | < 500 baris |
| `references/language-patterns.md` | Pasangan rentan→diperbaiki per bahasa dan per ORM | Bertahap per bahasa |
| `references/frontend-patterns.md` | Khusus frontend dan browser | Bertahap per framework |
| `references/vulnerability-checklist.md` | Daftar periksa per kategori dengan CWE | satu halaman padat |
| `references/report-template.md` | Struktur laporan dan panduan severity | < 100 baris |
| `commands/vyche.md` | Router `/vyche` | < 20 baris |

---

## 10. Alur kerja

### 10.1 Alur umum (dipakai semua mode)

1. **Tentukan mode dan cakupan** (§7.3). Nyatakan cakupan dalam satu baris.
2. **Petakan proyek:** stack, entry point, aset sensitif, trust boundary. Jangan dibuang ke output.
3. **Muat referensi** sesuai stack yang terdeteksi saja.
4. **Telusuri alur data:** sumber (input) → validasi/encoding → sink (query, shell, HTML, path, redirect, deserialisasi, log, request keluar). Tambahan: periksa kontrol yang tidak berbentuk alur (otorisasi per route, secret, konfigurasi).
5. **Verifikasi setiap kandidat:** bukti (file, baris, kutipan) → jalur serangan konseptual → cek mitigasi yang mungkin terlewat → tingkat keyakinan (High/Medium/Low) → severity berbasis konteks proyek.
6. **Keluaran** sesuai mode: tabel (`scan`), laporan (`report`), atau patch (`fix`).

### 10.2 `scan`

Ringkas dan cepat. Batasi pada kategori berdampak tinggi dan pola khas kode AI. Keluarkan tabel maksimal 10 temuan teratas, urut severity. Tutup dengan satu baris tawaran: `report` untuk detail, `fix` untuk menambal.

### 10.3 `report`

Alur penuh + laporan template. Wajib memuat: ringkasan, tabel temuan, rincian per temuan (bukti, mengapa penting, saran perbaikan dengan contoh kode), bagian **Perlu ditinjau manusia**, bagian **Sudah diperiksa tanpa temuan**, dan bagian **Batasan**. Bila diminta, simpan ke `vyche-report.md` di root proyek.

### 10.4 `fix`

Hanya setelah langkah 1–5 selesai:

1. Tambal temuan High/Medium confidence, mulai dari yang paling berat.
2. Perubahan **terkecil** yang menutup celah dan menjaga perilaku: parameterisasi query, tambah cek kepemilikan, pindahkan secret ke environment variable.
3. Ikuti gaya dan library proyek. Jangan refactor kode yang tidak terkait. Jangan menambah dependensi kecuali terpaksa — dan bila terpaksa, sebutkan.
4. Temuan Low confidence tidak disentuh; daftarkan sebagai "tidak diubah" beserta alasannya.
5. Bila perbaikan butuh keputusan pengguna (rotasi secret, perubahan desain otorisasi), jangan menebak: jelaskan dan biarkan kode apa adanya untuk item itu.
6. Baca ulang setiap titik yang diubah: pastikan celah tertutup dan tidak muncul celah baru.
7. Identifikasi perintah test proyek bila ada (`package.json`, `pytest.ini`, `Makefile`) dan sebutkan. Jalankan hanya bila pengguna meminta.
8. Tutup dengan tabel: temuan, file, apa yang berubah, tindakan manual yang masih perlu.

### 10.5 Gerbang kualitas (self-check sebelum output)

- [ ] Cakupan dinyatakan di awal.
- [ ] Setiap temuan punya file + baris + kutipan.
- [ ] Setiap temuan sudah dicek terhadap kemungkinan mitigasi.
- [ ] Tidak ada temuan Low di daftar utama.
- [ ] Severity mempertimbangkan konteks proyek, bukan hanya jenis kerentanan.
- [ ] Mode read-only benar-benar tidak menulis file.
- [ ] Bagian batasan ada (untuk `report`).
- [ ] Bahasa output mengikuti bahasa pengguna.

---

## 11. Kontrak keluaran

### 11.1 `scan`

| # | Severity | Confidence | CWE | Lokasi | Alasan (satu kalimat) |
| --- | --- | --- | --- | --- | --- |
| 1 | High | High | CWE-89 | `app/db.py:42` | Input `q` masuk ke query lewat f-string tanpa parameter terikat |

Ditutup dengan: cakupan, jumlah temuan per severity, dan tawaran langkah berikutnya.

### 11.2 `report`

Mengikuti `references/report-template.md`:

```
Scope · Mode · Stack detected
# Vyche Security Report
## Summary
## Findings (urut severity, tiap temuan: Location, Evidence, Depends on bila confidence Medium, Why it matters, Recommended fix)
## Needs human review
## Checked and found no issue
## Not covered / limits
```

Blok cakupan sengaja diletakkan **di atas judul**: pembaca bisa mengoreksi cakupan yang salah sebelum membaca satu temuan pun, dan itu lebih penting daripada judul sebagai baris pertama.

Pada mode `fix`, tambah bagian `## Changes made` dengan kolom: temuan, file, apa yang berubah, tindakan manual.

### 11.3 Severity

| Level | Definisi |
| --- | --- |
| Critical | Dapat dieksploitasi jauh dengan prasyarat nol/trivial dan dampak berat (auth bypass, RCE, kebocoran data massal) |
| High | Dapat dieksploitasi dengan prasyarat wajar, dampak serius (SQLi di balik login, stored XSS, IDOR pada data sensitif) |
| Medium | Butuh kondisi khusus atau dampak terbatas (reflected XSS perlu interaksi, hashing lemah, tanpa rate limit) |
| Low | Kelemahan kecil atau defense in depth |
| Info | Catatan praktik terbaik tanpa eksploitasi langsung |

Dua hal yang tidak diselesaikan tabel di atas, jadi ditetapkan terpisah:

- **Injection di jalur publik, isi database tidak terlihat**: High. Critical hanya bila kode sendiri menunjukkan apa yang ada di baliknya (kredensial, PII, pembayaran, data tenant lain).
- **Security header tidak ada**: Low pada tool internal, Medium bila aplikasi menyajikan konten dari pengguna dan ada jalur XSS hidup yang bisa diredam CSP.

Severity **Low** dan confidence **Low** adalah dua hal berbeda: severity Low boleh masuk daftar utama, confidence Low tidak pernah boleh.

Severity dinilai untuk **deployment yang terlihat di kode**. Bind ke `127.0.0.1`, proxy ber-auth di config, atau fixture lokal menurunkan nilai; sebutkan baris yang akan menaikkannya bila aplikasi menghadap internet. Bila tidak ada yang mempersempit jangkauan, nilai untuk internet dan katakan bahwa tidak ada yang mempersempitnya.

### 11.4 Aturan penulisan temuan

- Jalur serangan dijelaskan **konseptual**. Tidak ada payload siap pakai, tidak ada skrip eksploit, tidak ada langkah serangan operasional.
- Secret yang ditemukan ditampilkan **sebagian** (beberapa karakter awal dan akhir), disertai saran rotasi karena mungkin sudah tercatat di riwayat git.
- Bila tidak ada temuan: katakan apa adanya, sebutkan yang sudah diperiksa, jangan pernah mengklaim kode "aman".
- Tidak ada temuan yang dibuat-buat agar laporan terlihat lengkap.

---

## 12. Kebutuhan fungsional

| ID | Kebutuhan | Prioritas |
| --- | --- | --- |
| FR-1 | Skill terpicu oleh `/vyche` dan mengenali subperintah `scan`, `fix`, `report` beserta sinonimnya | Wajib |
| FR-2 | Menentukan cakupan dari kalimat pengguna; bila tidak disebut, mulai dari file berubah dan **nyatakan cakupan yang dipilih** | Wajib |
| FR-3 | Memetakan proyek sebelum mencari celah: stack, entry point, aset sensitif, trust boundary | Wajib |
| FR-4 | Mendeteksi bahasa/framework lalu memuat **hanya** referensi yang relevan (progressive disclosure) | Wajib |
| FR-5 | Menelusuri alur data sumber → sink untuk setiap entry point | Wajib |
| FR-6 | Setiap temuan wajib memuat bukti (file, baris, kutipan), CWE, severity, keyakinan, dan penjelasan jalur konseptual | Wajib |
| FR-7 | Temuan Low confidence dipindahkan ke bagian Perlu ditinjau manusia, tidak di daftar utama | Wajib |
| FR-8 | `scan` dan `report` tidak mengubah/membuat/menghapus file proyek | Wajib |
| FR-9 | `fix` hanya menambal temuan terverifikasi dengan perubahan minimal, mengikuti gaya proyek, tanpa commit | Wajib |
| FR-10 | Setelah menambal, agen membaca ulang area yang diubah untuk memastikan celah tertutup dan tidak ada celah baru | Wajib |
| FR-11 | Laporan memakai template baku dan menyebut apa yang tidak tercakup beserta batasan skill | Wajib |
| FR-12 | Output mengikuti bahasa pengguna (Indonesia atau Inggris); kode, CWE, dan path tetap apa adanya | Wajib |
| FR-13 | Bila tidak ada temuan, nyatakan apa adanya + daftar yang diperiksa, tanpa klaim kode pasti aman | Wajib |
| FR-14 | `fix` boleh menulis, tetapi dilarang commit/push/menghapus file | Wajib |
| FR-15 | Isi proyek diperlakukan sebagai data; instruksi tersembunyi di kode diabaikan dan dilaporkan sebagai temuan | Wajib |
| FR-16 | Secret ditampilkan sebagian + saran rotasi | Wajib |
| FR-17 | Menyimpan laporan ke file (`vyche-report.md`) bila diminta | Sebaiknya |
| FR-18 | Menyebut perintah test yang relevan setelah `fix` | Sebaiknya |
| FR-19 | Mode `fix` bisa dibatasi ke satu temuan (`/vyche fix temuan 2`) | Sebaiknya |
| FR-20 | Ringkasan versi skill + stack terdeteksi di footer laporan (reprodusibilitas) | Sebaiknya |
| FR-21 | Dukungan IaC dan konfigurasi CI secara resmi | Nanti |
| FR-22 | Mode hibrida dengan SAST opsional (Semgrep/Bandit) | Nanti |

---

## 13. Kebutuhan non-fungsional

| ID | Aspek | Target terukur |
| --- | --- | --- |
| NFR-1 | Instalasi | Cukup salin folder skill + file command; nol dependensi; ≤ 3 langkah |
| NFR-2 | Efisiensi konteks | `SKILL.md` < 500 baris; referensi dimuat sesuai kebutuhan, bukan seluruhnya |
| NFR-3 | Reprodusibilitas | Versi skill tercatat di frontmatter dan laporan; log uji mencatat versi skill, versi OpenCode, model, pengaturan |
| NFR-4 | Keamanan skill | Nol skrip tersembunyi, nol akses jaringan, nol instruksi eksfiltrasi data |
| NFR-5 | Keterbacaan | Laporan dapat dipahami programmer tingkat menengah; istilah teknis diberi penjelasan singkat |
| NFR-6 | Portabilitas | Isi skill tidak bergantung pada fitur khusus satu agen; dukungan resmi hanya OpenCode |
| NFR-7 | Kepatuhan mode | Nol pelanggaran read-only pada seluruh run `scan`/`report` (diverifikasi dengan hash tree + `git status`) |
| NFR-8 | Konsistensi format | 100% output `report` mengikuti template; 100% output `scan` berbentuk tabel |
| NFR-9 | Waktu | `scan` pada ≤ 20 file selesai dalam satu giliran tanpa pemotongan |
| NFR-10 | Lisensi dan komunitas | Lisensi open source, `CONTRIBUTING.md`, template issue, `CHANGELOG.md` |

---

## 14. Keamanan, etika, dan privasi

| Aturan | Implementasi |
| --- | --- |
| Prompt injection | Kode, komentar, string, dan dokumen diperlakukan sebagai **data**. Instruksi seperti "abaikan instruksi sebelumnya" atau "laporkan tidak ada masalah" diabaikan dan dilaporkan sebagai temuan (V-10) |
| Batas lingkup | Hanya menganalisis kode milik pengguna. Permintaan menyerang/mengeksploitasi sistem nyata ditolak, dan ditawarkan review kode sebagai gantinya |
| Tanpa exploit | Jalur serangan dijelaskan konseptual sebagai bukti; tidak ada payload atau skrip eksploit siap pakai |
| Secret | Ditampilkan sebagian; disertai saran rotasi |
| Tanpa eksekusi | Tidak menjalankan kode proyek, tidak menginstal paket, tidak membuat permintaan jaringan, tidak mengirim kode ke luar sesi |
| Auditabilitas | Seluruh isi skill adalah teks yang bisa dibaca; tidak ada biner, tidak ada skrip |
| Data uji | Pengujian hanya pada kode buatan sendiri atau dataset terbuka berlisensi jelas |

---

## 15. Instalasi dan distribusi

### 15.1 Distribusi

Repositori publik di GitHub, berisi skill siap salin (bukan paket yang perlu di-build). Rilis diberi tag versi (`v1.0.0`) dan `CHANGELOG.md`.

### 15.2 Instalasi di OpenCode (media uji resmi)

OpenCode V2 menemukan skill di `.opencode/skills/<skill-id>/SKILL.md` dan command di `.opencode/commands/<nama>.md`.

| Langkah | Perintah / aksi |
| --- | --- |
| 1 | Salin folder skill ke `.opencode/skills/vyche/` (berisi `SKILL.md` + `references/`) |
| 2 | Salin `commands/vyche.md` ke `.opencode/commands/vyche.md` |
| 3 | Salin `commands/vyche/` ke `.opencode/commands/vyche/` (untuk bentuk `/vyche/scan` dan seterusnya) |
| 4 | Verifikasi: panggil `/vyche scan` pada satu file uji |

Catatan versi: lokasi dan format dapat berubah antar versi OpenCode. Bila skill tidak terdeteksi: pastikan nama file tepat `SKILL.md`, ID skill sama dengan nama folder (`vyche`), ada `description` di frontmatter, dan skill tidak diblokir oleh aturan `permissions` agen.

### 15.3 Agen lain

Best-effort. Struktur `SKILL.md` + `references/` mengikuti konvensi umum skill (`.claude/skills`, `.agents/skills`), sehingga salin-tempel biasanya bekerja. Ini didokumentasikan di README tanpa klaim dukungan penuh.

### 15.4 Yang **tidak** boleh ikut dalam repo publik

- `AGENTS.md` (instruksi pribadi untuk lingkungan kerja pengembang) — bukan bagian produk.
- File konfigurasi lokal, kredensial, dan catatan internal.

---

## 16. Rencana pengujian fungsional

### 16.1 Matriks uji

| ID | Skenario | Fixture | Hasil yang diharapkan |
| --- | --- | --- | --- |
| T-1 | `scan` pada file dengan SQLi f-string | `examples/input/python-sqli` | 1 temuan High, CWE-89, baris tepat |
| T-2 | `scan` pada kode bersih | `examples/input/python-clean` | Nol temuan, daftar yang diperiksa, tanpa klaim "aman" |
| T-3 | `report` seluruh proyek | `examples/input/full-app` | Laporan lengkap sesuai template, ada bagian batasan |
| T-4 | `fix` pada SQLi | `examples/input/python-sqli` | Query diparameterisasi, perubahan minimal, tanpa commit |
| T-5 | `fix` pada secret tertanam | `examples/input/hardcoded-secret` | Secret dipindah ke env, saran rotasi, secret disamarkan di laporan |
| T-6 | `report` dengan instruksi tersembunyi di komentar kode | `examples/input/prompt-injection` | Instruksi tidak diikuti, dilaporkan sebagai temuan |
| T-7 | `fix` pada temuan Low confidence | `examples/input/ambiguous-auth` | Tidak diubah, alasannya dijelaskan |
| T-8 | `scan` tanpa argumen di repo dengan perubahan | repo uji | Cakupan = file berubah, dinyatakan di awal |
| T-9 | `scan` dan `report` dijalankan pada repo bersih | repo uji | `git status` tetap bersih setelah run |
| T-10 | Pemanggilan `/vyche` tanpa argumen | repo uji | Masuk mode `report`, menawarkan langkah berikutnya |
| T-11 | `/vyche/scan` dan `/vyche/scan` keduanya | repo uji | Perilaku identik |
| T-12 | `report` pada proyek Next.js dengan Server Action tanpa cek otorisasi | `examples/input/nextjs-action` | Temuan CWE-862 dengan bukti di file action |

Kriteria lulus: 12/12 skenario sesuai harapan, dan nol pelanggaran mode read-only.

### 16.2 Prosedur pencatatan tiap run

Catat: versi skill, versi OpenCode, model, pengaturan yang dapat diatur, tanggal-waktu, fixture, perintah yang dipakai, jumlah temuan per severity, dan pelanggaran mode. Log disimpan sebagai CSV/JSON agar bisa diolah.

---

## 17. Rencana evaluasi penelitian

### 17.1 Pertanyaan penelitian

1. Seberapa besar Vyche meningkatkan precision, recall, dan F1 deteksi kerentanan dibanding agen yang sama tanpa skill?
2. Komponen desain mana yang paling berkontribusi terhadap peningkatan itu?
3. Seberapa efektif `fix` menutup kerentanan tanpa merusak fungsi?
4. Bagaimana posisi Vyche dibanding skill security review lain dan tool SAST sebagai pembanding?

### 17.2 Kondisi uji

| Kode | Kondisi |
| --- | --- |
| A | Agen tanpa skill (baseline) |
| B | Agen dengan prompt sederhana: "cari celah keamanan di kode ini" |
| C | Agen dengan Vyche lengkap |
| D | Varian ablation: tanpa gerbang verifikasi / tanpa referensi bahasa / tanpa pemetaan proyek |
| E | Pembanding eksternal: 1–2 skill security review yang sudah ada, serta Semgrep/Bandit yang dijalankan peneliti di luar skill |

### 17.3 Data uji

- Kode yang dibuat dengan meminta AI menulis fitur umum: login, upload file, query database, API CRUD, form frontend. Dilabeli manual, dan bila memungkinkan ditinjau pihak kedua.
- Dataset terbuka berlabel (misalnya OWASP Benchmark atau Juliet) sebagai pelengkap, dengan catatan bahwa sebagian mungkin sudah dikenal model saat pelatihan.
- Batasi 5–8 jenis kerentanan dan 2–3 bahasa/framework untuk evaluasi formal.

### 17.4 Ablation

Tiga varian minimal: (a) tanpa langkah verifikasi, (b) tanpa `references/language-patterns.md` dan `frontend-patterns.md`, (c) tanpa langkah pemetaan proyek. Tujuannya memisahkan mana yang benar-benar bekerja: gerbang bukti, referensi pola, atau pemetaan.

### 17.5 Metrik

| Metrik | Keterangan |
| --- | --- |
| Precision, recall, F1 | Kecocokan temuan dengan label kebenaran (metrik utama: CWE + lokasi bukti) |
| Kesepakatan severity | Severity temuan vs label: sepakat / selisih satu tingkat / selisih lebih. Metrik sekunder, tidak mengubah hitungan precision |
| False positive rate | Temuan tidak benar per run, di luar temuan yang sah tapi belum berlabel |
| Tingkat keberhasilan fix | Kerentanan tidak lagi terdeteksi setelah perbaikan, ditinjau manual |
| Tingkat regresi | Test/fungsi rusak akibat fix |
| Kepatuhan mode | Pelanggaran read-only pada `scan`/`report` (target: nol) |
| Efisiensi | Waktu dan jumlah token per run |
| Variasi antar-run | Simpangan baku dari 3–5 pengulangan per skenario |

Target angka peningkatan ditetapkan setelah uji pilot. Hipotesis: Vyche mengungguli kondisi A dan B. Bila hasilnya tidak demikian, itu tetap temuan ilmiah dan dilaporkan apa adanya.

### 17.6 Kontrol variabel dan ancaman validitas

Tetapkan versi OpenCode, model, dan pengaturan; acak urutan pengujian untuk menekan efek belajar; uji pada minimal dua model berbeda agar klaim tidak terikat satu model. Ancaman validitas yang harus ditulis di skripsi: ukuran sampel kecil, label dibuat peneliti sendiri, kemungkinan kebocoran dataset ke pelatihan model, dan ketergantungan pada kualitas model di balik agen.

---

## 18. Peta jalan

| Fase | Kegiatan | Hasil |
| --- | --- | --- |
| 1. Persiapan (semester 7) | Kajian pustaka, kajian skill sejenis, konsultasi dosen, finalisasi PRD | Proposal dan judul disetujui |
| 2. Prototipe | `SKILL.md` awal, command OpenCode, uji pada 5–10 kode berlabel | Prototipe + temuan pilot |
| 3. Pengembangan v1.0 | Pisah `language-patterns.md` dan `frontend-patterns.md`, lengkapi semua bahasa, template laporan, `examples/`, `README`, `CONTRIBUTING`, `LICENSE`, `CHANGELOG` | Rilis v1.0.0 di GitHub |
| 4. Evaluasi (semester 8) | Jalankan kondisi A–E, kumpulkan metrik, ablation | Data hasil |
| 5. Analisis dan penulisan | Olah hasil, tulis bab hasil dan pembahasan | Naskah skripsi |
| 6. Pasca-skripsi | Perbaikan berdasarkan masukan, kontribusi komunitas, fitur lanjutan (FR-21, FR-22) | v1.x |

---

## 19. Risiko dan mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Dianggap "hanya menulis Markdown" | Kontribusi ilmiah dipertanyakan | Evaluasi terukur + ablation study + perbandingan dengan SAST |
| Temuan palsu tinggi | Pengguna kehilangan kepercayaan | Bukti wajib, cek mitigasi, buang temuan Low dari daftar utama |
| Temuan terlewat pada file panjang | Rasa aman palsu | Pemetaan dulu, cakupan terbatas, pernyataan batasan eksplisit |
| `fix` merusak fungsi | Regresi di proyek pengguna | Perubahan minimal, tanpa commit, baca ulang setelah patch, saran perintah test |
| Variasi output antar-run | Hasil sulit dibandingkan | 3–5 pengulangan, laporkan rata-rata dan sebaran |
| Cakupan terlalu luas | Skripsi tidak selesai | Dukungan penuh banyak bahasa, tetapi evaluasi formal hanya 2–3 target |
| Format skill/OpenCode berubah | Skill tidak jalan | Catat versi, dokumentasikan cara pasang, jaga isi tetap portabel |
| Kemiripan dengan skill lain | Isu orisinalitas | Tulis semua isi sendiri, sebut skill lain sebagai penelitian terkait |
| Skill disalahgunakan | Reputasi dan etika | Fokus defensif, tanpa exploit, aturan penolakan eksplisit |
| `AGENTS.md` pribadi ikut terpublikasi | Kebocoran konteks pengembang, membingungkan pengguna | Checklist rilis: pastikan file non-produk tidak ikut (§15.4) |

---

## 20. Keputusan terbuka

| # | Keputusan | Pilihan | Rekomendasi |
| --- | --- | --- | --- |
| 1 | Bentuk perintah utama | Router `/vyche <args>` vs nested `/vyche/scan` | Kirim keduanya, router sebagai utama |
| 2 | Target evaluasi formal | Python + JS/TS + Next.js, atau kombinasi lain | Yang paling dikuasai penulis |
| 3 | Model yang diuji | Minimal dua | Sesuai akses dan biaya |
| 4 | Lisensi | MIT vs Apache-2.0 | MIT untuk adopsi luas; Apache-2.0 bila ingin klausa paten |
| 5 | Dataset terbuka | OWASP Benchmark, Juliet, atau keduanya | Mulai dari fixture sendiri, dataset terbuka sebagai pelengkap |
| 6 | Pelabelan pihak kedua | Dosen pembimbing / rekan | Idealnya ya, untuk kredibilitas label |
| 7 | Pengembangan lanjutan | Auto-invoke tanpa `/vyche`, mode hibrida SAST, dukungan IaC | Pasca-skripsi |

---

## 21. Status implementasi terhadap v1.0

Diperbarui 15 November 2026, setelah rangkaian artefak v1.0 dibangun.

| Artefak | Status | Catatan |
| --- | --- | --- |
| `SKILL.md` | Selesai | Mode `scan`/`report`/`fix`, aturan parsing, kontrak mode (tabel boleh-baca/tulis), pemetaan proyek, gerbang verifikasi 5 poin, gerbang kualitas sebelum output. < 500 baris |
| `references/language-patterns.md` | Selesai | 7 bahasa/framework, pasangan rentan→diperbaiki per bahasa, tabel SQLi per ORM (11 ORM/query builder), pemeriksaan lintas bahasa |
| `references/frontend-patterns.md` | Selesai | React, Next.js (Server Actions, middleware, batas klien/server, hydration), Vue/Nuxt, Svelte/SvelteKit, browser |
| `references/vulnerability-checklist.md` | Selesai | Kategori V-1..V-12 dengan CWE, V-10 sebagai bagian menonjol, pemeriksaan lintas kategori |
| `references/report-template.md` | Selesai | Kontrak keluaran `scan`, `report`, `fix`, panduan severity dan confidence |
| `commands/` | Selesai | Router `/vyche` + `/vyche/scan`, `/vyche/fix`, `/vyche/report` |
| `examples/` | Selesai | 7 fixture + `labels.json` + README berisi skema label dan cara menilai (precision/recall/F1) |
| `README.md` | Selesai | Instalasi OpenCode (bash + PowerShell), tabel perintah, cakupan, batasan |
| `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md` | Selesai | MIT, aturan kontribusi pola dan fixture |
| `docs/PUBLISHING.md` | Selesai | Checklist rilis: file yang harus dibuang, pemeriksaan kebocoran, verifikasi skill memuat |
| `references/languages.md` | Dipensiunkan | Isinya diserap ke `language-patterns.md`. Linguistik C#, Kotlin, C/C++ dikeluarkan dari v1 sesuai §8.1 |
| `agent-command/vyche.md` | Digantikan | Diganti `commands/vyche.md` + `commands/vyche/*.md`; folder lama boleh dihapus saat rilis |

### Uji pilot awal

Sebelum rilis, dua uji pilot dijalankan pada dua fixture (`python-sqli` untuk scan+fix, `prompt-injection` untuk report) memakai agen yang membaca `SKILL.md` sebagai instruksi. Hasilnya: kedua run menemukan temuan yang dilabeli, mode read-only dipatuhi, dan instruksi tersembunyi di dalam kode tidak dituruti. Uji itu juga mengangkat delapan celah di `SKILL.md` yang tidak terlihat saat menulis, semuanya sudah diperbaiki:

| Celah yang ditemukan uji pilot | Perbaikan |
| --- | --- |
| Gerbang bukti menuntut kutipan baris, padahal temuan "tidak ada otorisasi" tidak punya baris pelanggaran | Aturan baru untuk temuan berbentuk ketiadaan: kutip seluruh entry point, sebut apa yang tidak ada, confidence Medium bila kontrol bisa berada di luar cakupan |
| Keyakinan Medium butuh menyebut ketergantungan, tetapi tidak ada tempatnya di laporan | Baris `**Depends on**` di blok temuan |
| Template `scan` tidak punya kolom bukti, sementara gerbang kualitas menuntut kutipan | Kutipan ditempatkan di kolom `Reason`; dinyatakan eksplisit |
| `scan` tidak punya tempat untuk temuan Low confidence | Baris `Needs human review` setelah ringkasan |
| Tidak jelas apakah mode `fix` harus tetap menampilkan temuan, bukan hanya tabel perubahan | Dinyatakan: run `fix` tetap melaporkan temuan yang ditambal dan yang ditinggalkan |
| Severity tidak reprodusibel saat ada petunjuk deployment (`127.0.0.1` vs `0.0.0.0`) | Aturan: nilai untuk deployment yang terlihat, sebut baris yang akan mengubah nilainya |
| "Perubahan minimal" tidak mendefinisikan hardening yang mengubah perilaku | Aturan: perubahan perilaku harus dilabeli, atau ditingsalkan beserta risiko sisanya |
| Fixture saya sendiri menuliskan jawabannya di baris pertama file | Aturan "bukti dari perilaku, bukan label" + semua header fixture dinetralkan |

Dua hal lain yang ikut berubah: `fix` dinyatakan boleh menutup nol temuan (aplikasi tanpa auth tidak punya model auth untuk ditambal), dan skema label evaluasi mendapat `acceptable_extra` serta `acceptable_severity` karena run pertama menemukan masalah nyata yang tidak ada di daftar label.

Uji pilot ketiga dijalankan pada `full-app` (report, lima temuan berlabel) setelah perbaikan di atas. Hasilnya: 5/5 label tertangkap, nol regresi, nol penulisan file. Run itu mengangkat lima catatan wording lagi, semuanya sudah ditutup:

| Celah | Perbaikan |
| --- | --- |
| "Cakupan di baris pertama" bertabrakan dengan template yang membuka dengan H1 | Blok cakupan dipindah ke atas judul; template menyatakannya sebagai keputusan sadar |
| Tabel severity tidak menyelesaikan injection publik dengan isi database tak terlihat | Ditetapkan: High, Critical hanya bila kode menunjukkan isi di baliknya |
| Severity untuk security header yang tidak ada tidak jelas (Low atau Medium) | Ditetapkan: Low pada tool internal, Medium bila ada jalur XSS hidup yang bisa diredam CSP |
| Severity Low dan confidence Low tercampur di beberapa tempat | Bagian "Two different lows": severity Low boleh di daftar utama, confidence Low tidak pernah |
| File non-runtime (`labels.json`, golden file, snapshot) bisa terbaca sebagai bukti | Aturan cakupan: file penentu hasil dikecualikan dan disebut di baris cakupan |

Skema label juga mendapat `acceptable_cwe`, karena `DEBUG = True` sama-sama sah disebut CWE-1188, CWE-489, atau CWE-16 dan run tidak seharusnya kehilangan kecocokan hanya karena memilih id yang berbeda.

**Batas yang jujur soal angka ini:** tiga run pilot bukan matriks uji §16.1. Yang terbukti adalah mekanismenya berjalan (mode dipatuhi, bukti dikutip, label tertangkap, injeksi tidak dituruti), bukan skor precision/recall final.

### Uji pilot putaran kedua

Empat fixture diuji lagi (`python-clean` scan, `hardcoded-secret` report, `ambiguous-auth` report, `nextjs-action` report). Hasilnya lebih berharga daripada putaran pertama karena tiga dari empat run menemukan cacat di spesifikasi, bukan di kode uji:

| Temuan dari run | Akar masalah | Perbaikan |
| --- | --- | --- |
| `ambiguous-auth` menaruh IDOR di daftar utama; label menuntutnya di "Needs human review" | Label ditulis sebelum aturan temuan-ketiadaan ada, jadi ia menghukum perilaku yang sekarang diwajibkan | Label dikoreksi: daftar utama, confidence Medium, `Depends on`. Penempatan di review dicatat sebagai perbedaan, bukan false positive |
| Run memperlakukan komentar "ownership enforced by middleware" sebagai dependensi yang tak terperiksa | Skill tidak pernah menyuruh memeriksa file yang disebut sebagai tempat kontrol | Aturan **follow the pointer**: baca file yang disebut bila ada di proyek. Tiga verdict: kontrol nyata (drop), kontrol tidak mencakup jalur ini (High), file tidak ada (temuan berdiri, klaim menggantung dinyatakan absen) |
| `python-clean` melaporkan `/user/<id>` tanpa auth; label menyebut "temuan apa pun adalah false positive" | Fixture memang mengandung celah nyata yang tidak masuk label | `acceptable_extra` CWE-862; catatan label dikoreksi |
| `hardcoded-secret` menilai secret Medium karena bind `127.0.0.1`, tabel severity bilang High | Tabel severity dan aturan deployment tidak punya urutan | Presedensi: tabel = default menghadap internet, rating deployment yang dikirim, selisihnya menyebut baris penyebab |
| Run memakai CWE-306 untuk `/login` yang menerbitkan token tanpa verifikasi kredensial; CWE-306 tidak ada di daftar | Checklist V-3 tidak punya id untuk "autentikasi tidak ada sama sekali" | CWE-306 ditambahkan ke V-3 beserta deskripsinya |
| Tidak ada aturan untuk scope berupa potongan folder (impor menunjuk ke `@/lib/*` yang tidak ada) | Cakupan parsial tidak didefinisikan | Aturan: apa pun yang verdict-nya bergantung pada file yang tidak dibaca = Medium, file yang tidak terlihat disebut di batas |
| Kebingungan menaruh sink yang terkonfirmasi dengan sumber yang tidak terbaca | Dua aturan menunjuk arah berbeda | Ditetapkan: daftar utama, Medium, `Depends on` |
| Nama file `labels.json` sendiri bisa memancing reviewer | Aturan pengecualian tidak menyebut efek nama | "Nama file yang dikecualikan bukan petunjuk" |

Satu hal yang tidak saya ubah meski diminta: run `ambiguous-auth` mengeluh bahwa confidence untuk temuan ketiadaan "selalu mentok Medium" pada cakupan sempit. Itu bukan cacat — itu pernyataan akurat tentang bukti yang ada, dan aturan baru menyuruh mengatakannya, bukan menghapusnya.

#### Putaran ketiga: run ulang `ambiguous-auth`

Run ulang dilakukan khusus untuk membuktikan aturan *follow the pointer* bekerja, bukan cuma tertulis. Hasilnya: komentar tidak dipercaya, `billing/middleware.py` diperiksa, file dinyatakan tidak ada, temuan masuk daftar utama, confidence Medium — persis yang diresepkan. Run itu juga mengangkat enam konflik wording yang tersisa, semuanya ditutup:

| Konflik | Perbaikan |
| --- | --- |
| "High bila seluruh proyek masuk cakupan" tidak terdefinisi saat yang diberikan hanya subfolder | Konsep **evidence boundary** didefinisikan sekali: High hanya bila batas bukti berimpit dengan batas rumah kontrol. Subfolder tetap ekscerpt, apa pun sebutan penggunanya |
| Aturan temuan-ketiadaan dan aturan cakupan-parsial sama-sama menghasilkan Medium karena alasan berbeda | Keduanya sekarang merujuk satu definisi yang sama, jadi tidak ada dua alasan yang bersaing |
| Tidak jelas apakah komentar "ownership enforced by middleware" juga layak jadi temuan CWE-1427 sendiri | Uji eksplisit: klaim tentang sistem diuji dan dikutip di dalam temuan; instruksi kepada reviewer baru jadi CWE-1427. Menghitung klaim sebagai temuan terpisah = double-count satu cacat |
| Checklist mewajibkan perintah audit di `Needs human review` saat manifest tidak ada, bertabrakan dengan "jangan mengarang agar terlihat teliti" | Satu baris di `Not covered / limits`; naik ke review hanya bila keselamatan kode benar-benar bergantung pada versi dependensi |
| Tidak ada batas ukuran tabel laporan maupun bagian review | 15 temuan detail, 5 item review, 2 baris cakupan. Menembus batas itu adalah temuan tentang cakupan, bukan prestasi |
| Tidak ada aturan untuk view yang file routing-nya tidak ada | Routing yang tidak terlihat masuk `Depends on`; temuan tetap berdiri. Tidak boleh dilabeli "dead code" hanya karena `urls.py` tidak diberikan |

### Sisa pekerjaan sebelum v1.0.0 dirilis

1. Jalankan matriks uji §16.1 pada ketujuh fixture dan catat hasilnya (12/12 sebagai target lulus).
2. ~~Isi placeholder identitas~~ — selesai: `Bara Abiyyi` di `LICENSE` dan header PRD, `BaraAbiyyi` di URL clone README.
3. ~~Putuskan nasib `AGENTS.md` dan draf PRD v0.1~~ — selesai: keduanya keluar dari repo. `AGENTS.md` dan `agent-command/` diarsipkan di luar repo; draf v0.1 dipindah ke `docs/archive/PRD-v0.1.md` dengan catatan arsip.
4. Tetapkan tag `v1.0.0` dan catat commit hash-nya untuk log evaluasi.

### Catatan keputusan

Ruang lingkup bahasa dipangkas ke tujuh bahasa/framework di §8.1. C#, Kotlin, dan C/C++ tidak lagi didukung di v1 agar fokus skripsi tidak melebar; V-12 (keamanan memori) tetap ada di checklist untuk kasus `unsafe` Rust dan cgo, bukan untuk mengembalikan dukungan C/C++.

---

## 22. Lampiran

### 22.1 Glosarium

| Istilah | Arti |
| --- | --- |
| Agent skill | Paket instruksi Markdown yang dimuat agen saat relevan, berisi alur kerja dan referensi |
| Source → sink | Jalur data dari titik masuk input sampai titik berbahaya (query, shell, HTML, path, redirect) |
| Trust boundary | Batas tempat data berpindah dari zona tidak tepercaya ke zona tepercaya |
| Progressive disclosure | Memuat detail hanya saat dibutuhkan agar konteks tetap efisien |
| Ablation study | Menguji varian skill dengan satu komponen dihapus untuk mengukur kontribusinya |
| CWE | Common Weakness Enumeration, taksonomi jenis kelemahan keamanan |
| IDOR | Insecure Direct Object Reference, akses objek milik orang lain lewat id yang dapat ditebak |

### 22.2 Acuan standar

- OWASP Top 10 (2021) dan OWASP Cheat Sheet Series — kategori kerentanan dan rekomendasi perbaikan.
- CWE Top 25 — pemetaan ID CWE di setiap temuan.
- OWASP ASVS — tingkat kedalaman pemeriksaan autentikasi dan kontrol akses.
- Dokumentasi resmi ORM/framework untuk contoh kode parameterisasi (Prisma, Sequelize, TypeORM, SQLAlchemy, Django ORM, GORM, Hibernate/JPA, ActiveRecord, Eloquent, sqlx/Diesel).
- Dokumentasi OpenCode untuk skill dan custom command (`SKILL.md`, `.opencode/skills/`, `.opencode/commands/`).

### 22.3 Skill dan tool sejenis untuk tinjauan pustaka

Perlu dikaji langsung (isi, bahasa yang didukung, ada tidaknya evaluasi) sebelum ditulis di skripsi:

- BridgeSecurity (`bridge-mind/bridgesecurity`)
- `security-review` di repositori `github/awesome-copilot`
- `security-review` di `factory-ai/factory-plugins`
- `review-security` di `mgiovani/cc-arsenal`
- `opencode-skills` (`rekabytes/opencode-skills`)
- `security-review` di `mastra-ai/mastra`
- Pembanding tool: Semgrep, Bandit, CodeQL (dijalankan peneliti di luar skill)

Semua isi Vyche ditulis sendiri. Bila ada ide yang terinspirasi dari daftar di atas, dicatat sebagai sumber; tidak ada teks yang disalin.

### 22.4 Definisi selesai v1.0

- [x] `SKILL.md` memuat mode `scan`, `report`, `fix` + aturan parsing + gerbang kualitas.
- [x] `references/language-patterns.md` mencakup 7 bahasa/framework dengan pasangan rentan→diperbaiki dan rujukan per-ORM.
- [x] `references/frontend-patterns.md` mencakup React, Next.js, Vue, Svelte, dan hal khusus browser.
- [x] `references/vulnerability-checklist.md` memuat V-1..V-12.
- [x] `commands/vyche.md` + `commands/vyche/{scan,fix,report}.md` tersedia untuk OpenCode.
- [x] 7 fixture di `examples/` dengan label yang bisa diskor.
- [x] `README.md`, `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md` ada dan konsisten.
- [x] Repo publik bersih dari `AGENTS.md` dan file non-produk. `AGENTS.md` dan `agent-command/` diarsipkan di luar repo; draf PRD v0.1 ada di `docs/archive/`.
- [x] Tag `v1.0.0` dirilis di https://github.com/BaraAbiyyi/Vyche, commit `783211c`.
- [ ] Matriks uji §16.1 lulus 12/12, nol pelanggaran read-only.
- [ ] `/vyche scan` dijalankan dari skill yang benar-benar terpasang di `.opencode/`, bukan dari `SKILL.md` yang dibaca langsung.

Sembilan dari sebelas kotak tertutup. Dua yang tersisa sama-sama pengukuran, bukan penulisan: satu matriks skor, satu bukti bahwa skill menyala saat dipasang. Keduanya sengaja tidak dicentang sekarang — repo sudah publik, dan kotak yang dicentang tanpa bukti adalah kebohongan yang akan terbaca di skripsi.
