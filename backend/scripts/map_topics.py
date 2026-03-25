import json
import os

TOPIC_MAPPING = {
    # Grade 5
    "Pakartojame": "skaiciai/naturalieji",
    "1. Natūralieji skaičiai ir dešimtainė skaičiavimo sistema": "skaiciai/naturalieji",
    "2. Veiksmai su natūraliaisiais skaičiais": "skaiciai/naturalieji",
    "3. Natūraliųjų skaičių palyginimas": "skaiciai/naturalieji",
    "4. Natūraliųjų skaičių apvalinimas": "skaiciai/naturalieji",
    "5. Romėniškaisiais skaitmenimis rašomi skaičiai": "skaiciai/naturalieji",
    "6. Dalumo požymiai": "skaiciai/dalumas",
    "9. Perstatomumo, jungiamumo ir skirstomumo dėsniai": "skaiciai/veiksmu_tvarka",
    "10. Skaičiaus skaidymas pirminiais daugikliais": "skaiciai/dalumas",
    "4. Trupmenų sudėtis ir atimtis": "skaiciai/trupmenos",
    "5. Mišriųjų skaičių sudėtis ir atimtis": "skaiciai/trupmenos",
    "6. Natūraliojo skaičiaus daugyba iš trupmenos arba mišriojo skaičiaus": "skaiciai/trupmenos",
    "7. Veiksmų su trupmenomis dėsniai": "skaiciai/veiksmu_tvarka",
    "1. Dešimtainiai skaičiai": "skaiciai/trupmenos",
    "2. Dešimtainių skaičių palyginimas, apvalinimas": "skaiciai/trupmenos",
    "3. Procentai": "skaiciai/procentai",
    "4. Veiksmai su dešimtainiais skaičiais": "skaiciai/trupmenos",
    "5. Dalies ir visumos radimas": "skaiciai/procentai",
    "1. Skaičių sekos": "algebra/sekos",
    "2. Raidiniai reiškiniai": "algebra/reiskiniai",
    "3. Raidinio reiškinio prastinimas": "algebra/reiskiniai",
    "1. Simetriškos figūros": "geometrija/transformacijos",
    "2. Simetriškų figūrų atkūri mas, užbaigimas": "geometrija/transformacijos",
    "3. Figūrų transformacijos": "geometrija/transformacijos",
    "1. Ilgio matavimo vienetai": "geometrija/matavimo_vienetai",
    "2. Ploto matavimo vienetai": "geometrija/matavimo_vienetai",
    "3. Kampų rūšys. Kampų matavimas": "geometrija/kampai",
    "4. Trikampio kampų suma": "geometrija/trikampiai",
    "5. Kvadrato ir stačiakampio perimetro ir ploto formulės": "geometrija/perimetras_plotas",
    "8. Plokščiųjų figūrų pertvarkymas": "geometrija/transformacijos",
    "9. Teiginių pagrindimas ir matematinis įrodymas": "KITA", # praleidziame
    "5. Stačiakampio gretasienio paviršiaus plotas ir tūris": "geometrija/turis",
    "6. Sudėtingesnių erdvinių figūrų paviršiaus plotas ir tūris": "geometrija/turis",
    "1. Stochastinis bandymas": "tikimybes/atsitiktiniai_ivykiai",
    "2. Bandymai, kurių baigtys vienodai arba nevienodai galimos": "tikimybes/atsitiktiniai_ivykiai",
    "3. Bandymo baigties tikimybė": "tikimybes/atsitiktiniai_ivykiai",
    
    # Grade 8
    "1.1. Kvadratinė šaknis": "skaiciai/saknys",
    "1.2. Kubinė šaknis": "skaiciai/saknys",
    "1.3. Iracionalieji skaičiai": "skaiciai/saknys",
    "1.4. Palyginame": "skaiciai/saknys",
    "1.5. Sudedame ir atimame": "skaiciai/saknys",
    "1.6. Šaknis iš sandaugos": "skaiciai/saknys",
    "1.7. Šaknis iš trupmenos": "skaiciai/saknys",
    "1.8. Iškeliame prieš šaknies ženklą, įkeliame į pošaknį": "skaiciai/saknys",
    "1.9. Skaitinių reiškinių su šaknimis pertvarkiai": "skaiciai/saknys",
    "1.10. Raidinių reiškinių su šaknimis pertvarkiai": "skaiciai/saknys",
    "2.1. Skaičių aibės": "skaiciai/sveikieji",
    "2.2. Skaičių aibės poaibis": "skaiciai/sveikieji",
    "2.3. Realieji skaičiai": "skaiciai/sveikieji",
    "2.4. Veiksmai su realiaisiais skaičiais": "skaiciai/sveikieji",
    "3.1. Valiutų kursai": "tikimybes/finansiniai",
    "3.2. Paprastosios ir sudėtinės palūkanos": "tikimybes/finansiniai",
    "3.3. Paprastosios palūkanos ir grafikai": "tikimybes/finansiniai",
    "3.4. Pirkimas išsimokėtinai": "tikimybes/finansiniai",
    "3.5. Mažėjančiosios palūkanos": "tikimybes/finansiniai",
    "4.1. Vienanaris ir daugianaris": "algebra/daugianariai",
    "4.2. Atskliautimas": "algebra/daugianariai",
    "4.3. Daugianarių daugyba": "algebra/daugianariai",
    "4.4. Dvinario kėlimas kvadratu": "algebra/daugianariai",
    "4.5. Dviejų narių sumos dauginimas iš tų narių skirtumo": "algebra/daugianariai",
    "4.6. Bendrojo dauginamojo iškėlimas prieš skliaustus": "algebra/daugianariai",
    "4.7. Skaidymas dauginamaisiais grupavimo būdu": "algebra/daugianariai",
    "4.8. Skaidymas dauginamaisiais taikant greitosios daugybos formules": "algebra/daugianariai",
    "5.1. Tiesinė lygtis su dviem nežinomaisiais": "algebra/tiesines_lygtys",
    "5.2. Tiesinės lygties su dviem nežinomaisiais grafikas": "funkcijos/grafikai",
    "5.3. Tiesinių lygčių su dviem nežinomaisiais sistema": "algebra/lygtys_sistemos",
    "5.4. Tiesinių lygčių sistemos sprendinių skaičius": "algebra/lygtys_sistemos",
    "5.5. Sprendžiame tiesinių lygčių sistemas keitimo būdu": "algebra/lygtys_sistemos",
    "5.6. Sprendžiame tiesinių lygčių sistemas sulyginimo būdu": "algebra/lygtys_sistemos",
    "5.7. Sprendžiame tiesinių lygčių sistemas sudėties būdu": "algebra/lygtys_sistemos",
    "5.8. Judėjimo uždaviniai": "tikimybes/judejimo_uzdaviniai",
    "5.9. Įvairūs tekstiniai uždaviniai": "tikimybes/judejimo_uzdaviniai",
    "6.1. Vektoriaus sąvoka": "geometrija/trikampiai", # vektoriams nera tiesiogines srities
    "6.2. Vektorių lygumas": "geometrija/trikampiai",
    "6.3. Vektorių sudėtis": "geometrija/trikampiai",
    "6.4. Vektorių atimtis": "geometrija/trikampiai",
    "6.5. Vektoriaus daugyba iš skaičiaus": "geometrija/trikampiai",
    "7.1. Pitagoro teorema": "geometrija/trikampiai",
    "7.2. Atvirkštinė Pitagoro teorema": "geometrija/trikampiai",
    "7.3. Atstumas tarp dviejų koordinačių plokštumos taškų": "geometrija/koordinates",
    "7.4. Stačiojo trikampio statinis, esantis prieš 30° kampą": "geometrija/trikampiai",
    "7.5. Lygiašonis ir lygiakraštis trikampiai": "geometrija/trikampiai",
    "7.6. Trikampio vidurio linija": "geometrija/trikampiai",
    "7.7. Trapecijos vidurio linija": "geometrija/keturkampiai",
    "8.1. Stačioji prizmė": "geometrija/erdvines_figuros",
    "8.2. Taisyklingoji piramidė": "geometrija/erdvines_figuros",
    "8.3. Ritinys": "geometrija/erdvines_figuros",
    "8.4. Kūgis": "geometrija/erdvines_figuros",
    "8.5. Rutulys ir sfera": "geometrija/erdvines_figuros",
    "9.1. Empirinis skirstinys": "statistika/duomenu_rinkimas",
    "9.2. Sukauptasis ir sukauptasis santykinis dažniai": "statistika/duomenu_rinkimas",
    "9.3. Histograma": "statistika/diagramos",
    "9.4. Empirinio skirstinio tankis": "statistika/duomenu_rinkimas",
    "9.5. Imties skaitinės charakteristikos": "statistika/vidurkis_mediana_moda",
    "9.6. Kvartiliai": "statistika/vidurkis_mediana_moda",
    "9.7. Stačiakampė diagrama su „ūsais“": "statistika/diagramos"
}

def map_topics(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for cycle in data:
        for topic in cycle["topics"]:
            name = topic["name"]
            if name in TOPIC_MAPPING:
                mapped = TOPIC_MAPPING[name]
                if mapped != "KITA":
                    area, subtopic = mapped.split('/')
                    topic["global_area"] = area
                    topic["global_subtopic"] = subtopic
            else:
                # Some generic topics like "Pasitikriname", "Savarankiškas darbas" etc.
                pass
                
    # Filter out empty topics or ones without links if it's not a generic one
    for cycle in data:
        cleaned_topics = []
        for t in cycle["topics"]:
            # Keep topic if it has a global subtopic
            if "global_subtopic" in t:
                cleaned_topics.append(t)
        cycle["topics"] = cleaned_topics

    # filter out empty cycles
    data = [c for c in data if c["topics"]]
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    map_topics(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_5.json")
    map_topics(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8_fixed.json")
    # rename fixed to final
    os.rename(r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8_fixed.json", 
              r"D:\MATEMATIKA 2026_2\Matematikos programa\Atnaujinta\curriculum_8.json")
    print("Mapping complete!")
