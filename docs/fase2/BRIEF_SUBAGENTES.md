# Phase 2 brief — shared by every literature subagent

Project: ENAHO 2025 (Peru household survey) app, repo root
`C:/Users/Usuario/Documents/Portfolio/DespliegueML/proyecto_enaho_ingresos`.
Two models over 47,632 employed people aged 14+ with positive labor income:
(1) monthly labor income regression (predictive Gradient Boosting "E9" + explanatory
population-weighted WLS "E6"); (2) informal-employment classifier (INEI rule:
self-employed without RUC, or employee without pension contributions).

## Findings of the app you must cross with the literature (all «hallazgo propio»)

Explanatory E6 (WLS weighted by FAC500A, R² 0.473, HC3 errors; effect = (exp(b)−1)·100,
associational, NOT causal):
- +1 year of schooling: +4.8 % income. Experience +4.1 %/yr, concave.
- Male vs female: +43.4 % (same schooling, experience, hours, industry, category, firm size, region).
- Urban vs rural: +32.3 %. log(hours) elasticity 0.34.
- Self-employed vs employee: −49.6 %. Employer: +34.1 %. Domestic worker: −3.0 % (n.s.).
- Firm ≤20 people vs >500: −33.4 %. Sierra Norte vs Lima Metropolitana: −31.1 %; Sierra Centro −19.9 %.
- Mining +73.7 % vs commerce; agriculture −10.2 %.
- Sensitivity: adding in-kind income, the urban premium goes from 54.6 % to 52.0 %
  (simpler spec); in-kind/own consumption received by 24.6 % of workers.

Classifier (logit odds ratios, base: woman, rural, Lima, commerce, firm >500, employee):
- Firm ≤20: OR 16.7. Self-employed: OR 5.2. Domestic worker: OR 3.7. Agriculture 2.9.
- Each year of schooling: OR 0.82. Male: OR 0.67. Urban: OR 0.56.
- Gradient Boosting PR-AUC ≈ 0.96 (baseline = prevalence 0.678 sample / 0.641 weighted).
  Removing firm size AND category, PR-AUC still ≈ 0.94. The classifier "flags job
  configurations, not people" (targeting tool, not causal, not individual prediction).
- Reconstructed informality over all employed: 67.3 % vs INEI official 70.2 % (2025).
- Informality by firm size in our data vs INEI's 88.6 % (1–10 workers) / 15.6 % (>50).
- Population restriction: 6,500 unpaid family workers (income = 0) excluded → selection
  (only employed with income > 0 are modeled).
- Potential experience = age − schooling − 6.

Design choices already in the app: separation E9 predictive vs E6 explanatory
(Breiman 2001 / Shmueli 2010 style); Duan (1983) smearing; R² of Mincer equations
~0.2–0.4 in the literature.

References ALREADY in `app/referencias.py` (ids): mincer1974, card1999, lemieux2006,
heckman2006, duan1983, belloni2014, athey2019, sohnesen2016, psacharopoulos2018,
yamada2007, inei_informal, oit_17ciet, saito2015, loayza2008, perry2007. Their `nota`
fields are UNVERIFIED this round. The app once attributed to Lemieux and Heckman things
they did not say. Read the file to see each note.

## Non-negotiable verification rules

1. A reference counts as VERIFIED only if you opened it (URL or DOI that resolves,
   via WebFetch/WebSearch/firecrawl/PubMed tools) and read at least the abstract or the
   section that backs the sentence. Record the exact URL you opened.
2. For each verified reference give a SHORT verbatim quote (≤ 40 words) from what you
   read that supports the claim, plus page/section if available.
3. Confirm author(s), year, title, journal/publisher, DOI. If the seed list got any of
   these wrong, say so explicitly.
4. If you cannot open it (paywall 403 with no abstract, no open copy), mark
   `verificado: no` and say why. Never fill gaps from memory. A seed item you cannot
   verify is reported as unverified or discarded — it is fine to have fewer references.
5. `acceso`: `abierto` if the full text is free at the URL you give, `pago` otherwise.
   Prefer open-access versions (author PDF, SSRN, NBER, IZA, RePEc, institutional repos).
6. Never attribute to an author something they did not say. If a paper only
   suggests or finds mixed results, say that.
7. No causal language for our findings («se asocia a», not «causa»). Sensitive
   variables (sex, mother tongue, ethnicity, region) only aggregated, structural-gap framing.

## Output format (return this, in Spanish, as your final message; ≤ 1,800 words)

A. **Referencias** — one block per reference:
   `id sugerido` · cita completa (APA) · DOI · URL abierta · acceso · verificado sí/no ·
   cita textual ≤40 palabras + sección/página · qué dice en 1–2 frases.
B. **Cruces con la app** — for each app finding relevant to your axis: finding →
   what the literature says → coincide / discrepa / no podemos concluir → label
   (hallazgo propio / consistente con la literatura / lectura nuestra) → reference ids.
C. **Descartadas** — seed items or candidates you dropped and why (unverifiable,
   misattributed, wrong year, not relevant).
D. **Errores de la semilla** — corrections to the seed list's author/year/title/journal.

Do NOT edit any file in the repo. Read-only. You may write scratch notes only in
`C:/Users/Usuario/AppData/Local/Temp/claude/C--Users-Usuario-Documents-Portfolio-DespliegueML/9a034c66-a8cd-46ba-b880-9dfb8ace8c33/scratchpad/fase2/`.

## Additional rules (added after review — they override anything above)

8. **Raw text for quotes.** WebFetch returns a model-processed summary, NOT raw page
   text, so a quote taken from it is not verbatim. Take every quote from RAW text:
   `curl -sL <url> -o x.pdf` + `pdftotext` (or Python `pypdf` from the repo venv
   `./.venv/Scripts/python.exe`), `curl` of the HTML, firecrawl scrape (markdown), or
   PubMed full text. Save the raw text you quote from to
   `scratchpad/fase2/raw/<id>.txt` (UTF-8). The main thread will grep every quote in
   its raw file; a quote not found there downgrades the reference to `verificado: no`.
   Copy quotes character for character (keep original language; no ellipsis inside a
   quote — use two shorter quotes instead).
9. **Books: two separate columns.** `metadatos verificados` (publisher/IEP catalog,
   WorldCat, Google Books, library record) and `contenido verificado` (open chapter,
   introduction, or a published review/syllabus text that states the claim, saved to
   raw/). A book with metadata only may be cited for existing and covering a topic,
   never for a specific sentence. Report both columns for every reference (articles too).
10. **Existing refs you OWN.** Your prompt lists the ids from `app/referencias.py` that
    your axis owns. For each: open the source, check `cita`, `url`, `acceso` AND that the
    `nota` (and any app sentence citing it — grep `ref('<id>')` in `app/`) matches what
    the source says. Report: OK / corregir (with the exact fix) / retirar.
11. **Durable output.** Write your FULL result (sections A–D plus section E «Refs
    existentes» when you own any) to `scratchpad/fase2/eje_<N>.md`. Your final message
    to the main thread is only: the path, counts (verified / unverified / discarded),
    and ≤ 10 lines of the most important points.
