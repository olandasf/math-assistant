# 📚 Uždavinių Bazės Valdymo Skriptai

Šie skriptai padeda valdyti matematikos uždavinių bazę - valyti senus, užkrauti naujus iš HuggingFace.

---

## 🗑️ clean_ai_problems.py - Senų Uždavinių Valymas

Ištrina senus AI generuotus uždavinius, kurie dažnai būna prastos kokybės.

### Naudojimas

```bash
# 1. Pirmiausia - DRY RUN (tik parodo ką ištrins)
cd backend
python scripts/clean_ai_problems.py --dry-run

# 2. Ištrinti tik nepatikrintus Gemini uždavinius
python scripts/clean_ai_problems.py --unverified

# 3. Ištrinti visus Gemini uždavinius
python scripts/clean_ai_problems.py

# 4. Ištrinti žemos kokybės (< 0.5)
python scripts/clean_ai_problems.py --quality 0.5

# 5. Rasti dublikatus
python scripts/clean_ai_problems.py --find-duplicates
```

### Parametrai

- `--dry-run` - Tik parodo ką ištrins, bet neištrina (REKOMENDUOJAMA PIRMA)
- `--all-ai` - Ištrina visus AI generuotus (ne tik Gemini)
- `--unverified` - Ištrina tik nepatikrintus
- `--quality N` - Ištrina uždavinius su kokybe < N (default: 0.3)
- `--find-duplicates` - Randa dublikatus pagal klausimo tekstą

### Pavyzdys

```bash
# Saugus būdas - pirma pažiūrėti
python scripts/clean_ai_problems.py --dry-run

# Išvestis:
# ======================================================================
# SENŲ AI UŽDAVINIŲ VALYMAS
# ======================================================================
# Iš viso uždavinių bazėje: 1250
# Ieškoma Gemini AI generuotų uždavinių
# Filtruojama: kokybė < 0.3
#
# Rasta uždavinių trynimui: 87
#
# PAVYZDŽIAI (pirmi 5):
# 1. ID: 123
#    Šaltinis: gemini
#    Klasė: 6-7
#    Sunkumas: medium
#    Patikrintas: False
#    Kokybė: 0.2
#    Klausimas: Iš 6 kg grūdų pagaminama 18 kg miltų...
#
# DRY RUN REŽIMAS - NIEKO NETRINAMA!
# Būtų ištrinta 87 uždavinių iš 1250

# Jei viskas gerai - trinti iš tikrųjų
python scripts/clean_ai_problems.py
```

---

## 📥 load_problems.py - Naujų Uždavinių Užkrovimas

Užkrauna uždavinius iš HuggingFace dataset'ų ir išverčia į lietuvių kalbą.

### Palaikomi šaltiniai

1. **GSM8K** - 8500 žodinių uždavinių (6-8 klasė)
   - Aukštos kokybės
   - Su step-by-step sprendimais
   - Tinka kasdieniam naudojimui

2. **Competition Math** - Olimpiadiniai uždaviniai (10-12 klasė)
   - Sudėtingesni
   - Tinka A lygiui ir olimpiadoms

### Naudojimas

```bash
cd backend

# 1. Pirma patikrinti statistiką
python scripts/load_problems.py stats

# 2. Testuoti vertimą
python scripts/load_problems.py test-translate

# 3. Užkrauti GSM8K (100 uždavinių)
python scripts/load_problems.py gsm8k --limit 100

# 4. Užkrauti daugiau GSM8K (su offset)
python scripts/load_problems.py gsm8k --limit 200 --offset 100

# 5. Užkrauti Competition Math
python scripts/load_problems.py competition --limit 50

# 6. Užkrauti be vertimo (greičiau, bet anglų kalba)
python scripts/load_problems.py gsm8k --limit 100 --no-translate
```

### Parametrai

- `--limit N` - Kiek uždavinių užkrauti (default: 100)
- `--offset N` - Kiek praleisti nuo pradžios (default: 0)
- `--split train|test` - Dataset split (default: train)
- `--no-translate` - Neversti į lietuvių kalbą

### Pavyzdys

```bash
# Užkrauti 100 GSM8K uždavinių
python scripts/load_problems.py gsm8k --limit 100

# Išvestis:
# ======================================================================
# GSM8K UŽKROVIMAS (train)
# ======================================================================
# Limit: 100
# Offset: 0
# Versti: True
#
# HuggingFace Loader statistika:
#   Cache dir: D:\MATEMATIKA 2026_2\backend\data\huggingface_cache
#   Datasets library: True
#   Kešuoti failai:
#     - gsm8k_train.json: 7473 uždavinių
#
# Kraunami uždaviniai...
# [1/100] Verčiamas: Janet's ducks lay 16 eggs...
# [2/100] Verčiamas: A robe takes 2 bolts...
# ...
#
# ======================================================================
# REZULTATAI:
# ======================================================================
#   Užkrauta: 100
#   Išsaugota: 98
#   Praleista: 2 (dublikatai)
#   Klaidos: 0
```

---

## 📊 Statistika

```bash
# Parodyti bazės statistiką
python scripts/load_problems.py stats

# Išvestis:
# ======================================================================
# UŽDAVINIŲ BAZĖS STATISTIKA
# ======================================================================
#
# Iš viso uždavinių: 1250
#
# Pagal šaltinį:
#   gsm8k: 850
#   template: 300
#   competition: 50
#   gemini: 50
#
# Pagal sunkumą:
#   easy: 400
#   medium: 600
#   hard: 200
#   olympiad: 50
#
# Pagal klasę:
#   5 klasė: 150
#   6 klasė: 300
#   7 klasė: 350
#   8 klasė: 250
#   10 klasė: 100
#   11 klasė: 50
#   12 klasė: 50
#
# Patikrinti: 450
# Aktyvūs: 1200
```

---

## 🔄 Tipinis Workflow

### 1. Išvalyti senus AI uždavinius

```bash
# Pirma pažiūrėti ką ištrins
python scripts/clean_ai_problems.py --dry-run

# Jei viskas gerai - trinti
python scripts/clean_ai_problems.py

# Patikrinti statistiką
python scripts/load_problems.py stats
```

### 2. Užkrauti naujus iš GSM8K

```bash
# Testuoti vertimą
python scripts/load_problems.py test-translate

# Užkrauti 200 uždavinių
python scripts/load_problems.py gsm8k --limit 200

# Patikrinti statistiką
python scripts/load_problems.py stats
```

### 3. Užkrauti olimpiadinius

```bash
# Užkrauti 50 Competition Math
python scripts/load_problems.py competition --limit 50

# Patikrinti statistiką
python scripts/load_problems.py stats
```

---

## ⚙️ Reikalavimai

### Python paketai

```bash
# Įdiegti HuggingFace datasets
pip install datasets

# Arba
pip install -r requirements.txt
```

### API raktai

Vertimui reikalingas **Gemini API raktas**:

1. Eikite į https://aistudio.google.com/
2. Sukurkite API raktą
3. Nustatykite programoje (Nustatymai)

Arba `.env` faile:
```env
GEMINI_API_KEY=your_key_here
```

---

## 🐛 Problemų Sprendimas

### "datasets library neįdiegta"

```bash
pip install datasets
```

### "Gemini API raktas nenurodytas"

1. Eikite į programos Nustatymus
2. Įveskite Gemini API raktą
3. Paspauskite "Testuoti ryšį"
4. Išsaugokite

### "Klaida verčiant"

Patikrinkite:
- Ar Gemini API raktas teisingas
- Ar turite interneto ryšį
- Ar neviršijote API limito

### "Dublikatai"

Jei matote daug dublikatų:

```bash
# Rasti dublikatus
python scripts/clean_ai_problems.py --find-duplicates

# Ištrinti (palikti tik vieną)
# TODO: Implementuoti deduplikaciją
```

---

## 📝 Pastabos

1. **Vertimas užtrunka** - ~1-2 sek. per uždavinį
   - 100 uždavinių ≈ 2-3 minutės
   - 500 uždavinių ≈ 10-15 minučių

2. **Kešavimas** - HuggingFace dataset'ai kešuojami lokaliai
   - Pirmas užkrovimas lėtas (parsisiuntimas)
   - Kiti užkrovimai greiti (iš kešo)

3. **Kokybė** - GSM8K uždaviniai aukštos kokybės
   - Visi su sprendimais
   - Visi patikrinti
   - Tinka kasdieniam naudojimui

4. **Variacijos** - Kol kas negeneru ojamos
   - Galima įjungti su `generate_variations=True`
   - Sukuria 2-3 variacijas kiekvienam uždaviniui

---

**Sukurta:** 2026-01-20
**Autorius:** Kiro AI
