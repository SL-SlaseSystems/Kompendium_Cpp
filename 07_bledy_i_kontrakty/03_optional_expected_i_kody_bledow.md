[← Spis treści](../README.md)

# optional, expected i kody błędów

Nie każdy brak wyniku jest wyjątkiem. `std::optional<T>` reprezentuje wartość albo jej brak bez informacji o przyczynie. `std::expected<T, E>` z C++23 reprezentuje sukces albo jawny błąd. `std::error_code` niesie kod i kategorię, często przy interoperacyjności z API systemowym.

~~~cpp
#include <cassert>
#include <optional>
#include <string_view>

std::optional<int> find_level(std::string_view name) {
    if (name == "admin") {
        return 10;
    }
    return std::nullopt;
}

int main() {
    const auto level = find_level("guest");
    assert(!level.has_value());
    assert(find_level("admin").value_or(0) == 10);
}
~~~

`optional` jest dobry, gdy brak jest wystarczającą informacją, np. wyszukiwanie. Jeśli klient musi odróżnić błąd parsowania od braku uprawnień, użyj `expected` albo typu domenowego. Wywołanie `.value()` bez wartości rzuca; `operator*` bez wartości narusza precondition. Sprawdzaj stan, korzystaj z `value_or` świadomie lub używaj operacji monadycznych dostępnych w odpowiedniej wersji standardu.

`expected<T, E>` jest wartością i nie propaguje błędu automatycznym operatorem odpowiadającym Rustowemu `?`. Błąd powinien mieć stabilną, strukturalną postać; tekst można generować na granicy UI lub logowania. Wsparcie implementacyjne `std::expected` może wymagać nowszej biblioteki standardowej nawet przy fladze C++23.

Wyjątki i expected nie są wzajemnie wykluczające. Biblioteka może używać wyjątków dla złamania podstawowego kontraktu, a expected dla oczekiwanej odmowy operacji. Najważniejsza jest spójność na poziomie warstwy i jasne zasady konwersji.

## Jak to działa krok po kroku

`find_level("guest")` konstruuje pusty optional. Nie istnieje ukryta wartość `int`, którą można legalnie odczytać mimo pustego stanu. `has_value` albo konwersja do bool sprawdza obecność. Dla `optional<bool>` wynik testu dotyczy obecności, a nie przechowywanego bool: optional zawierający `false` nadal spełnia `if (value)`. Dopiero dereferencja po sprawdzeniu odczytuje zawartość.

`value_or(0)` wybiera wartość lub zamiennik i zwraca wartość odpowiedniego typu, nie referencję do magazynu optional. Argument funkcji jest obliczany przed wywołaniem, więc `value_or(expensive())` uruchomi kosztowną funkcję także przy obecnej wartości. W C++23 `or_else` pozwala zapisać leniwą gałąź braku, a `transform` mapuje istniejącą wartość. `and_then` stosuj, gdy wywoływana funkcja już zwraca optional i nie chcesz zagnieżdżenia.

Expected ma zawsze jeden z dwóch logicznych stanów: wartość sukcesu albo błąd. Konstrukcja `unexpected(error)` jawnie wybiera ścieżkę błędu, co jest szczególnie ważne, gdy T i E są tym samym typem. `expected<void, E>` opisuje operację bez dodatkowych danych sukcesu. Stan nadal trzeba sprawdzić; samo zwrócenie expected nie wymusza, aby klient go obsłużył, dlatego warto oznaczać istotne funkcje `[[nodiscard]]`.

## Pogłębienie mechanizmu

Dereferencja pustego optional i dereferencja expected zawierającego błąd naruszają precondition w C++23. `.value()` daje alternatywę sprawdzającą, która zgłasza odpowiedni wyjątek. Dla expected jest to `bad_expected_access<E>` z informacją o błędzie. Nie zamieniaj jednak każdego jawnego wyniku na wyjątek bez decyzji na poziomie API: utracisz przewidywalną kontrolę przepływu, dla której wybrano typ wyniku.

Oba typy przechowują aktywny obiekt jako część własnego magazynu, bez wymaganej osobnej alokacji samej otoczki. Zawartość, np. string, może oczywiście alokować. Przeniesienie optional zwykle nie resetuje obecności źródła: źródło może nadal zawierać przeniesione T. Jeśli logika wymaga zużycia i opróżnienia, zrób to jawnie. Referencje do wartości tracą ważność po `reset`, zniszczeniu lub odpowiedniej zmianie stanu właściciela.

`error_code` składa się z liczby i kategorii nadającej jej znaczenie. Sam numer nie identyfikuje błędu między różnymi kategoriami. `error_condition` służy do porównań z bardziej przenośnymi warunkami, np. kategorią ogólną. Własna kategoria powinna mieć trwały czas życia. Komunikat generowany przez `message()` służy diagnostyce i może wymagać alokacji; nie jest stabilnym protokołem dla innego programu.

Operacje monadyczne nie wykonują automatycznie całej obsługi błędów za klienta. `transform` zmienia sukces, pozostawiając istniejącą porażkę; `transform_error` w expected zmienia reprezentację błędu, a `and_then` łączy kroki zwracające zgodny typ wyniku. Nazwy pomagają rozdzielić logikę, lecz trzeba pilnować kategorii wartości i kosztu kopiowania. Wywołanie na lvalue może przekazywać referencję, a na przenoszonym wyniku umożliwiać zużycie zawartości; stan źródła po przeniesieniu nadal podlega regułom danego typu.

## Drugi przykład

Parser rozróżnia pusty argument, niepoprawną składnię i wartość spoza zakresu. `from_chars` pozwala sprawdzić zarówno status konwersji, jak i miejsce zatrzymania. Przykład wymaga biblioteki z obsługą `std::expected` z C++23.

~~~cpp
#include <cassert>
#include <charconv>
#include <expected>
#include <string_view>
#include <system_error>

enum class PortError { empty, syntax, range };

[[nodiscard]] std::expected<int, PortError> parse_port(std::string_view text) {
    if (text.empty()) return std::unexpected{PortError::empty};
    int value = 0;
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec == std::errc::result_out_of_range)
        return std::unexpected{PortError::range};
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size())
        return std::unexpected{PortError::syntax};
    if (value < 1 || value > 65535)
        return std::unexpected{PortError::range};
    return value;
}

int main() {
    const auto good = parse_port("443");
    assert(good && *good == 443);
    const auto trailing = parse_port("80x");
    assert(!trailing && trailing.error() == PortError::syntax);
    const auto large = parse_port("70000");
    assert(!large && large.error() == PortError::range);
}
~~~

Sprawdzenie końcowego wskaźnika odrzuca częściowo poprawny tekst, taki jak `80x`. Sama poprawna konwersja początkowej liczby byłaby niewystarczająca. `from_chars` nie pomija białych znaków tak jak część starszych funkcji i nie akceptuje dowolnej składni locale. To świadomy, wąski kontrakt parsera; ewentualne przycinanie wejścia powinno być oddzielnym krokiem.

## Porównanie i decyzje

Optional wybieraj, gdy „nie ma” jest pełną informacją domenową. Expected jest lepszy, gdy odbiorca ma podjąć różne działania zależnie od przyczyny. Wyjątki upraszczają propagację przez warstwy, które nie potrafią niczego naprawić. `error_code` pomaga integrować systemowe kategorie, ale często wymaga osobnego miejsca na wynik. Nie koduj porażki magiczną liczbą, jeśli pełna dziedzina tej liczby jest legalnym wynikiem.

**Ćwiczenie.** Dlaczego `optional<int>{0}` nie powinno oznaczać tego samego co `nullopt`? **Odpowiedź:** zero jest istniejącą wartością. Rozdzielenie obecności od zawartości pozwala zachować całą dziedzinę typu i uniknąć specjalnego traktowania legalnych danych. Dla licznika „zero znalezionych elementów” może być pełnym sukcesem operacji.

Źródła reguł: [C++23: optional](https://timsong-cpp.github.io/cppwp/n4950/optional), [expected](https://timsong-cpp.github.io/cppwp/n4950/expected), [kody błędów](https://timsong-cpp.github.io/cppwp/n4950/syserr).

## Powiązane tematy

- [Wyjątki](01_wyjatki_try_catch_throw.md)
- [Assertions i preconditions](04_assertions_preconditions_i_contracts.md)
- [tuple, variant i any](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
