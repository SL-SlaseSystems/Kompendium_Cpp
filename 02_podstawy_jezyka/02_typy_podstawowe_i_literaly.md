[← Spis treści](../README.md)

# Typy podstawowe i literały

C++ udostępnia typ logiczny `bool`, typy znakowe, całkowite i zmiennoprzecinkowe oraz `void`. Dokładne szerokości wielu typów są zależne od implementacji. Standard gwarantuje porządek minimalnych możliwości, ale nie zakładaj, że `int` zawsze ma 32 bity. Gdy protokół wymaga dokładnej szerokości, korzystaj z opcjonalnych typów `std::int32_t` i podobnych z `<cstdint>` oraz sprawdzaj ich dostępność.

~~~cpp
#include <cassert>
#include <cstdint>
#include <limits>
#include <type_traits>

int main() {
    int decimal = 42;
    int hex = 0x2A;
    std::uint32_t bits = 0b101010u;
    double ratio = 1.5;
    char32_t symbol = U'λ';

    static_assert(std::is_same_v<decltype(bits), std::uint32_t>);
    assert(decimal == hex && hex == static_cast<int>(bits));
    assert(ratio > 1.0);
    assert(symbol != U' ');
    static_assert(std::numeric_limits<unsigned char>::digits >= 8);
}
~~~

Sufiksy wpływają na typ literału: `42u` jest unsigned, `42LL` to `long long`, `1.0f` to `float`. Literały znakowe i napisowe mają kodowanie zależne od prefiksu: zwykłe, `u8`, `u`, `U` lub `L`. Od C++20 literał `u8"..."` składa się z `char8_t`, nie `char`.

Arytmetyka signed integer overflow powoduje undefined behavior, natomiast unsigned działa modulo `2^N`. To nie znaczy, że unsigned jest właściwym typem dla każdej liczby nieujemnej: mieszanie typów signed i unsigned może zaskoczyć przez usual arithmetic conversions. Do rozmiarów kolekcji używa się `std::size_t`, ale przy odejmowaniu i porównaniach trzeba uważać.

Wartości zmiennoprzecinkowe są zwykle zgodne z IEEE 754, lecz standard dopuszcza różnice. Porównanie wyników obliczeń przez dokładne `==` bywa niewłaściwe; tolerancja powinna wynikać z dziedziny problemu, nie z arbitralnego `epsilon`.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Typy podstawowe i literały”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Rozmiary typów całkowitych zależą od implementacji, ale standard gwarantuje minimalne zakresy i kolejność szerokości. Typ literału wynika z zapisu oraz sufiksu, co może zmienić wynik overload resolution i konwersji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Typy podstawowe i literały” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Typy podstawowe i literały
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Typy podstawowe i literały”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Operatory i konwersje](04_operatory_i_konwersje.md)
- [Random i numeryka](../11_io_i_system/04_random_i_numeryka.md)
- [Layout i alignment](../zaawansowane/03_layout_alignment_padding_i_triviality.md)

