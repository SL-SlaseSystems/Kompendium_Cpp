[← Spis treści](../README.md)

# thread, jthread i stop_token

`std::thread` reprezentuje wątek wykonania. Przed zniszczeniem obiektu trzeba wykonać `join` albo `detach`; destrukcja joinable thread kończy proces. `std::jthread` z C++20 automatycznie dołącza w destruktorze i integruje się z cooperative cancellation przez `std::stop_token`.

~~~cpp
#include <atomic>
#include <cassert>
#include <thread>

int main() {
    std::atomic<int> iterations{0};

    std::jthread worker([&iterations](std::stop_token stop) {
        while (!stop.stop_requested()) {
            ++iterations;
            if (iterations.load() >= 3) {
                break;
            }
        }
    });

    worker.join();
    assert(iterations.load() >= 3);
}
~~~

Argumenty `std::thread` są przechowywane według wartości po odpowiednich przekształceniach. Aby przekazać referencję, można użyć `std::ref`, ale wtedy obiekt musi żyć do końca wątku. Lambda przechwytująca lokalne zmienne przez referencję ma to samo wymaganie. `jthread` zmniejsza ryzyko pominięcia join, lecz nie naprawia dangling references.

Stop token nie zabija wątku. Kod musi regularnie sprawdzać żądanie albo korzystać z operacji świadomych zatrzymania. Projektuj punkty anulowania i określ, jaki stan pozostaje po przerwaniu. Blokująca funkcja nieobsługująca stop może opóźnić destruktor `jthread`.

`detach` oddziela lifetime uchwytu od wątku i bardzo utrudnia kontrolę zasobów, błędów i zakończenia procesu. Preferuj structured concurrency: właściciel zadania żyje w zakresie, który gwarantuje oczekiwanie i propagację błędów.

Wyjątek opuszczający funkcję wątku wywołuje `std::terminate`; `join` nie propaguje go automatycznie. Jeśli błąd ma dotrzeć do właściciela, przechwyć go w wątku i zapisz w `promise`, `exception_ptr` albo kontrolowanym typie wyniku.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „thread, jthread i stop_token”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz publikację danych, ustanowienie synchronizacji, wykonanie pracy przez wiele wątków i bezpieczne zakończenie lub anulowanie. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wzajemne wykluczanie, komunikację, postęp algorytmu i czas życia danych współdzielonych. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant chroniony blokadą, memory order, ownership wątku, ślad TSan i test kontrolowanego zamknięcia. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Współbieżny program opisuje relacje happens-before między operacjami. Sam czas zegarowy lub obserwowana kolejność logów nie ustanawia synchronizacji; dostęp do współdzielonego, nieatomowego obiektu bez właściwej relacji może być data race i UB. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `jthread` dołącza wątek w destruktorze i współpracuje ze `stop_token`, zmniejszając ryzyko `terminate` przez joinable thread. Prośba stop jest kooperacyjna: kod pracy musi sprawdzać token i kończyć zasoby.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „thread, jthread i stop_token” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: thread, jthread i stop_token
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „thread, jthread i stop_token”, oceniaj najprostszy poprawny model, możliwość anulowania, brak data race, ograniczone contention i udowodniony lifetime. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [mutex i condition_variable](02_mutex_lock_i_condition_variable.md)
- [future, promise i async](03_future_promise_async.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
