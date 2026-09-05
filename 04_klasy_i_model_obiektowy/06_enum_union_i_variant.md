[← Spis treści](../README.md)

# enum, union i variant

`enum class` definiuje typ wyliczeniowy bez niejawnego eksportowania enumeratorów do otaczającego zakresu i bez automatycznej konwersji do liczby. Jest zwykle bezpieczniejszy od nieograniczonego `enum`. Typ bazowy można wskazać jawnie, co jest istotne dla protokołu lub ABI, ale nie rozwiązuje wszystkich problemów serializacji.

~~~cpp
#include <cassert>
#include <string>
#include <type_traits>
#include <variant>

enum class Status : unsigned char { idle, running, failed };

using Result = std::variant<int, std::string>;

std::string describe(const Result& result) {
    return std::visit([](const auto& value) {
        using T = std::remove_cvref_t<decltype(value)>;
        if constexpr (std::is_same_v<T, std::string>) {
            return value;
        } else {
            return std::to_string(value);
        }
    }, result);
}

int main() {
    const Status status = Status::running;
    const Result result = 42;
    assert(status != Status::failed);
    assert(describe(result) == "42");
}
~~~

Przykład wykorzystuje fakt, że `std::to_string` przyjmuje liczbę; w realnym visitorze różne alternatywy często wymagają `if constexpr` lub zestawu przeciążonych lambd. `std::variant` jest bezpieczną unią dyskryminowaną: pamięta aktywną alternatywę, prawidłowo zarządza lifetime i wymusza kontrolowany dostęp.

Wbudowany `union` przechowuje kilka pól w tej samej pamięci, ale programista odpowiada za wiedzę, które jest aktywne, zwłaszcza dla typów nietrywialnych. Czytanie nieaktywnego elementu jest na ogół niedozwolone. Union pozostaje użyteczny w ABI, embedded i implementacji niskopoziomowych struktur, lecz typowy kod aplikacyjny powinien wybierać `variant`.

`std::get<T>` rzuca `std::bad_variant_access`, gdy aktywny jest inny typ; `std::get_if<T>` zwraca wskaźnik lub `nullptr`. Variant może wejść w `valueless_by_exception`, choć dobrze zaprojektowane typy alternatyw czynią ten stan rzadkim.

## Jak to działa krok po kroku

`enum class Status` tworzy odrębny typ, którego wartości zapisuje się przez kwalifikację, na przykład `Status::running`. Typ bazowy określa reprezentację całkowitą, ale nie sprawia, że każdy bitowy wzorzec ma nazwany enumerator. Dla typu o ustalonej reprezentacji konwersja liczby może dać poprawną wartość enumu bez odpowiadającej nazwy. Dane z protokołu wymagają zatem osobnego sprawdzenia dozwolonych przypadków.

`variant<int, string>` rezerwuje miejsce zdolne pomieścić jedną alternatywę wraz z informacją o stanie aktywności. Konstrukcja z `42` wybiera `int`. Wywołanie `visit` rozpoznaje aktywną alternatywę i przekazuje ją do odpowiedniego wywołania visitora. Kod visitora musi być poprawny dla każdej możliwej alternatywy, nawet jeśli konkretny test uruchamia tylko jedną z nich.

Zmiana aktywnej alternatywy może zakończyć życie starej wartości i rozpocząć nowe w tym samym obiekcie `variant`. Referencja do dawnej wartości nie staje się automatycznie referencją do alternatywy innego typu. Interfejs `get` sprawdza aktywność, ale nie naprawia obserwatorów zachowanych przed zmianą stanu.

## Pogłębienie mechanizmu

Domyślny `variant<Ts...>` próbuje skonstruować pierwszą alternatywę. Jeżeli nie jest ona domyślnie konstruowalna, odpowiedni konstruktor wariantu jest usunięty. `std::monostate` jako pierwsza alternatywa pozwala reprezentować jawny pusty stan. Nie jest tym samym co `valueless_by_exception`, które oznacza brak aktywnej alternatywy po określonym niepowodzeniu operacji zmieniającej stan.

`get<T>` wymaga, aby `T` występował na liście alternatyw dokładnie raz. Wariant może zawierać powtarzający się typ, ale wtedy dostęp i konstrukcję trzeba rozróżniać indeksem. `get_if` przyjmuje wskaźnik do wariantu i zwraca pusty wskaźnik, gdy typ lub indeks nie jest aktywny. Jest wygodny, kiedy brak konkretnej alternatywy jest zwykłą gałęzią programu, a nie wyjątkowym naruszeniem oczekiwania.

Dla zwykłego `std::visit` rezultaty wszystkich potencjalnych wywołań visitora muszą mieć zgodny wymagany typ i kategorię wartości. Lambda zwracająca raz liczbę, a raz napis nie tworzy automatycznie nowego wariantu. Można jawnie wybrać wspólny typ wyniku lub użyć odpowiedniego przeciążenia `visit<R>` dostępnego od C++20. Przy wielu wariantach liczba kombinacji typów rośnie jak iloczyn liczb alternatyw.

Wbudowany `union` nie przechowuje automatycznie znacznika aktywnego pola. Dla nietrywialnych alternatyw może wymagać ręcznej konstrukcji i destrukcji. Odczyt nieaktywnego pola jest zasadniczo niedozwolony, z wąskimi wyjątkami, takimi jak odpowiednio użyty common initial sequence klas standard-layout. Nie jest to ogólna technika reinterpretowania `float` jako `unsigned`. Do legalnego kopiowania reprezentacji odpowiednich trywialnie kopiowalnych typów służy `std::bit_cast` od C++20.

Enum flagowy wymaga osobno zdefiniowanych operacji bitowych i polityki dopuszczalnych kombinacji. `enum class` celowo ich nie dostarcza przez niejawną konwersję do liczby. `std::to_underlying` od C++23 zwraca wartość w typie bazowym, ale nie waliduje, czy odpowiada jednemu z zadeklarowanych enumeratorów. Serializacja musi też uwzględniać kolejność bajtów i format protokołu.

## Drugi przykład

Jawne alternatywy uniemożliwiają przechowanie jednocześnie danych sukcesu i błędu jako niezależnych, sprzecznych pól. `monostate` oznacza brak jeszcze otrzymanej odpowiedzi.

~~~cpp
#include <cassert>
#include <string>
#include <variant>

struct Success { int count; };
struct Failure { std::string message; };
using Reply = std::variant<std::monostate, Success, Failure>;

int main() {
    Reply reply;
    assert(std::holds_alternative<std::monostate>(reply));
    reply.emplace<Success>(Success{3});
    if (const auto* success = std::get_if<Success>(&reply)) {
        assert(success->count == 3);
    } else {
        assert(false);
    }
    reply.emplace<Failure>(Failure{"invalid input"});
    assert(std::get_if<Success>(&reply) == nullptr);
    assert(std::get<Failure>(reply).message == "invalid input");
}
~~~

## Porównanie i decyzje

Używaj enumu do skończonego zestawu nazw bez różnych danych. Wybierz `variant`, gdy poszczególne stany mają różne pola. `optional<T>` odpowiada prostemu „jest lub nie ma T”, a `expected<T, E>` w C++23 szczególnie dobrze opisuje wynik lub błąd. Surowa unia jest narzędziem dla warstwy implementacyjnej wymagającej kontroli reprezentacji, nie domyślnym modelem stanu aplikacji.

**Ćwiczenie.** Czy `Status value = static_cast<Status>(200);` dowodzi, że `value` oznacza legalny stan aplikacji, jeśli typ bazowy to `unsigned char`?

**Odpowiedź.** Nie. Liczba mieści się w reprezentacji, ale może nie odpowiadać żadnej dopuszczalnej wartości domenowej. Parser powinien rozpoznać dozwolone kody i zwrócić błąd dla pozostałych, zanim taki stan trafi do dalszej logiki.

Źródła: [wyliczenia](https://timsong-cpp.github.io/cppwp/n4950/dcl.enum), [unie](https://timsong-cpp.github.io/cppwp/n4950/class.union), [variant](https://timsong-cpp.github.io/cppwp/n4950/variant), [visit](https://timsong-cpp.github.io/cppwp/n4950/variant.visit).

## Powiązane tematy

- [tuple, pair, variant i any](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
- [Wyjątki](../07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md)
- [Layout i triviality](../zaawansowane/03_layout_alignment_padding_i_triviality.md)
