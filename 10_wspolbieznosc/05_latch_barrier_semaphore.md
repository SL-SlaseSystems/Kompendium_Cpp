[← Spis treści](../README.md)

# latch, barrier i semaphore

C++20 dodał narzędzia koordynacji wyższego poziomu. `std::latch` jest jednorazowym licznikiem: uczestnicy zmniejszają go, a oczekujący ruszają po dojściu do zera. `std::barrier` działa fazami i może wykonać completion function między nimi. `std::counting_semaphore` kontroluje liczbę równoczesnych pozwoleń.

~~~cpp
#include <cassert>
#include <latch>
#include <thread>

int main() {
    int left = 0;
    int right = 0;
    std::latch done{2};

    std::jthread first([&] {
        left = 20;
        done.count_down();
    });
    std::jthread second([&] {
        right = 22;
        done.count_down();
    });

    done.wait();
    assert(left + right == 42);
}
~~~

Operacje latch ustanawiają synchronizację wymaganą do odczytu wyników po `wait`. Latch nie można zresetować; jeśli algorytm ma wiele iteracji, użyj barrier. Uczestnik barrier może `arrive_and_drop`, gdy nie bierze udziału w kolejnych fazach.

Semaphore nie chroni sam z siebie konkretnego obiektu jak mutex. Reprezentuje pulę zasobów lub limit przepustowości, np. maksymalnie osiem równoczesnych zapytań. Binary semaphore ma licznik o maksymalnej wartości co najmniej jeden i może służyć jako sygnał, ale jego reguły ownership różnią się od mutexa.

Te prymitywy są niskopoziomowymi elementami. Wyższy model powinien nazywać stan domenowy, zapewniać anulowanie i nie dopuszczać, by wyjątek ominął wymagane `count_down` lub `release`. Pomocny jest RAII guard albo metoda `arrive_and_wait`, zależnie od operacji.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „latch, barrier i semaphore”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz publikację danych, ustanowienie synchronizacji, wykonanie pracy przez wiele wątków i bezpieczne zakończenie lub anulowanie. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wzajemne wykluczanie, komunikację, postęp algorytmu i czas życia danych współdzielonych. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant chroniony blokadą, memory order, ownership wątku, ślad TSan i test kontrolowanego zamknięcia. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Współbieżny program opisuje relacje happens-before między operacjami. Sam czas zegarowy lub obserwowana kolejność logów nie ustanawia synchronizacji; dostęp do współdzielonego, nieatomowego obiektu bez właściwej relacji może być data race i UB. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Latch jest jednorazowym licznikiem dojścia, barrier działa fazami i może wykonywać completion step, a semaphore kontroluje liczbę dostępnych pozwoleń. Nie zastępują one ochrony dowolnego inwariantu danych.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „latch, barrier i semaphore” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: latch, barrier i semaphore
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „latch, barrier i semaphore”, oceniaj najprostszy poprawny model, możliwość anulowania, brak data race, ograniczone contention i udowodniony lifetime. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wątki i jthread](01_thread_jthread_i_stop_token.md)
- [Atomiki](04_atomiki_i_model_pamieci.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)

