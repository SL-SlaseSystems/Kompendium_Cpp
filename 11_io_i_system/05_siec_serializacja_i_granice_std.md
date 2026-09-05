[← Spis treści](../README.md)

# Sieć, serializacja i granice std

C++23 nie zawiera kompletnej standardowej biblioteki TCP/UDP ani uniwersalnego formatu serializacji. Programy używają API systemowych, Boost.Asio, standalone Asio, bibliotek HTTP/RPC albo platformowych frameworków. Są to zależności zewnętrzne o własnych modelach wykonania, błędów i anulowania.

Niezależnie od biblioteki TCP jest strumieniem bajtów, nie strumieniem wiadomości. Pojedynczy odczyt może zwrócić fragment rekordu albo dane kilku rekordów. Dla niepustego żądanego bufora zero zwrócone przez typowe strumieniowe API odczytu oznacza uporządkowany koniec danych, a nie pustą wiadomość aplikacji. Protokół potrzebuje framingu: stałego rozmiaru, delimitera, prefiksu długości lub samopisującego formatu.

~~~cpp
#include <array>
#include <cassert>
#include <cstdint>

std::uint32_t decode_be32(const std::array<std::uint8_t, 4>& bytes) {
    return (static_cast<std::uint32_t>(bytes[0]) << 24)
         | (static_cast<std::uint32_t>(bytes[1]) << 16)
         | (static_cast<std::uint32_t>(bytes[2]) << 8)
         | static_cast<std::uint32_t>(bytes[3]);
}

int main() {
    const std::array<std::uint8_t, 4> bytes{0x00, 0x00, 0x01, 0x00};
    assert(decode_be32(bytes) == 256);
}
~~~

Serializacja nie może kopiować surowych bajtów dowolnego obiektu i zakładać przenośności. Padding, endianess, rozmiar typów, wersja schema, alignment i lifetime mogą się różnić. Zdefiniuj jawne typy pól, limity długości, kodowanie tekstu oraz zachowanie wobec nieznanych pól.

Niezaufany pakiet wymaga walidacji przed alokacją i arytmetyki odpornej na overflow. Timeout, backpressure, częściowy zapis i anulowanie są częścią poprawności, nie dodatkiem. TLS zapewnia inne własności niż framing i uwierzytelnienie aplikacyjne.

Zapis również może przyjąć tylko fragment bufora. Warstwa transportu musi zachować niewysłaną część i wznowić operację bez duplikowania danych. Kolejka wyjściowa potrzebuje limitu; bez backpressure powolny odbiorca może spowodować nieograniczony wzrost pamięci całej usługi.

## Jak to działa krok po kroku

Odbiornik powinien przechowywać bufor nieprzetworzonych bajtów i stan parsera. Po odczycie dodaje nowe dane, sprawdza dostępność nagłówka, waliduje długość, a dopiero potem czeka na resztę rekordu. Jeśli ma cały rekord, przekazuje go logice aplikacji i kontynuuje analizę pozostałych bajtów. Jeden odczyt nie wyznacza granic rekordów.

Podczas wysyłania zapamiętaj liczbę zaakceptowanych bajtów. Następna próba zaczyna się od pozostałej części bufora. Nie wysyłaj ponownie całej wiadomości po częściowym sukcesie. Dla asynchronicznego API bufor musi żyć do zakończenia operacji zgodnie z kontraktem biblioteki; lokalny napis zniszczony po zleceniu zapisu jest częstym źródłem błędu lifetime.

## Pogłębienie mechanizmu

Prefiks długości również jest niezaufany. Jeżeli ogłasza kilka gigabajtów, parser nie powinien automatycznie alokować takiego bufora. Limit ustal przed alokacją, a przy sprawdzaniu dostępności danych stosuj arytmetykę odporną na przepełnienie. Warunek `length <= buffer.size() - header_size` jest użyteczny po wcześniejszym sprawdzeniu, że bufor zawiera cały nagłówek.

Endianowość opisuje kolejność bajtów reprezentacji wielobajtowej liczby. Nie określa szerokości liczby, znakowości, kodowania tekstu ani wersji protokołu. Typy `uint8_t` i `uint32_t` są dostępne tylko na implementacjach z odpowiednimi dokładnymi szerokościami. W protokole oktetowym możesz jawnie wymagać ośmiobitowego bajtu i traktować brak tego warunku jako nieobsługiwaną platformę.

Obiekt zawierający `std::string` ma reprezentację zarządzającą napisem, nie sam uniwersalny zapis tekstu. Skopiowanie `sizeof(object)` bajtów może utrwalić adresy i padding, a nie wartość logiczną. Nawet trivially copyable nie oznacza stabilnego formatu między maszynami. Serializuj pola według schematu, a następnie konstruuj legalne obiekty odbiorcy z odczytanych wartości.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <climits>
#include <cstddef>
#include <cstdint>
#include <span>

static_assert(CHAR_BIT == 8, "Protokol wymaga oktetow");
enum class State { need_more, ready, invalid };
struct Frame {
    State state;
    std::size_t consumed;
    std::span<const unsigned char> payload;
};

Frame parse(std::span<const unsigned char> bytes) {
    if (bytes.size() < 4) return {State::need_more, 0, {}};
    const std::uint32_t n = (std::uint32_t{bytes[0]} << 24)
                         | (std::uint32_t{bytes[1]} << 16)
                         | (std::uint32_t{bytes[2]} << 8)
                         | std::uint32_t{bytes[3]};
    if (n > 1024) return {State::invalid, 0, {}};
    if (n > bytes.size() - 4) return {State::need_more, 0, {}};
    return {State::ready, 4 + n, bytes.subspan(4, n)};
}

int main() {
    const std::array<unsigned char, 7> bytes{0, 0, 0, 2, 'O', 'K', 9};
    const auto frame = parse(bytes);
    assert(frame.state == State::ready && frame.consumed == 6);
    assert(frame.payload.size() == 2 && frame.payload[1] == 'K');
    assert(parse(std::span{bytes}.first(5)).state == State::need_more);
    const std::array<unsigned char, 4> too_large{0, 0, 4, 1};
    assert(parse(too_large).state == State::invalid);
}
~~~

Parser pozostawia siódmy bajt do następnego rekordu. Wynik jest widokiem na oryginalny bufor: realokacja lub usunięcie jego danych unieważnia `payload`. Funkcja nie obsługuje całego transportu, ale precyzyjnie rozróżnia brak danych, gotowy rekord i naruszenie limitu. Po EOF stan `need_more` może oznaczać uciętą wiadomość, a nie powód dalszego oczekiwania.

## Porównanie i decyzje

Format tekstowy ułatwia diagnostykę, binarny pozwala ściślej kontrolować rozmiar i typy. Oba potrzebują wersjonowania, limitów i walidacji. Gotowa biblioteka serializacji może zapewnić schemat i obsługę ewolucji pól, ale nie zastępuje decyzji o maksymalnym rozmiarze ani tożsamości nadawcy. Wybieraj ją według wymagań interoperacyjności i trwałości danych.

## Ćwiczenie z odpowiedzią

Dlaczego po wyniku `ready` nie można od razu wykonać `erase` początkowych bajtów bufora, a dopiero potem odczytać `payload`? Widok nadal wskazuje na usuwane lub przesuwane dane. Najpierw przetwórz wynik, skopiuj potrzebną wartość albo zastosuj bufor o gwarancjach lifetime odpowiednich dla odbiorców.

Kontrakt strumienia TCP: [IETF RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html). Reguły serializacji powyżej są projektem warstwy aplikacyjnej, a nie dodatkową gwarancją TCP.

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Fuzzing](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
