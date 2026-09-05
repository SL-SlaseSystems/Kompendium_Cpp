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

Typ literału ustala się przed przypisaniem do zmiennej. W `long long n = 2'000'000'000 * 2;` oba operandy mogą mieć typ `int`, więc poszerzenie wyniku do `long long` nie naprawi wcześniejszego przepełnienia na implementacji z 32-bitowym `int`. Zapis `2'000'000'000LL * 2` zmienia typ obliczenia. Apostrof jest separatorem cyfr i nie wpływa na wartość.

Dla dziesiętnego literału całkowitego bez sufiksu kompilator wybiera pierwszy mieszczący wartość typ z listy `int`, `long`, `long long`. Dla zapisu szesnastkowego, ósemkowego i binarnego lista uwzględnia również odpowiednie typy unsigned. Dlatego dwa zapisy tej samej dużej wartości nie muszą mieć takiego samego typu. Prefiks zero oznacza zapis ósemkowy: `010` oznacza osiem, a nie dziesięć.

W wyrażeniu z małymi typami całkowitymi zachodzą promocje. Dwa `unsigned char` często są dodawane jako `int`, a dopiero wynik zostaje skonwertowany do typu celu. Reguły operatora dotyczą typu obliczenia, nie tylko typów przechowywanych zmiennych. Z kolei `-1` składa się z operatora minusa i dodatniego literału; minus nie jest częścią tokenu literału całkowitego.

## Pogłębienie mechanizmu

`sizeof(char)` zawsze wynosi jeden, ale ten jeden bajt zawiera `CHAR_BIT` bitów, co najmniej osiem. `char`, `signed char` i `unsigned char` są trzema różnymi typami. Znak zwykłego `char` zależy od implementacji. `std::byte` służy reprezentacji surowych bajtów; celowo nie udostępnia zwykłej arytmetyki liczbowej. `void` oznacza brak wartości lub nieokreślony typ obiektu za wskaźnikiem, lecz nie można utworzyć zwykłej zmiennej typu `void`.

Literał `"abc"` ma typ tablicy czterech stałych znaków: trzy litery i terminator. `"a\0b"` zawiera wewnętrzne zero, więc jego długość jako tablicy i długość interpretowana przez funkcję C są różne. Literał surowy `R"(C:\tmp\file)"` upraszcza zapis ukośników, ale nadal reprezentuje zwykły ciąg znaków. Prefiks kodowania nie zamienia jednostki kodowej w pełny znak Unicode: pojedynczy znak może potrzebować kilku jednostek UTF-8 lub UTF-16.

Dla liczb zmiennoprzecinkowych `min()` z `numeric_limits` oznacza najmniejszą dodatnią wartość znormalizowaną, natomiast `lowest()` najbardziej ujemną wartość skończoną. `epsilon()` opisuje odstęp wokół jedynki. Nie jest uniwersalnym progiem błędu dla liczb o dowolnej skali. Gdy dziedzina wymaga dokładnych wartości dziesiętnych, warto rozważyć reprezentację całkowitą ze zdefiniowaną skalą zamiast przypadkowej tolerancji.

## Drugi przykład

Granice typu można sprawdzać bez zakładania liczby jego bitów. Program pokazuje też różnicę między literałem zawierającym zero a napisem interpretowanym jako C string.

~~~cpp
#include <cassert>
#include <climits>
#include <limits>
#include <string_view>
#include <type_traits>

int main() {
    constexpr unsigned maximum = std::numeric_limits<unsigned>::max();
    static_assert(maximum + 1u == 0u);
    static_assert(sizeof(char) == 1);
    static_assert(CHAR_BIT >= 8);
    static_assert(std::is_same_v<decltype(1.0f), float>);
    static_assert(std::is_same_v<decltype(1.0), double>);

    static constexpr char raw[] = "a\0b";
    constexpr std::string_view all{raw, sizeof(raw) - 1};
    constexpr std::string_view c_text{raw};
    static_assert(all.size() == 3);
    static_assert(c_text.size() == 1);
    assert(all[2] == 'b');
}
~~~

W konstruktorze z długością `string_view` nie szuka terminatora i zachowuje wszystkie trzy znaki. Konstruktor przyjmujący sam wskaźnik ustala długość do pierwszego zera. Dane binarne i tekst z jawnie podaną długością należy zatem przekazywać interfejsem zawierającym rozmiar.

## Porównanie i decyzje

Wybieraj typ na podstawie zakresu i operacji. `int` jest dobrym domyślnym typem dla niedużych liczb ze znakiem. `std::size_t` odpowiada wynikom `sizeof` i rozmiarom obiektów, lecz nie jest naturalnym typem dla różnic mogących być ujemne. Sufiks `z` dodany w C++23 pozwala tworzyć literały związane z typem rozmiaru; `uz` daje `std::size_t`. Sam większy typ nie zastępuje sprawdzania przepełnienia na niezaufanych danych.

Dokładna szerokość typu nie określa kolejności bajtów, wyrównania ani formatu transmisji. Nawet używając `std::uint32_t`, serializuj protokół zgodnie z jego kolejnością bajtów. Dla przenośnej reprezentacji znaku oddziel kodowanie tekstu od signedness typu `char`.

**Ćwiczenie.** Dlaczego `double result = 5 / 2;` daje dwa zamiast dwa i pół? Jak uzyskać wynik ułamkowy?

**Odpowiedź.** Najpierw odbywa się dzielenie dwóch `int`, które obcina część ułamkową w kierunku zera. Dopiero dwa jest zamieniane na `double`. Zapis `5.0 / 2` lub konwersja jednego operandu przed dzieleniem powoduje obliczenie zmiennoprzecinkowe.

Źródła: [literały całkowite](https://timsong-cpp.github.io/cppwp/n4950/lex.icon), [typy podstawowe](https://timsong-cpp.github.io/cppwp/n4950/basic.fundamental), [literały napisowe](https://timsong-cpp.github.io/cppwp/n4950/lex.string).

## Powiązane tematy

- [Operatory i konwersje](04_operatory_i_konwersje.md)
- [Random i numeryka](../11_io_i_system/04_random_i_numeryka.md)
- [Layout i alignment](../zaawansowane/03_layout_alignment_padding_i_triviality.md)

