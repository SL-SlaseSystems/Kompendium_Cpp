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

Konstruktor wątku przygotowuje funkcję i argumenty, a następnie uruchamia nowe wykonanie. To, który wątek pierwszy wykona kolejną instrukcję po rozpoczęciu pracy, zależy od harmonogramu. Nie zakładaj, że pracownik jeszcze nie wystartował, dopóki konstruktor nie wrócił do klienta. Inicjalizację danych potrzebnych pracownikowi wykonaj przed jego uruchomieniem albo publikuj je przez osobny poprawny protokół.

`join` czeka na zakończenie reprezentowanego wykonania i ustanawia synchronizację z jego zakończeniem. Dlatego po skutecznym join właściciel może czytać wynik zapisany wyłącznie przez pracownika do zwykłej zmiennej. W pierwszym przykładzie licznik jest atomic, ale przy braku równoległych odczytów i przy odczycie wyłącznie po join wystarczyłby zwykły `int`. Atomik jest potrzebny dopiero, gdy projekt rzeczywiście wymaga współbieżnego dostępu.

`joinable` oznacza, że obiekt reprezentuje wykonanie, które nie zostało dołączone ani odłączone. Nie oznacza, że wątek aktualnie wykonuje instrukcje. Nawet już zakończony pracownik pozostawia joinable `thread`, dopóki właściciel go nie dołączy. Próba join na sobie prowadzi do błędu, a zarządzanie tym samym uchwytem równolegle wymaga osobnej synchronizacji.

## Pogłębienie mechanizmu

Destruktor joinable `jthread` najpierw zgłasza żądanie zatrzymania, a potem wykonuje join. Samo jawne `join()` nie zgłasza stop, co ma znaczenie w pierwszym przykładzie: pracownik kończy po trzech iteracjach własnym warunkiem. Jeżeli pętla kończy się wyłącznie po stop, jawne join bez wcześniejszego `request_stop` będzie czekało na żądanie pochodzące skądinąd.

Stan zatrzymania jest współdzielony przez `stop_source`, `stop_token` i zarejestrowane callbacki. Żądanie jest trwałe i nie można go wycofać do stanu „nie zatrzymuj”. Token pozwala obserwować i rejestrować reakcje, a źródło zgłasza żądanie. Callback może być wykonany synchronicznie w wątku wywołującym `request_stop`, a rejestracja po zgłoszeniu stop może wykonać go od razu. Nie traktuj callbacka jak zadania zawsze przekazanego do osobnego executora.

Anulowanie wymaga decyzji domenowej: czy kończymy bieżący rekord, porzucamy częściowy wynik, czy zwracamy oznaczenie niekompletności? Flaga stop nie cofa zapisu do pliku i nie zwalnia automatycznie blokującego API nieświadomego tokena. `condition_variable_any` ma przeciążenia oczekiwania świadome stop; zwykłe `condition_variable::wait` nie dostaje tej własności tylko dlatego, że wątek jest typu jthread.

Kolejność pól właściciela ma znaczenie. Są niszczone w odwrotnej kolejności deklaracji, dlatego wątek korzystający z innych pól często powinien być zadeklarowany po nich, aby dołączył przed ich zniszczeniem. Równie ważne jest niewywoływanie join podczas trzymania mutexa, którego pracownik potrzebuje do zakończenia. Automatyczna destrukcja nie jest dowodem braku deadlocka.

## Drugi przykład

Pracownik czeka w sposób świadomy zatrzymania. Program działa również wtedy, gdy żądanie dotrze jeszcze przed rozpoczęciem oczekiwania; nie polega na opóźnieniach czasowych.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <mutex>
#include <thread>

int main() {
    std::mutex mutex;
    std::condition_variable_any changed;
    bool job_ready = false;
    bool stopped = false;
    std::jthread worker([&](std::stop_token token) {
        std::unique_lock lock{mutex};
        const bool ready = changed.wait(lock, token, [&] { return job_ready; });
        stopped = !ready && token.stop_requested();
    });

    worker.request_stop();
    worker.join();
    assert(stopped);
}
~~~

Wynik przeciążenia z predykatem informuje o wartości predykatu po zakończeniu oczekiwania. Gdy prawdziwy predykat i stop wystąpią razem, aplikacja musi określić pierwszeństwo pracy lub anulowania. Tutaj predykat stale pozostaje fałszywy, więc wynik oznacza przerwanie. Zmienna `stopped` nie jest atomowa, bo główny wątek czyta ją dopiero po join; mutex i condition variable żyją dłużej od pracownika.

## Porównanie i decyzje

Jthread jest dobrym właścicielem samodzielnego długotrwałego pracownika, ale nie tworzy puli zadań. Uruchamianie systemowego wątku dla każdego drobnego elementu może kosztować więcej niż obliczenie. Liczba zadań i liczba wątków nie muszą być równe. `hardware_concurrency` jest wskazówką i może zwrócić zero; nie jest gwarantowaną receptą na optymalny rozmiar puli.

**Ćwiczenie.** Czy `detach` rozwiązuje problem długiego oczekiwania w destruktorze? **Odpowiedź:** usuwa czekanie właściciela, ale pozostawia wykonanie bez tej kontroli czasu życia. Jeśli korzystało z lokalnych danych, może dostać wiszące referencje. Prawidłową naprawą jest określenie zakończenia i odblokowania pracy, nie samo porzucenie uchwytu.

Źródła reguł: [C++23: wątki](https://timsong-cpp.github.io/cppwp/n4950/thread.threads), [zatrzymanie kooperacyjne](https://timsong-cpp.github.io/cppwp/n4950/thread.stoptoken), [condition_variable_any](https://timsong-cpp.github.io/cppwp/n4950/thread.condition.condvarany).

## Powiązane tematy

- [mutex i condition_variable](02_mutex_lock_i_condition_variable.md)
- [future, promise i async](03_future_promise_async.md)
- [Korutyny](../12_wspolczesny_cpp/05_korutyny.md)
