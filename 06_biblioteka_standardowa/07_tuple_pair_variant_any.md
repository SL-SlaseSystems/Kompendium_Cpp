[← Spis treści](../README.md)

# tuple, pair, variant i any

`std::pair<T, U>` i `std::tuple<Ts...>` są typami produktowymi: przechowują wszystkie składowe naraz. `std::variant<Ts...>` jest typem sumy: przechowuje dokładnie jedną alternatywę. `std::any` przechowuje jedną wartość dowolnego kopiowalnego typu i odzyskuje ją przez kontrolowany rzut runtime.

~~~cpp
#include <any>
#include <cassert>
#include <string>
#include <tuple>
#include <variant>

int main() {
    const auto record = std::tuple{7, std::string{"Ada"}, true};
    const auto& [id, name, active] = record;

    std::variant<int, std::string> answer = std::string{"ok"};
    std::any payload = 42;

    assert(id == 7 && name == "Ada" && active);
    assert(std::get<std::string>(answer) == "ok");
    assert(std::any_cast<int>(payload) == 42);
}
~~~

Structured bindings mogą rozpakować pair, tuple, tablicę i typy o odpowiednim protokole. Użycie `auto` kopiuje składowe, a `auto&` lub `const auto&` wiąże referencje. Typy referencji ukryte pod structured binding mają szczegółowe reguły; przy lifetime-sensitive kodzie sprawdzaj rzeczywisty typ inicjalizatora.

Tuple jest dobry dla lokalnego, oczywistego zestawu danych lub generycznej infrastruktury. Gdy pola mają trwałe znaczenie domenowe, nazwana struktura daje lepszy kontrakt. Variant najlepiej reprezentuje zamknięty zbiór przypadków; visitor powinien być wyczerpujący. Any jest bardziej dynamiczny, ale traci compile-time exhaustiveness i wymaga znajomości dokładnego typu przy `any_cast`.

`std::optional<T>` opisuje obecność lub brak jednego `T`, więc jest prostszy niż `variant<monostate, T>`. `expected<T, E>` opisuje sukces albo błąd i również powinien być preferowany nad anonimową tuple flagi z wartością.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „tuple, pair, variant i any”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `enum class` ogranicza zasięg nazw i nie konwertuje się niejawnie do liczby. Surowa `union` wymaga ręcznego śledzenia aktywnego członu, natomiast `variant` przechowuje tag i kontroluje lifetime wariantu.
- `pair` i `tuple` modelują produkt typów, `variant` bezpieczną sumę rozłączną, a `any` type erasure pojedynczej kopiowalnej wartości. Im słabsza informacja statyczna, tym więcej kontroli i błędów przechodzi do runtime.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „tuple, pair, variant i any” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: tuple, pair, variant i any
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „tuple, pair, variant i any”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [enum, union i variant](../04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)
- [optional i expected](../07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)
- [Type erasure](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)

