[← Spis treści](../README.md)

# string, string_view i tekst

`std::string` jest właścicielskim, dynamicznym ciągiem elementów `char`. Przechowuje bajty i zapewnia ciągłość pamięci; nie rozumie automatycznie znaków Unicode ani grapheme clusters. `std::string_view` jest niewłaścicielskim widokiem na ciąg bajtów i nie zapewnia terminatora na końcu wybranego fragmentu.

~~~cpp
#include <cassert>
#include <cctype>
#include <string>
#include <string_view>

std::string normalize_name(std::string_view name) {
    std::string result{name};
    if (!result.empty()) {
        result.front() = static_cast<char>(std::toupper(
            static_cast<unsigned char>(result.front())));
    }
    return result;
}

int main() {
    assert(normalize_name("ada") == "Ada");
    const std::string text = "C++23";
    assert(std::string_view{text}.substr(0, 3) == "C++");
}
~~~

Funkcje klasyfikujące z `<cctype>` wymagają wartości reprezentowalnej jako `unsigned char` albo `EOF`; przekazanie ujemnego `char` może być UB. Przykład wykonuje bezpieczne rzutowanie, ale nadal przetwarza tylko bajt według bieżącej locale, nie pełne Unicode.

Kodowanie UTF-8 mieści się w `std::string`, lecz `size()` zwraca liczbę bajtów. Indeks może wskazać środek wielobajtowej sekwencji. Normalizacja, podział na grapheme clusters, zmiana wielkości liter i porównania językowe wymagają wyspecjalizowanej biblioteki, np. ICU; nie są częścią kompletnego modelu tekstu w C++23.

`c_str()` zwraca wskaźnik do danych zakończonych nullem, użyteczny przy C API. Wskaźnik może zostać unieważniony przez modyfikację napisu. Nul wewnątrz `std::string` jest dozwolony, ale C API może potraktować go jako koniec.

## Jak to działa krok po kroku

W pierwszym przykładzie parametr `name` kopiuje tylko opis zakresu, a nie jego znaki. Instrukcja `std::string result{name}` tworzy niezależnego właściciela. Zmiana pierwszego bajtu dotyczy już kopii, więc wejściowy napis pozostaje niezmieniony. Zwrócenie wartości pozwala kompilatorowi zastosować NRVO; nawet bez tej optymalizacji poprawność nie zależy od życia lokalnego bufora, ponieważ wynik jest przenoszony lub kopiowany zgodnie z regułami języka.

Inaczej działa `std::string_view{text}.substr(0, 3)`: powstaje drugi widok, ograniczony do trzech pierwszych elementów istniejącego napisu. Operacja nie tworzy nowej tablicy znaków. Jeśli potrzebujesz trwałego wycinka do zapisania w obiekcie, `std::string{wycinek}` jest jawnym momentem przejęcia własności. Warto rozdzielić etap parsowania bez kopii od etapu utrwalania wybranych pól.

Przy wyszukiwaniu sprawdzaj wynik względem `npos`, zanim dodasz jeden lub wykonasz indeksowanie. `npos` jest maksymalną wartością typu rozmiaru, więc arytmetyka bez sprawdzenia może zawinąć się modulo. `substr(pos, count)` obcina zbyt duże `count`, lecz `pos > size()` powoduje `std::out_of_range`. Dla `remove_prefix(n)` obowiązuje warunek `n <= size()`; nie jest to funkcja walidująca dowolną liczbę.

## Pogłębienie mechanizmu

Widok nie obiecuje niezmienności źródła. Nie pozwala modyfikować znaków przez własny interfejs, ale właściciel nadal może je zmienić. Zastąpienie istniejącego elementu przez `text[0] = 'X'` nie wymaga przenoszenia bufora i jest widoczne przez widok. Operacja mogąca unieważnić bufor, taka jak rozbudowa napisu, wymaga ponownego utworzenia widoków. Nie opieraj bezpieczeństwa na zaobserwowanej pojemności ani implementacyjnej optymalizacji małych napisów, zwanej SSO.

Konstruktor ze wskaźnika C wyznacza długość do pierwszego zera; konstruktor ze wskaźnika i długości zachowuje także wewnętrzne zera. Analogicznie literał `"a\0b"sv` ma długość trzy, podczas gdy `std::string_view{"a\0b"}` ma długość jeden. Końcowy terminator napisu właścicielskiego nie należy do zakresu jego zwykłych elementów. W szczególności odczyt `view[view.size()]` narusza wymagania widoku, choć podobna pozycja w `std::string` ma specjalnie określone znaczenie.

Od C++20 literał `u8"..."` zawiera elementy `char8_t`. `std::u8string` opisuje jednostki kodowe UTF-8, ale nadal nie sprawdza poprawności całej sekwencji podczas każdej modyfikacji. `wchar_t` także nie jest przenośną obietnicą pełnego znaku Unicode: jego szerokość i kodowanie zależą od implementacji. W API zapisuj osobno format kodowania i reguły własności.

Dla protokołów liczbowych `from_chars` i `to_chars` z `<charconv>` rozdzielają konwersję od własności napisu. Parser dostaje jawne granice bufora i zwraca pozycję końcową oraz kod błędu. Nie wymaga terminatora ani aktualnej locale. Dołączanie fragmentów w pętli może natomiast wielokrotnie alokować: jeśli znasz całkowity rozmiar, zarezerwuj miejsce w jednym napisie i dopisuj do niego. Warto mierzyć alokacje całej operacji, a nie tylko koszt skopiowania małego widoku.

## Drugi przykład

Parser oddziela nazwę od wartości bez alokowania. Zwracany widok pożycza pamięć argumentu; to istotna część kontraktu funkcji.

~~~cpp
#include <cassert>
#include <optional>
#include <string>
#include <string_view>

std::optional<std::string_view> value_part(std::string_view line) {
    const auto equal = line.find('=');
    if (equal == std::string_view::npos) {
        return std::nullopt;
    }
    return line.substr(equal + 1);
}

int main() {
    const std::string line = "mode=fast";
    const auto borrowed = value_part(line);
    assert(borrowed && *borrowed == "fast");
    const std::string saved{*borrowed};
    assert(saved == "fast");
    assert(value_part("key=")->empty());
    assert(!value_part("missing"));
}
~~~

Rozróżniamy brak separatora i poprawną pustą wartość. `optional` odpowiada za obecność pola, a `string_view` za jego lokalizację; żaden z tych typów nie przedłuża życia `line`. Wywołanie parsera z tymczasowym `std::string` i zachowanie wyniku na później stworzyłoby wiszący widok po zakończeniu pełnego wyrażenia.

## Porównanie i decyzje

Przyjmuj `string_view` przez wartość do synchronicznego odczytu, `string&` do modyfikowania cudzego napisu, a `string` do przejęcia tekstu przechowywanego na później. Nie zwracaj bezrefleksyjnie widoku z każdej funkcji tylko dlatego, że jest mały. Bezpieczny wynik właścicielski często upraszcza życie klienta bardziej niż oszczędność pojedynczej kopii.

**Ćwiczenie.** Czy przechowanie `value_part(std::string{"a=b"})` w zmiennej i odczyt w następnej instrukcji jest poprawne? **Odpowiedź:** nie. Tymczasowy właściciel znika na końcu instrukcji inicjalizacji. Rozwiązaniem jest nazwana zmienna `string` żyjąca dłużej niż widok albo skopiowanie wyniku do `string`, zanim tymczasowy właściciel zostanie zniszczony.

Źródła reguł: [C++23: string_view](https://timsong-cpp.github.io/cppwp/n4950/string.view), [wymagania basic_string](https://timsong-cpp.github.io/cppwp/n4950/string.require).

## Powiązane tematy

- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Strumienie i formatowanie](../11_io_i_system/01_strumienie_i_formatowanie.md)
- [Sieć i serializacja](../11_io_i_system/05_siec_serializacja_i_granice_std.md)
