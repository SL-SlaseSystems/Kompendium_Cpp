# Raport modernizacji repozytorium Kompendium_Cpp

Data: 2026-11-12. Docelowy katalog: `/Users/sebastianlarma/Documents/GitHub/Kompendium_Cpp`.

## Zakres wykonanej modernizacji

Punktem wyjścia jest większa wersja kompendium z działami 01–30, a nie wcześniejszy folder ChatGPT. Zachowano nazwy i ścieżki istniejących materiałów. Osiem rozdziałów fundamentów, diagnozę, scenariusze z rozwiązaniami i laboratoria opracowane wcześniej włączono do tej wersji bez zastępowania jej map starszymi plikami.

- Osiem nowych rozdziałów o inicjalizacji, sequencing, arytmetyce, lifetime wyników, silnych typach, generyczności, Unicode i kończeniu pracy kolejki.
- Czternaście przepisanych rozdziałów warsztatowych i produkcyjnych: presety, walidacja danych, pakiety CMake, ABI, pomiary, bisect, testy kontraktowe, klient HTTP, transakcje, shutdown, retry, histogramy, FFI oraz pipeline CI. Ogólne akapity i przykłady z flagami zastąpiono konkretnymi regułami, scenariuszami i ograniczeniami.
- Kompletny indeks 30 działów oraz uzupełnione istniejące mapy pierwszych 13 działów. Brakujące `Projekty.md` łączy trzydzieści istniejących propozycji portfolio.
- 78 dodatkowych zadań z rozwiązaniami, 24 problemy diagnostyczne, ścieżka pogłębienia powiązana z działami 14–30 oraz dwanaście rozszerzeń laboratoriów. Dotychczasowe 30 zestawów ćwiczeń pozostaje dostępne.
- Trzy uruchamiane laboratoria: parser i CLI statystyk, Money oraz ograniczona kolejka. Dołączono presety Debug/Release/UBSan i workflow z macierzą kompilatorów/configuracji.
- Testowalny walidator z rozróżnieniem rozdziałów, map i ćwiczeń, sprawdzaniem indeksów, filtrem działu i metrykami JSON. Poprawiono przyczynę błędnego odrzucania istniejących worksheetów oraz sześciu martwych odsyłaczy do mapy projektów.

## Wyniki kontroli

Metryki pochodzą z pełnego przebiegu `bash scripts/verify.sh --metrics`, z kompilowaniem wszystkich bloków cpp.

| Kontrola lub miara | Wynik |
|---|---:|
| Działy główne | 30 |
| Rozdziały główne / eksperckie | 179 / 15 |
| Rozdziały łącznie | 194 |
| Pliki Markdown poza planami i katalogami budowania | 282 |
| Mapy działów głównych / mapa ekspercka | 30 / 1 |
| Dotychczasowe zestawy ZESTAW-CWICZEN | 30 |
| Bloki cpp sprawdzone składniowo | 417 / 417 |
| Błędy struktury, nawigacji i lokalnych linków | 0 |
| Testy narzędzia walidującego | 36 / 36 |
| Wykonane programy z nowych/zmienionych rozdziałów | 34 / 34 |
| Niezależnie wykonane nowe programy z UBSan | 32 / 32 |
| CTest laboratoriów Debug | 4 / 4 |
| CTest laboratoriów Release | 4 / 4 |
| CTest laboratoriów UBSan, halt_on_error=1 | 4 / 4 |
| Osobna konfiguracja Ninja + CTest | 4 / 4 |

34 programy obejmują 32 nowe lub przepisane przykłady oraz dwa istniejące programy w rozdziale C++26, gdzie zaktualizowano status publikacji. Nie sumuje się tych liczb z 417, ponieważ są to różne kontrole tych samych bloków.

W rzeczywistych testach wieloplikowych zbudowano pakiet Meter, przeniesiono instalację, ukryto źródła i build producenta, a następnie zbudowano niezależnego konsumenta. Osobno sprawdzono przechodnią zależność Threads. Dwa klienty C11 połączono z biblioteką C++23; niezależny przegląd wykonał je również z UBSan oraz przypadkami granic reprezentacji i bufora błędu.

Odtworzono zachowanie dwóch połączeń SQLite w WAL i rollback journal. Próba utworzenia nowego, izolowanego klastra PostgreSQL 16.10 zatrzymała się na `initdb`: `shmget: Operation not permitted`. Serwer nie wystartował; nie dotykano istniejących baz ani usług. Scenariusz PostgreSQL pozostaje zweryfikowany dokumentacyjnie, bez deklaracji wykonania.

Przegląd wykrył trzy fragmenty wieloplikowe błędnie oznaczone jako samowystarczalne cpp oraz niezgodną liczbę w objaśnieniu budżetu HTTP. Oznaczenia i obliczenie poprawiono przed pełnym odbiorem. Żaden celowo niepoprawny blok nie był uruchamiany.

Workflow GitHub Actions dodano jako wykonywalną konfigurację kontroli; nie wykonano push ani zdalnego przebiegu i nie deklaruje się jego wyniku.

## Granice wniosków

Pełna kontrola Markdown kompiluje bloki cpp przez `-fsyntax-only`. Nie jest uruchamianiem wszystkich programów ani testowaniem serwerów, baz i bibliotek zewnętrznych. Nowe pełne przykłady wykonano oddzielnie; SQL, konfiguracje oraz konteksty wieloplikowe mają jawnie opisane wymagania. Lokalny wynik CMake/CTest jest odrębny od zdalnego wykonania workflow GitHub Actions.

ASan zatrzymywał się wcześniej w tym samym środowisku również dla pustego main i poza sandboxem. Nie został uznany za zaliczony. Osobny UBSan jest rzeczywiście wykonywany. Nie przeprowadzono TSan ani testów całego repo na drugim niezależnym toolchainie. Systemowe g++ na tym Macu jest również sterownikiem Apple Clang.

Przepisanie czternastu rozdziałów nie jest deklaracją ponownej recenzji merytorycznej wszystkich historycznych materiałów. Część pozostałych tematów produkcyjnych ma charakter wprowadzenia i wymaga dalszej pracy na rzeczywistych adapterach. Wartość dydaktyczna nie wynika z samej liczby słów ani udanej kompilacji.

## Odtworzenie

~~~text
python3 -m unittest discover -s scripts -p 'test_*.py' -v
bash scripts/verify.sh
python3 scripts/verify_content.py --metadata-only --metrics
cd praktyka
cmake --preset debug
cmake --build --preset debug
ctest --preset debug
~~~

Pozostałe konfiguracje i dobór lokalnego SDK opisują [laboratoria](praktyka/README.md). Środowisko odbioru to Apple Clang 17.0.0, arm64, C++23, libc++, CMake 4.4.3, SDK MacOSX26.0 z Xcode. Prywatnej ścieżki SDK nie zapisano w wersjonowanych presetach.

## Punkt startowy

[Diagnoza](test_diagnostyczny.md) → [pogłębiona ścieżka](sciezka_nauki.md) → [zadania z rozwiązaniami](cwiczenia/README.md) i [laboratoria](praktyka/README.md). Pełny zakres zawiera [główny indeks](README.md).

## Zapis w docelowym folderze

Do wskazanego repozytorium GitHub zapisano 43 nowe i 35 zmienionych plików. Synchronizacja porównała skróty SHA-256 z początkowym stanem i zachowała poprzednie wersje zmienianych plików w katalogu roboczym zadania. Nie usuwano plików i nie modyfikowano historii, indeksu ani konfiguracji Git.

Po zapisie powtórzono w docelowym repo testy walidatora (36/36), kontrolę metadanych (282 pliki, zero błędów) i git diff --check. Laboratoria skompilowano ponownie z rzeczywistych źródeł w katalogu GitHub, w zewnętrznych katalogach budowania: Debug, Release i UBSan po 4/4. Ostatnia uwaga redakcyjna została usunięta przez jawne wskazanie sh/bash w poleceniach git bisect, dzięki czemu nie wymagają wcześniejszego chmod skryptów.
