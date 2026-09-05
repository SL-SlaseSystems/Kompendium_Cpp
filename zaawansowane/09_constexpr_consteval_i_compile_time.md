[← Spis treści](../README.md)

# constexpr, consteval i compile time

Constant evaluation wykonuje podzbiór semantyki C++ podczas kompilacji. Nie jest oddzielnym językiem: coraz więcej zwykłych konstrukcji działa w `constexpr`. Nadal istnieją zakazane operacje i ograniczenia zależne od wersji, np. efekty uboczne poza ewaluacją, niektóre formy dynamicznej pamięci i dostęp do obiektów o niewłaściwym lifetime.

~~~cpp
#include <array>
#include <cassert>
#include <cstdint>
#include <string_view>

consteval std::uint32_t hash_literal(std::string_view text) {
    std::uint32_t hash = 2166136261u;
    for (unsigned char byte : text) {
        hash = (hash ^ byte) * 16777619u;
    }
    return hash;
}

int main() {
    constexpr auto id = hash_literal("status");
    static_assert(id != 0);
    assert(id == hash_literal("status"));
}
~~~

Unsigned overflow w tym hash jest zdefiniowany modulo. `consteval` gwarantuje compile-time dla potencjalnie ewaluowanych wywołań. Jeśli chcemy jedną funkcję dostępną także runtime, wybieramy `constexpr`.

`std::is_constant_evaluated()` pozwala wykryć, czy bieżąca ewaluacja jest stała, a `if consteval` z C++23 daje bezpieczniejszą składnię rozdzielenia gałęzi. Nie używaj tego do tworzenia różnych wyników semantycznych bez wyraźnego kontraktu; compile-time i runtime powinny zwykle zgadzać się.

Dynamiczna alokacja podczas constant evaluation może być dozwolona w określonych przypadkach, ale pamięć musi zostać zwolniona w ramach ewaluacji i nie może „wyciec” do runtime. Biblioteka standardowa stopniowo rozszerza constexpr support.

Koszt przenosi się z runtime do kompilatora. Monitoruj czas, pamięć, cache builda i jakość diagnostyki. Precomputed table może zwiększyć binarium i pogorszyć cache bardziej niż krótki runtime calculation.

## Jak to działa krok po kroku

`hash_literal("status")` otrzymuje widok na literał o statycznym czasie przechowywania. Pętla odczytuje kolejne bajty, wykonuje XOR i mnożenie unsigned, a następnie zwraca gotową liczbę. Ponieważ funkcja jest `consteval`, wymagane wywołanie musi spełnić reguły stałego wyrażenia. Literał i wszystkie użyte operacje to umożliwiają. Zwykły napis odczytany z pliku nie mógłby zostać przekazany w tym samym miejscu.

`constexpr` na funkcji nie wymaga, aby każde wywołanie odbywało się podczas kompilacji. Wymaga odpowiednio poprawnej definicji i pozwala na stałą ewaluację, gdy kontekst jej żąda. `constexpr` na zmiennej wymaga natomiast stałego inicjalizatora i daje obiekt const. `constinit` dotyczy gwarancji inicjalizacji statycznej; nie czyni obiektu niezmiennym i nie jest synonimem `constexpr`.

## Pogłębienie mechanizmu

Stała ewaluacja operuje na abstrakcyjnych obiektach o śledzonym lifetime, nie na przyszłych adresach procesu. Wolno modyfikować lokalne wartości powstałe w tej ewaluacji, więc pętle i akumulatory są naturalną techniką. Nie wolno dowolnie odczytywać modyfikowalnego stanu globalnego lub zwrócić wskaźnika do lokalnego obiektu, który już nie istnieje. Stałe wyrażenia mają także ograniczenia dotyczące operacji takich jak reinterpret_cast i wywołania funkcji nieobsługujących constant evaluation.

Dynamiczna pamięć w C++20 i C++23 ma charakter przejściowy. `vector` może służyć jako warsztat do obliczenia liczby, jeśli jego przydziały zostają zwolnione w obrębie właściwej ewaluacji. Nie oznacza to możliwości zachowania dowolnego dynamicznego wektora jako trwałej zmiennej `constexpr`. Obiekt wynikowy nie może zawierać wskaźników do „sterty kompilatora”. Małe napisy mogą dodatkowo ujawniać zależności od reprezentacji biblioteki, dlatego obserwacja działania krótkiego `constexpr string` nie dowodzi działania wszystkich długości.

`if consteval` oznacza kontekst natychmiastowy wewnątrz odpowiedniej gałęzi i pozwala bezpiecznie wywoływać funkcję natychmiastową z funkcji dostępnej także runtime. Natomiast `if constexpr (std::is_constant_evaluated())` to pułapka: sam warunek `if constexpr` wymaga stałej ewaluacji, więc nie wybiera gałęzi na podstawie późniejszego wywołania funkcji. Do zwykłego rozpoznania trybu używa się zwykłego `if` albo `if consteval`.

UB napotkane w wymaganej stałej ewaluacji zwykle powoduje odrzucenie stałego wyrażenia. Dzięki temu `static_assert` może ujawniać przepełnienia i wyjścia poza zakres na konkretnych danych. Nie dowodzi jednak poprawności funkcji dla wszystkich wejść runtime. Kompilatory mają też limity liczby kroków, głębokości wywołań i zużycia pamięci; ich zwiększanie flagą nie zastępuje rozsądnej złożoności algorytmu.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <vector>

constexpr int triangular(int n) {
    std::vector<int> values;
    for (int i = 1; i <= n; ++i) values.push_back(i);
    int result = 0;
    for (int value : values) result += value;
    return result;
}
constexpr std::array<int, 4> table{
    triangular(0), triangular(1), triangular(2), triangular(3)};
int main() {
    static_assert(table[3] == 6);
    int n = 4;
    assert(triangular(n) == 10);
}
~~~

Przy budowaniu tablicy wektor istnieje tylko podczas obliczeń i zostaje zniszczony przed zwróceniem liczby. Wynikowa `array` nie zawiera żadnego wskaźnika do jego pamięci. To samo ciało funkcji obsługuje wywołanie ze zwykłym `n`. Przykład ma małe, kontrolowane argumenty: dla dużych `n` należałoby rozwiązać przepełnienie sumy i licznika pętli. Deklaracja `constexpr` nie rozszerza zakresu `int`.

## Porównanie i decyzje

Używaj `consteval` do kontraktu wymagającego gotowego wyniku przy kompilacji, na przykład walidacji literału opisującego format. Współdzielona implementacja `constexpr` lepiej pasuje do algorytmu potrzebnego w obu trybach. Duże tablice warto porównać z generowaniem podczas budowania projektu: osobny generator może dać lepszy cache i krótszą kompilację wielu jednostek translacji.

**Ćwiczenie.** Czy funkcja `constexpr` musi być szybsza runtime? **Odpowiedź:** nie; optymalizator może obliczyć zwykłą funkcję wcześniej lub pozostawić wywołanie constexpr w runtime. Czy `constinit int counter = 0` pozwala później zwiększyć `counter`? Tak; słowo kontroluje fazę inicjalizacji, nie mutowalność. Czy zwrócenie `values.data()` z przykładu byłoby dopuszczalne jako trwały wynik? Nie, po destrukcji wektora wskaźnik nie oznacza żywych elementów.

Źródła: [N4950: constant expressions](https://timsong-cpp.github.io/cppwp/n4950/expr.const) i [constexpr functions](https://timsong-cpp.github.io/cppwp/n4950/dcl.constexpr).

### Wynik obliczeń a tożsamość obiektu

Nie każdy wynik stałej ewaluacji jest zwykłą liczbą. Może zawierać wskaźniki lub referencje, których poprawność zależy od obiektów o dostatecznym czasie przechowywania. Widok na literał tekstowy może być prawidłowym stałym wynikiem, podczas gdy widok na lokalną tablicę utworzoną wewnątrz funkcji już nie. Przeniesienie obliczenia do compile time nie usuwa problemu wiszących referencji; kompilator po prostu ma większą możliwość jego wykrycia.

`constexpr` nie wymaga automatycznie inliningu ani nie wyklucza istnienia symbolu funkcji w binarium. Funkcję można wykorzystać również w kontekstach runtime i pobierać odpowiednie adresy, z zastrzeżeniem szczególnych ograniczeń funkcji natychmiastowych. Z kolei `consteval` nie służy do wyboru konkretnego poziomu optymalizacji: określa dopuszczalną fazę wywołania. Te mechanizmy warto rozdzielać także w opisie publicznego API.

Hash z pierwszego przykładu ma kolizje, ponieważ odwzorowuje dowolnie długi tekst na skończony zbiór liczb. Stałe obliczenie nie czyni go kryptograficznym ani unikatowym. Jeżeli wynik identyfikuje trwały protokół, należy ustalić kodowanie bajtów, wersję algorytmu i sposób wykrywania kolizji, niezależnie od tego, kiedy kompilator oblicza liczbę.

## Powiązane tematy

- [constexpr i metaprogramowanie](../05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [Wydajność](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
