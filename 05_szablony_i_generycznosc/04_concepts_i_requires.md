[← Spis treści](../README.md)

# Concepts i requires

Concept jest nazwanym predykatem compile-time opisującym wymagania wobec argumentów szablonu. Constrained templates uczestniczą w overload resolution tylko wtedy, gdy constraints są spełnione. Dzięki temu interfejs wyraża potrzebne zachowanie, a błędy pojawiają się bliżej miejsca wywołania.

~~~cpp
#include <cassert>
#include <concepts>
#include <string>

template<class T>
concept Addable = requires(const T& left, const T& right) {
    { left + right } -> std::same_as<T>;
};

template<Addable T>
T add(const T& left, const T& right) {
    return left + right;
}

int main() {
    assert(add(2, 3) == 5);
    assert(add(std::string{"C"}, std::string{"++"}) == "C++");
}
~~~

Requires-expression może zawierać simple requirements sprawdzające poprawność wyrażenia, type requirements, compound requirements z typem wyniku i `noexcept` oraz nested requirements. Nie wykonuje wyrażeń; bada, czy byłyby poprawne po podstawieniu.

Concept nie powinien jedynie sprawdzać składni. Semantyczne wymagania, takie jak relacja równoważności lub brak modyfikacji argumentu, nie zawsze są weryfikowalne przez kompilator, lecz nadal należą do kontraktu. Standardowe concepts, np. `std::integral`, `std::regular`, `std::ranges::range` i `std::invocable`, tworzą wspólny język takich wymagań.

Constraints mogą być zapisane po nazwie template, przy parametrze, jako trailing `requires` lub requires-clause. Wybierz postać, która najlepiej pokazuje interfejs. Złożone reguły normalizacji i subsumption wpływają na wybór „bardziej ograniczonego” przeciążenia; tekstowo podobne predykaty nie muszą być traktowane identycznie.

## Jak to działa krok po kroku

Concept jest obliczanym podczas kompilacji warunkiem, ale nie jest nowym rodzajem obiektu przekazywanego podczas działania. Gdy wywołujesz `add`, kompilator dedukuje `T`, podstawia go do ograniczenia i sprawdza wymagania. Dopiero spełnienie warunków pozwala danemu przeciążeniu pozostać kandydatem. Niespełnione ograniczenie nie oznacza wykonania gałęzi błędu w funkcji, ponieważ do jej wywołania nie dochodzi.

W `requires(T left, T right)` lokalne parametry opisują wyrażenia, nie tworzą dwóch rzeczywistych obiektów. Wymaganie `{ left + right } -> std::same_as<T>` sprawdza poprawność dodawania oraz dokładny typ jego wyniku z użyciem reguły `decltype((expression))`. Nie wystarczy możliwość konwersji do `T`. Dlatego małe typy całkowite promowane do `int`, na przykład `short`, mogą nie spełnić takiego conceptu dla własnego `T`.

Ważne jest dopasowanie sprawdzanej kategorii do rzeczywistego użycia. Funkcja `add` przyjmuje stałe referencje, więc concept również powinien badać dodawanie stałych argumentów. Test wykonany tylko na modyfikowalnych lvalue mógłby zaakceptować typ, którego operator nie działa w faktycznym ciele funkcji. Constraints są użyteczne tylko wtedy, gdy wiernie opisują wymagane operacje.

## Pogłębienie mechanizmu

Simple requirement w postaci `expression;` sprawdza składnię i poprawność wyrażenia, lecz nie wymaga, aby jego wartość była prawdziwa. Zapis `sizeof(T) > 4;` nie filtruje małych typów; sprawdza, że da się napisać takie porównanie. Do żądania prawdy służy nested requirement: `requires sizeof(T) > 4;`. To częsta pomyłka, ponieważ oba zapisy wyglądają jak warunek.

Type requirement `typename T::value_type;` sprawdza istnienie typu. Compound requirement może oprócz typu wyniku żądać `noexcept`. Wymagania są analizowane w kolejności potrzebnej do rozstrzygnięcia, a odpowiednio zapisane ograniczenia logiczne pozwalają uniknąć podstawiania niepoprawnej dalszej części po już fałszywym warunku. Ograniczenie w niewłaściwym, niezależnym od szablonu kontekście nie jest jednak uniwersalnym mechanizmem zamiany dowolnego błędu w `false`.

Subsumption pomaga wybrać bardziej ograniczone przeciążenie. Mechanizm porównuje strukturę znormalizowanych ograniczeń i tożsamość ograniczeń atomowych, a nie dowolną matematyczną równoważność formuł. Dwa osobno zapisane wyrażenia o takim samym sensie nie muszą być tym samym atomem. Budowanie silniejszego conceptu przez ponowne użycie nazwanego słabszego conceptu pomaga zachować oczekiwaną relację.

Wymagania semantyczne nadal mają znaczenie. Kompilator może sprawdzić, czy `a == b` daje odpowiedni wynik typowy, ale zwykle nie dowiedzie przechodniości równości dla wszystkich danych. Standardowe concepts rozróżniają składniowe spełnienie ograniczeń od modelowania pełnego kontraktu. Napisanie operatora zwracającego losowy `bool` nie tworzy poprawnej relacji równoważności, mimo poprawnej sygnatury.

Constraints nie zapewniają poprawności arytmetyki dla wszystkich wartości. `std::integral<T>` potwierdza kategorię typu, lecz nie wyklucza przepełnienia konkretnej sumy. Ograniczenia danych runtime nadal należą do kontraktu funkcji, walidacji wejścia lub reprezentacji uniemożliwiającej błędne stany.

## Drugi przykład

Silniejszy concept ponownie używa słabszego. Dzięki temu przeciążenie z operacją rezerwacji może zostać wybrane dla wektora, a zwykły odczyt rozmiaru pozostaje dostępny dla listy.

~~~cpp
#include <cassert>
#include <concepts>
#include <cstddef>
#include <list>
#include <vector>

template<class T>
concept Sized = requires(const T& value) {
    { value.size() } -> std::convertible_to<std::size_t>;
};

template<class T>
concept Reservable = Sized<T> && requires(T& value, std::size_t n) {
    value.reserve(n);
};

template<Sized T>
int category(const T&) { return 1; }

template<Reservable T>
int category(const T&) { return 2; }

int main() {
    assert(category(std::list<int>{}) == 1);
    assert(category(std::vector<int>{}) == 2);
}
~~~

Przykład bada dostępność operacji i relację ograniczeń; nie wywołuje `reserve`. Funkcja służąca rzeczywiście do rezerwowania musiałaby przyjmować modyfikowalny obiekt i określić skutki ewentualnej realokacji. Sama przynależność do conceptu nie wykonuje ani nie wymusza tej operacji.

## Porównanie i decyzje

Preferuj istniejący standardowy concept, jeśli dokładnie odpowiada wymaganiu algorytmu. Własny nazwany concept jest przydatny, gdy kilka funkcji współdzieli specyficzny kontrakt domenowy. Nie żądaj pełnego `regular`, jeśli algorytm potrzebuje jedynie odczytu pojedynczej metody: nadmiarowe wymagania niepotrzebnie odrzucają wartościowe typy, na przykład niekopiowalnych właścicieli.

**Ćwiczenie.** Czy `requires(T x) { x.valid(); }` gwarantuje, że `x.valid()` zwróci prawdę?

**Odpowiedź.** Nie. Gwarantuje tylko poprawność wywołania dla takiego wyrażenia. Można dodatkowo sprawdzić typ wyniku, lecz wynik zależny od stanu obiektu nadal trzeba odczytać i obsłużyć podczas wykonania.

Źródła: [requires-expression](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.req), [ograniczenia atomowe](https://timsong-cpp.github.io/cppwp/n4950/temp.constr.atomic), [uporządkowanie ograniczeń](https://timsong-cpp.github.io/cppwp/n4950/temp.constr.order).

## Powiązane tematy

- [SFINAE](03_specialization_i_sfinAE.md)
- [Concept normalization i subsumption](../zaawansowane/08_concepts_normalization_i_subsumption.md)
- [Ranges](../06_biblioteka_standardowa/06_ranges_i_views.md)

