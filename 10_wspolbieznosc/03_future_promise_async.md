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

Utworzenie promise tworzy kanał wyniku oparty na stanie współdzielonym. `get_future()` wydaje odbiornik powiązany z tym stanem i może być wykonane tylko raz dla tej obietnicy. Producent ustawia wartość przez `set_value` albo wyjątek przez `set_exception`. Gotowość oznacza, że odbiorca może zakończyć oczekiwanie. Próba ponownego zaspokojenia tej samej obietnicy jest błędem protokołu sygnalizowanym przez `future_error`.

`future::get()` oczekuje, a następnie pobiera wartość albo ponownie rzuca zapisany wyjątek. Po takim pobraniu zwykły future traci stan i nie nadaje się do kolejnego get. `valid()` odpowiada, czy posiada stan, a nie czy wynik już jest gotowy. Do badania gotowości służą metody oczekiwania z odpowiednim statusem. Zapisanie wyniku przed jego odebraniem zapewnia wymaganą synchronizację, ale nie chroni przyszłych niezależnych modyfikacji danych współdzielonych.

`std::async(std::launch::async, f, args...)` uruchamia wywołanie z polityką asynchroniczną i samo przechwytuje wyjątek do stanu future. Przy polityce deferred funkcja zostanie wykonana w wątku, który rozpocznie odpowiednie oczekiwanie, a niekoniecznie w osobnym pracowniku. Domyślna kombinacja dopuszcza wybór implementacji. Jeśli architektura wymaga określonej polityki, wybierz ją jawnie.

## Pogłębienie mechanizmu

`wait()` tylko czeka i nie pobiera wyniku ani nie zgłasza zapisanego wyjątku jako wyniku zadania. Dopiero get jest punktem obserwacji błędu. Dla deferred oczekiwanie czasowe może zwrócić status `deferred`, zamiast uruchomić pracę i odliczać do jej końca. Pętla sprawdzająca tylko `ready` i `timeout` może więc pominąć trzeci legalny stan.

Future pochodzący z async ma szczególne reguły czasu życia. Zwolnienie ostatniego odniesienia do jeszcze niegotowego stanu utworzonego z polityką async może blokować do zakończenia wątku. Dwie instrukcje tworzące i natychmiast porzucające tymczasowe future mogą przez to wykonywać zadania kolejno. Aby pozwolić im działać równolegle, przechowaj oba odbiorniki, a dopiero potem pobieraj wyniki.

Zwykły future otrzymany z promise nie daje analogicznego automatycznego join dla dowolnego producenta. Producent ma osobnego właściciela wątku lub zadania. Porzucenie promise bez ustawienia wyniku prowadzi do `broken_promise` w stanie współdzielonym, dzięki czemu odbiorca nie czeka bez końca tylko dlatego, że obiekt obietnicy zniknął. To sygnał porzucenia protokołu, nie normalny kod sukcesu.

`shared_future` pozwala wielu odbiorcom czekać na ten sam wynik. Dla typowego T get zwraca referencję do wartości przechowywanej w stanie; jego żywotność musi wystarczyć odbiorcom. Kopie shared_future mogą być używane w różnych wątkach, ale mutowalny obiekt osiągalny przez wynik nadal wymaga własnych reguł synchronizacji. Współdzielenie kanału nie nadaje każdemu wskazanemu obiektowi automatycznej niezmienności.

## Drugi przykład

Producent sam zarządza obietnicą i świadomie przekazuje wyjątek. Dzięki temu odbiorca obsługuje błąd na swoim stosie wykonania.

~~~cpp
#include <cassert>
#include <exception>
#include <future>
#include <stdexcept>
#include <thread>
#include <utility>

int main() {
    std::promise<int> promise;
    auto result = promise.get_future();
    std::jthread producer([output = std::move(promise)]() mutable {
        try {
            throw std::runtime_error{"cannot compute"};
        } catch (...) {
            output.set_exception(std::current_exception());
        }
    });

    bool failed = false;
    try {
        (void)result.get();
    } catch (const std::runtime_error&) {
        failed = true;
    }
    assert(failed);
    assert(!result.valid());
}
~~~

Przeniesienie promise do lambdy wyraża jednego producenta i zapobiega przypadkowemu użyciu obietnicy przez dwa miejsca. `mutable` jest potrzebne, aby zmieniać stan przechwyconego obiektu. W tym kontrolowanym protokole `set_exception` jest pierwszym ustawieniem prawidłowego stanu. W większym systemie ponowne ustawienie obietnicy samo mogłoby rzucić i nie powinno przypadkowo opuścić funkcji startowej wątku.

## Porównanie i decyzje

Future pasuje do jednorazowego rezultatu. Kolejka lub inny kanał jest właściwszy dla strumienia wielu wiadomości. `packaged_task` łączy wywoływalny obiekt z jego future, ale sam nie wybiera executora ani nie uruchamia automatycznie wątku; można przekazać go do własnej puli. C++23 nie ma standardowego `.then`, ogólnej puli ani automatycznego anulowania pracy przez zniszczenie zwykłego future.

**Ćwiczenie.** Czy `result.wait()` wystarcza, aby zewnętrzny `catch` odebrał wyjątek zadania async? **Odpowiedź:** nie. Wait zapewnia gotowość, lecz wyjątek jest ponownie zgłaszany przez get. Porzucenie gotowego future może więc zgubić informację o porażce, jeśli architektura nie wymaga obserwacji wyniku każdego zadania.

Źródła reguł: [C++23: future i promise](https://timsong-cpp.github.io/cppwp/n4950/futures), [polityki async](https://timsong-cpp.github.io/cppwp/n4950/futures.async), [stan współdzielony](https://timsong-cpp.github.io/cppwp/n4950/futures.state).

## Powiązane tematy

- [Wątki](01_thread_jthread_i_stop_token.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
- [Mechanika korutyn](../zaawansowane/12_korutyny_promise_awaitery_i_frame.md)
