[← Spis treści](README.md)

# Ściąga C++23

To skrót składni, nie zamiennik rozdziałów o lifetime, błędach i kontraktach.

## Kompilacja

~~~text
clang++ -std=c++23 -Wall -Wextra -Wpedantic main.cpp -o app
clang++ -std=c++23 -g -O1 -fsanitize=address,undefined main.cpp -o app
~~~

## Typy, inicjalizacja i sterowanie

~~~cpp
#include <array>
#include <cassert>
#include <string>

int main() {
    const int count{3};
    constexpr double ratio = 0.5;
    auto name = std::string{"Ada"};
    std::array values{1, 2, 3};

    int total = 0;
    for (int value : values) total += value;
    if (const int doubled = total * 2; doubled > 10) total = doubled;

    assert(count == 3 && ratio == 0.5);
    assert(name == "Ada" && total == 12);
}
~~~

Podstawowe typy: `bool`, char types, signed/unsigned integer types, `float`, `double`, `long double`, `void`. Dokładne szerokości sprawdzaj przez `<cstdint>` i `numeric_limits`.

## Funkcje, referencje i zakresy

~~~cpp
#include <cassert>
#include <span>
#include <string>
#include <string_view>

std::string greet(std::string_view name) { return "Hi " + std::string{name}; }
int sum(std::span<const int> values) {
    int result{};
    for (int value : values) result += value;
    return result;
}

int main() {
    const int values[]{20, 22};
    assert(greet("Ada") == "Hi Ada");
    assert(sum(values) == 42);
}
~~~

`T` — wartość, `const T&` — obowiązkowy odczyt bez własności, `T&` — modyfikacja istniejącego obiektu, `T*` — często opcjonalny/niewłaścicielski dostęp, `unique_ptr<T>` — wyłączna własność, `shared_ptr<T>` — współdzielona własność.

## Klasy i value semantics

~~~cpp
#include <cassert>
#include <compare>

class Point {
public:
    Point(int x, int y) : x_{x}, y_{y} {}
    auto operator<=>(const Point&) const = default;
    int x() const noexcept { return x_; }
private:
    int x_;
    int y_;
};

int main() {
    const Point point{2, 4};
    assert(point.x() == 2);
    assert((point == Point{2, 4}));
}
~~~

Preferuj rule of zero. Jeśli wolno niszczyć obiekt przez wskaźnik do bazy, baza potrzebuje odpowiedniego wirtualnego destruktora; alternatywny projekt może zabraniać takiego usuwania przez chroniony niewirtualny destruktor. Używaj `override` i unikaj slicing przy przechowywaniu wartości bazowej.

## Szablony i concepts

~~~cpp
#include <cassert>
#include <concepts>

template<std::integral T>
constexpr T square(T value) { return value * value; }

template<class... T>
constexpr auto sum(T... values) { return (values + ... + 0); }

int main() {
    static_assert(square(4) == 16);
    assert(sum(10, 20, 12) == 42);
}
~~~

Dedukcja: `auto`, `decltype(expr)`, `decltype(auto)`, CTAD. Forwarding: dedukowane `T&&` wraz z `std::forward<T>(value)`. Constraints zapisuje concept lub trailing `requires`.

## Kontenery, algorytmy i ranges

~~~cpp
#include <algorithm>
#include <cassert>
#include <ranges>
#include <vector>

int main() {
    std::vector values{4, 1, 3, 2};
    std::ranges::sort(values);
    auto even = values | std::views::filter([](int value) { return value % 2 == 0; });
    assert(std::ranges::distance(even) == 2);
}
~~~

Domyślny kontener sekwencyjny: `vector`. Uporządkowane klucze: `map/set`. Średnio szybkie lookup bez kolejności: `unordered_map/set`. Sprawdzaj reguły invalidacji po każdej modyfikacji.

## Błędy

~~~cpp
#include <cassert>
#include <optional>

std::optional<int> half_even(int value) {
    if (value % 2 != 0) return std::nullopt;
    return value / 2;
}

int main() {
    assert(half_even(84) == 42);
    assert(!half_even(3));
}
~~~

Wyjątki — niezdolność do spełnienia zwykłego kontraktu i propagacja przez warstwy. `optional` — wartość lub brak. `expected<T,E>` — wynik albo jawny błąd w C++23. `error_code` — interoperacyjność z kategoriami kodów. Assertions — błędy programisty, nie niezaufane wejście.

## Współbieżność

~~~cpp
#include <atomic>
#include <cassert>
#include <thread>

int main() {
    std::atomic<int> value{0};
    std::jthread worker([&] { value.fetch_add(1); });
    worker.join();
    assert(value.load() == 1);
}
~~~

Preferuj `jthread`, RAII locks i prymitywy wysokiego poziomu. Data race to UB. `volatile` nie synchronizuje. Słabsze memory ordering stosuj dopiero po zapisaniu dowodu happens-before.

## Najważniejsze nagłówki

`<algorithm>`, `<array>`, `<atomic>`, `<chrono>`, `<concepts>`, `<filesystem>`, `<functional>`, `<memory>`, `<mutex>`, `<optional>`, `<ranges>`, `<span>`, `<string>`, `<string_view>`, `<thread>`, `<tuple>`, `<type_traits>`, `<unordered_map>`, `<utility>`, `<variant>`, `<vector>`.

## Pułapki, które trzeba umieć wyjaśnić

| Zapis lub sytuacja | Właściwy wniosek |
|---|---|
| `std::move(x)` | Rzutowanie do xvalue; wybór rzeczywistej kopii lub ruchu następuje później. |
| `std::move(const_object)` | Zachowuje `const`, więc często kończy się kopią. |
| `auto x = object` / `auto& x = object` | Wartość / alias; znak `&` zmienia zależność od oryginału. |
| `decltype(x)` / `decltype((x))` | Dla nazwy obiektu pierwszy może dać zadeklarowany typ, drugi uwzględnia kategorię wyrażenia. |
| `vector.reserve(n)` | Rezerwuje pojemność, ale nie tworzy `n` elementów. |
| `map[key]` | Może wstawić nowy element; do samego szukania użyj `find` lub `contains`. |
| `string_view` albo `span` | Widok nie przedłuża automatycznie życia danych. |
| `shared_ptr<T>` | Licznik własności nie synchronizuje dowolnych operacji na `T`. |
| `const`, `constexpr`, `constinit`, `consteval` | Cztery różne kontrakty; nie są zamiennikami „stałej”. |
| `noexcept` | Wyjątek opuszczający funkcję prowadzi do `terminate`; nie oznacza braku UB lub kodów błędu. |
| `if constexpr(false)` | Nie jest uniwersalnym sposobem ukrycia błędnego kodu poza szablonem. |
| `co_await` | Może zawiesić wykonanie; nie tworzy automatycznie wątku. |
| `relaxed` | Zapewnia właściwości operacji atomowej, ale nie publikuje automatycznie sąsiednich zwykłych danych. |
| `while (!stream.eof())` | Zwykle niewłaściwy warunek odczytu; sprawdzaj wynik samej operacji. |
| Poprawne `-fsyntax-only` | Potwierdza kompilowalność, nie linkowanie, wykonanie ani zgodność ABI. |

Do każdego wiersza znajdziesz pełne wyjaśnienie w rozdziałach i [katalogu 150 mechanizmów](150-zaawansowanych-mechanizmow-cpp.md). Rozwiązuj ćwiczenia w odpowiednich rozdziałach, zanim uznasz skrót za opanowany.

## Ściąga decyzyjna

Zaczynaj od wartości i rule of zero. Użyj `unique_ptr`, gdy obiekt wymaga dynamicznego lifetime i jednego właściciela; `shared_ptr` dopiero dla rzeczywiście współdzielonej własności; referencji lub widoku dla niepustego, niewłaścicielskiego dostępu o udowodnionym lifetime. Do kolekcji domyślnie rozważ `vector`, a inny kontener wybierz po wymaganiach invalidacji, lokalności i operacji.

~~~text
błąd spodziewany       -> expected<T, E> albo jawny kod
brak wartości          -> optional<T>
sprzątanie zasobu      -> RAII
zamknięty zbiór typów  -> variant
generyczny kontrakt    -> concept
współdzielony stan     -> najpierw mutex i inwariant
optymalizacja          -> najpierw profil i reprezentatywny benchmark
~~~

Przy każdym skrócie sprawdź cztery pytania: kto posiada dane, co invaliduje dostęp, jak raportowana jest porażka i czy typ koduje jednostkę lub stan. Jeśli odpowiedź znajduje się wyłącznie w komentarzu, rozważ silniejszy typ albo mniejszy interfejs.

## Powiązane tematy

- [Słownik](slownik.md)
- [Dalsza nauka](dalsza_nauka.md)
- [Źródła](zrodla.md)
