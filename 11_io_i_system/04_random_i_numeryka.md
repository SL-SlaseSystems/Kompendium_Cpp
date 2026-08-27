[← Spis treści](../README.md)

# random i numeryka

Biblioteka `<random>` rozdziela silnik generujący pseudolosowe bity od rozkładu mapującego je na wartości. `std::mt19937` jest deterministycznym silnikiem o dobrych właściwościach do symulacji, ale nie jest kryptograficznie bezpieczny. `std::random_device` może dostarczać entropię albo zachowywać się zależnie od implementacji.

~~~cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <random>

int main() {
    std::mt19937 engine{12345};
    std::uniform_int_distribution<int> die{1, 6};
    const int roll = die(engine);
    assert(roll >= 1 && roll <= 6);

    std::array values{1, 2, 3, 4};
    std::shuffle(values.begin(), values.end(), engine);
    std::ranges::sort(values);
    assert((values == std::array{1, 2, 3, 4}));
}
~~~

Stały seed daje reprodukowalny test. W aplikacji można seedować z `random_device` lub kontrolowanego źródła, ale zapisuj seed symulacji, aby odtworzyć błąd. Nie generuj zakresu przez `engine() % n`, bo modulo może wprowadzać bias; użyj odpowiedniego distribution.

Nagłówek `<numeric>` oferuje `accumulate`, `inner_product`, `iota` oraz algorytmy skanowania. C++17 dodał warianty umożliwiające przestawianie działań, dlatego wyniki floating point mogą różnić się kolejnością zaokrągleń. `std::reduce` ma inne wymagania niż sekwencyjne `accumulate`.

Overflow signed integer pozostaje UB także w obliczeniach numerycznych. Sprawdzaj zakres przed działaniem albo używaj typu i biblioteki odpowiadającej domenie. Dla kryptografii, statystyki i dużych liczb wybierz zweryfikowaną bibliotekę; standardowe prymitywy nie tworzą kompletnego rozwiązania domenowego.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „random i numeryka”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz normalizację wejścia, wykonanie operacji systemowej lub bibliotecznej, sprawdzenie wyniku i zamknięcie zasobu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel format danych od obiektu domenowego, czas monotoniczny od kalendarzowego oraz API standardowe od zależności platformowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź kod błędu, liczbę przetworzonych bajtów, stan strumienia, jednostkę pomiaru i wynik dla przerwanej operacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: I/O przekracza granicę procesu i dlatego jest częściowe, opóźnione oraz zależne od reprezentacji. Każda operacja potrzebuje modelu błędów, limitu danych, kodowania lub jednostki oraz zasad własności uchwytu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Generator pseudolosowy tworzy deterministyczny ciąg ze stanu, a distribution mapuje go na wymagany rozkład bez ręcznego modulo bias. Seed odpowiada za odtwarzalność eksperymentu, nie za kryptograficzne bezpieczeństwo.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „random i numeryka” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: random i numeryka
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „random i numeryka”, oceniaj jawne kodowanie, kontrolowane limity, odporność na częściowy odczyt, bezpieczne ścieżki i deterministyczne sprzątanie. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Typy podstawowe](../02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
- [Algorytmy](../06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
- [Testy i fuzzing](../09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)

