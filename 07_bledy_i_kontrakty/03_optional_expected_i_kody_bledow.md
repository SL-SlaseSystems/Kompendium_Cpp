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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „optional, expected i kody błędów”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wykrycie niespełnionego warunku, zbudowanie informacji o błędzie, propagację przez granice oraz odtworzenie prawidłowego stanu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd możliwy do obsłużenia od naruszenia precondition i zagwarantuj sprzątanie niezależnie od wybranej ścieżki. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ błędu, zachowany kontekst, stan obiektów po porażce i spełniony poziom exception safety. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Obsługa błędów zaczyna się od klasyfikacji niepowodzenia: naruszenie kontraktu programisty, spodziewany brak wyniku, błąd środowiska albo awaria uniemożliwiająca kontynuację. Mechanizm raportowania powinien odpowiadać tej kategorii. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `optional` modeluje obecność albo brak wartości bez informacji o przyczynie. `expected<T,E>` przenosi typowany błąd i wspiera kompozycję, natomiast kody błędów są użyteczne na granicach bez wyjątków i w interfejsach systemowych.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „optional, expected i kody błędów” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: optional, expected i kody błędów
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „optional, expected i kody błędów”, oceniaj częstotliwość błędu, koszt ścieżki sukcesu, możliwość pominięcia wyniku, zgodność z RAII i czytelność kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wyjątki](01_wyjatki_try_catch_throw.md)
- [Assertions i preconditions](04_assertions_preconditions_i_contracts.md)
- [tuple, variant i any](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)

