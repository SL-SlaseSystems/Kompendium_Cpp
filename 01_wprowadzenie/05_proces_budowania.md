[← Spis treści](../README.md)

# Proces budowania

Plik źródłowy C++ nie staje się programem w jednym logicznym kroku. Preprocesor obsługuje dyrektywy, takie jak `#include`, `#define` i warunkowa kompilacja. Następnie kompilator analizuje wynik jako jednostkę translacji, sprawdza typy i generuje kod obiektowy. Linker łączy obiekty oraz biblioteki, rozwiązuje symbole i tworzy program lub bibliotekę.

~~~text
clang++ -std=c++23 -E main.cpp -o main.ii
clang++ -std=c++23 -c main.cpp -o main.o
clang++ main.o -o app
~~~

Opcja `-E` zatrzymuje proces po preprocessing, a `-c` tworzy plik obiektowy bez linkowania. W rzeczywistym projekcie system budowania pilnuje zależności i uruchamia tylko potrzebne kroki. Polecenia ręczne są jednak dobrym narzędziem diagnostycznym.

~~~cpp
#include <numeric>
#include <vector>

int sum(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

int main() {
    return sum({1, 2, 3}) == 6 ? 0 : 1;
}
~~~

Deklaracja mówi kompilatorowi, że nazwa istnieje i jaki ma typ. Definicja dostarcza byt lub ciało funkcji. Ta sama funkcja nieinline powinna mieć dokładnie jedną definicję w całym programie; to część One Definition Rule. Szablony i funkcje `inline` mają inne warunki i dlatego ich definicje często znajdują się w nagłówkach.

Biblioteka statyczna jest kopiowana przez linker do wyniku na poziomie potrzebnych obiektów, natomiast dynamiczna pozostaje osobnym artefaktem ładowanym podczas startu lub działania programu. Szczegóły nazw plików, wyszukiwania bibliotek i ABI są platformowe.

## Typowe pułapki

Błąd „undefined reference” zwykle oznacza brak definicji albo brak biblioteki przy linkowaniu, a „multiple definition” naruszenie ODR. Zmiana ABI bez przebudowania zależnych obiektów może dać trudne błędy. Czyść build directory po zmianie kompilatora, istotnych flag ABI albo wersji biblioteki standardowej.

## Jak to działa krok po kroku

Załóżmy, że aplikacja składa się z `main.cpp`, `math.cpp` i nagłówka `math.hpp`. Oba źródła włączają nagłówek, więc oba znają deklarację funkcji. Każde źródło jest kompilowane osobno w kontekście treści włączonych nagłówków. Powstają dwa pliki obiektowe: jeden odwołuje się do funkcji, drugi zawiera jej definicję. Linker łączy je w program.

Zmiana samego ciała funkcji w `math.cpp` zwykle wymaga przebudowania tego pliku i ponownego linkowania. Zmiana jej deklaracji w nagłówku może wymagać przebudowania wszystkich korzystających jednostek. System budowania powinien znać te zależności, również nagłówki dołączane pośrednio. Zbyt szeroki nagłówek zwiększa koszt nawet małej zmiany.

Preprocesor działa przed analizą typów. Makro rozwija tokeny, a nie wywołuje funkcji C++; jego tekst może zmienić deklarację zależnie od konfiguracji danej jednostki. Dlatego sprzeczne flagi `-D` między plikami mogą doprowadzić do różnych definicji tej samej klasy i naruszenia ODR, mimo że każdy plik osobno się kompiluje.

## Pogłębienie mechanizmu

Nagłówek nie jest magicznym plikiem linkera. `#include` udostępnia treść do kompilacji, ale zwykle nie dołącza biblioteki binarnej. Z kolei dodanie biblioteki do linkowania nie udostępnia kompilatorowi deklaracji jej funkcji. Do użycia zewnętrznego API potrzebujesz obu części oraz zgodności ich wersji.

Funkcja `inline` może mieć definicję w wielu jednostkach pod warunkami ODR. Słowo to nie nakazuje optymalizatorowi wstawienia instrukcji w miejscu wywołania. Zwykła funkcja zdefiniowana w nagłówku bez odpowiedniego mechanizmu może spowodować wiele definicji. Include guard zapobiega wielokrotnemu włączeniu w obrębie jednej jednostki, ale nie usuwa definicji z innych jednostek.

Linkowanie statyczne i dynamiczne zmienia sposób dostarczania implementacji. W drugim przypadku program może potrzebować właściwej biblioteki także podczas uruchomienia. Pomyślne linkowanie na komputerze autora nie gwarantuje odnalezienia biblioteki na komputerze użytkownika. Ścieżki wyszukiwania, architektura i zgodność ABI są częścią pakowania programu.

## Drugi przykład

Utwórz trzy osobne pliki. Poniższy blok ma etykietę `text`, ponieważ nie jest jedną jednostką translacji.

~~~text
// math.hpp
#ifndef COMPENDIUM_MATH_HPP
#define COMPENDIUM_MATH_HPP
int twice(int value);
#endif

// math.cpp
#include "math.hpp"
int twice(int value) { return value * 2; }

// main.cpp
#include "math.hpp"
int main() { return twice(21) == 42 ? 0 : 1; }

// Polecenia terminala, nie zawartość pliku C++:
clang++ -std=c++23 -Wall -Wextra -c main.cpp -o main.o
clang++ -std=c++23 -Wall -Wextra -c math.cpp -o math.o
clang++ main.o math.o -o app
./app
~~~

Jeżeli pominiesz `math.o` podczas linkowania, deklaracja nadal wystarcza do kompilacji `main.cpp`, ale definicja nie będzie dostępna przy tworzeniu programu. Jeżeli omyłkowo dostarczysz definicję `twice` również w `main.cpp`, naruszysz regułę jednej definicji. Dane testowe mieszczą się w `int`; ogólna funkcja podwajająca dowolny `int` wymaga dodatkowego kontraktu zakresu.

## Porównanie i decyzje

Ręczne polecenia są najlepsze do zrozumienia etapów i zminimalizowania błędu. CMake lub inny system budowania przydaje się, gdy rośnie graf zależności, liczba konfiguracji i platform. System powinien modelować cele oraz ich wymagania, zamiast wyłącznie składać globalną listę flag.

Pełna czysta przebudowa pomaga wykryć brakujące zależności ukryte przez stare artefakty. Nie powinna jednak być jedynym sposobem uzyskania poprawnego programu po każdej zmianie nagłówka. Jeżeli build przyrostowy produkuje nieaktualny wynik, trzeba naprawić graf zależności. To problem konfiguracji, a nie naturalna cecha C++.

## Ćwiczenie z odpowiedzią

Przenieś definicję `twice` do nagłówka i dołącz go w obu plikach. Co należy rozważyć? Dla tak małej funkcji można użyć definicji `inline`, identycznej i zgodnej z ODR we wszystkich jednostkach. Alternatywą pozostaje pojedyncza definicja w `math.cpp`. Nie dodawaj `static` tylko po to, by uciszyć linker, jeśli potrzebujesz jednej wspólnej encji programu.

Podstawa modelu translacji: [C++23, phases of translation](https://timsong-cpp.github.io/cppwp/n4950/lex.phases).

## Powiązane tematy

- [Translation units i nagłówki](../08_budowanie_i_organizacja/01_translation_units_headers_i_include.md)
- [Linkowanie, ODR i inline](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
- [CMake](../08_budowanie_i_organizacja/05_cmake.md)

