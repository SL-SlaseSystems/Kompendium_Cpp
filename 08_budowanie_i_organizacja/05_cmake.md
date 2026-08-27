[← Spis treści](../README.md)

# CMake

CMake nie jest kompilatorem ani częścią standardu C++. Generuje lub steruje systemem budowania i opisuje zależności między targetami. Współczesny styl jest target-oriented: wymagania kompilacji, include paths, definicje i biblioteki przypisuje się do konkretnego targetu, a nie globalnego stanu katalogu.

~~~text
cmake_minimum_required(VERSION 3.28)
project(example LANGUAGES CXX)

add_library(core src/core.cpp)
target_include_directories(core PUBLIC include)
target_compile_features(core PUBLIC cxx_std_23)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE core)

include(CTest)
add_test(NAME app_runs COMMAND app)
~~~

`PUBLIC`, `PRIVATE` i `INTERFACE` opisują propagację usage requirements. Jeśli publiczny nagłówek `core` wymaga C++23 i katalogu `include`, klient targetu powinien odziedziczyć te wymagania. Flagi ostrzeżeń zależne od kompilatora zwykle przypisuje się prywatnie i warunkowo.

Konfiguracja out-of-source oddziela artefakty od źródeł:

~~~text
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
ctest --test-dir build --output-on-failure
~~~

Generatory wielokonfiguracyjne, np. Visual Studio i Xcode, wybierają konfigurację przy budowaniu, więc `CMAKE_BUILD_TYPE` może nie mieć zastosowania. Presets pozwalają zapisać powtarzalne warianty w repozytorium projektu.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „CMake”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Nowoczesny CMake opisuje wymagania targetów przez właściwości `PRIVATE`, `PUBLIC` i `INTERFACE`. Globalne flagi i katalogowe include paths ukrywają zależności, utrudniając ponowne użycie oraz instalację pakietu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „CMake” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: CMake
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „CMake”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Pułapki

Nie używaj globalnego `include_directories` i `add_definitions`, jeśli właściwość należy do jednego targetu. Nie wstawiaj bezwarunkowo flag GCC do MSVC. Nie pobieraj zależności podczas każdego builda bez kontroli wersji i trybu offline. Minimalna wersja CMake powinna wynikać z używanych funkcji, nie z przypadkowej instalacji autora.

## Powiązane tematy

- [Proces budowania](../01_wprowadzenie/05_proces_budowania.md)
- [Conan, vcpkg i zależności](06_conan_vcpkg_i_zaleznosci.md)
- [Moduły C++](04_moduly_cpp.md)

