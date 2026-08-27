# Raport końcowy rozbudowy kompendium C++

Data odbioru: 2026-08-27

## Zakres

Projekt zawiera jeden polskojęzyczny podręcznik współczesnego C++:

- 13 kategorii głównej ścieżki;
- 73 rozdziały główne;
- 15 rozdziałów eksperckich w katalogu `zaawansowane`;
- 88 rozdziałów i 59 251 słów prozy poza blokami kodu;
- 48 763 słowa w głównej ścieżce i 10 488 w części eksperckiej;
- 2 327 słów w słowniku, ściądze, przewodniku dalszej nauki i źródłach;
- łącznie 61 578 słów materiału edukacyjnego;
- 183 bloki przykładów w rozdziałach, w tym 83 samowystarczalne bloki `cpp`, 97 scenariuszy `text` i 3 kontrolowane bloki `cpp,notest`.

Każdy rozdział główny oraz ekspercki zawiera model krok po kroku, pogłębienie właściwych pojęć, drugi przykład i porównanie decyzji projektowych. Nazwy i ścieżki istniejących plików zostały zachowane.

## Środowisko odbioru

- standard przykładów: C++23;
- kompilator: Apple Clang 17.0.0;
- tryb kontroli: `-std=c++23 -Wall -Wextra -Wpedantic -fsyntax-only`;
- aktualny standard ISO: C++23, ISO/IEC 14882:2024(E);
- materiał C++26 sprawdzony względem publicznego draftu WG21 N5054 dostępnego 2026-08-27;
- repozytorium Git: nie utworzono i nie używano.

## Wyniki kontroli

- Testy zachowania walidatora: 3 zaliczone, 0 niezaliczonych.
- Pliki Markdown objęte końcowym walidatorem po dodaniu raportu: 96.
- Przykłady C++23 kompilowane przez walidator: 91.
- Rozdziały główne spełniające minimum 500 słów: 73/73.
- Rozdziały eksperckie spełniające minimum 650 słów: 15/15.
- Rozdziały posiadające cztery sekcje pogłębienia i co najmniej dwa bloki przykładów: 88/88.
- Rozdziały nieobecne w głównym README: 0.
- Brakujące cele linków lokalnych: 0.
- Katalogi `.git`, `node_modules` i pliki `package.json`: 0.

Kontrola przekrojowa objęła rozdział z każdej z trzynastu kategorii, cztery materiały eksperckie oraz wszystkie materiały przekrojowe. Sprawdzono rozdzielenie gwarancji standardu od ABI i szczegółów implementacji, poprawność modeli ownership i lifetime, decyzje dotyczące RAII, generyczności, współbieżności oraz wydajności.

## Uruchomienie kontroli

Z katalogu głównego projektu:

~~~text
python3 -m unittest scripts/test_verify.py -v
bash scripts/verify.sh
~~~

Pierwsze polecenie sprawdza, czy walidator rzeczywiście odrzuca zbyt krótki lub niekompletny rozdział. Drugie kontroluje dokumenty, linki, wymagane sekcje, liczbę przykładów i kompiluje samowystarczalne bloki C++23.

## Ograniczenia

- Walidator kompiluje przykłady przez `-fsyntax-only`, ale ich nie uruchamia. Zachowanie runtime wymaga testów i właściwych sanitizerów.
- Bloki `cpp,notest` przedstawiają funkcje C++26, kod platformowy albo kontrolowany przypadek niebezpieczny i nie są kompilowane automatycznie.
- Wynik jednego kompilatora nie dowodzi przenośności ABI ani zachowania kodu zawierającego undefined behavior.
- Status implementacji C++26 należy ponownie sprawdzić przed użyciem funkcji w projekcie produkcyjnym.

## Punkt wejścia

Pełny indeks znajduje się w [README](README.md), skrót w [ściądze](sciaga.md), definicje w [słowniku](slownik.md), a źródła dalszej weryfikacji w [bibliografii](zrodla.md).
