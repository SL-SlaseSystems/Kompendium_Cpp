[← Spis treści](../README.md)

# Dedukcja, auto, decltype i CTAD

Dedukcja typu ogranicza powtarzanie informacji, ale działa według konkretnych reguł. `auto` dedukuje podobnie do parametru szablonu przekazywanego przez wartość: usuwa referencję i najwyższy poziom `const`. `auto&`, `const auto&` oraz `auto&&` mają inne zachowanie. `decltype(expr)` zachowuje kategorię wartości według szczególnej reguły dla nieujętej w nawiasy nazwy.

~~~cpp
#include <cassert>
#include <type_traits>
#include <utility>
#include <vector>

int main() {
    const int value = 3;
    auto copy = value;
    const auto& reference = value;
    decltype(auto) exact = (value);
    std::pair pair{1, 2.5}; // CTAD

    static_assert(std::is_same_v<decltype(copy), int>);
    static_assert(std::is_same_v<decltype(reference), const int&>);
    static_assert(std::is_same_v<decltype(exact), const int&>);
    assert(pair.first == 1);
}
~~~

Nawiasy w `decltype((value))` sprawiają, że analizowane jest wyrażenie lvalue i wynikiem jest referencja. To użyteczne w kodzie generycznym, ale może przypadkowo zwrócić dangling reference. `decltype(auto)` w typie zwracanym należy stosować tylko wtedy, gdy dokładne propagowanie referencji jest świadomą częścią API.

CTAD (*class template argument deduction*) pozwala wywnioskować parametry szablonu klasy z konstruktora lub deduction guide. `std::pair pair{1, 2.5}` daje `pair<int, double>`. Nie każda pożądana semantyka wynika z konstruktorów, więc biblioteka może dostarczyć własne guides. Alias template deduction ma dodatkowe ograniczenia implementacyjne i wersyjne.

## Jak to działa krok po kroku

Dla `auto x = expression` wyobraź sobie dedukcję parametru przekazywanego przez wartość. Referencyjność źródła oraz najwyższe `const` nie przechodzą do nowego obiektu. Jeśli źródło ma typ `const int*`, usuwanie najwyższych kwalifikatorów nie usuwa stałości wskazanego `int`. To inny poziom typu. `auto&` żąda związania referencji i zachowuje kwalifikację obiektu źródłowego.

`auto&&` podczas odpowiedniej dedukcji zachowuje się jak forwarding reference. Dla lvalue typu `T` dedukcja i zwijanie referencji prowadzą do `T&`. Dla rvalue zwykle powstaje `T&&`. We wszystkich tych przypadkach użycie samej nazwy zadeklarowanej zmiennej jest wyrażeniem lvalue. Aby przekazać dalej oryginalną kategorię, kod generyczny stosuje `std::forward` z właściwie wydedukowanym parametrem.

`decltype` ma szczególną regułę dla nieujętej w nawiasy nazwy lub dostępu do pola: daje zadeklarowany typ oznaczonej encji. Poza tym bada kategorię wyrażenia: lvalue daje `T&`, xvalue daje `T&&`, a prvalue daje `T`. Dlatego `decltype(value)` i `decltype((value))` mogą się różnić. Dodatkowe nawiasy nie są tu wyłącznie zmianą wizualną.

## Pogłębienie mechanizmu

`decltype(auto)` stosuje dokładnie reguły `decltype` do inicjalizatora lub zwracanego wyrażenia. Zapis `decltype(auto) x = value;` może utworzyć wartość, a `decltype(auto) x = (value);` referencję. W funkcji zwracającej obiekt własnościowy przypadkowe nawiasy wokół lokalnej nazwy mogą więc stworzyć wiszącą referencję. Typ dedukowany nie zwalnia z analizy życia obiektu.

Nawiasy klamrowe mają odrębne reguły. `auto a = {1, 2}` daje `std::initializer_list<int>`, a `auto b{1}` daje `int`. Bezpośrednia inicjalizacja `auto b{1, 2}` jest niepoprawna. Zwykły szablon `f(T)` nie potrafi na ogół wydedukować `T` z samego `{1, 2}`, ponieważ lista klamrowa nie jest zwykłym wyrażeniem o jednym typie. Parametr `initializer_list<T>` stanowi odpowiednio zaprojektowany wyjątek.

Dedukcja przekazywana przez wartość zwykle zamienia tablicę na wskaźnik, a referencyjna może zachować rozmiar tablicy. To wpływa na `auto text = "abc"`, którego typem jest wskaźnik do stałych znaków. `auto& text = "abc"` zachowuje referencję do tablicy. Żaden z tych zapisów nie tworzy samodzielnego `std::string`.

CTAD tworzy zbiór przewodników dedukcji, między innymi na podstawie konstruktorów, i wybiera parametry klasy. Dopiero potem odbywa się inicjalizacja obiektu konkretnej specjalizacji. Deduction guide nie jest wykonywaną funkcją i nie tworzy brakującego konstruktora. Może wybrać typ o zamierzonej własności, na przykład kopiujący dane zamiast zachowujący referencję, ale wybrany typ nadal musi nadawać się do inicjalizacji.

Brak dedukcji nie oznacza braku możliwej konwersji. Gdy parametr występuje wyłącznie w kontekście niededukowanym, argument szablonu trzeba uzyskać z innego miejsca albo podać jawnie. `std::type_identity_t<T>` od C++20 pozwala świadomie wyłączyć dedukcję z danego parametru. Przydaje się, kiedy pierwszy argument określa typ, a drugi ma się do niego skonwertować.

## Drugi przykład

Program sprawdza kategorie wyrażeń i pokazuje, że utworzenie kopii jest niezależną decyzją od dostępu do referencji. Wszystkie zależności typów są kontrolowane przez kompilator.

~~~cpp
#include <cassert>
#include <type_traits>
#include <utility>

int main() {
    int value = 7;
    auto&& alias = value;
    auto&& temporary = 9;
    decltype(auto) copy = value;
    decltype(auto) reference = (value);
    static_assert(std::is_same_v<decltype(alias), int&>);
    static_assert(std::is_same_v<decltype(temporary), int&&>);
    static_assert(std::is_same_v<decltype((temporary)), int&>);
    static_assert(std::is_same_v<decltype(std::move(value)), int&&>);
    static_assert(std::is_same_v<decltype(copy), int>);
    static_assert(std::is_same_v<decltype(reference), int&>);
    reference = 12;
    assert(value == 12 && copy == 7);
    assert(temporary == 9);
}
~~~

`temporary` jest referencją rvalue, ale jej nazwa nadal oznacza lvalue. Życie związanej tutaj liczby tymczasowej jest przedłużone przez lokalne związanie. Takiej gwarancji nie można przenosić bez sprawdzenia na referencję zwróconą z innej funkcji.

## Porównanie i decyzje

Używaj zwykłego `auto` do niezależnej wartości, `const auto&` do odczytu istniejącego obiektu, a `decltype(auto)` wtedy, gdy propagowanie dokładnego typu i referencyjności należy do kontraktu. Dla API, w którym własność ma być od razu czytelna, jawny typ wyniku często jest cenniejszy niż oszczędność kilku znaków. CTAD jest wygodne, gdy wybierany typ odpowiada oczywistej intencji danych wejściowych.

**Ćwiczenie.** Dla `const int* pointer` jaki typ ma `auto copy = pointer`? Czy można przez `copy` zmienić wskazaną liczbę?

**Odpowiedź.** Typem jest `const int*`. Sam wskaźnik można przestawić, ale stałość wskazanego obiektu pozostaje. `auto` usuwa tylko najwyższe kwalifikacje przy dedukcji przez wartość, nie wszystkie `const` wewnątrz złożonego typu.

Źródła: [dedukcja auto](https://timsong-cpp.github.io/cppwp/n4950/dcl.type.auto.deduct), [decltype](https://timsong-cpp.github.io/cppwp/n4950/dcl.type.decltype), [CTAD](https://timsong-cpp.github.io/cppwp/n4950/over.match.class.deduct).

## Powiązane tematy

- [Szablony funkcji i klas](01_function_i_class_templates.md)
- [Value categories i forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)

