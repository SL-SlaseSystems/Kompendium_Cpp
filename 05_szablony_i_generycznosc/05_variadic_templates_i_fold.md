[← Spis treści](../README.md)

# Variadic templates i fold expressions

Parameter pack reprezentuje zero lub więcej argumentów typowych albo wartościowych. Rozwinięcie packa powtarza wzorzec dla każdego elementu. Mechanizm pozwala budować heterogeniczne struktury, forwardować argumenty i tworzyć interfejsy o zmiennej liczbie parametrów bez C-style variadic functions.

~~~cpp
#include <cassert>
#include <string>
#include <utility>

template<class... Numbers>
auto sum(Numbers... numbers) {
    return (numbers + ... + 0);
}

template<class... Parts>
std::string join(Parts&&... parts) {
    std::string result;
    (result.append(std::forward<Parts>(parts)), ...);
    return result;
}

int main() {
    assert(sum(1, 2, 3, 4) == 10);
    assert(join("C", "+", "+") == "C++");
}
~~~

Fold expression od C++17 może być lewo- lub prawostronne oraz unary lub binary. Wartość inicjalna `0` sprawia, że `sum()` działa również dla pustego packa, choć ograniczenia typu wyniku nadal wymagają przemyślenia. Operator przecinka w drugim foldzie sekwencjonuje wywołania `append` od lewej do prawej.

`sizeof...(Parts)` zwraca liczbę elementów packa. Pack może zostać rozwinięty w listach argumentów, inicjalizatorach, bazach klasy i wielu innych kontekstach. Rekurencyjne rozpakowywanie było popularne przed fold expressions, ale dziś bywa niepotrzebnie skomplikowane.

Przy forwardowaniu używa się `T&&` w kontekście dedukowanym oraz `std::forward<T>`. Samo nazwane `argument` jest lvalue niezależnie od typu deklaracji. Nie forwarduj tej samej wartości wielokrotnie, jeśli pierwsze użycie mogło ją przenieść.

## Jak to działa krok po kroku

W `template<class... Numbers>` nazwa `Numbers` oznacza pakiet typów. Parametry `Numbers... numbers` tworzą odpowiadający mu pakiet argumentów funkcji. Wywołanie `sum(1, 2, 3)` dedukuje trzy typy `int`. Fold `(numbers + ... + 0)` rozwija się jak `1 + (2 + (3 + 0))`, ponieważ jest prawostronny. Nie tworzy ukrytej kolekcji ani pętli po obiektach jednego wspólnego typu.

Rozwinięcie pakietu powtarza wzorzec zawierający nieprzetworzony pakiet. W `std::forward<Parts>(parts)...` wzorcem jest całe wywołanie `forward`, więc każdy argument otrzymuje odpowiadający mu parametr typu. Jeżeli jeden wzorzec równocześnie rozwija dwa pakiety, ich długości muszą być zgodne. Wielokropek nie oznacza dowolnego automatycznego zestawiania wszystkich kombinacji.

W `join` fold po przecinku wykonuje kolejne `append`. Dla wbudowanego operatora przecinka lewa operacja jest sekwencjonowana przed prawą, więc znaki trafiają w przewidzianej kolejności. To gwarancja użytego operatora, a nie ogólna własność rozwijania pakietów. Przekazanie rozwiniętych wywołań jako argumentów innej funkcji nadal podlega regułom kolejności argumentów funkcji.

## Pogłębienie mechanizmu

Unary left fold ma postać `(... op pack)` i grupuje od lewej. Unary right fold `(pack op ...)` grupuje od prawej. Binary fold dodaje jawny element początkowy po odpowiedniej stronie. Dla odejmowania, dzielenia, konkatenacji o asymetrycznych przeciążeniach lub liczb zmiennoprzecinkowych kierunek może zmieniać wynik. Łączność nie jest kosmetycznym wyborem składni.

Dla pustego pakietu unary fold jest zdefiniowany tylko dla określonych operatorów: `&&` daje prawdę, `||` fałsz, a przecinek `void()`. Puste sumowanie wymaga inicjalizatora albo osobnej obsługi. Wybór `0` narzuca jednak typ `int` na wynik pustej sumy i uczestniczy w konwersjach sumy niepustej. Dla typów domenowych potrzebny może być element neutralny jawnie podany przez wywołującego.

Złożenie po wbudowanym `&&` i `||` zachowuje krótkie spięcie podczas wykonania. Mimo to wyrażenia dla wszystkich elementów muszą być poprawne podczas instancjacji. Wcześniejszy runtime'owy wynik fałszywy nie ukryje błędnego operatora dla późniejszego typu. Do rozdzielania implementacji zależnych od typu służą constraints i `if constexpr`.

Forwarding reference powstaje z `T&&` przy dedukowanym parametrze typu w odpowiednim kontekście. `const T&&` nie jest tym samym mechanizmem. Nazwane `parts` pozostają lvalue, dlatego forwarding jest jawny. Przekazanie rvalue dalej nie musi oznaczać ruchu, lecz pozwala odbiorcy wybrać ruch. Jeżeli ten sam argument zostanie przekazany jako rvalue dwa razy, drugie użycie może zobaczyć stan po pierwszym przejęciu zasobu.

Do rozpakowywania krotki według indeksów służą `index_sequence` i `make_index_sequence`, a `std::apply` często usuwa konieczność pisania tej infrastruktury. Są przydatne, gdy dane już istnieją w `tuple`; pakiet parametrów jest natomiast konstrukcją szablonu. Nie można traktować pakietu dokładnie jak wektora i indeksować go zwykłą zmienną runtime w C++23.

## Drugi przykład

Dwa foldy z tymi samymi liczbami pokazują wpływ grupowania. Trzeci używa konwersji do `void`, aby świadomie wybrać wbudowany przecinek i wykonywać kolejne operacje w kolejności pakietu.

~~~cpp
#include <cassert>
#include <vector>

template<class... T>
int subtract_left(T... values) { return (10 - ... - values); }

template<class... T>
int subtract_right(T... values) { return (values - ... - 10); }

template<class... T>
void append(std::vector<int>& target, T... values) {
    (static_cast<void>(target.push_back(values)), ...);
}

int main() {
    assert(subtract_left(1, 2, 3) == 4);
    assert(subtract_right(1, 2, 3) == -8);
    assert(subtract_left() == 10);
    std::vector<int> values;
    append(values, 3, 1, 4);
    append(values);
    assert((values == std::vector{3, 1, 4}));
}
~~~

Lewy wynik to `((10 - 1) - 2) - 3`. Prawy to `1 - (2 - (3 - 10))`. Kolejność zapisanych liczb nie zmienia się, lecz nawiasowanie zmienia sens działania. Dla dodawania liczb rzeczywistych reprezentowanych przybliżeniem również nie wolno zakładać matematycznej łączności.

## Porównanie i decyzje

Wybieraj pakiet, gdy liczba i typy argumentów są znane podczas kompilacji i mogą się różnić. Wybieraj kontener lub `span`, gdy liczba danych pochodzi z wejścia runtime. Fold upraszcza jednorodne działanie operatorem, ale bardziej złożona obsługa argumentów może być czytelniejsza jako lambda wywoływana kolejno dla każdego elementu.

**Ćwiczenie.** Czy `(check(values) && ...)` wywoła `check` dla wszystkich argumentów, jeśli pierwsze sprawdzenie zwróci fałsz?

**Odpowiedź.** Nie, o ile używany jest wbudowany `&&`. Kolejne wywołania zostaną pominięte. Nadal jednak każde z nich musi być poprawnym wyrażeniem dla swojego typu, ponieważ kompilator tworzy cały odpowiedni kod przed jego wykonaniem.

Źródła: [pakiety parametrów](https://timsong-cpp.github.io/cppwp/n4950/temp.variadic), [fold expressions](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.fold), [instancjacja foldów](https://timsong-cpp.github.io/cppwp/n4950/temp.variadic#9).

## Powiązane tematy

- [Szablony funkcji](01_function_i_class_templates.md)
- [Value categories i perfect forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [tuple i pair](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
