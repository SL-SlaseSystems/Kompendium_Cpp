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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „enum, union i variant”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `enum class` ogranicza zasięg nazw i nie konwertuje się niejawnie do liczby. Surowa `union` wymaga ręcznego śledzenia aktywnego członu, natomiast `variant` przechowuje tag i kontroluje lifetime wariantu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „enum, union i variant” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: enum, union i variant
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „enum, union i variant”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [tuple, pair, variant i any](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
- [Wyjątki](../07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md)
- [Layout i triviality](../zaawansowane/03_layout_alignment_padding_i_triviality.md)
