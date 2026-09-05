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

Polecenie z `-S` i `-B` uruchamia konfigurację: CMake czyta projekt, identyfikuje kompilator, wykonuje testy konfiguracji i zapisuje cache w katalogu budowania. Następnie generuje reguły dla wybranego backendu, np. Ninja. `cmake --build` uruchamia właściwe narzędzie budujące, a nie ponownie ręcznie wybraną listę komend kompilatora. `ctest` wykonuje zarejestrowane testy; samo `add_test` nie tworzy programu testowego ani nie zastępuje `add_executable`.

W przykładzie `core` jest biblioteką, a `app` jej klientem. `target_link_libraries(app PRIVATE core)` opisuje zależność między targetami, więc CMake zna zarówno kolejność budowania, jak i wymagania przekazywane przez bibliotekę. Publiczny katalog nagłówków i minimalny standard C++23 stają się dostępne podczas kompilacji klienta. Nie trzeba ręcznie powtarzać tych parametrów dla każdego programu.

`PRIVATE` oznacza wymaganie własnej kompilacji targetu, `INTERFACE` wymaganie jego użytkowników, a `PUBLIC` oba zakresy. Nie wybieraj zakresu według intuicji „ta biblioteka jest ważna”. Jeśli nagłówek publiczny zawiera typ obcej biblioteki, odbiorca zwykle potrzebuje odpowiednich wymagań interfejsu. Jeśli zależność występuje wyłącznie w `.cpp`, jej wymagania kompilacji nie powinny zanieczyszczać klienta.

## Pogłębienie mechanizmu

Biblioteka statyczna nie linkuje do środka automatycznie wszystkich swoich zależności. Jest archiwum własnych obiektów, a wymagane biblioteki muszą znaleźć się przy końcowym linkowaniu programu. CMake potrafi zachować także prywatne zależności linkowania statycznej biblioteki jako wymagania potrzebne końcowemu linkowi, bez propagowania wszystkich wymagań kompilacji. Dlatego prosty slogan „PRIVATE nigdy nie przechodzi dalej” byłby nieścisły.

`target_compile_features(... cxx_std_23)` wyraża minimalny poziom standardu, nie obietnicę dostępności każdej funkcji biblioteki C++23. Kompilator i biblioteka standardowa są oddzielnymi składnikami. Jeśli wymagane są konkretne nagłówki lub makra cech, projekt powinien je sprawdzić albo dokumentować wspierane wersje. `CXX_EXTENSIONS OFF` pomaga wybrać tryb bez dodatkowych rozszerzeń języka, lecz nie zastępuje ostrzeżeń o nieprzenośnym kodzie.

Cache zawiera ustawienia właściwe danemu build tree, między innymi wybór toolchainu. Zmienianie kompilatora w istniejącym katalogu może prowadzić do niespójnej konfiguracji; dla innego toolchainu używaj osobnego katalogu. Plik toolchain ustawia się przy pierwszej konfiguracji. Zwykłe flagi projektu przypisuj targetom, zamiast dopisywać je globalnie do `CMAKE_CXX_FLAGS`, co utrudnia kontrolę zakresu i integrację jako podprojekt.

Generator expressions, np. `$<CONFIG:Debug>`, są oceniane w kontekście generowania i konfiguracji targetu. Nie są tym samym co zwykły `if`, wykonywany podczas konfiguracji. To istotne dla generatorów wielokonfiguracyjnych, gdzie jeden build tree zawiera jednocześnie Debug i Release. Presets zapisują powtarzalne konfiguracje; lokalne ścieżki użytkownika trzymaj poza współdzielonym plikiem projektu, w odpowiednich ustawieniach lokalnych.

Opcja `BUILD_TESTING` w przykładzie steruje rejestracją testu, ale target `numbers_test` jest tworzony wcześniej bezwarunkowo. Jeśli wyłączenie testów ma również usuwać koszt ich kompilacji, przenieś `add_executable` i jego konfigurację do tego samego warunku. To pokazuje różnicę między grafem budowania a listą zadań CTest. Podobnie `ctest` sam nie przebudowuje nieaktualnego programu: w zwykłym przepływie najpierw wykonuje się build, a dopiero później testy gotowych artefaktów.

## Drugi przykład

Biblioteka zawierająca wyłącznie nagłówki może być targetem INTERFACE. Ma własne wymagania użycia, choć nie powstaje dla niej archiwum z kodem.

~~~text
# CMakeLists.txt
cmake_minimum_required(VERSION 3.28)
project(header_example LANGUAGES CXX)

add_library(numbers INTERFACE)
target_include_directories(numbers INTERFACE
    "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
    "$<INSTALL_INTERFACE:include>")
target_compile_features(numbers INTERFACE cxx_std_23)

add_executable(numbers_test tests/numbers_test.cpp)
target_link_libraries(numbers_test PRIVATE numbers)
set_target_properties(numbers_test PROPERTIES CXX_EXTENSIONS OFF)

include(CTest)
if(BUILD_TESTING)
    add_test(NAME numbers_values COMMAND numbers_test)
endif()

# include/numbers.hpp
#ifndef GUIDE_NUMBERS_HPP
#define GUIDE_NUMBERS_HPP
inline constexpr int answer() noexcept { return 42; }
#endif

# tests/numbers_test.cpp
#include "numbers.hpp"
int main() { return answer() == 42 ? 0 : 1; }

# Generator jednokonfiguracyjny:
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
~~~

`BUILD_INTERFACE` wskazuje katalog źródeł podczas pracy w repozytorium, a `INSTALL_INTERFACE` opisuje względną ścieżkę docelowej instalacji. Przykład nie zawiera jeszcze reguł `install` ani eksportu pakietu; same wyrażenia nie instalują plików. Ich rozdzielenie zapobiega późniejszemu umieszczaniu absolutnej ścieżki komputera autora w interfejsie dostarczanym użytkownikowi.

## Porównanie i decyzje

Preferuj imported targets dostarczane przez `find_package` zamiast ręcznych ścieżek do archiwów. Lista źródeł zapisanych jawnie ułatwia przegląd zmian; automatyczne globowanie wymaga świadomej obsługi ponownej konfiguracji. Używaj małych targetów odpowiadających odpowiedzialnościom, lecz unikaj dzielenia bez potrzeby na setki bibliotek, które komplikują graf i końcowe linkowanie.

**Ćwiczenie.** Publiczny nagłówek `core` używa `std::span`, ale standard ustawiono tylko prywatnie na bibliotece. Dlaczego klient może nie kompilować się poprawnie? **Odpowiedź:** wymaganie języka nie przechodzi do klienta. Jeżeli cecha należy do publicznego interfejsu, odpowiedni poziom standardu powinien należeć do PUBLIC lub INTERFACE. Flagi samej implementacji mogą pozostać PRIVATE.

Źródła: [CMake: model targetów](https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html), [compile features](https://cmake.org/cmake/help/latest/manual/cmake-compile-features.7.html), [presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html).

## Powiązane tematy

- [Proces budowania](../01_wprowadzenie/05_proces_budowania.md)
- [Conan, vcpkg i zależności](06_conan_vcpkg_i_zaleznosci.md)
- [Moduły C++](04_moduly_cpp.md)
