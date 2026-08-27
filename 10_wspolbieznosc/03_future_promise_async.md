[← Spis treści](../README.md)

# future, promise i async

`std::promise<T>` zapisuje wynik lub wyjątek w shared state, a `std::future<T>` odbiera go jednokrotnie. `std::async` tworzy future dla wywołania funkcji, ale polityka startu ma znaczenie: bez jawnej `std::launch::async` implementacja może odroczyć wykonanie do wywołania `get` lub `wait`.

~~~cpp
#include <cassert>
#include <future>

int square(int value) {
    return value * value;
}

int main() {
    auto result = std::async(std::launch::async, square, 7);
    assert(result.get() == 49);
}
~~~

`get()` czeka na gotowość, zwraca wartość albo ponownie rzuca wyjątek zapisany przez zadanie. Zwykły future jest move-only i wynik można pobrać raz. `std::shared_future` umożliwia wielu odbiorcom odczyt tego samego rezultatu.

Destruktor future zwróconego przez `std::async` może blokować w określonych okolicznościach, co odróżnia go od wielu bibliotek task-based. Standard C++23 nie dostarcza ogólnego executora, kontynuacji `.then` ani kompletnego modelu structured concurrency. Biblioteki takie jak oneTBB, Boost.Asio i runtime’y platformowe mają własne modele.

Promise jest użyteczny, gdy producent wyniku jest zarządzany oddzielnie. Każda obietnica powinna ostatecznie ustawić wartość lub wyjątek; zniszczenie bez wyniku daje odbiorcy `broken_promise`. Synchronizacja shared state nie czyni pozostałych danych programu bezpiecznymi.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „future, promise i async”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz publikację danych, ustanowienie synchronizacji, wykonanie pracy przez wiele wątków i bezpieczne zakończenie lub anulowanie. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wzajemne wykluczanie, komunikację, postęp algorytmu i czas życia danych współdzielonych. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant chroniony blokadą, memory order, ownership wątku, ślad TSan i test kontrolowanego zamknięcia. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Współbieżny program opisuje relacje happens-before między operacjami. Sam czas zegarowy lub obserwowana kolejność logów nie ustanawia synchronizacji; dostęp do współdzielonego, nieatomowego obiektu bez właściwej relacji może być data race i UB. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Promise zapisuje wynik współdzielonego stanu, a future pobiera go najwyżej zgodnie z kontraktem danego typu. Polityka `std::async` może dopuścić wykonanie deferred, więc jawna polityka jest potrzebna, gdy wymagany jest osobny wątek.
- `co_await` jest rozwijane przez protokół `await_ready`, `await_suspend` i `await_resume`. Ownership coroutine handle oraz chwila zniszczenia frame muszą być jawne, szczególnie przy wyjątkach i anulowaniu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „future, promise i async” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: future, promise i async
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „future, promise i async”, oceniaj najprostszy poprawny model, możliwość anulowania, brak data race, ograniczone contention i udowodniony lifetime. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Jawnie wybieraj launch policy, gdy zależy Ci na równoległości. Nie twórz nieograniczonej liczby systemowych wątków przez `async`. Dla większych systemów użyj executora lub puli z jasnym backpressure, anulowaniem i strategią obsługi błędów.

## Powiązane tematy

- [Wątki](01_thread_jthread_i_stop_token.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
- [Mechanika korutyn](../zaawansowane/12_korutyny_promise_awaitery_i_frame.md)

