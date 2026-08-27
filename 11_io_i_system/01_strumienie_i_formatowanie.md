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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Strumienie i formatowanie”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz normalizację wejścia, wykonanie operacji systemowej lub bibliotecznej, sprawdzenie wyniku i zamknięcie zasobu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel format danych od obiektu domenowego, czas monotoniczny od kalendarzowego oraz API standardowe od zależności platformowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź kod błędu, liczbę przetworzonych bajtów, stan strumienia, jednostkę pomiaru i wynik dla przerwanej operacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: I/O przekracza granicę procesu i dlatego jest częściowe, opóźnione oraz zależne od reprezentacji. Każda operacja potrzebuje modelu błędów, limitu danych, kodowania lub jednostki oraz zasad własności uchwytu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Stan iostream obejmuje flagi `good`, `fail`, `bad` i `eof`; samo EOF nie zawsze oznacza błąd formatu. Formatowanie powinno rozdzielać reprezentację dla człowieka od stabilnego protokołu danych.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Strumienie i formatowanie” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Strumienie i formatowanie
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Strumienie i formatowanie”, oceniaj jawne kodowanie, kontrolowane limity, odporność na częściowy odczyt, bezpieczne ścieżki i deterministyczne sprzątanie. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Pliki i filesystem](02_pliki_i_filesystem.md)
- [string i tekst](../06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
- [Sieć i serializacja](05_siec_serializacja_i_granice_std.md)

