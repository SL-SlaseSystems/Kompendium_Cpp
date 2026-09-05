[← Spis treści](../README.md)

# Translation units, nagłówki i include

Po preprocessing każdy plik źródłowy wraz z włączonymi nagłówkami tworzy jednostkę translacji (*translation unit*). Jednostki są kompilowane oddzielnie, dlatego deklaracje potrzebne klientowi muszą być widoczne w każdej z nich. Linker łączy powstałe pliki obiektowe.

Typowy podział umieszcza publiczną deklarację w `.hpp`, a definicję funkcji nieinline w `.cpp`:

~~~text
// math.hpp
#pragma once
int square(int value);

// math.cpp
#include "math.hpp"
int square(int value) { return value * value; }

// main.cpp
#include "math.hpp"
int main() { return square(4) == 16 ? 0 : 1; }
~~~

`#include` jest tekstowym włączeniem pliku. Include guards zapobiegają wielokrotnemu przetworzeniu tego samego nagłówka w jednej jednostce:

~~~text
#ifndef PROJECT_MATH_HPP
#define PROJECT_MATH_HPP
int square(int value);
#endif
~~~

`#pragma once` jest szeroko wspierane, lecz formalnie pozostaje mechanizmem implementacji. Guards są przenośne, o ile nazwa makra jest unikalna i nieużywa identyfikatorów zarezerwowanych.

Nagłówek powinien być samowystarczalny: po jego bezpośrednim dołączeniu dostępne są wszystkie potrzebne deklaracje. Nie polegaj na przypadkowym transitive include. Forward declaration zmniejsza zależności tylko wtedy, gdy wystarczy typ niekompletny; wiele operacji, w tym przechowywanie wartości jako pola, wymaga pełnej definicji.

Szablony i funkcje inline zwykle mają definicje w nagłówku, ponieważ muszą być widoczne przy instancjacji lub spełniać ODR w wielu jednostkach. Moduły C++ rozwiązują część problemów tekstowych nagłówków, lecz współistnienie i wsparcie build systemów nadal wymagają świadomej konfiguracji.

## Jak to działa krok po kroku

Dla `main.cpp` preprocesor odnajduje `math.hpp`, rozwija dyrektywy i makra oraz pozostawia deklarację `square`. Kompilator może dzięki temu sprawdzić liczbę argumentów i typ wyniku. Ciało funkcji nie jest potrzebne, aby wygenerować wywołanie z odniesieniem do symbolu, który zostanie rozstrzygnięty później. Dla `math.cpp` powstaje oddzielna jednostka zawierająca tę samą deklarację oraz definicję funkcji.

Kompilacja przez `-c` w typowym toolchainie zatrzymuje się na pliku obiektowym. Dopiero linkowanie obu obiektów daje program wykonywalny. Dołączenie nagłówka nie dodaje automatycznie `math.cpp` do budowania. Jeśli definicji zabraknie na etapie linkowania, poprawna kompilacja klienta nie wystarczy. To podstawowa różnica między dostępnością deklaracji a dostarczeniem implementacji.

Zmiana ciała funkcji w `math.cpp` wymaga zwykle przebudowania tylko tej jednostki i ponownego linkowania. Zmiana deklaracji lub definicji klasy w nagłówku wymaga przebudowania wszystkich jednostek zależnych od tego nagłówka. Narzędzie budowania powinno śledzić zależności wygenerowane przez kompilator, także pośrednie. Ręczna lista najważniejszych nagłówków jest podatna na nieaktualne artefakty.

## Pogłębienie mechanizmu

Include guard działa w obrębie jednej jednostki translacji: po pierwszym włączeniu makro jest zdefiniowane i kolejne włączenie pomija treść. Nie scala definicji między różnymi plikami obiektowymi. Zwykła definicja funkcji nieinline w chronionym nagłówku może więc nadal łamać ODR, gdy nagłówek dołączają dwie jednostki. Unikalność makra także ma znaczenie: przypadkowa kolizja z guardem innej biblioteki może po cichu usunąć potrzebne deklaracje.

Deklaracja wyprzedzająca `class Widget;` pozwala deklarować wskaźniki i referencje oraz pewne funkcje korzystające z typu. Nie wystarczy do pola `Widget value;`, obliczenia `sizeof(Widget)` ani wywoływania jego metod. Nie dopisuj własnych deklaracji typów biblioteki standardowej w `namespace std`; używaj odpowiednich nagłówków, ewentualnie przewidzianych nagłówków wyprzedzających takich jak `<iosfwd>`.

Wzorzec PImpl oddziela publiczny nagłówek od definicji implementacji przez wskaźnik właścicielski. Przy `unique_ptr<Impl>` destruktor klasy zwykle definiuje się w `.cpp` po pełnej definicji Impl, aby domyślny deleter znał kompletny typ w miejscu niszczenia. Tak samo analizuj miejsce definicji operacji przenoszących i konstruktorów, których ścieżki sprzątania mogą wymagać destrukcji pola. Sam forward declaration nie rozwiązuje każdej zależności.

Nagłówek powinien bezpośrednio dołączać to, czego używa w swoim interfejsie. Sprawdzenie samowystarczalności polega na skompilowaniu jednostki zawierającej tylko ten nagłówek i minimalne `main`. W implementacji dołącz własny nagłówek jako pierwszy: brakujące zależności nie zostaną wtedy przypadkowo zamaskowane wcześniejszymi include. Nie dołączaj plików `.cpp` jako sposobu naprawiania linkera; zmienia to granice jednostek i może tworzyć wielokrotne definicje.

## Drugi przykład

Poniższy układ celowo pokazuje wszystkie trzy pliki oraz oddzielne kroki kompilacji. Nazwa guarda należy do projektu i nie zaczyna się od zarezerwowanej kombinacji znaków.

~~~text
// counter.hpp
#ifndef GUIDE_COUNTER_HPP
#define GUIDE_COUNTER_HPP
class Counter {
    int value_ = 0;
public:
    void increment();
    int value() const noexcept;
};
#endif

// counter.cpp
#include "counter.hpp"
void Counter::increment() { ++value_; }
int Counter::value() const noexcept { return value_; }

// main.cpp
#include "counter.hpp"
int main() {
    Counter counter;
    counter.increment();
    return counter.value() == 1 ? 0 : 1;
}

# Polecenia dla Clang/GCC, po zapisaniu plików:
clang++ -std=c++23 -c counter.cpp -o counter.o
clang++ -std=c++23 -c main.cpp -o main.o
clang++ counter.o main.o -o counter_app
./counter_app
~~~

Definicja klasy jest widoczna klientowi, bo musi on znać rozmiar obiektu Counter. Ciała metod pozostają w implementacji. Przykład wykonuje jedno zwiększenie; pełne API licznika musi oddzielnie określić zachowanie przy granicy reprezentowalnej liczby. Rozdzielenie plików samo nie zmienia reguł arytmetyki ani nie zapewnia kontroli przepełnienia.

## Porównanie i decyzje

Nagłówki są prostym, szeroko wspieranym mechanizmem integracji. Koszt rośnie wraz z wielkością interfejsów i liczbą klientów, szczególnie gdy publiczny nagłówek wciąga ciężkie zależności implementacyjne. Forward declarations i PImpl ograniczają przebudowy kosztem pośredniego dostępu lub bardziej złożonej organizacji. Moduły zmieniają model udostępniania deklaracji, ale nadal wymagają poprawnego grafu zależności.

**Ćwiczenie.** Dwa pliki źródłowe dołączają nagłówek z guardem i definicją `int version() { return 1; }`. Dlaczego guard nie zapobiega błędowi wielokrotnej definicji? **Odpowiedź:** każdy plik ma własne przetwarzanie preprocesora i własną definicję funkcji. Przenieś ciało do jednej implementacji albo użyj właściwej semantyki inline, jeśli definicja ma należeć do nagłówka.

Źródła reguł: [C++23: jednostki translacji](https://timsong-cpp.github.io/cppwp/n4950/lex.separate), [dyrektywa include](https://timsong-cpp.github.io/cppwp/n4950/cpp.include), [Clang: etapy kompilacji](https://clang.llvm.org/docs/CommandGuide/clang.html).

## Powiązane tematy

- [Linkowanie, ODR i inline](02_linkowanie_odr_i_inline.md)
- [Moduły C++](04_moduly_cpp.md)
- [Proces budowania](../01_wprowadzenie/05_proces_budowania.md)
