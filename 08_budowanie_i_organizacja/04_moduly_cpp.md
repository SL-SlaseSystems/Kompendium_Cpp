[← Spis treści](../README.md)

# Moduły C++

Moduły wprowadzone w C++20 pozwalają eksportować deklaracje bez tekstowego kopiowania całego interfejsu przez `#include`. Mogą poprawić izolację makr i czas budowania, ale wymagają współpracy kompilatora oraz systemu budowania, który zna zależności między module interface units.

~~~text
// math.cppm — module interface unit
export module math;

export int square(int value) {
    return value * value;
}

// main.cpp
import math;

int main() {
    return square(4) == 16 ? 0 : 1;
}
~~~

Przykład pozostaje blokiem `text`, ponieważ sposób kompilowania modułów w Clang, GCC i MSVC oraz format artefaktów BMI/CMI nie ma jednolitego ręcznego interfejsu. Standard opisuje semantykę języka, nie polecenia toolchainu. W praktyce powierz obsługę nowoczesnemu CMake lub natywnemu systemowi środowiska i testuj każdą wspieraną konfigurację.

Jednostka może mieć global module fragment przed deklaracją modułu, część eksportowaną, implementacyjną i private module fragment. `export import` reeksportuje zależność. Header units pozwalają importować pewne nagłówki, ale nie zamieniają automatycznie każdego legacy header w dobry moduł.

Moduły nie rozwiązują stabilności ABI, dystrybucji bibliotek binarnych ani wszystkich naruszeń ODR. Makra nie są eksportowane jak zwykłe deklaracje, co jest zaletą izolacji, ale może komplikować biblioteki konfigurowane preprocesorem. Migrację warto zaczynać od dobrze odseparowanych targetów, nie od mechanicznego zastąpienia wszystkich include.

## Jak to działa krok po kroku

Deklaracja `export module math;` oznacza główną jednostkę interfejsu nazwanego modułu. `export` przy funkcji udostępnia ją importerom. Kompilator przetwarza interfejs i zapisuje własny artefakt informacji semantycznej, często nazywany BMI. Jednostka z `import math;` musi uzyskać dostęp do tego artefaktu podczas kompilacji. Nie wystarcza dopiero późniejsze przekazanie pliku obiektowego linkerowi.

Zbudowanie zależnego programu wymaga więc kolejności: interfejs dostawcy przed kompilacją importera, a następnie linkowanie kodu obu jednostek. Konkretne narzędzie może generować BMI i plik obiektowy w jednym lub kilku krokach. Rozszerzenie `.cppm` jest konwencją toolchainu, nie semantyczną treścią deklaracji modułu. System budowania musi rozpoznać importy i zapisać ich zależności również przy kompilacji równoległej.

`export import other;` udostępnia importerowi także eksportowany interfejs zależności. Zwykłe `import other;` pozwala korzystać z niego wewnętrznie bez takiego reeksportu. To decyzja o publicznym API: reeksport zwiększa zakres, od którego zależy klient. Rozdzielaj zależności potrzebne użytkownikowi interfejsu od tych używanych tylko w implementacji.

## Pogłębienie mechanizmu

Global module fragment zaczyna się od `module;` i pozwala umieścić dyrektywy preprocesora przed deklaracją nazwanego modułu. To zwykłe miejsce dla nagłówków starszych bibliotek wymagających tekstowego dołączenia. Deklaracje po `export module` są już związane z odpowiednim kontekstem modułu. Mechaniczne przeniesienie wszystkich include do tej części może zmienić przywiązanie deklaracji i wywołać problemy przy współistnieniu z innymi jednostkami.

Named modules nie eksportują makr do importera. Makro zdefiniowane w importerze nie powinno konfigurować już skompilowanego interfejsu tak, jak konfigurowało tekstowy nagłówek. Header units są osobnym mechanizmem: import nagłówka ma szczególne zasady, między innymi dotyczące makr. Nie mieszaj ich z obietnicami izolacji nazwanego modułu i nie zakładaj, że obsługa jednego mechanizmu oznacza pełną obsługę drugiego przez build system.

Partycje dzielą moduł na jednostki o nazwach takich jak `math:detail`. Mogą dostarczać części interfejsu lub implementacji. Zwykli klienci importują nazwany moduł, a wewnętrzny podział powinien pozostawać jego sprawą. Jednostka implementacji zaczyna się od `module math;` bez `export` i może definiować funkcje zadeklarowane w interfejsie. Nieeksportowane nazwy nie są po prostu równoważne `private` klasy: widoczność, osiągalność deklaracji i linkage są oddzielnymi pojęciami.

BMI nie jest przenośnym odpowiednikiem pliku nagłówkowego dla dowolnego kompilatora. Może zależeć od wersji kompilatora, opcji, ścieżek i biblioteki standardowej. Dystrybucja samego BMI między różnymi toolchainami wymaga udokumentowanego wsparcia konkretnej implementacji. Moduł nie zwalnia także z dostarczenia kodu wykonywalnego dla zwykłych funkcji. Import usuwa tekstowe kopiowanie interfejsu, ale nie usuwa linkowania.

## Drugi przykład

Globalny fragment izoluje tradycyjny nagłówek, a implementacja pozostaje w oddzielnej jednostce. Poniższy opis CMake korzysta z file set `CXX_MODULES`, dostępnego od CMake 3.28; potrzebny jest również wspierany kompilator, skaner zależności i generator.

~~~text
// arithmetic.cppm
module;
#include <cstdint>
export module arithmetic;
export std::int64_t twice(std::int32_t value);

// arithmetic.cpp
module;
#include <cstdint>
module arithmetic;
std::int64_t twice(std::int32_t value) {
    return static_cast<std::int64_t>(value) * 2;
}

// main.cpp
import arithmetic;
int main() { return twice(21) == 42 ? 0 : 1; }

# CMakeLists.txt
cmake_minimum_required(VERSION 3.28)
project(module_example LANGUAGES CXX)
add_library(arithmetic)
target_sources(arithmetic PUBLIC
    FILE_SET CXX_MODULES FILES arithmetic.cppm)
target_sources(arithmetic PRIVATE arithmetic.cpp)
target_compile_features(arithmetic PUBLIC cxx_std_23)
add_executable(app main.cpp)
target_link_libraries(app PRIVATE arithmetic)
~~~

Rozszerzenie typu przed mnożeniem sprawia, że wynik mieści się dla całej dziedziny `int32_t` na implementacji dostarczającej te typy. To niezależna kwestia od organizacji modułów. Konfigurację budowania należy sprawdzić dla konkretnego narzędzia zgodnie z aktualną tabelą wsparcia CMake; sama wersja minimalna projektu nie zapewnia obsługi modułów w Apple Clang ani w każdym generatorze.

## Porównanie i decyzje

Moduły są atrakcyjne w dużych projektach z uporządkowanymi granicami bibliotek i kontrolowanym toolchainem. Nagłówki pozostają praktyczne dla szerokiej dystrybucji, integracji C oraz starszych środowisk. Migrację zacznij od małego modułu i zmierz pełne oraz przyrostowe budowanie. Skrócenie parsowania nie gwarantuje przyspieszenia całego zadania, jeśli graf importów ogranicza równoległość albo dominują instancjacje szablonów.

**Ćwiczenie.** Czy po skompilowaniu `arithmetic.cppm` można skompilować `main.cpp` i pominąć obiekt implementacji przy linkowaniu? **Odpowiedź:** nie, funkcja `twice` ma definicję w jednostce implementacji. BMI przekazuje deklarację potrzebną do kompilacji, a kod funkcji nadal musi trafić do programu. To dwa różne rodzaje artefaktów.

Źródła: [C++23: moduły](https://timsong-cpp.github.io/cppwp/n4950/module), [CMake i obsługa modułów](https://cmake.org/cmake/help/latest/manual/cmake-cxxmodules.7.html), [oficjalna dokumentacja modułów Clang](https://clang.llvm.org/docs/StandardCPlusPlusModules.html).

## Powiązane tematy

- [Translation units i nagłówki](01_translation_units_headers_i_include.md)
- [CMake](05_cmake.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
