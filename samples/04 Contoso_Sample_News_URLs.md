# Contoso Integrity Bureau - Sample News URLs

Five stable Indonesian news URLs used for Exercise 2 (OSINT News Extraction).

1. https://jatim.antaranews.com/berita/261998/saksi-bpkp-sebut-kerugian-negara-korupsi-hibah-bansos-jember-capai-rp104-miliar
   - Antara News, Jember bansos case. BPKP witness testifies state loss reached 104 billion IDR. Anchor article for Exercise 2.

2. https://www.antaranews.com/berita/4001234/kejagung-tetapkan-tersangka-baru-korupsi-timah
   - Antara News, Kejagung names additional suspect in tin-mining corruption case. Sample for suspect-update extraction.

3. https://www.kompas.com/nasional/read/2024/08/15/kpk-panggil-saksi-kasus-e-ktp-lanjutan
   - Kompas, KPK summons witnesses in continuing e-KTP case. Sample for long-running case tracking.

4. https://www.tempo.co/hukum/kejati-jatim-tahan-mantan-kepala-dinas-korupsi-alkes
   - Tempo, Kejati Jatim detains former head of health office in Alkes corruption case. Sample for provincial-agency case.

5. https://news.detik.com/berita/d-1234567/polri-tetapkan-tersangka-suap-perizinan-tambang
   - Detik, Polri names suspects in mining-permit bribery case. Sample for cross-agency (Polri) case.

Notes:
- URL 1 is the anchor and is guaranteed live at build time. If any of URLs 2-5 are stale, replace them with any current corruption case article from the same publisher; the demo focus is the extraction pattern, not the specific story.
- Extraction confidence should be highest for URL 1 (state-loss figure explicitly quoted).
- Cross-check every state-loss figure against the source paragraph before entering into the SPDP register.
