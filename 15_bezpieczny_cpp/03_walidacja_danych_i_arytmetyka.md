[← Spis treści](../README.md)

# Walidacja danych i arytmetyka

Bezpieczny parser ma ustalić, co dokładnie oznacza wejście, zanim posłuży ono do indeksowania, alokacji albo wyboru operacji. Samo sprawdzenie, że tekst zawiera cyfry, nie dowodzi poprawności rozmiaru. Liczba może nie mieścić się w typie, przekraczać limit usługi lub opisywać fragment poza buforem. Te warunki należą do różnych warstw i powinny mieć osobne testy. Podobnie poprawnie zakodowany napis może być niedozwolonym identyfikatorem domenowym.

Dobrą granicą jest funkcja przyjmująca nieufne bajty i zwracająca zweryfikowaną wartość albo nazwany błąd. Dalej przekazujemy już rozpoznaną liczbę, zakres lub obiekt domenowy. W produkcyjnym API warto rozróżnić błędną składnię, przekroczenie zakresu typu i przekroczenie limitu produktu. Poniższe krótkie przykłady używają `optional`, aby skoncentrować się na warunkach arytmetycznych; brak wartości zawsze oznacza odrzucenie wejścia.

## Jak to działa krok po kroku

Najpierw ustalamy gramatykę. W protokole pole `offset` może oznaczać wyłącznie dziesiętne cyfry ASCII, bez znaku, spacji i separatorów tysięcy. Nie należy wtedy używać parsera zależnego od lokalizacji ani automatycznie „naprawiać” danych. `from_chars` zgłasza wynik przez kod błędu i wskaźnik końca. Sukces konwersji prefiksu nie wystarcza: `42abc` musi zostać odrzucone, jeżeli kontrakt wymaga całego pola. Ograniczenie długości pola chroni również przed niepotrzebną pracą nad ogromnym wejściem. Szczegóły kodów błędu oraz wskaźnika końca określa [N4950, charconv.from.chars](https://raw.githubusercontent.com/cplusplus/draft/n4950/source/utilities.tex).

Następnie sprawdzamy relacje. Dla fragmentu o początku `offset` i długości `length` w buforze rozmiaru `size` nie zaczynamy od `offset + length <= size`. Dodawanie może zawinąć wynik typu bez znaku. Najpierw wymagamy `offset <= size`, a następnie `length <= size - offset`. Odejmowanie jest bezpieczne dopiero po pierwszym warunku. Ta kolejność daje dowód, że późniejsze utworzenie widoku mieści się w buforze.

~~~cpp
#include <array>
#include <cassert>
#include <charconv>
#include <cstddef>
#include <limits>
#include <optional>
#include <span>
#include <string_view>
#include <system_error>

std::optional<std::size_t> decimal(std::string_view text) {
    if (text.empty() || text.size() > 32) return std::nullopt;
    for (char c : text) {
        if (c < '0' || c > '9') return std::nullopt;
    }
    std::size_t value{};
    auto [end, error] = std::from_chars(
        text.data(), text.data() + text.size(), value);
    if (error != std::errc{} || end != text.data() + text.size()) {
        return std::nullopt;
    }
    return value;
}

std::optional<std::span<const int>> fragment(
    std::span<const int> input, std::size_t offset, std::size_t length) {
    if (offset > input.size()) return std::nullopt;
    if (length > input.size() - offset) return std::nullopt;
    return input.subspan(offset, length);
}

int main() {
    const std::array input{10, 20, 30, 40};
    auto offset = decimal("1");
    auto length = decimal("2");
    assert(offset && length);
    auto view = fragment(input, *offset, *length);
    assert(view && view->size() == 2 && (*view)[1] == 30);
    assert(fragment(input, 4, 0));
    assert(!fragment(input, 5, 0));
    assert(!fragment(input, 1, std::numeric_limits<std::size_t>::max()));
    assert(!decimal("-1") && !decimal("2x") && !decimal(" 2"));
}
~~~

Pusty zakres na końcu bufora jest tutaj poprawny. To decyzja kontraktu, a nie przypadek do usunięcia przez warunek `offset < size`. Widok nie przejmuje pamięci: po zwróceniu `span` oryginalny bufor nadal musi istnieć. Walidacja granic nie rozwiązuje czasu życia ani równoczesnej modyfikacji danych. Jeśli inny wątek może zmienić rozmiar kontenera między kontrolą a użyciem, potrzebne jest także właściwe zarządzanie dostępem.

## Pogłębienie mechanizmu

Typ bez znaku nie jest automatycznie „bezpieczną liczbą”. Jego arytmetyka jest wykonywana modulo potęga dwójki, więc zawinięcie jest określone przez język, lecz zwykle błędne dla rozmiaru pakietu. Przepełnienie arytmetyki typu ze znakiem może natomiast prowadzić do niezdefiniowanego zachowania. Sprawdzenie wyniku po niebezpiecznym działaniu jest za późne. Reguły opisują N4950, [basic.fundamental](https://raw.githubusercontent.com/cplusplus/draft/n4950/source/basic.tex) i [expr.pre](https://raw.githubusercontent.com/cplusplus/draft/n4950/source/expressions.tex).

Konwersja też wymaga dowodu. Wartość `-1` zamieniona na `size_t` staje się dużą dodatnią wartością. Najpierw sprawdzamy dziedzinę wejścia i reprezentowalność, dopiero później rzutujemy. Szerszy typ pośredni pomaga tylko wtedy, gdy naprawdę mieści wszystkie możliwe wyniki. `uint64_t` nie jest uniwersalną ochroną przed mnożeniem dwóch wartości `uint64_t`. Rozwiązaniem jest kontrola nierówności przed działaniem albo dobrze określona biblioteka arytmetyki sprawdzanej.

Granica tekstowa ma osobną semantykę. `string::size()` liczy elementy `char`, a dla umówionego UTF-8 zwykle bajty, nie punkty kodowe ani znaki widoczne dla użytkownika. Ucięcie po dowolnym bajcie może rozdzielić sekwencję. Walidację kodowania, normalizację oraz politykę dopuszczalnych znaków trzeba określić osobno. Parser liczb ASCII celowo nie przyjmuje innych znaków wyglądających jak cyfry. Dla nazw użytkowników decyzja może być inna, lecz powinna być wspólna przy zapisie, porównywaniu i autoryzacji.

Normalizacja nie zastępuje parsowania. Najpierw należy wiedzieć, czy pole jest nazwą, ścieżką czy liczbą protokołu. Dwa systemy, z których jeden odrzuca nietypowy zapis, a drugi go normalizuje, mogą przypisać temu samemu wejściu inne znaczenia. Testy powinny obejmować również osadzone zero, niepoprawne kodowanie i znaki łączące, jeżeli takie dane docierają do interfejsu. Nie wolno zakładać, że zewnętrzny napis jest zakończony zerem.

Limit rozmiaru wejścia i limit wyniku nie są wymienne. Skompresowany dokument o małej liczbie bajtów może po rozwinięciu zająć dużo pamięci, a krótki zapis liczby może sterować ogromną liczbą iteracji. Dla parserów zagnieżdżonych określamy także maksymalną głębokość oraz liczbę elementów. Budżet powinien być sprawdzany podczas przetwarzania, zanim powstanie kosztowna reprezentacja, i obejmować cały dokument zamiast zerować się dla każdego pola. Podobnie wielokrotne poprawne zapytania mogą przekroczyć budżet pojedynczego klienta.

Zestaw testów granicznych budujemy z nierówności użytych w kodzie. Dla każdego limitu sprawdzamy wartość dokładnie na granicy, tuż poniżej oraz tuż powyżej, o ile istnieje w typie. Dodajemy zero, pusty tekst, największą reprezentowalną wartość i kombinacje pól, które osobno są poprawne, lecz razem nie mieszczą się w buforze. Fuzzing może rozszerzyć ten zbiór, ale nie zastępuje nazwanych oczekiwań dotyczących wyniku i kosztu.

## Drugi przykład

Przy alokacji tablicy zapisujemy budżet w tej samej jednostce co wynik: bajtach. Najpierw odejmujemy nagłówek od dostępnego budżetu, potem dzielimy pozostałe miejsce przez szerokość elementu. Dzięki temu nie trzeba obliczać ryzykownego iloczynu, aby sprawdzić, czy iloczyn jest dozwolony. Nawet poprawny rozmiar nie gwarantuje dostępnej pamięci; rzeczywista alokacja może jeszcze zgłosić błąd.

~~~cpp
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <utility>

std::optional<std::size_t> packet_size(
    std::size_t count, std::size_t width,
    std::size_t header, std::size_t budget) {
    if (header > budget) return std::nullopt;
    const auto remaining = budget - header;
    if (width != 0 && count > remaining / width) return std::nullopt;
    return header + count * width;
}

std::optional<std::size_t> accepted_count(std::int64_t raw) {
    if (raw < 0 || raw > 1000 || !std::in_range<std::size_t>(raw)) {
        return std::nullopt;
    }
    return static_cast<std::size_t>(raw);
}

int main() {
    const auto count = accepted_count(100);
    assert(count);
    assert(packet_size(*count, 4, 16, 1024) == 416);
    assert(packet_size(252, 4, 16, 1024) == 1024);
    assert(!packet_size(253, 4, 16, 1024));
    assert(!packet_size(0, 4, 17, 16));
    assert(!packet_size(std::numeric_limits<std::size_t>::max(), 4, 16, 1024));
    assert(packet_size(500, 0, 16, 1024) == 16);
    assert(!accepted_count(-1) && !accepted_count(1001));
}
~~~

Szerokość zero jest obsłużona jawnie: wynik zawiera sam nagłówek. Jeżeli domena zabrania pustych elementów, odrzucamy zero osobnym warunkiem zamiast liczyć na dzielenie przez zero. Takie doprecyzowanie odróżnia bezpieczną arytmetykę od pełnej walidacji biznesowej. Warto też ograniczyć liczbę rekordów niezależnie od liczby bajtów, jeśli każdy rekord powoduje kosztowną operację.

## Porównanie i decyzje

Walidacja syntaktyczna odpowiada na pytanie, czy zapis należy do gramatyki. Walidacja zakresu sprawdza reprezentowalność i budżet. Walidacja semantyczna bada relacje, na przykład czy początek poprzedza koniec i czy klient może zamówić daną ilość. Żadnej z tych warstw nie zastępuje sanitizer: może wykryć wykonane naruszenie, ale nie ustanawia polityki wejścia. Powtarzanie identycznych kontroli w wielu miejscach utrudnia zmianę kontraktu, dlatego warto zamykać zweryfikowane wartości w małych typach.

**Zadanie 1.** Bufor ma 64 bajty. Określ dopuszczalność par `(64, 0)`, `(64, 1)` oraz `(1, SIZE_MAX)` bez dodawania argumentów.

<details><summary>Rozwiązanie</summary>

Pierwsza para opisuje poprawny pusty fragment. Druga przekracza pozostałe zero bajtów. Trzecia odpada, ponieważ długość jest większa niż `64 - 1`. Nie obliczamy sumy, która mogłaby się zawinąć.

</details>

**Zadanie 2.** Nagłówek zajmuje 24 bajty, element 12, budżet wynosi 100. Ile elementów można przyjąć i co zmienia limit domenowy pięciu elementów?

<details><summary>Rozwiązanie</summary>

Pozostaje 76 bajtów, więc ograniczenie pamięci dopuszcza `76 / 12`, czyli sześć elementów. Limit domenowy zmniejsza wynik do pięciu. Obie kontrole są potrzebne: opisują inne wymagania i mogą zmieniać się niezależnie.

</details>

## Powiązane tematy

- [Mapa działu](README.md)
- [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)
- [Bezpieczne API i typy](02_bezpieczne_api_i_typy.md)
- [Arytmetyka, przepełnienia i float](../02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md)
