> **Archived.** This is the v0.1 draft, superseded by `docs/PRD.md` (v1.1). Kept for history; do not treat it as the current specification.

# PRD Vyche: Agent Skill untuk Analisis, Perbaikan, dan Pelaporan Keamanan Kode

Versi 0.1 (draf) · 15 November 2026 · Penyusun: \[nama kamu\] · Status: untuk didiskusikan dengan dosen pembimbing

## 1. Ringkasan

Vyche adalah *agent skill* open source yang membantu programmer memeriksa keamanan kode, terutama kode yang ditulis dengan bantuan AI, sebelum masuk tahap production. Pengguna memasang skill ini pada agen AI masing-masing (diuji pada OpenCode) lalu memanggilnya lewat `/vyche scan`, `/vyche fix`, atau `/vyche report`.

Vyche berupa paket instruksi (Markdown) yang dibaca agen. Tidak ada program tambahan yang harus dipasang, dan analisis dilakukan murni oleh agen dengan membaca kode. Dokumen ini juga menjadi dasar skripsi: Vyche adalah objek yang dirancang lalu dievaluasi seberapa besar ia meningkatkan kemampuan agen yang sama dalam mendeteksi dan memperbaiki kerentanan.

## 2. Latar belakang dan masalah

- Penggunaan AI untuk menulis kode makin luas, tetapi hasilnya tidak selalu aman. Aspek keamanan sering tidak diminta secara eksplisit di prompt, sehingga validasi input, otorisasi, dan pengelolaan secret kerap terlewat.
- Programmer yang mengandalkan AI belum tentu punya waktu atau keahlian untuk meninjau keamanan kodenya sendiri.
- Tool pemindai keamanan konvensional butuh instalasi dan konfigurasi, dan hasilnya sering berupa daftar panjang tanpa penjelasan atau perbaikan.
- Sudah ada beberapa skill security review untuk agen AI (lihat Lampiran), tetapi belum jelas seberapa besar peningkatan yang diberikannya secara terukur. Celah inilah yang ingin dijawab penelitian ini.

## 3. Tujuan dan non-tujuan

### Tujuan produk

1. Membantu pengguna menemukan kerentanan pada kodenya dengan cepat, dengan bukti dan penjelasan yang bisa diverifikasi.
2. Membantu memperbaiki kerentanan dengan perubahan minimal yang aman dan bisa ditinjau.
3. Menghasilkan laporan keamanan yang terstruktur dan mudah dibaca.
4. Mudah dipasang dan dipakai: cukup salin skill, tanpa dependensi tambahan.

### Tujuan penelitian

1. Mengukur peningkatan precision, recall, dan F1 deteksi kerentanan saat agen memakai Vyche dibanding tanpa skill.
2. Mengetahui komponen desain skill mana yang paling berpengaruh (ablation study).
3. Mengukur efektivitas perbaikan: kerentanan tertutup tanpa merusak fungsi.

### Non-tujuan (v1)

- Bukan pengganti penetration test, SAST, atau review manusia, dan bukan jaminan kode aman.
- Tidak membuat exploit siap pakai, tidak menyerang sistem, tidak memindai jaringan atau infrastruktur.
- Tidak menjalankan kode proyek pengguna, tidak menginstal paket, dan tidak mengirim kode ke luar sesi agen.
- Tidak memakai tool eksternal (Semgrep, CodeQL, dan sejenisnya) di dalam skill. Tool tersebut hanya dipakai peneliti sebagai pembanding saat evaluasi.
- Dukungan resmi hanya untuk OpenCode. Agen lain bersifat best-effort.

## 4. Pengguna target

| Persona | Kebutuhan |
| --- | --- |
| Programmer yang banyak memakai AI untuk coding (termasuk pemula dan mahasiswa) | Cara cepat memeriksa apakah kode hasil AI aman, dengan penjelasan yang mudah dipahami |
| Tim kecil / pengembang mandiri tanpa tim keamanan | Laporan yang bisa dilampirkan di PR atau dokumentasi sebelum rilis |
| Reviewer kode | Daftar temuan berbukti untuk mempercepat review |
| Peneliti (penyusun skripsi ini) | Skill yang perilakunya terkontrol dan hasilnya bisa diukur |

## 5. Skenario penggunaan

| ID | Sebagai | Saya ingin | Agar |
| --- | --- | --- | --- |
| US-1 | Programmer | menjalankan `/vyche scan` pada file yang baru saya buat dengan AI | tahu cepat jika ada celah yang jelas |
| US-2 | Programmer | menjalankan `/vyche report` | mendapat laporan lengkap yang bisa saya simpan atau bagikan |
| US-3 | Programmer | menjalankan `/vyche fix` | celah yang terbukti ditambal tanpa saya menulis ulang manual |
| US-4 | Pengguna | menentukan cakupan (file, folder, fitur) dengan kalimat bebas setelah perintah | pemeriksaan sesuai kebutuhan dan hemat waktu |
| US-5 | Pengguna | yakin bahwa scan dan report tidak mengubah file saya | aman dijalankan kapan saja |
| US-6 | Pengguna | melihat perubahan fix lewat `git diff` tanpa commit otomatis | tetap memegang kendali |
| US-7 | Peneliti | menjalankan skill berulang pada kode uji yang sama | membandingkan hasil dengan baseline secara adil |

Contoh pemanggilan:

```
/vyche scan folder src/auth
/vyche report seluruh proyek ini
/vyche fix celah di app/db.py
```

## 6. Ruang lingkup v1

### Bahasa dan framework yang didukung

| Referensi | Cakupan |
| --- | --- |
| `language-patterns.md` | JavaScript/TypeScript, Python, Go, Rust, Java/Spring, Ruby/Rails, PHP. Berisi pola kerentanan, pasangan kode rentan dan kode yang sudah diperbaiki, serta referensi SQL injection per ORM |
| `frontend-patterns.md` | React, Next.js (Server Actions, middleware, hydration), Vue, Svelte, dan hal khusus browser |

Referensi SQL injection per ORM yang disarankan: Prisma, Sequelize, TypeORM, SQLAlchemy, Django ORM, GORM, Hibernate/JPA, ActiveRecord, Eloquent, serta sqlx/Diesel untuk Rust. Semua contoh kode ditulis sendiri dan dicocokkan dengan sumber resmi (OWASP Cheat Sheet, dokumentasi ORM).

**Didukung vs dievaluasi.** Semua bahasa di atas didukung sebagai produk, tetapi evaluasi formal di skripsi dibatasi pada 2 sampai 3 target (usulan: Python, JavaScript/TypeScript, dan satu framework frontend seperti Next.js). Sisanya dinyatakan sebagai didukung namun belum dievaluasi secara formal.

### Kategori kerentanan v1

Berpedoman pada OWASP Top 10 dan CWE: injeksi (SQL, perintah OS, XSS, path traversal), kontrol akses dan IDOR, autentikasi dan sesi (JWT, cookie, CSRF), kriptografi dan secret yang tertanam, paparan data sensitif, upload dan deserialisasi tidak aman, SSRF dan open redirect, serta konfigurasi tidak aman. Ditambah satu kategori khusus: **pola umum pada kode hasil AI** (secret placeholder, validasi dilewati, default tidak aman, paket yang diragukan).

## 7. Kebutuhan fungsional

### 7.1 Perintah

| Perintah | Tujuan | Mengubah file? | Keluaran |
| --- | --- | --- | --- |
| `/vyche scan` | Deteksi cepat pada cakupan yang diminta | Tidak | Ringkasan temuan di chat: lokasi, CWE, severity, satu kalimat alasan |
| `/vyche report` | Analisis menyeluruh dan laporan terstruktur | Tidak (menyimpan ke file hanya jika diminta) | Laporan lengkap dengan bukti dan rekomendasi perbaikan |
| `/vyche fix` | Analisis, lalu perbaikan temuan yang terverifikasi | Ya, hanya perubahan minimal, tanpa commit | Daftar perubahan, hal yang perlu dilakukan manual, saran perintah test |

Jika perintah tidak dikenali atau tidak ada kata perintah, skill memakai `scan` (aman, tidak mengubah file) dan menawarkan langkah berikutnya.

### 7.2 Kebutuhan

| ID | Kebutuhan | Prioritas |
| --- | --- | --- |
| FR-1 | Skill terpicu oleh `/vyche` dan mengenali sub-perintah `scan`, `fix`, `report` | Wajib |
| FR-2 | Menentukan cakupan dari kalimat pengguna; bila tidak disebut, mulai dari file yang berubah (working tree) dan menyatakan cakupan yang dipilih | Wajib |
| FR-3 | Memetakan proyek sebelum mencari celah: stack, entry point, aset sensitif, trust boundary | Wajib |
| FR-4 | Mendeteksi bahasa dan framework, lalu hanya memuat referensi yang relevan (progressive disclosure) | Wajib |
| FR-5 | Menelusuri alur data dari sumber (input) ke sink (query, shell, HTML, file, request) | Wajib |
| FR-6 | Setiap temuan wajib disertai bukti (file, baris, kutipan), CWE, severity, tingkat keyakinan, dan penjelasan jalur serangan secara konseptual | Wajib |
| FR-7 | Temuan berkeyakinan rendah tidak masuk daftar utama, melainkan bagian Perlu ditinjau manusia | Wajib |
| FR-8 | `scan` dan `report` tidak boleh mengubah, membuat, atau menghapus file proyek | Wajib |
| FR-9 | `fix` hanya menambal temuan terverifikasi dengan perubahan minimal, mengikuti gaya dan library proyek, tanpa commit dan tanpa menambah dependensi kecuali terpaksa dan dilaporkan | Wajib |
| FR-10 | Setelah menambal, agen membaca ulang area yang diubah untuk memastikan celah tertutup dan tidak muncul celah baru | Wajib |
| FR-11 | Laporan memakai template baku dan menyebut apa yang tidak tercakup beserta batasan skill | Wajib |
| FR-12 | Output mengikuti bahasa pengguna (Indonesia atau Inggris) | Wajib |
| FR-13 | Jika tidak ada temuan, menyatakan hal itu apa adanya dan menyebut yang sudah diperiksa, tanpa mengklaim kode pasti aman | Wajib |
| FR-14 | Menyimpan laporan ke file (misalnya `vyche-report.md`) bila pengguna memintanya | Sebaiknya |
| FR-15 | Dukungan tambahan: IaC dan konfigurasi CI (Dockerfile, GitHub Actions) | Nanti |

## 8. Kebutuhan non-fungsional

- **Instalasi sederhana:** cukup menyalin folder skill dan file command ke proyek, tanpa dependensi.
- **Efisiensi konteks:** `SKILL.md` ringkas (di bawah 500 baris), detail di folder `references/` dimuat sesuai kebutuhan.
- **Reprodusibilitas:** skill diberi nomor versi; hasil uji mencatat versi skill, versi OpenCode, model, dan pengaturan.
- **Keamanan skill itu sendiri:** tidak ada skrip tersembunyi, tidak ada akses jaringan, tidak ada instruksi yang mengirim data keluar. Seluruh isi mudah diaudit.
- **Keterbacaan:** laporan dapat dipahami programmer tingkat menengah; istilah teknis diberi penjelasan singkat.
- **Lisensi dan kontribusi:** lisensi open source (usulan MIT atau Apache-2.0), dengan CONTRIBUTING dan template issue.

## 9. Arsitektur skill

Struktur repositori yang diusulkan:

```
vyche/
â”œâ”€â”€ SKILL.md                      # alur kerja inti, aturan mode, aturan keamanan
â”œâ”€â”€ references/
â”‚   â”œâ”€â”€ language-patterns.md      # JS/TS, Python, Go, Rust, Java/Spring, Ruby/Rails, PHP
â”‚   â”œâ”€â”€ frontend-patterns.md      # React, Next.js, Vue, Svelte, browser
â”‚   â”œâ”€â”€ vulnerability-checklist.md# kategori, CWE, pola kode hasil AI
â”‚   â””â”€â”€ report-template.md        # format laporan dan panduan severity
â”œâ”€â”€ agent-command/
â”‚   â””â”€â”€ vyche.md                  # mendaftarkan /vyche di OpenCode
â”œâ”€â”€ examples/                     # contoh input dan output
â”œâ”€â”€ README.md
â”œâ”€â”€ CONTRIBUTING.md
â””â”€â”€ LICENSE
```

### Alur kerja inti

1. **Tentukan perintah dan cakupan** dari teks setelah `/vyche`.
2. **Petakan proyek:** stack, entry point, aset sensitif, trust boundary.
3. **Muat referensi** sesuai bahasa dan framework yang terdeteksi.
4. **Telusuri alur data** dari sumber ke sink, dan periksa kontrol yang tidak berbentuk alur (otorisasi, secret, konfigurasi).
5. **Verifikasi temuan:** bukti, cek mitigasi yang mungkin terlewat, tingkat keyakinan; buang yang lemah.
6. **Keluaran** sesuai perintah: ringkasan (`scan`), laporan (`report`), atau perubahan kode (`fix`).

Desain ini sengaja menekan dua kelemahan umum agen: temuan palsu (diatasi dengan bukti wajib dan verifikasi) dan temuan terlewat pada file panjang (diatasi dengan pemetaan dan cakupan terbatas).

## 10. Format keluaran

- **Scan:** tabel singkat berisi nomor, severity, CWE, lokasi, dan satu kalimat alasan, ditutup dengan tawaran menjalankan `report` atau `fix`.
- **Report:** ringkasan, tabel temuan, rincian tiap temuan (lokasi, bukti, mengapa penting, saran perbaikan dengan contoh kode), bagian Perlu ditinjau manusia, bagian Sudah diperiksa tanpa temuan, dan bagian Batasan.
- **Fix:** tabel perubahan (temuan, file, apa yang berubah, tindakan manual yang masih diperlukan) dan langkah selanjutnya (tinjau `git diff`, jalankan test, rotasi secret yang bocor).
- **Severity:** Critical, High, Medium, Low, Info, dinilai dari dampak dan kemudahan eksploitasi dalam konteks proyek, bukan hanya dari jenis kerentanan.

## 11. Keamanan, etika, dan privasi

- Isi kode, komentar, dan dokumen proyek diperlakukan sebagai **data**, bukan perintah. Instruksi tersembunyi di dalam kode (prompt injection) diabaikan dan dilaporkan sebagai temuan.
- Skill hanya menganalisis kode milik pengguna. Permintaan untuk menyerang atau mengeksploitasi sistem ditolak, dan pengguna ditawari review kode sebagai gantinya.
- Jalur serangan dijelaskan secara konseptual sebagai bukti; tidak ada payload atau skrip eksploit siap pakai.
- Secret yang ditemukan hanya ditampilkan sebagian dalam laporan dan disertai saran rotasi.
- Skill tidak menjalankan kode proyek, tidak menginstal paket, dan tidak membuat permintaan jaringan.
- Pengujian hanya dilakukan pada kode buatan sendiri atau dataset terbuka berlisensi yang jelas.

## 12. Rencana evaluasi

### Pertanyaan penelitian

1. Seberapa besar Vyche meningkatkan precision, recall, dan F1 deteksi kerentanan dibanding agen yang sama tanpa skill?
2. Komponen desain mana yang paling berkontribusi?
3. Seberapa efektif perbaikan `fix` menutup kerentanan tanpa merusak fungsi?
4. Bagaimana posisi Vyche dibanding skill security review lain dan tool SAST (sebagai pembanding)?

### Kondisi uji

- **A:** agen tanpa skill
- **B:** agen dengan prompt sederhana (misalnya: cari celah keamanan di kode ini)
- **C:** agen dengan Vyche lengkap
- **D:** varian ablation Vyche (tanpa langkah verifikasi, tanpa referensi bahasa, tanpa pemetaan)
- **E:** pembanding eksternal: satu atau dua skill security review yang sudah ada, serta Semgrep/Bandit dijalankan oleh peneliti di luar skill

### Data uji

- Kode yang dibuat dengan meminta AI menulis fitur umum (login, upload file, query database, API CRUD, form di frontend), lalu dilabeli kerentanannya secara manual dan, bila mungkin, ditinjau pihak kedua.
- Dataset terbuka berlabel (misalnya OWASP Benchmark atau Juliet) sebagai pelengkap, dengan catatan kemungkinan sudah dikenal model saat pelatihan.
- Batasi 5 sampai 8 jenis kerentanan dan 2 sampai 3 bahasa/framework untuk evaluasi formal.

### Metrik

| Metrik | Keterangan |
| --- | --- |
| Precision, recall, F1 | Kecocokan temuan dengan label kebenaran |
| False positive rate | Temuan yang tidak benar per run |
| Tingkat keberhasilan fix | Kerentanan tidak lagi terdeteksi setelah perbaikan, ditinjau manual |
| Tingkat regresi | Test atau fungsi yang rusak akibat fix |
| Kepatuhan mode | Pelanggaran scan/report yang mengubah file (target: nol) |
| Efisiensi | Waktu dan jumlah token per run |
| Variasi antar-run | Simpangan baku dari 3 sampai 5 pengulangan tiap skenario |

Target angka peningkatan ditetapkan setelah uji pilot. Hipotesisnya Vyche mengungguli kondisi A dan B; jika hasilnya tidak demikian, itu tetap temuan ilmiah yang dilaporkan apa adanya.

### Kontrol variabel

Catat dan tetapkan versi OpenCode, model, suhu/pengaturan yang dapat diatur, versi skill, dan urutan pengujian. Idealnya uji pada minimal dua model berbeda agar klaim tidak hanya berlaku pada satu model.

## 13. Asumsi dan ketergantungan

- OpenCode mendukung skill dan custom command dengan mekanisme yang akan dikonfirmasi pada versi yang dipakai (lokasi folder dan format dapat berubah antar versi).
- Teks setelah `/vyche` diteruskan ke agen sebagai argumen.
- Pengguna memakai model yang cukup kuat untuk menganalisis kode; kualitas hasil bergantung pada model di baliknya.
- Pengguna mengizinkan agen membaca berkas proyek, dan menulis berkas hanya pada mode `fix`.

## 14. Risiko dan mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Dianggap hanya menulis Markdown | Kontribusi ilmiah dipertanyakan | Evaluasi terukur dan ablation study |
| Temuan palsu tinggi | Pengguna kehilangan kepercayaan | Bukti wajib, verifikasi, buang temuan berkeyakinan rendah |
| Temuan terlewat pada file panjang | Rasa aman palsu | Pemetaan dulu, cakupan terbatas, pernyataan batasan di laporan |
| `fix` merusak fungsi | Regresi di proyek pengguna | Perubahan minimal, tanpa commit, saran menjalankan test |
| Variasi output antar-run | Hasil sulit dibandingkan | Pengulangan 3 sampai 5 kali, laporkan rata-rata dan sebaran |
| Cakupan terlalu luas (banyak bahasa dan framework) | Skripsi tidak selesai | Evaluasi formal hanya 2 sampai 3 target |
| Format skill/OpenCode berubah | Skill tidak jalan | Catat versi, dokumentasikan cara pasang |
| Kemiripan dengan skill lain | Isu orisinalitas | Tulis semua isi sendiri, sebut skill lain sebagai penelitian terkait |
| Skill disalahgunakan | Reputasi dan etika | Fokus defensif, tanpa eksploit, aturan penolakan di skill |

## 15. Peta jalan

| Fase | Kegiatan | Hasil |
| --- | --- | --- |
| 1. Persiapan (semester 7) | Kajian pustaka, kajian skill serupa, konsultasi dosen, finalisasi PRD | Proposal dan judul disetujui |
| 2. Prototipe | `SKILL.md` awal, command OpenCode, uji pada 5 sampai 10 kode berlabel | Prototipe dan temuan pilot |
| 3. Pengembangan v1 | Lengkapi referensi bahasa dan frontend, template laporan, contoh | Rilis v1.0 di GitHub |
| 4. Evaluasi (semester 8) | Jalankan semua kondisi uji, kumpulkan metrik, ablation | Data hasil |
| 5. Analisis dan penulisan | Olah hasil, tulis bab hasil dan pembahasan | Naskah skripsi |
| 6. Pasca-skripsi | Perbaikan, kontribusi komunitas, fitur lanjutan | v1.x |

## 16. Keputusan yang masih terbuka

1. **Perbedaan scan dan report.** Usulan di dokumen ini: scan = ringkasan cepat, report = laporan lengkap. Alternatif: gabungkan menjadi satu agar evaluasi lebih sederhana.
2. **Target evaluasi formal:** bahasa dan framework mana yang dipilih (disarankan yang paling dikuasai).
3. **Model yang diuji:** minimal dua; tentukan sesuai akses dan biaya.
4. **Lisensi:** MIT atau Apache-2.0.
5. **Pemakaian dataset terbuka** dan cara pelabelan oleh pihak kedua.
6. **Pengembangan lanjutan:** aktivasi otomatis tanpa `/vyche`, mode hibrida dengan SAST opsional, dukungan IaC.

## 17. Lampiran: skill serupa untuk tinjauan pustaka

Skill berikut ditemukan melalui pencarian dan perlu dikaji langsung (isi, bahasa yang didukung, ada tidaknya evaluasi) sebelum ditulis di skripsi:

- BridgeSecurity (bridge-mind/bridgesecurity)
- security-review di repositori github/awesome-copilot
- security-review di factory-ai/factory-plugins
- review-security di mgiovani/cc-arsenal
- opencode-skills (rekabytes/opencode-skills)
- security-review di mastra-ai/mastra

Catatan: struktur dan daftar cakupan Vyche harus ditulis dan diverifikasi sendiri. Jika ada ide yang terinspirasi dari skill di atas, sebutkan sebagai sumber, dan jangan menyalin teksnya.
