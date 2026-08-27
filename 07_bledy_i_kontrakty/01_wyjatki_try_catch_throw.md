[← Spis treści](../README.md)

# Wyjątki: try, catch i throw

Wyjątek oddziela zwykły wynik od rzadkiej ścieżki błędu. `throw` tworzy obiekt wyjątku, a wykonanie szuka pasującego `catch`, rozwijając stos i niszcząc kompletne obiekty automatyczne po drodze. Jeśli nie znajdzie handlera, program kończy się przez `std::terminate`.

~~~cpp
#include <cassert>
#include <stdexcept>
#include <string_view>

int parse_port(std::string_view text) {
    if (text == "80") {
        return 80;
    }
    throw std::invalid_argument{"nieobsługiwany port"};
}

int main() {
    try {
        (void)parse_port("abc");
        return 1;
    } catch (const std::invalid_argument& error) {
        assert(std::string_view{error.what()} == "nieobsługiwany port");
    }
}
~~~

Łap wyjątki przez `const&`, aby uniknąć kopii i object slicing. Handlery są sprawdzane w kolejności, więc typy bardziej szczegółowe umieszczaj przed bazowym `std::exception`. `catch (...)` łapie dowolny wyjątek, ale powinien zwykle posprzątać, zalogować na granicy procesu albo ponownie rzucić przez `throw;`.

Wyjątki są odpowiednie, gdy funkcja nie może spełnić zwykłego kontraktu, a błąd ma propagować przez wiele warstw. Nie są dobrym zamiennikiem normalnego rozgałęzienia, np. „nie znaleziono elementu” w częstej ścieżce. Projekty bez wyjątków wymagają konsekwentnej alternatywy i muszą uwzględnić, że wiele elementów standardowej biblioteki może rzucać.

Nie rzucaj wskaźników ani typów niekopiowalnych. Hierarchia błędów powinna przenosić stabilną informację, a nie zmuszać klienta do parsowania tekstu `what()`. Wyjątki nie mogą przekraczać granicy C ABI.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Wyjątki: try, catch i throw”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wykrycie niespełnionego warunku, zbudowanie informacji o błędzie, propagację przez granice oraz odtworzenie prawidłowego stanu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd możliwy do obsłużenia od naruszenia precondition i zagwarantuj sprzątanie niezależnie od wybranej ścieżki. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ błędu, zachowany kontekst, stan obiektów po porażce i spełniony poziom exception safety. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Obsługa błędów zaczyna się od klasyfikacji niepowodzenia: naruszenie kontraktu programisty, spodziewany brak wyniku, błąd środowiska albo awaria uniemożliwiająca kontynuację. Mechanizm raportowania powinien odpowiadać tej kategorii. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Rzucenie wyjątku rozpoczyna wyszukiwanie handlera i niszczenie automatycznych obiektów na opuszczanych zakresach. Catch przez `const&` zachowuje dynamiczny typ i unika kopiowania lub slicing.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Wyjątki: try, catch i throw” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Wyjątki: try, catch i throw
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Wyjątki: try, catch i throw”, oceniaj częstotliwość błędu, koszt ścieżki sukcesu, możliwość pominięcia wyniku, zgodność z RAII i czytelność kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Exception safety i noexcept](02_raii_exception_safety_i_noexcept.md)
- [optional, expected i kody błędów](03_optional_expected_i_kody_bledow.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)

