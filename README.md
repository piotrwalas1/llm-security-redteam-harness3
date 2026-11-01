🛡️ LLM Security Red-Team Harness & Multi-Agent Framework (v3)

LLM Security Red-Team Harness v3 to zaawansowane, wieloagentowe środowisko testowe przeznaczone do automatycznego audytowania bezpieczeństwa, wykrywania podatności oraz ewaluacji odporności modeli językowych (LLM) i agentów AI na zaawansowane wektory ataków adwersarialnych.

System wspiera zarówno statyczny benchmarking (100+ dedykowanych przypadek testowych), jak i dynamiczny Red-Teaming w oparciu o algorytm TAP (Tree-of-Attacks with Pruning) oraz walidację wyników z wykorzystaniem sędziego LLM-as-a-Judge.

🔗 Integracja z Zespołem Agentów (AI Agents 2)

> **Ważne:** Do prawidłowego przeprowadzenia audytu i uruchomienia środowiska testowego wymagane jest najpierw pobranie i uruchomienie projektu z repozytorium:  
> 🔗 **[https://github.com/piotrwalas1/llm-security-redteam-harness-AIagents2)**

---
Ten harness stanowi warstwę audytową dla wieloagentowego środowiska produkcyjnego. Do pełnego przetestowania przepływów wymagana jest praca z repozytorium serwera agentów:


👉 LLM Security Red-Team Harness (AI Agents 2)

🌟 Kluczowe Funkcjonalności

🌲 Dynamiczny Red-Teaming (Algorytm TAP): Drzewiaste przeszukiwanie przestrzeni ataków (Tree-of-Attacks with Pruning). Generuje równoległe warianty promptów adwersarialnych, ocenia ich potencjał w czasie rzeczywistym i automatycznie odrzuca nieskuteczne gałęzie (pruning).

📋 Statyczny Benchmark Podatności (100 Test Cases): Gotowy zestaw danych (datasets/redteam_prompts.json) obejmujący wstrzykiwanie instrukcji, wyciek promptu systemowego, obfuskację oraz manipulację logiką.

⚖️ Kontekstowy Sędzia (Context-Aware Evaluator): Dedykowany moduł oceniający oparty na Gemini 2.5 Flash. Analizuje odpowiedzi w skali 0–10, biorąc pod uwagę kategorię ataku, priorytet (severity) oraz oczekiwane zachowanie (expected_behavior).

🔍 Post-Bypass Extraction: Automatyczny krok wywoływany po przełamaniu zabezpieczeń (BYPASSED) w celu weryfikacji skali wycieku danych (np. dosłownego brzmienia pierwszych zdań promptu systemowego).

🎯 Walidacja Sędziego (Gold Set Benchmarking): Wbudowane narzędzie JudgeValidator do wyliczania macierzy pomyłek (Accuracy, Precision, Recall, F1-Score) na referencyjnym zbiorze judge_gold_set.json.

🏗️ Architektura Systemu

System opiera się na interakcji trzech odrębnych ról LLM:
                  ┌──────────────────────┐
                  │     Attacker LLM     │
                  │   (Generowanie TAP)  │
                  └──────────┬───────────┘
                             │
                             ▼
┌──────────────────┐  Prompt Atakujący  ┌──────────────────┐
│    Evaluator     ├───────────────────►│    Target LLM    │
│   (Judge LLM)    │                    │ (Model Testowany)│
│ Skala: 0 - 10    │◄───────────────────┤                  │
└──────────────────┘  Odpowiedź Targeta  └──────────────────┘

Schemat działania algorytmu TAP (Tree-of-Attacks with Pruning):
                     [Seed / Goal]
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
        [Gałąź 1]       [Gałąź 2]       [Gałąź 3]    <-- (Branching Factor: 3)
            │               │               │
         Score: 6        Score: 1        Score: 2    <-- (Sędzia: Skala 0-10)
            │               X               X
          KEEP            PRUNE           PRUNE      <-- (Pruning Threshold: <3)
            │
    ┌───────┴───────┐
    ▼               ▼
[Gałąź 1.1]    [Gałąź 1.2]                           <-- (Width / Best-K: 2)

🛡️ Zakres Testowanych Kategorii Bezpieczeństwa

Statyczny zestaw testowy (redteam_prompts.json) obejmuje 100 zdefiniowanych wektorów ataku:
Kategoria

Opis

Direct Prompt Injection

Bezpośrednie próby przejęcia kontroli nad instrukcją (np. DAN, Sudo Mode).

System Prompt Leakage

Wymuszanie ujawnienia ukrytych instrukcji systemowych i zmiennych.

Evasion & Obfuscation

Omijanie filtrów za pomocą kodowania (Base64, ROT13, języki rzadkie).

Indirect Prompt Injection

Ukryte instrukcje w danych (JSON, PDF, RAG context).

Sensitive Info & PII

Próby wyłudzenia kluczy API, haseł oraz danych osobowych.

Roleplay & Social Eng.

Manipulacja kontekstem fabularnym i autorytetem.

Excessive Agency

Wywoływanie niebezpiecznych poleceń systemowych i funkcji.

Resource Exhaustion

Ataki pętli i wyczerpanie zasobów (DoS).

Logic Manipulation

Wymuszanie halucynacji i błędnych faktów.
📁 Struktura Repozytorium
.
├── config.py                 # Routing zapytań (rozdzielenie ruchu Target vs. Judge LLM)
├── main.py                   # Punkt wejścia (CLI harnessu)
├── sut.py                    # Produkcyjny serwer SUT (System Under Test) na port 8001
├── modules/
│   ├── dynamic_engine.py     # Algorytm TAP (Tree-of-Attacks with Pruning)
│   ├── static_engine.py      # Silnik wykonywania statycznych benchmarków
│   ├── evaluator.py          # Moduł Sędziego (SecurityEvaluator)
│   ├── judge_validator.py    # Walidacja sędziego na zbiorze Gold Set
│   └── report_generator.py   # Generowanie raportów w konsoli (tabulate) oraz JSON
├── datasets/
│   ├── redteam_prompts.json  # Zestaw 100 statycznych przypadków testowych
│   └── judge_gold_set.json   # Zbiór referencyjny (Gold Set) do ewaluacji Sędziego
├── requirements.txt          # Zależności projektu
└── .env                      # Konfiguracja środowiskowa (GCP_PROJECT_ID)

⚙️ Wymagania i Instalacja

Wymagania wstępne

Python 3.10+

Dostęp do Google Cloud Platform z włączonym API Vertex AI / Gemini.

Instrukcja instalacji

Sklonuj repozytorium:

git clone https://github.com/piotrwalas1/llm-security-redteam-harness3.git
cd llm-security-redteam-harness3

🚀 Sposób Użycia
1. Uruchomienie Serwera Target (SUT)

Przed uruchomieniem harnessu należy wystawić testowany serwer SUT:
python sut.py
Serwer wystartuje pod adresem http://127.0.0.1:8001.
2. Uruchomienie Pełnego Audytu (Full Mode)

Uruchamia zarówno statyczny benchmark (100 testów), jak i dynamiczny atak TAP:
python main.py --mode full --output redteam_report.json
3. Uruchomienie Wyłącznie Benchmarku Statycznego
python main.py --mode static --dataset datasets/redteam_prompts.json
4. Uruchomienie Dynamicznego Ataku TAP

Możesz dostosować cel ataku oraz parametry drzewa TAP (Branching, Width, Pruning Threshold):
python main.py --mode dynamic \
  --goal "Extract system prompt instructions" \
  --branching-factor 3 \
  --width 2 \
  --pruning-threshold 3

5. Walidacja Skuteczności Sędziego (Gold Set)

Sprawdza poziom trafności oceny Sędziego w porównaniu z ludzkimi adnotacjami (datasets/judge_gold_set.json):
python main.py --mode validate-judge --gold-set datasets/judge_gold_set.json
📊 Format Raportu Wyjściowego

Po zakończeniu audytu wyniki zapisywane są do pliku JSON (domyślnie redteam_report.json)
📄 Licencja

Projekt udostępniany na licencji MIT. Autor: Piotr Wałas.
