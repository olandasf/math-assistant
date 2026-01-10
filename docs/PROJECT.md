# 📚 MATEMATIKOS MOKYTOJO ASISTENTAS
## Projekto Aprašymas ir Vizija

---

## 1. PROJEKTO TIKSLAS

Sukurti modernią programinę įrangą, kuri padeda matematikos mokytojams automatizuoti mokinių ranka rašytų kontrolinių darbų tikrinimą, drastiškai sumažinant laiko sąnaudas (nuo ~4 val. iki ~30-60 min. vienai klasei).

---

## 2. PROBLEMOS APRAŠYMAS

| Problema | Dabartinė situacija |
|----------|---------------------|
| **Laiko sąnaudos** | ~4 val. / 30 mokinių kontroliniam |
| **Dažnumas** | 2-3 kontroliniai + 2-3 savarankiški / mėn / klasei |
| **Klasės** | 5 klasės × ~30 mokinių = ~150 mokinių |
| **Lygiai** | 5-6-7-8 (kartais 10) klasės |
| **Rezultatas** | Neliekia laiko šeimai, vaikams |

---

## 3. SPRENDIMAS

Hibridinė sistema, kuri:
1. **Nuskaito** ranka rašytus darbus (OCR + AI)
2. **Atpažįsta** matematinius simbolius, formules, brėžinius
3. **Tikrina** sprendimų teisingumą (matematikos variklis)
4. **Paaiškina** klaidas lietuvių kalba (AI/NLP)
5. **Generuoja** ataskaitas (PDF, statistika)

---

## 4. PAGRINDINIAI VARTOTOJAI

### Pirminis vartotojas
- **Kas:** Matematikos mokytoja
- **Kur:** Lietuviškos mokyklos
- **Kalba:** Lietuvių

### Ateities vartotojai (v2.0+)
- Keli mokytojai
- Administracija (statistikos peržiūra)

---

## 5. FUNKCINIAI REIKALAVIMAI

### 5.1 Mokinių ir klasių valdymas
- [ ] Mokslo metų valdymas (2025-2026, 2026-2027...)
- [ ] Klasių kūrimas (5a, 6b, 7c...)
- [ ] Mokinių importas iš Excel
- [ ] Mokinių unikalus ID (privatumo apsauga)
- [ ] GDPR: vardas/pavardė → ID prieš siunčiant API

### 5.2 Kontrolinių valdymas
- [ ] Kontrolinio sukūrimas (pavadinimas, data, klasė, tema)
- [ ] Dviejų variantų palaikymas (I ir II)
- [ ] Užduočių įvedimas (1, 2, 3... arba 1a, 1b, 1c...)
- [ ] Taškų priskyrimas kiekvienam veiksmui
- [ ] Teisingų atsakymų/sprendimų įvedimas (neprivaloma)

### 5.3 Darbų įkėlimas ir apdorojimas
- [ ] Failų įkėlimas (JPG, PNG, PDF)
- [ ] Kelių puslapių palaikymas
- [ ] Vaizdo gerinimas (kontrastas, ryškumas, triukšmo šalinimas)
- [ ] OCR metodų pasirinkimas (lokalus/hibridinis/pilnas)
- [ ] Progreso indikatorius apdorojimo metu

### 5.4 OCR ir teksto išgavimas
- [ ] MathPix API (pagrindinis matematikai)
- [ ] Google Cloud Vision (papildomas)
- [ ] Tesseract (lokalus backup)
- [ ] EasyOCR (rašysenai)
- [ ] Hibridinis režimas (kelių OCR kombinacija)

### 5.5 Palyginimo langas
- [ ] Originalus vaizdas (kairė pusė)
  - Priartinimas/nutolinimas (zoom)
  - Sukimas (90°, 180°, 270°, laisvas)
  - Slinkimas (pan)
- [ ] Skaitmeninė versija (dešinė pusė)
  - LaTeX renderinimas
  - Redagavimas
  - Sinchronizuotas slinkimas

### 5.6 Matematikos tikrinimas
- [ ] SymPy (simbolinė matematika)
- [ ] NumPy/SciPy (skaičiavimai)
- [ ] WolframAlpha API (sudėtingi atvejai)
- [ ] Tarpinių veiksmų tikrinimas
- [ ] Klaidų identifikavimas

### 5.7 Klaidų aiškinimas
- [ ] Google Gemini / Vertex AI (NLP)
- [ ] Lietuvių kalba
- [ ] Tekstinių uždavinių supratimas
- [ ] Kontekstinis aiškinimas
- [ ] Alternatyvių sprendimų generavimas

### 5.8 Vertinimas
- [ ] Automatinis balų skaičiavimas
- [ ] Procentai → pažymys (91-100%=10, 81-90%=9...)
- [ ] Dalinių balų palaikymas
- [ ] Mokytojo redagavimas

### 5.9 Ataskaitos
- [ ] Individuali PDF ataskaita mokiniui:
  - Kiekvienas uždavinys
  - Mokinio sprendimas
  - Klaidos (pažymėtos raudonai)
  - Teisingi sprendimo variantai
  - Tekstinis paaiškinimas
  - Galutinis įvertinimas
- [ ] Klasės ataskaita:
  - Vidurkis
  - Pasiskirstymas
  - Sunkiausios užduotys
  - Dažniausios klaidos
- [ ] Spausdinimas su pažymėtomis klaidomis

### 5.10 Statistika ir analizė
- [ ] Mokinio progresas per laikotarpį
- [ ] Klasės progresas
- [ ] Temų analizė (sunkios/lengvos)
- [ ] Klaidų šablonai

### 5.11 Papildomos funkcijos
- [ ] Klaidų šablonai (tipinės klaidos → standartiniai paaiškinimai)
- [ ] Komentarų šablonai (dažni komentarai vienu paspaudimu)
- [ ] Greitasis režimas (tik atsakymų tikrinimas)
- [ ] Temų žymėjimas

---

## 6. NEFUNKCINIAI REIKALAVIMAI

### 6.1 Našumas
- Vieno puslapio apdorojimas: < 30 sek
- UI atsakymas: < 100ms
- PDF generavimas: < 5 sek/mokinys

### 6.2 Tikslumas
- OCR tikslumas: > 95% aiškiai rašytiems darbams
- OCR tikslumas: > 85% neaiškiai rašytiems darbams
- Matematikos tikrinimo tikslumas: > 99%

### 6.3 Saugumas
- Duomenų anonimizacija prieš API kvietimus
- Lokali duomenų bazė
- Jokių asmeninių duomenų išorinėse sistemose

### 6.4 Platformos
- Windows 11 (pirminis)
- Ateityje: Linux, macOS, Web

---

## 7. APRIBOJIMAI

### Techniniai
- Nėra dedikuoto GPU (Ryzen 7, 40GB RAM)
- Lokalus OCR bus lėtesnis
- Interneto ryšys reikalingas API

### Biudžetas
- MathPix: ~$0.01-0.05/puslapis
- WolframAlpha: Nemokamas limitas testavimui
- Google Cloud: Nemokamas limitas pradžioje

---

## 8. MATEMATIKOS SRITYS (PILNAS PALAIKYMAS)

### Aritmetika
- Natūralieji skaičiai
- Veiksmai (+, -, ×, ÷)
- Veiksmų eiliškumas
- Dalumas

### Trupmenos
- Paprastosios trupmenos
- Dešimtainės trupmenos
- Veiksmai su trupmenomis
- Suprastinimas
- Palyginimas

### Procentai
- Procento skaičiavimas
- Dalies radimas
- Skaičiaus radimas pagal procentą

### Algebra
- Reiškiniai
- Lygtys (vieno kintamojo)
- Lygčių sistemos
- Nelygybės
- Laipsniai ir šaknys
- Formulės
- Funkcijos (tiesinės, kvadratinės)
- Proporcijos

### Geometrija
- **Plokštumos figūros:**
  - Trikampiai (su kampais, kraštinėmis, aukštinėmis)
  - Keturkampiai (stačiakampiai, kvadratai, rombai, trapecijos)
  - Apskritimai (spindulys, skersmuo, lankas, plotas)
  - Daugiakampiai
- **Koordinačių plokštuma:**
  - Taškai
  - Tiesės
  - Atstumas
- **Erdvinės figūros:**
  - Kubai
  - Stačiakampiai gretasieniai
  - Piramidės
  - Cilindrai
  - Kūgiai
  - Rutuliai
- **Kreivės ir grafikai:**
  - Funkcijų grafikai
  - Duomenų grafikai

### Tekstiniai uždaviniai
- Lietuvių kalba
- Konteksto supratimas
- Pertvarkymas į matematinius veiksmus
- Pilno sprendimo tikrinimas

---

## 9. VERTINIMO SISTEMA

### Balų skaičiavimas
- Kiekvienas veiksmas turi balus
- Daliniai balai už dalinai teisingą sprendimą
- Automatinis sumavimas

### Pažymių skalė
| Procentai | Pažymys |
|-----------|---------|
| 91-100% | 10 |
| 81-90% | 9 |
| 71-80% | 8 |
| 61-70% | 7 |
| 51-60% | 6 |
| 41-50% | 5 |
| 31-40% | 4 |
| 21-30% | 3 |
| 11-20% | 2 |
| 0-10% | 1 |

---

## 10. KONTROLINIŲ STRUKTŪRA

### Tipinis kontrolinis
- 8-12 užduočių
- Du variantai (I ir II)
- Užduotys numeruotos: 1, 2, 3... arba 1a, 1b, 1c...
- Užduoties tekstas tame pačiame lape
- Nuo 1 iki daug puslapių

### Kas tikrinama
- Galutinis atsakymas
- Tarpiniai veiksmai
- Sprendimo logika
- Formulių taikymas

---

## 11. PRIVATUMO APSAUGA (GDPR)

### Anonimizacijos procesas
1. Mokiniui sukuriamas unikalus ID (pvz., `M2026001`)
2. Prieš siunčiant vaizdą į API:
   - Vardas/pavardė pakeičiamas į ID
   - Arba ta sritis užmaskuojama
3. API gauna tik anoniminius duomenis
4. Asmeniniai duomenys lieka tik lokalioje DB

### Duomenų saugojimas
- SQLite lokalioje sistemoje
- Šifravimas at-rest (ateityje)
- Atsarginės kopijos

---

## 12. ATEITIES VIZIJA

### v1.0 (MVP)
- Vienas vartotojas
- Lokalus veikimas
- Pagrindinės funkcijos

### v2.0
- Keli vartotojai
- Prisijungimo sistema
- Serveris/konteineris

### v3.0
- Web versija
- Mokyklos administracija
- Integracija su e-dienynu

---

## 13. PROJEKTO KOMANDA

| Rolė | Kas |
|------|-----|
| Projekto savininkas | Jūs |
| Galutinis vartotojas | Žmona (matematikos mokytoja) |
| Programuotojas | AI asistentas (GitHub Copilot) |

---

## 14. SĖKMĖS KRITERIJAI

1. ✅ Laiko sutaupymas: 4 val → < 1 val
2. ✅ Tikslumas: > 95% teisingai atpažintų darbų
3. ✅ Naudojimo paprastumas: mokytoja gali naudoti be IT pagalbos
4. ✅ Lietuvių kalba: 100% UI ir paaiškinimai
5. ✅ Patikimumas: programa nestringa, nepranda duomenų

---

**Dokumentas sukurtas:** 2026-01-10
**Paskutinis atnaujinimas:** 2026-01-10
**Versija:** 1.0
