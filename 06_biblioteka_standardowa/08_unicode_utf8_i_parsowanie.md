[← Spis treści](../README.md)

# Unicode, UTF-8 i ścisłe parsowanie

**Wymagania wstępne:** `string`, `string_view`, zakresy pamięci, `optional` i podstawy obsługi błędów. Przykłady używają C++23.

Program przetwarzający tekst musi jednocześnie pilnować reprezentacji i znaczenia. Liczba bajtów określa rozmiar bufora, ale nie liczbę liter widzianych przez użytkownika. Poprawna reprezentacja Unicode nie gwarantuje z kolei, że napis spełnia reguły identyfikatora, mieści się w limicie formularza albo przedstawia dozwoloną liczbę. Łączenie tych warstw w jeden niejawny krok prowadzi do trudnych błędów na granicach systemu.

Praktyczny kontrakt powinien osobno określić kodowanie, dopuszczalność błędnych sekwencji, jednostkę limitu długości oraz własność pamięci. Dla pola liczbowego potrzebna jest także gramatyka: czy dozwolony jest plus, biały znak, separator tysięcy lub końcowy komentarz. Nazwa „parsowanie tekstu” jest za szeroka, aby sama rozstrzygała te decyzje.

## Jak to działa krok po kroku

Rozróżnij cztery poziomy. Bajt jest jednostką transportu i pamięci; w przykładach zakładamy osiem bitów. Jednostka kodowa jest elementem konkretnego kodowania: UTF-8 używa jednostek ośmiobitowych, więc tutaj ich liczba odpowiada liczbie bajtów. Punkt kodowy jest numerem w przestrzeni Unicode. Rozszerzony klaster grafemowy przybliża znak postrzegany przez użytkownika i może obejmować kilka punktów kodowych. Definicje kodowania opisuje [Unicode Standard, rozdział 3](https://www.unicode.org/versions/Unicode16.0.0/core-spec/chapter-3/).

Litera `é` może wystąpić jako U+00E9 albo sekwencja U+0065 U+0301. Te reprezentacje mają różne długości UTF-8 i różną liczbę punktów kodowych. W typowym podziale każda stanowi jeden rozszerzony klaster grafemowy. Sekwencje emoji mogą być jeszcze dłuższe, dlatego zwiększenie indeksu o jeden punkt kodowy nie wystarcza do poprawnego przesuwania kursora. Segmentację określają reguły [UAX #29](https://www.unicode.org/reports/tr29/).

~~~cpp
#include <cassert>
#include <climits>
#include <concepts>
#include <string>
#include <string_view>

std::string copy_utf8_bytes(std::u8string_view text) {
    static_assert(CHAR_BIT == 8);
    if (text.empty()) {
        return {};
    }
    // Odczyt reprezentacji obiektowej przez char jest dozwolony.
    return std::string{reinterpret_cast<const char*>(text.data()), text.size()};
}

int main() {
    static_assert(std::same_as<decltype(u8"x"[0]), const char8_t&>);
    const std::u8string composed = u8"\u00E9";
    const std::u8string decomposed = u8"e\u0301";
    assert(composed.size() == 2);
    assert(decomposed.size() == 3);
    assert(composed != decomposed);

    const std::string wire = copy_utf8_bytes(composed);
    assert(wire.size() == 2);
    assert(static_cast<unsigned char>(wire[0]) == 0xC3);
    assert(static_cast<unsigned char>(wire[1]) == 0xA9);

    const std::u8string with_zero{u8"A\0B", 3};
    const auto bytes = copy_utf8_bytes(with_zero);
    assert(bytes.size() == 3 && bytes[1] == '\0');
    assert(copy_utf8_bytes({}).empty());
}
~~~

`char8_t` odróżnia jednostki UTF-8 od zwykłego `char`, lecz `u8string` nadal jest kontenerem. Można umieścić w nim niepoprawne sekwencje; typ nie dowodzi poprawności zawartości. Funkcja kopiująca zachowuje reprezentację do API przyjmującego bajty. Nie dekoduje, nie naprawia i nie normalizuje tekstu. Jawny zakres zachowuje wewnętrzny znak zerowy, który wiele funkcji C potraktowałoby jako koniec napisu.

Porównanie napisów w przykładzie sprawdza jednostki kodowe, więc daje nierówność. Nie jest to dowód, że użytkownik zobaczy inne słowo. Jeżeli domena wymaga utożsamienia kanonicznie równoważnych zapisów, trzeba zdefiniować normalizację i zastosować ją we właściwym miejscu. NFC, NFD, NFKC oraz NFKD mają różne przeznaczenie. Normalizacja kompatybilności może usuwać rozróżnienia ważne dla aplikacji; nie należy wybierać jej jedynie dlatego, że daje więcej równych napisów. [UAX #15](https://www.unicode.org/reports/tr15/) określa te formy.

## Pogłębienie mechanizmu

C++23 nie dostarcza kompletnej standardowej walidacji UTF-8, normalizacji, segmentacji grafemów ani językowego porównywania tekstu. Zmiana `string` na `u8string` nie dodaje tych algorytmów. Potrzebujesz biblioteki realizującej wymagany standard Unicode oraz jawnej polityki wersji i błędów. Wymagania dla danych trwałych mogą różnić się od potrzeb interfejsu, który jedynie wyświetla otrzymany tekst.

Walidator musi wykrywać między innymi ucięte sekwencje, błędne bajty kontynuacji, zapisy nadmiarowe, zakodowane surogaty oraz wartości poza dozwolonym zakresem. Policzenie bajtów niebędących kontynuacją nie jest walidacją i nie daje bezpiecznego dekodera. Dlatego ten rozdział nie buduje skróconej wersji takiego algorytmu. Dla granic bezpieczeństwa ważna jest zgodność wszystkich etapów: filtr i odbiorca nie mogą inaczej interpretować tych samych danych.

Limity dobieraj do zasobu. Limit bajtów ogranicza pamięć i transfer; limit grafemów lepiej odpowiada długości pola widocznego w formularzu. Zwykle potrzebujesz obu. Bardzo długi ciąg znaków łączących może tworzyć mało grafemów, a nadal wymagać dużo pamięci i pracy. Normalizacja może też zmienić długość reprezentacji, więc limit na wejściu nie zastępuje kontroli wyniku przekształcenia.

Cięcie według limitu wymaga osobnej decyzji. `substr(0, n)` ogranicza jednostki kodowe i może pozostawić fragment niepoprawnej sekwencji UTF-8. Cięcie na granicy punktu kodowego zachowuje kodowanie, ale nadal może oddzielić znak łączący albo część sekwencji emoji. Przy skracaniu tekstu widocznego użytkownikowi wybieraj granice grafemów dostarczone przez algorytm segmentacji. Dla transportu dopuszczającego fragmentację można dzielić bajty inaczej, o ile odbiorca składa pełną sekwencję przed interpretacją. To kontrakt protokołu, a nie własność metody `substr`.

Do pól liczbowych protokołu pasuje `from_chars`, ponieważ operuje na jawnym zakresie i nie zależy od bieżącej locale. Sukces konwersji oznacza jednak rozpoznanie poprawnego prefiksu, a nie całego pola. Trzeba sprawdzić jednocześnie `ec` i wskaźnik `ptr`. Wersja całkowitoliczbowa nie pomija początkowych białych znaków, nie przyjmuje plusa, a minus dopuszcza tylko dla typu ze znakiem. Przy podstawie szesnaście nie konsumuje automatycznie prefiksu `0x`. To cechy gramatyki, a nie braki wymagające przypadkowego „naprawiania” wejścia. [N4950: `from_chars`](https://timsong-cpp.github.io/cppwp/n4950/charconv.from.chars).

## Drugi przykład

Parser ramki przyjmuje format `liczba_bajtów:ładunek`. Metadane są ASCII, a ładunek pozostaje surowym zakresem bajtów. Akceptacja ramki nie stwierdza poprawności UTF-8: taką walidację musi wykonać kolejny etap, jeśli protokół wymaga tekstu. Funkcja zwraca widok pożyczający pamięć wejścia.

~~~cpp
#include <cassert>
#include <charconv>
#include <cstddef>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>

std::optional<std::string_view> payload_of(std::string_view packet) {
    constexpr std::size_t max_payload = 1024;
    constexpr std::size_t max_header = 20;
    if (packet.size() > max_payload + max_header + 1) {
        return std::nullopt;
    }
    const auto colon = packet.find(':');
    if (colon == std::string_view::npos || colon == 0 || colon > max_header) {
        return std::nullopt;
    }
    const auto number = packet.substr(0, colon);
    if (number.size() > 1 && number.front() == '0') {
        return std::nullopt; // Kontrakt wymaga zapisu kanonicznego.
    }
    std::size_t declared = 0;
    const char* end = number.data() + number.size();
    const auto parsed = std::from_chars(number.data(), end, declared, 10);
    if (parsed.ec != std::errc{} || parsed.ptr != end || declared > max_payload) {
        return std::nullopt;
    }
    const auto payload = packet.substr(colon + 1);
    if (payload.size() != declared) {
        return std::nullopt;
    }
    return payload;
}

int main() {
    const std::string ordinary = "3:abc";
    const auto parsed = payload_of(ordinary);
    assert(parsed && *parsed == "abc");
    assert(payload_of("0:")->empty());
    assert(payload_of("2:\xC3\xA9")->size() == 2);
    assert(!payload_of("1:\xC3\xA9"));
    assert(!payload_of("+1:a"));
    assert(!payload_of(" 1:a"));
    assert(!payload_of("1x:a"));
    assert(!payload_of("01:a"));
    assert(!payload_of("99999999999999999999:"));
    assert(!payload_of("1025:"));
    assert(!payload_of(std::string_view{"1:a\0b", 5}));
}
~~~

Kolejność kontroli ogranicza pracę i upraszcza dowód poprawności. Najpierw ograniczamy cały bufor, potem długość pola liczbowego, dopiero później wykonujemy konwersję i porównujemy rozmiary. Nie obliczamy oczekiwanego końca przez dodanie niezweryfikowanej liczby do wskaźnika. Nie przydzielamy pamięci według deklaracji nadawcy. Warstwa odczytu z sieci musi niezależnie ograniczać ilość danych przed ich zgromadzeniem; parser nie cofnie kosztu już wykonanego odczytu.

Test z końcowym `x` pokazuje, dlaczego samo puste `ec` nie wystarcza. Test z zerem wewnętrznym pokazuje znaczenie długości przekazanej razem ze wskaźnikiem. Odrzucenie zer wiodących jest decyzją protokołu, a nie wymaganiem `from_chars`. Jeśli format je dopuszcza, można usunąć tę jedną kontrolę bez osłabiania sprawdzania granic.

## Porównanie i decyzje

Przetwarzaj składnię ASCII jako ASCII, a tekst użytkownika zgodnie z wybraną specyfikacją Unicode. Nie stosuj bajtowego `toupper` do implementacji porównywania nazw wielojęzycznych. Oddziel surową postać otrzymaną od nadawcy od ewentualnej postaci kanonicznej służącej wyszukiwaniu. Jeżeli normalizacja uczestniczy w równości kluczy, musi również uczestniczyć w odpowiadającym jej haszowaniu.

Środowisko kompilacji także ma dwie warstwy: obsługę języka i dostarczoną bibliotekę standardową. Samo `-std=c++23` nie gwarantuje wszystkich funkcji bibliotecznych. [Dokumentacja Clang](https://clang.llvm.org/cxx_status.html) prowadzi oddzielnie do informacji o zgodności i implementacjach bibliotek. Przykłady korzystają z niewielkiego, jawnego zestawu nagłówków i nie polegają na standardowym dekoderze Unicode.

**Ćwiczenie 1.** Formularz dopuszcza dwadzieścia znaków. Dlaczego `text.size() <= 20` nie wystarcza jako specyfikacja?

<details>
<summary>Rozwiązanie</summary>

Nie określa jednostki ani kodowania. Dla UTF-8 `size()` liczy jednostki kodowe, czyli przy ośmiobitowych bajtach bajty. Potrzebny jest osobny limit zasobów oraz uzgodniony limit punktów kodowych lub, zwykle bliżej oczekiwań użytkownika, grafemów liczonych przez właściwy algorytm segmentacji.

</details>

**Ćwiczenie 2.** Czy poprawna ramka `2:` z dwoma dowolnymi bajtami zawsze zawiera poprawny tekst UTF-8?

<details>
<summary>Rozwiązanie</summary>

Nie. Parser sprawdza format i długość binarną. Ładunek może zawierać błędną sekwencję, wewnętrzne zero albo tekst zabroniony przez reguły domeny. Kolejne etapy powinny jawnie wykonać walidację kodowania i walidację znaczenia, zachowując poprawny czas życia bufora.

</details>

Źródło uzupełniające: [N4950: literały napisowe i kodowanie UTF-8](https://timsong-cpp.github.io/cppwp/n4950/lex.string).

## Powiązane tematy

- [string, string_view i tekst](01_string_string_view_i_tekst.md)
- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Sieć, serializacja i granice std](../11_io_i_system/05_siec_serializacja_i_granice_std.md)
