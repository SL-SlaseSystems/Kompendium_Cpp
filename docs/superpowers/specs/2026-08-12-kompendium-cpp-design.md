# Kompendium języka C++ — projekt

Data: 2026-08-12

## Cel

Powstanie samodzielny, polskojęzyczny projekt dokumentacyjny prowadzący od pierwszego programu w C++ do zagadnień eksperckich. Materiał ma jednocześnie działać jak podręcznik czytany po kolei i jak kompendium, w którym można szybko odnaleźć konkretny mechanizm.

Projekt będzie zawierał zwykłe pliki Markdown z opisowym tekstem i przykładami kodu osadzonymi bezpośrednio w rozdziałach. Nie powstaną osobne projekty demonstracyjne, generator strony ani repozytorium Git.

## Podstawa językowa i status standardów

Główną bazą materiału będzie opublikowany standard C++23, formalnie ISO/IEC 14882:2024. Starsze mechanizmy pozostające częścią współczesnego C++ zostaną opisane w kontekście ich obecnego, zalecanego użycia. Elementy C++26 będą wydzielone lub jednoznacznie oznaczone jako należące do nowszego standardu i potencjalnie nieobecne jeszcze we wszystkich kompilatorach.

Kod będzie domyślnie sprawdzany jako C++23 za pomocą lokalnego `clang++`. Fragmenty zależne od niezaimplementowanych funkcji biblioteki, konkretnego systemu operacyjnego, zewnętrznej biblioteki albo C++26 otrzymają wyraźne oznaczenie i nie będą udawały przenośnych przykładów C++23.

## Rozważone warianty

### Wariant wybrany: podział tematyczny

Numerowane katalogi wyznaczają kolejność nauki, a każdy plik odpowiada jednemu zagadnieniu. Informacje o wersjach standardu znajdują się przy omawianej funkcji. Taki układ najlepiej łączy naukę od zera z funkcją referencyjną i odpowiada strukturze kompendium Rusta.

### Wariant odrzucony: jeden duży podręcznik

Jeden plik byłby łatwy do przeszukiwania, ale trudny w nawigacji, utrzymaniu i testowaniu. Przy objętości obejmującej cały język oraz bibliotekę standardową stałby się nieporęczny.

### Wariant odrzucony: osobne książki C++11, C++14, C++17, C++20 i C++23

Ułatwiłby analizę historii języka, ale prowadziłby do dużych powtórzeń i utrudniał naukę współczesnych praktyk. Historia standardów pozostanie osobnym przekrojem, a nie podstawową osią organizacji.

## Architektura informacji

Główny `README.md` będzie zawierał kompletny spis treści, legendę oznaczeń i trzy ścieżki: naukę od zera, szybkie przejście dla doświadczonego programisty oraz ścieżkę ekspercką. Numerowane katalogi obejmą kolejno:

1. wprowadzenie, kompilatory i pierwszy program;
2. składnię, typy podstawowe, wyrażenia i sterowanie przepływem;
3. pamięć, czas życia obiektów, RAII, wskaźniki i semantykę przenoszenia;
4. klasy, model obiektowy, przeciążanie, dziedziczenie i polimorfizm;
5. szablony, dedukcję, concepts i metaprogramowanie;
6. bibliotekę standardową, kontenery, iteratory, algorytmy i ranges;
7. błędy, wyjątki, `noexcept`, `optional`, `variant` i `expected`;
8. preprocesor, nagłówki, ODR, moduły, kompilację, CMake i zależności;
9. testowanie, diagnostykę, sanitizery, analizę statyczną i profilowanie;
10. współbieżność, synchronizację, atomiki i zadania asynchroniczne;
11. I/O, system plików, tekst, czas, liczby losowe i granice biblioteki standardowej;
12. korutyny, moduły oraz ewolucję C++11–C++23;
13. idiomy, projektowanie API, architekturę i wydajność.

Osobny katalog `zaawansowane` obejmie co najmniej:

- undefined behavior, model pamięci, czas życia i pointer provenance;
- layout, alignment, padding, triviality i reguły reprezentacji;
- własne alokatory, `std::pmr` i przeciążanie `new`/`delete`;
- SFINAE, dependent names, two-phase lookup i zaawansowaną dedukcję;
- concepts, constraint normalization i subsumption;
- `constexpr`, `consteval` i metaprogramowanie;
- overload resolution, ADL i hidden friends;
- value categories, forwarding references, perfect forwarding i copy elision;
- type erasure, vtables, ABI i symbol visibility;
- memory ordering, lock-free, ABA i reclamation;
- mechanikę korutyn, promise types i awaitery;
- ODR, moduły, FFI i interoperacyjność z C;
- SIMD, wektoryzację, lokalność cache i diagnostykę optymalizacji;
- status C++26 i feature-test macros.

Materiały przekrojowe to `slownik.md`, `sciaga.md`, `dalsza_nauka.md`, `zrodla.md` i `CONTRIBUTING.md`.

## Format rozdziału

Każdy zwykły rozdział zaczyna się łączem do głównego spisu treści i zawiera, jeśli ma to zastosowanie:

1. intuicję oraz cel mechanizmu;
2. precyzyjne reguły języka lub biblioteki;
3. samowystarczalny przykład;
4. omówienie wyniku i zachowania;
5. typowe pułapki, w tym ryzyko UB;
6. dobre praktyki współczesnego C++;
7. informację o wersji standardu lub zależności zewnętrznej;
8. sekcję „Powiązane tematy”.

Tekst będzie standardowo opisowy. Tabele będą używane tylko tam, gdzie rzeczywiście upraszczają porównanie, na przykład kategorii czasu przechowywania, kontenerów lub memory ordering.

## Przykłady kodu

Bloki `cpp` mają być możliwie samowystarczalne i kompilowane z ostrzeżeniami. Przykłady celowo błędne, pseudokod, fragmenty zależne od bibliotek zewnętrznych oraz kod demonstrujący UB bez wykonywania otrzymają osobne oznaczenie tekstowe.

Walidator wyodrębni testowalne bloki C++ do katalogu tymczasowego, skompiluje je poleceniem odpowiadającym `clang++ -std=c++23 -Wall -Wextra -Wpedantic`, a następnie usunie pliki tymczasowe. Dodatkowo sprawdzi puste pliki, niedomknięte ogrodzenia kodu, martwe linki lokalne, łącza powrotne i wymagane sekcje nawigacyjne.

Nie każdy fragment powinien być uruchamiany. Kod sieciowy, wątki bez deterministycznego wyniku, celowe wyjątki, operacje systemowe i demonstracje UB będą co najwyżej kompilowane lub oznaczone jako nietestowalne.

## Zakres merytoryczny

Kompendium obejmie zarówno core language, jak i najważniejszą część biblioteki standardowej. Uwzględni ręczne zarządzanie pamięcią, ale będzie konsekwentnie promować RAII, typy wartościowe, standardowe kontenery i smart pointery zamiast surowego `new`/`delete` w kodzie aplikacyjnym.

Tematy ekosystemowe, takie jak CMake, Conan, vcpkg, Catch2, GoogleTest, Boost.Asio czy biblioteki serializacji, będą przedstawione jako narzędzia spoza standardu. Kompendium wyjaśni ich rolę, ale nie będzie udawać, że są częścią ISO C++.

Sieci i serializacja zostaną opisane na poziomie modeli i praktyk z wyraźną informacją, że C++23 nie dostarcza kompletnej standardowej biblioteki sieciowej ani uniwersalnego formatu serializacji.

## Dokładność i terminologia

Podstawą merytoryczną będą opublikowany standard C++23, publiczny working draft WG21, dokumenty WG21, C++ Core Guidelines oraz oficjalne instrukcje kompilatorów i narzędzi. `cppreference` może pełnić rolę wygodnego indeksu pomocniczego, ale nie będzie traktowane jako norma.

Polskie terminy będą podawane razem z angielskimi odpowiednikami przy pierwszym użyciu. W miejscach, gdzie polskie tłumaczenie jest nienaturalne lub niejednoznaczne, zachowany zostanie rozpowszechniony termin angielski z objaśnieniem.

Stwierdzenia dotyczące zachowania implementacyjnie zdefiniowanego, unspecified, indeterminate, erroneous i undefined będą rozróżniane. Materiał nie będzie upraszczał „kompiluje się” do „jest poprawne”.

## Kryteria odbioru

Projekt jest ukończony, gdy:

- wszystkie zaplanowane rozdziały istnieją i zawierają rzeczywistą treść;
- główny indeks prowadzi do każdego materiału użytkowego;
- folder zaawansowany ma własną mapę i wymagania wstępne;
- każdy rozdział ma link powrotny i sekcję tematów powiązanych;
- testowalne przykłady przechodzą lokalny kompilator w trybie C++23;
- lokalne linki, bloki kodu i pliki przechodzą walidator;
- C++23, C++26, rozszerzenia kompilatora i biblioteki zewnętrzne są rozróżnione;
- nie ma placeholderów ani pustych szkieletów;
- projekt nie zawiera `.git` ani osobnych projektów demonstracyjnych.

