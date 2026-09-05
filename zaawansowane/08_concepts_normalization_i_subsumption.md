[← Spis treści](../README.md)

# Concept normalization i subsumption

Constraints są normalizowane do atomic constraints połączonych logicznie. Subsumption określa, czy jeden zestaw wymagań jest co najmniej tak restrykcyjny jak drugi i wpływa na partial ordering przeciążeń. Kompilator nie wykonuje ogólnego dowodzenia logicznego; tożsamość atomic constraints zależy od ich pochodzenia po normalizacji.

~~~cpp
#include <cassert>
#include <concepts>

template<class T>
concept Numeric = std::integral<T> || std::floating_point<T>;

template<class T>
concept SignedNumeric = Numeric<T> && std::signed_integral<T>;

template<Numeric T>
constexpr int category(T) { return 1; }

template<SignedNumeric T>
constexpr int category(T) { return 2; }

int main() {
    static_assert(category(1) == 2);
    static_assert(category(1u) == 1);
    assert(category(1.0) == 1);
}
~~~

Nazwany concept `Numeric` jest ponownie użyty w `SignedNumeric`, więc kompilator może rozpoznać wspólne atomic constraint. Powtórzenie tekstowo podobnego wyrażenia w dwóch miejscach nie zawsze buduje tę samą tożsamość i może dać niejednoznaczność.

Kolejność `&&` i `||` ma znaczenie także dla podstawiania: constraints są sprawdzane w kolejności lewo–prawo z short-circuit. Najpierw umieszczaj wymaganie, które czyni późniejsze wyrażenie poprawnym. Nie używaj zwykłej funkcji bool zamiast concept, jeśli potrzebna jest normalizacja i subsumption.

Semantyczne wymagania standardowych concepts, np. equality preservation, mogą nie być sprawdzane. Typ może syntaktycznie spełniać concept i łamać jego semantykę, co narusza kontrakt algorytmu.

## Jak to działa krok po kroku

Dla wywołania `category(1)` parametr `T` jest `int`. Spełnione są zarówno `Numeric`, jak i `SignedNumeric`. Normalizacja drugiego conceptu rozwija ponowne użycie `Numeric<T>` i dokłada wymaganie `signed_integral<T>`. Wspólne ograniczenia pochodzą z tych samych definicji, więc bardziej ograniczone przeciążenie może zostać rozpoznane i zwrócić `2`.

Dla `unsigned int` warunek `signed_integral` jest niespełniony, więc drugiego kandydata nie ma wśród pasujących funkcji. Dla `double` spełnione jest `floating_point`, lecz nie `signed_integral`, bo ten drugi concept dotyczy typów całkowitych. Nazwa `SignedNumeric` jest zatem w przykładzie umowna: jej dokładny zapis ogranicza ją do całkowitych typów ze znakiem, a nie wszystkich liczb dopuszczających ujemne wartości.

## Pogłębienie mechanizmu

Atomic constraint powstaje z wyrażenia i mapowania parametrów szablonu. Tożsamość nie oznacza po prostu, że dwa wyrażenia zwracają taką samą wartość. Dwa osobno zapisane `sizeof(T) > 1` mogą dać dwa różne atomy. Kompilator nie dowodzi też ogólnych implikacji arytmetycznych, na przykład że `sizeof(T) > 8` implikuje `sizeof(T) > 4`. Aby stworzyć przewidywalną hierarchię, buduj bardziej szczegółowy concept przez ponowne użycie nazwanego conceptu bazowego.

Podczas normalizacji rozpatrywane są spójniki constraints i definicje concepts. Zwykłe wywołanie funkcji zwracającej `bool` pozostaje atomem; kompilator nie rozwija jej ciała jako logicznego dowodu. Schowanie `A<T> && B<T>` wewnątrz pomocniczej funkcji może więc zmienić subsumption mimo niezmienionego wyniku logicznego. Z tego powodu refaktoryzacja constraints wymaga sprawdzenia nie tylko akceptowanych typów, ale również wyboru przeciążeń.

Sprawdzanie koniunkcji i alternatywy ma short-circuit. W `HasType<T> && Test<typename T::type>` lewy warunek może zatrzymać badanie prawego, gdy składowy typ nie istnieje. Jednak nie każdy problem da się w ten sposób osłonić: samo tworzenie niepoprawnych mapowań parametrów podczas normalizacji podlega osobnym regułom. Celowo konstruowane requirements niepoprawne dla wszystkich możliwych podstawień także nie są poprawną techniką zastępowania `false`.

Concepty standardowe zawierają wymagania semantyczne. `regular_invocable` wymaga właściwości wykraczających poza samo istnienie `operator()`, a relacja porządkująca musi zachowywać odpowiednie prawa. Kompilator nie udowodni przechodniości komparatora dla wszystkich danych. `static_assert(std::strict_weak_order<Comp, T, T>)` bada część syntaktyczną kontraktu i nie legalizuje sortowania komparatorem, którego wynik zależy od zmieniającego się licznika.

## Drugi przykład

~~~cpp
#include <concepts>
#include <cstddef>

template<class T>
concept HasSize = requires(const T& value) {
    { value.size() } -> std::convertible_to<std::size_t>;
};
template<class T>
concept NoThrowSize = HasSize<T> && requires(const T& value) {
    { value.size() } noexcept;
};
template<HasSize T>
constexpr int route(const T&) { return 1; }
template<NoThrowSize T>
constexpr int route(const T&) { return 2; }
struct Fast { std::size_t size() const noexcept { return 4; } };
struct Fallible { std::size_t size() const { return 4; } };
int main() {
    static_assert(route(Fast{}) == 2);
    static_assert(route(Fallible{}) == 1);
}
~~~

`NoThrowSize` jawnie powtarza nazwę `HasSize`, a następnie dodaje osobne wymaganie braku wyjątków. Metody nie są wywoływane w `route`, więc ich brak `constexpr` nie przeszkadza w asercjach. Pierwszy typ wybiera ścieżkę o silniejszym kontrakcie, drugi pozostaje obsługiwany przez ścieżkę ogólną. Gdyby drugi concept napisać od zera jako podobną requires-expression, rozstrzygnięcie hierarchii nie musiałoby działać tak samo.

## Porównanie i decyzje

Hierarchię concepts projektuj jako część publicznego interfejsu biblioteki. Mały zestaw ponownie używanych wymagań daje czytelniejsze przeciążenia niż wiele niezależnych predykatów o podobnym znaczeniu. Dla zachowania zależnego jedynie od wartości runtime zwykłe rozgałęzienie jest prostsze; constraints wybierają funkcje na podstawie typów i stałych dostępnych podczas kompilacji.

**Ćwiczenie.** Czy zapis `(A<T> && B<T>)` zawsze jest lepszym przeciążeniem niż niezależnie zdefiniowane `C<T>`, jeśli programista wie, że `C` oznacza `A`? **Odpowiedź:** nie; potrzebna jest odpowiednia tożsamość atomów po normalizacji. Czy zmiana `&&` na `&` zachowuje mechanizm constraints? Nie; bitowy operator tworzy inne wyrażenie, nie daje tego samego podziału normalizacji i short-circuit.

Opis dotyczy C++23. **C++26** zmienia między innymi reguły fold-expanded constraints; nie przenoś nowszego rozstrzygnięcia przeciążeń na C++23 bez osobnego sprawdzenia. Źródło: [N4950: normalizacja i porządkowanie](https://timsong-cpp.github.io/cppwp/n4950/temp.constr).

### Składnia sprawdzalna i prawa semantyczne

Concept wymaga wyniku ograniczenia odpowiedniego typu logicznego; nie każda klasa posiadająca `operator bool` może zostać użyta jako atomic constraint w dowolnej postaci. Requires-expression sama produkuje wartość logiczną, co pomaga uporządkować takie sprawdzanie. Jej parametr lokalny, na przykład `T value`, opisuje hipotetyczny obiekt i nie oznacza, że podczas testowania conceptu zostanie wywołany konstruktor ani destructor.

Compound requirement używa typu wyrażenia według odpowiednich reguł `decltype((expr))`. Wymaganie `same_as<int>` odrzuci zatem operację zwracającą `int&`, choć zwykłe przypisanie do `int` byłoby możliwe. `convertible_to<int>` ma inny kontrakt i może zaakceptować więcej wyników. Wybór pomiędzy tymi wymaganiami powinien odpowiadać temu, czy algorytm potrzebuje dokładnej referencji, wartości czy jedynie konwersji.

Testuj hierarchię na typach granicznych: typ z metodą nieconst, typ zwracający referencję, typ z usuniętą operacją oraz typ rzucający. Takie przypadki pokazują, czy concept naprawdę wyraża zamierzoną granicę. Dla wymagań algebraicznych dodaj sprawdzanie praw na danych: syntaktyczna akceptacja komparatora nie wykazuje przechodniości ani spójności relacji równoważności.

Zwróć uwagę na stabilność wyników sprawdzania ograniczeń. Dostępność składowej nie powinna zmieniać się wskutek badania tego samego ograniczenia raz przed ukończeniem typu, a raz po jego kompletnej definicji. Metaprogram opierający wybór na takim czasie może naruszyć reguły wymagające spójności spełnienia constraints. Zamiast sondować niegotową klasę, odłóż sprawdzenie do miejsca, w którym jej interfejs jest kompletny i wszystkie jednostki translacji widzą ten sam kontrakt.

## Powiązane tematy

- [Concepts i requires](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
- [Overload resolution](06_overload_resolution_adl_i_hidden_friends.md)
- [Dependent names i SFINAE](07_dependent_names_two_phase_lookup_i_sfinae.md)

