[← Spis treści](../README.md)

# Strumienie i formatowanie

Iostreams modelują wejście i wyjście przez `std::istream` i `std::ostream`. Standardowe obiekty to `cin`, `cout`, `cerr` i `clog`. Strumień zachowuje stan formatowania oraz flagi błędów, dlatego kolejna operacja może zależeć od wcześniejszego manipulatora.

~~~cpp
#include <cassert>
#include <iomanip>
#include <sstream>
#include <string>

int main() {
    std::ostringstream output;
    output << std::fixed << std::setprecision(2) << 12.5;
    assert(output.str() == "12.50");

    std::istringstream input{"42 Ada"};
    int id = 0;
    std::string name;
    input >> id >> name;
    assert(id == 42 && name == "Ada");
}
~~~

Po błędzie parsowania ustawiany jest `failbit`, a dalsze operacje również zawodzą, dopóki stan nie zostanie wyczyszczony. Sprawdzaj strumień bezpośrednio: `if (input >> value)`. `operator>>` dla napisu pomija whitespace; `std::getline` czyta cały wiersz. Łączenie obu wymaga obsłużenia pozostawionego znaku nowej linii.

`std::format` z C++20 i `std::print` z C++23 oferują format strings oraz bardziej jawny model niż trwałe manipulatory. Wsparcie zależy od wersji biblioteki standardowej, więc używaj feature-test macros. Biblioteka `{fmt}` jest zewnętrznym, historycznie powiązanym rozwiązaniem i nie jest tożsama z każdym szczegółem standardu.

Strumienie tekstowe podlegają locale, a kodowanie danych nie staje się automatycznie Unicode. Do protokołów binarnych nie używaj `operator<<` jako formatu serializacji; reprezentacja liczb, endianess, rozmiary i wersjonowanie wymagają jawnego kontraktu.

## Jak to działa krok po kroku

Odczyt `input >> id >> name` wykonuje dwie operacje na tym samym strumieniu. Pierwsza pomija początkowe białe znaki, próbuje rozpoznać liczbę i aktualizuje stan strumienia. Druga zaczyna w miejscu pozostawionym przez pierwszą. Jeśli liczby nie da się odczytać, ustawiony stan błędu wpływa także na następną operację. Łańcuch operatorów nie jest transakcją cofającą wcześniejsze odczyty.

Pętla powinna sprawdzać operację: `while (input >> value)`. Warunek `while (!input.eof())` sprawdza jedynie, czy wcześniejsza operacja odkryła koniec wejścia, i może dopuścić dodatkową nieudaną iterację. Po wyjściu z pętli odróżnij oczekiwany koniec danych od błędnego tokenu. Zależnie od formatu trzeba odrzucić cały rekord albo świadomie pominąć wadliwą część.

## Pogłębienie mechanizmu

`eofbit`, `failbit` i `badbit` opisują różne sytuacje. Samo osiągnięcie końca danych nie zawsze oznacza, że ostatnia wartość nie została odczytana. Na przykład końcowa liczba bez separatora może zostać rozpoznana poprawnie przy jednoczesnym ustawieniu `eofbit`. Konwersja strumienia do `bool` bada niepowodzenie, a nie po prostu brak końca pliku.

`clear()` resetuje stan, lecz nie usuwa błędnych znaków z bufora. Jeśli ponowisz ten sam odczyt bez przesunięcia wejścia, możesz trafić na ten sam token. Dla formatu wierszowego sensowną strategią jest odczyt całego wiersza i parsowanie go w osobnym strumieniu. Wtedy błąd jednego rekordu nie zatruwa stanu głównego strumienia.

Manipulatory również mają różne czasy działania. `std::hex`, `std::fixed` i precyzja pozostają ustawione, natomiast szerokość ustawiana `std::setw` jest zwykle zużywana przez następną odpowiednią operację formatowania. Funkcja drukująca na cudzym strumieniu powinna dokumentować zmianę stanu albo go odtworzyć. Budowanie lokalnego napisu przez `format` pozwala ograniczyć ten rodzaj ukrytej zależności.

## Drugi przykład

~~~cpp
#include <cassert>
#include <charconv>
#include <optional>
#include <string_view>
#include <system_error>

std::optional<int> parse_integer(std::string_view text) {
    if (text.empty()) return std::nullopt;
    int value{};
    const auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size()) {
        return std::nullopt;
    }
    return value;
}

int main() {
    assert(parse_integer("42") == 42);
    assert(!parse_integer("42kg"));
    assert(!parse_integer(" 42"));
    assert(!parse_integer("999999999999999999999999"));
    assert(!parse_integer(""));
}
~~~

`from_chars` zwraca pozycję zatrzymania i kod błędu. Sam sukces konwersji nie oznacza zużycia całego wejścia: `42kg` zawiera poprawny prefiks liczbowy. Funkcja wymaga obu warunków, przez co realizuje kontrakt całego tokenu. Odczyt całkowitoliczbowy `from_chars` nie pomija białych znaków i nie zależy od locale. Nie zakładaj więc identycznej gramatyki jak dla strumienia.

## Porównanie i decyzje

Strumienie dobrze łączą się z sekwencyjnym I/O i istniejącymi operatorami własnych typów. `from_chars` i `to_chars` nadają się do kontrolowanego, niezależnego od locale formatu liczbowego bez dodatkowych alokacji samej konwersji. `format` pozwala jawnie określić format tekstu dla użytkownika, a `print` połączyć formatowanie z wyjściem. Wybór zależy od gramatyki i kontraktu błędu, nie wyłącznie od krótszej składni.

Dla logowania wielowątkowego pojedynczy łańcuch `<<` nie jest automatycznie jedną niepodzielną wiadomością. `std::osyncstream` z C++20 pomaga grupować emisję, jeśli uczestnicy używają właściwego mechanizmu dla tego samego bufora. To osobne zagadnienie od tego, czy pojedynczy zapis do standardowego strumienia jest zabezpieczony przed data race.

## Ćwiczenie z odpowiedzią

Dlaczego `clear()` po nieudanym odczycie `"abc"` nie naprawia wejścia? Resetuje flagi, lecz `a` nadal czeka na odczyt. Ustal, czy parser ma zgłosić błąd, pominąć token czy pominąć wiersz. Każda strategia odpowiada innemu formatowi danych; bez takiej decyzji pętla może powtarzać błąd bez końca.

Źródła: [C++23, stan i formatowanie strumieni](https://timsong-cpp.github.io/cppwp/n4950/iostreams.base), [konwersje znakowe](https://timsong-cpp.github.io/cppwp/n4950/charconv).

## Powiązane tematy

- [Pliki i filesystem](02_pliki_i_filesystem.md)
- [string i tekst](../06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
- [Sieć i serializacja](05_siec_serializacja_i_granice_std.md)

