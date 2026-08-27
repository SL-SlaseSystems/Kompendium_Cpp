[← Spis treści](../README.md)

# Sieć, serializacja i granice std

C++23 nie zawiera kompletnej standardowej biblioteki TCP/UDP ani uniwersalnego formatu serializacji. Programy używają API systemowych, Boost.Asio, standalone Asio, bibliotek HTTP/RPC albo platformowych frameworków. Są to zależności zewnętrzne o własnych modelach wykonania, błędów i anulowania.

Niezależnie od biblioteki TCP jest strumieniem bajtów, nie strumieniem wiadomości. Pojedynczy odczyt może zwrócić fragment rekordu, kilka rekordów albo zero przy zamknięciu. Protokół potrzebuje framingu: stałego rozmiaru, delimitera, prefiksu długości lub samopisującego formatu.

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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Sieć, serializacja i granice std”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz normalizację wejścia, wykonanie operacji systemowej lub bibliotecznej, sprawdzenie wyniku i zamknięcie zasobu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel format danych od obiektu domenowego, czas monotoniczny od kalendarzowego oraz API standardowe od zależności platformowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź kod błędu, liczbę przetworzonych bajtów, stan strumienia, jednostkę pomiaru i wynik dla przerwanej operacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: I/O przekracza granicę procesu i dlatego jest częściowe, opóźnione oraz zależne od reprezentacji. Każda operacja potrzebuje modelu błędów, limitu danych, kodowania lub jednostki oraz zasad własności uchwytu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Biblioteka standardowa C++23 nie dostarcza pełnego przenośnego stosu sieciowego ani formatu serializacji. Granica potrzebuje kontroli długości, endianowości, wersji schematu, częściowych operacji i niezaufanych danych.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Sieć, serializacja i granice std” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Sieć, serializacja i granice std
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Sieć, serializacja i granice std”, oceniaj jawne kodowanie, kontrolowane limity, odporność na częściowy odczyt, bezpieczne ścieżki i deterministyczne sprzątanie. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Fuzzing](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
