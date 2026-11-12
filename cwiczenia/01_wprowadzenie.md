[← Mapa działu](../01_wprowadzenie/README.md) · [Spis treści](../README.md)

# Ćwiczenia: diagnoza środowiska C++

Jeżeli już programujesz, zacznij od przewidywania wyników. Nie instaluj nowego toolchainu tylko po to, aby rozwiązać zadanie; zapisz ograniczenia posiadanego środowiska. Rozwiązania porównuj z własnymi dowodami, a nie wyłącznie z komunikatem kompilatora.

## 1. „Mamy C++23” — co to właściwie potwierdza?

**Wejście:** projekt kompiluje się z `-std=c++23`, lecz nagłówek `<expected>` jest niedostępny. Kolega proponuje zmianę numeru wersji w dokumentacji na C++20. **Oddaj:** diagnozę trzech niezależnych składników środowiska i minimalny eksperyment sprawdzający potrzebną funkcję. Uwzględnij inną bibliotekę standardową używaną z tym samym kompilatorem. **Wskazówka:** opcja parsera nie instaluje nagłówków.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Sprawdź wersję kompilatora, faktycznie wybraną bibliotekę standardową oraz tryb języka. Skompiluj małą jednostkę używającą `std::expected`, a dostępność jego odmiany sprawdź właściwą makrodefinicją funkcji bibliotecznej. Ustal minimalne wspierane środowisko; obniżenie deklarowanego standardu nie naprawia brakującej implementacji. [Reguły: standard i implementacja](../01_wprowadzenie/02_standardy_i_implementacje.md).

</details>

## 2. Klasyfikator awarii budowania

**Wejście:** A: brak średnika po deklaracji klasy; B: funkcja zadeklarowana i wywołana, ale niezdefiniowana; C: program kończy się kodem 2 po błędnym argumencie. **Oddaj:** tabelę etapów i artefaktów, które mogą powstać. Zaznacz różnicę między kompilacją pojedynczego pliku a zbudowaniem programu. **Wskazówka:** obecność pliku obiektowego nie oznacza istnienia kompletnego programu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

A zatrzymuje analizę jednostki translacji, więc poprawny nowy plik obiektowy nie powstaje. B pozwala skompilować wywołanie przy widocznej deklaracji, ale typowo zatrzymuje linkowanie. C przechodzi budowanie; kod zakończenia jest wynikiem wykonania. Stary artefakt na dysku może mylić, dlatego diagnozę wykonuj w czystym katalogu. [Proces budowania](../01_wprowadzenie/05_proces_budowania.md).

</details>

## 3. Dwa pliki bez IDE

**Wejście:** `main.cpp` wywołuje `twice(21)`, `twice.cpp` zawiera definicję, a `twice.hpp` deklarację. **Oddaj:** plan kompilacji do dwóch plików obiektowych, linkowania i ponownego budowania po zmianie samej definicji. Kryterium: wynik 42 oraz brak ponownej kompilacji klienta, gdy publiczna deklaracja się nie zmieniła. **Wskazówka:** nagłówka nie trzeba traktować jak trzeciej jednostki implementacji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Obie jednostki kompiluje się osobno z tymi samymi wymaganiami ABI, następnie łączy ich pliki obiektowe. Zmiana wyłącznie ciała funkcji wymaga przebudowania `twice.cpp` i ponownego linkowania. Zmiana deklaracji wymaga także przebudowania jednostek włączających nagłówek. Zależności nagłówkowe musi śledzić system budowania. [Toolchain](../01_wprowadzenie/03_kompilatory_i_toolchain.md).

</details>

## 4. Przypadkowa akceptacja rozszerzenia

**Wejście:** fragment `int n = read_size(); int data[n];` działa u autora, a drugi kompilator odrzuca deklarację. **Oddaj:** diagnozę przenośności i dwie reprezentacje dla rozmiaru ustalanego podczas wykonania. Obsłuż zero i odrzuć rozmiar ujemny przed konwersją na typ rozmiaru. **Wskazówka:** akceptacja przez jeden kompilator nie ustanawia reguły standardu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Tablica o takim zmiennym rozmiarze jest rozszerzeniem części implementacji, a nie standardową tablicą C++23. Użyj `std::vector<int>` albo własności dynamicznej tablicy przez `std::unique_ptr<int[]>`, dobierając interfejs do potrzeb. Waliduj ujemny wynik i limit zasobów. Włącz tryb ostrzegający o rozszerzeniach. [Granice języka](../01_wprowadzenie/01_czym_jest_cpp.md).

</details>

## 5. Nagłówek działający tylko przypadkiem

**Wejście:** `widget.hpp` używa `std::string`, lecz nie włącza jego nagłówka; działa jedynie po wcześniejszym włączeniu `<iostream>`. **Oddaj:** eksperyment izolujący zależność i minimalną naprawę. Kryterium: jednostka zaczynająca się od `widget.hpp` kompiluje się bez specjalnej kolejności włączeń. **Wskazówka:** tranzytywne udostępnianie deklaracji może zmienić się między bibliotekami.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Utwórz testową jednostkę, której pierwszym i jedynym potrzebnym nagłówkiem projektu jest `widget.hpp`. Dodaj do tego nagłówka bezpośrednie `#include <string>`. Nie dopisuj deklaracji typów standardowych ręcznie do `namespace std`. Samodzielny nagłówek ujawnia własne wymagania i nie obciąża klienta odgadywaniem kolejności. [Budowanie jednostek](../01_wprowadzenie/05_proces_budowania.md).

</details>

## 6. Zgłoszenie „u mnie działa”

**Wejście:** błąd pojawia się tylko w Release na drugim komputerze; otrzymujesz sam zrzut ekranu programu. **Oddaj:** krótką specyfikację odtwarzalnego zgłoszenia oraz eksperyment rozdzielający różnicę konfiguracji od danych. Uwzględnij kod zakończenia, standardowe wyjście i błędy. **Wskazówka:** nazwa IDE nie opisuje konfiguracji kompilacji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Zapisz źródła minimalnego przypadku, dokładne wejście, oczekiwany wynik, polecenia, wersje narzędzi, bibliotekę, architekturę i flagi. Zbuduj te same źródła z identycznym wejściem w Debug oraz Release i porównaj diagnostykę. Różnica wyniku nie dowodzi błędu optymalizatora: może ujawniać naruszenie reguł programu. [Pierwszy powtarzalny program](../01_wprowadzenie/04_pierwszy_program.md).

</details>
