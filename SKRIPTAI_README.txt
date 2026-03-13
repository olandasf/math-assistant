╔══════════════════════════════════════════════════════════════════════════════╗
║                    MATEMATIKOS MOKYTOJO ASISTENTAS                           ║
║                         Paleidimo skriptai                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
                         📋 VISI SKRIPTAI
═══════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────────────┐
│ SETUP.bat                                                                    │
│ Pirminis nustatymas (tik pirmą kartą)                                       │
│                                                                              │
│ Ką daro:                                                                     │
│ • Tikrina Python ir Node.js                                                 │
│ • Sukuria .env failą                                                         │
│ • Įdiegia backend priklausomybes (Python venv)                              │
│ • Įdiegia frontend priklausomybes (npm)                                     │
│ • Inicializuoja duomenų bazę                                                │
│                                                                              │
│ Kada naudoti:                                                                │
│ • Pirmą kartą įdiegiant                                                      │
│ • Po Python/Node.js atnaujinimų                                              │
│ • Po priklausomybių atnaujinimų                                              │
│                                                                              │
│ Trukmė: 5-10 minučių                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ START.bat                                                                    │
│ Paleisti sistemą                                                             │
│                                                                              │
│ Ką daro:                                                                     │
│ • Tikrina priklausomybes                                                     │
│ • Sustabdo senus procesus                                                    │
│ • Paleidžia backend serverį (port 8000)                                      │
│ • Paleidžia frontend serverį (port 5173)                                     │
│ • Atidaro naršyklę                                                           │
│                                                                              │
│ Kada naudoti:                                                                │
│ • Kiekvieną kartą norint naudoti sistemą                                     │
│                                                                              │
│ Trukmė: 30-60 sekundžių                                                      │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ STOP.bat                                                                     │
│ Sustabdyti sistemą                                                           │
│                                                                              │
│ Ką daro:                                                                     │
│ • Sustabdo backend serverį                                                   │
│ • Sustabdo frontend serverį                                                  │
│ • Uždaro serverių langus                                                     │
│ • Ištrina laikinus failus                                                    │
│                                                                              │
│ Kada naudoti:                                                                │
│ • Norint sustabdyti sistemą                                                  │
│ • Prieš kompiuterio išjungimą                                                │
│                                                                              │
│ Trukmė: 2-5 sekundės                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ CHECK.bat                                                                    │
│ Patikrinti sistemą                                                           │
│                                                                              │
│ Ką daro:                                                                     │
│ • Tikrina Python, Node.js, npm                                               │
│ • Tikrina failus ir katalogus                                                │
│ • Tikrina backend priklausomybes                                             │
│ • Tikrina frontend priklausomybes                                            │
│ • Tikrina portus                                                             │
│ • Parodo problemas jei yra                                                   │
│                                                                              │
│ Kada naudoti:                                                                │
│ • Jei kažkas neveikia                                                        │
│ • Po SETUP.bat paleidimo                                                     │
│ • Norint patikrinti ar viskas gerai                                          │
│                                                                              │
│ Trukmė: 5-10 sekundžių                                                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ LOGS.bat                                                                     │
│ Atidaryti logų katalogą                                                      │
│                                                                              │
│ Ką daro:                                                                     │
│ • Atidaro backend/logs/ katalogą                                             │
│ • Parodo naujausią log failą                                                 │
│ • Gali atidaryti log failą Notepad                                           │
│                                                                              │
│ Kada naudoti:                                                                │
│ • Norint peržiūrėti sistemos logus                                           │
│ • Ieškant klaidų                                                             │
│ • Debugging                                                                  │
│                                                                              │
│ Trukmė: 1-2 sekundės                                                         │
└──────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                         🔄 TIPINIAI SCENARIJAI
═══════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────────────┐
│ PIRMĄ KARTĄ NAUDOJANT                                                        │
│                                                                              │
│ 1. SETUP.bat    ← Pirminis nustatymas (5-10 min)                            │
│ 2. CHECK.bat    ← Patikrinti ar viskas gerai                                │
│ 3. START.bat    ← Paleisti sistemą                                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ KASDIENINIS NAUDOJIMAS                                                       │
│                                                                              │
│ 1. START.bat    ← Paleisti                                                  │
│    ... dirbti su sistema ...                                                │
│ 2. STOP.bat     ← Sustabdyti                                                │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PO ATNAUJINIMŲ                                                               │
│                                                                              │
│ 1. STOP.bat     ← Sustabdyti seną versiją                                   │
│ 2. SETUP.bat    ← Atnaujinti priklausomybes                                 │
│ 3. CHECK.bat    ← Patikrinti                                                │
│ 4. START.bat    ← Paleisti naują versiją                                    │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ JEI KAŽKAS NEVEIKIA                                                          │
│                                                                              │
│ 1. STOP.bat     ← Sustabdyti                                                │
│ 2. CHECK.bat    ← Patikrinti problemas                                      │
│ 3. SETUP.bat    ← Bandyti pataisyti                                         │
│ 4. CHECK.bat    ← Patikrinti ar pataisyta                                   │
│ 5. START.bat    ← Paleisti                                                  │
│                                                                              │
│ Jei vis tiek neveikia:                                                       │
│ - LOGS.bat      ← Peržiūrėti logus                                          │
│ - Kreipkitės pagalbos                                                        │
└──────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                         📚 PAPILDOMA INFORMACIJA
═══════════════════════════════════════════════════════════════════════════════

DOKUMENTACIJA:
• GREITAS_STARTAS.txt      - Trumpa instrukcija
• NAUDOJIMO_INSTRUKCIJA.txt - Išsami instrukcija
• README.md                 - Projekto aprašymas
• docs/SCRIPTS.md           - Skriptų dokumentacija

PORTAI:
• Backend:  http://localhost:8000
• Frontend: http://localhost:5173
• API Docs: http://localhost:8000/docs

LOGAI:
• Backend: backend/logs/app_YYYY-MM-DD.log
• Frontend: Frontend Server lange

REIKALAVIMAI:
• Python 3.11+  - https://www.python.org/downloads/
• Node.js 18+   - https://nodejs.org/

API RAKTAI:
• Google Gemini - https://aistudio.google.com/ (BŪTINA)
• WolframAlpha  - https://developer.wolframalpha.com/ (pasirinktinai)

═══════════════════════════════════════════════════════════════════════════════

Sėkmės naudojant Matematikos Mokytojo Asistentą! 📐✨
