[← Spis treści](../README.md)

# Zadania w tle i kontrolowane zamykanie

Zadanie w tle nadal należy do jakiegoś właściciela. Jeżeli obsługuje żądania, zapisuje pliki albo publikuje komunikaty, jego czas życia jest częścią kontraktu aplikacji. Proces nie powinien kończyć pracy w przypadkowym momencie pomiędzy zapisem wyniku i potwierdzeniem zadania. Potrzebuje jawnej odpowiedzi na pytania: kiedy przestaje przyjmować pracę, co kończy, co porzuca i kiedy można zwolnić jego zależności.

Rozdziel trzy operacje: zamknięcie wejścia, żądanie anulowania i oczekiwanie na zakończenie. Pierwsza zabrania nowych zadań, druga prosi bieżącą pracę o przerwanie, trzecia ustala, że worker rzeczywiście przestał korzystać z pamięci i usług. Żadna z tych operacji nie zastępuje pozostałych. Flaga `stopping` bez wybudzenia czekającego workera może pozostawić proces zawieszony na zawsze.

## Jak to działa krok po kroku

Zamykanie zaczyna się na brzegu systemu. Przestań przyjmować połączenia lub usuń gotowość instancji zgodnie z protokołem wdrożenia. Następnie zatrzymaj producentów wewnętrznych, takich jak harmonogram i subskrypcje. Zamknij kolejkę, aby późne zgłoszenie dostało jednoznaczną odmowę. Dopiero wtedy można uznać, że zbiór zaakceptowanej pracy jest skończony.

Poniższy program realizuje **close i drain**: po zamknięciu odrzuca nowe elementy, ale przetwarza wszystkie wcześniej przyjęte. Zamknięcie oraz sprawdzenie kolejki odbywają się pod tym samym mutexem. To daje punkt rozstrzygający wyścig między `push()` i `close()`: konkretna operacja zostaje przyjęta albo odrzucona, bez stanu „zwrócono sukces, lecz zadanie zniknęło”.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <deque>
#include <iostream>
#include <mutex>
#include <optional>
#include <thread>
#include <vector>

class Queue {
    std::mutex mutex_;
    std::condition_variable ready_;
    std::deque<int> jobs_;
    bool closed_ = false;
public:
    bool push(int job) {
        {
            std::lock_guard lock(mutex_);
            if (closed_) return false;
            jobs_.push_back(job);
        }
        ready_.notify_one();
        return true;
    }
    std::optional<int> pop() {
        std::unique_lock lock(mutex_);
        ready_.wait(lock, [&] { return closed_ || !jobs_.empty(); });
        if (jobs_.empty()) return std::nullopt;
        int job = jobs_.front();
        jobs_.pop_front();
        return job;
    }
    void close() {
        {
            std::lock_guard lock(mutex_);
            closed_ = true;
        }
        ready_.notify_all();
    }
};

int main() {
    Queue queue;
    std::vector<int> results;
    results.reserve(3);
    // Zależności powstały przed workerem i żyją aż do join().
    std::jthread worker([&] {
        while (auto job = queue.pop()) results.push_back(*job * *job);
    });
    if (!queue.push(2) || !queue.push(3) || !queue.push(4)) return 1;
    queue.close();
    const bool late = queue.push(5);
    assert(!late);
    worker.join();
    assert((results == std::vector<int>{4, 9, 16}));
    for (int x : results) std::cout << x << '\n';
}
~~~

Worker nie używa tutaj tokena stop: wyjście wynika wyłącznie z opróżnienia zamkniętej kolejki. Predykat chroni przed pozornymi wybudzeniami i przed utratą powiadomienia wysłanego przed rozpoczęciem oczekiwania. Wyniki odczytujemy po `join()`, więc nie ścigamy się z zapisem wektora. To mała kolejka demonstracyjna, bez ograniczenia pojemności, raportowania błędów zadań i obsługi awarii alokacji; nie jest gotowym executorem produkcyjnym.

## Pogłębienie mechanizmu

`stop_source::request_stop()` zmienia wspólny stan i wywołuje zarejestrowane callbacki. Nie przerywa arbitralnej instrukcji, systemowego odczytu ani zwykłego `condition_variable::wait()`. `jthread` przy niszczeniu obiektu dołączalnego żąda zatrzymania, po czym wykonuje join. To oczekiwanie nie ma limitu czasu. Standard udostępnia natomiast warianty oczekiwania `condition_variable_any` przyjmujące token stop. [N4950: §33.3, §33.4.4, §33.7.5](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4950.pdf).

Z tego wynika ważna pułapka: zastąpienie `thread` przez `jthread` nie naprawi pierwszego programu, gdy usuniesz `close()`. Worker czeka na zwykłej zmiennej warunkowej, ignoruje token i nigdy nie dostanie powodu wyjścia. Destruktor uprzejmie poprosi go o stop, a następnie będzie czekał. Poprawność wynika z protokołu kolejki, a nie z samej nazwy typu wątku.

W klasie właściciela deklaruj stan kolejki, mutexy i klientów usług przed polem `jthread`, aby były niszczone po nim. Jeszcze czytelniej wykonuj jawne `shutdown()` i `join()` przed niszczeniem zależności. Nie wywołuj join, trzymając mutex potrzebny workerowi do wyjścia. Nie uruchamiaj również workera w konstruktorze, zanim powstaną wszystkie używane przez niego pola.

Tryb drain ma sens dla skończonej pracy mieszczącej się w budżecie. Anulowanie jest potrzebne, gdy zadania mogą być długie lub zależność nie odpowiada. Wtedy trzeba zdefiniować los pracy oczekującej i rozpoczętej: zwrot do brokera, oznaczenie anulowania w obietnicy, zapis checkpointu lub kompensację. Samo usunięcie elementów kolejki bez zakończenia odpowiadających im futures pozostawi klientów czekających bez wyniku.

## Drugi przykład

Drugi program pokazuje zatrzymanie workera czekającego na zmianę konfiguracji. Token trafia bezpośrednio do przerwalnego oczekiwania. Latch pozwala rozpocząć zamykanie po wejściu workera do sekcji oczekiwania, ale nie narzuca konkretnego przeplotu między rejestracją stop i samym wywołaniem `wait()`. Mechanizm obsługuje również żądanie stop nadesłane tuż przed oczekiwaniem.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <iostream>
#include <latch>
#include <mutex>
#include <optional>
#include <string>
#include <thread>

int main() {
    std::mutex mutex;
    std::condition_variable_any changed;
    std::optional<std::string> configuration;
    std::latch entered(1);
    unsigned applied = 0;
    bool cancelled = false;

    std::jthread worker([&](std::stop_token stop) {
        std::unique_lock lock(mutex);
        entered.count_down();
        for (;;) {
            bool available = changed.wait(lock, stop, [&] {
                return configuration.has_value();
            });
            // Polityka: stop ma pierwszeństwo nawet przy gotowych danych.
            if (stop.stop_requested() || !available) {
                configuration.reset();
                cancelled = true;
                return;
            }
            std::string next = std::move(*configuration);
            configuration.reset();
            lock.unlock();
            if (!next.empty()) ++applied; // Model zastosowania konfiguracji.
            lock.lock();
        }
    });

    entered.wait();
    worker.request_stop(); // Nie ma osobnego changed.notify_all().
    worker.join();
    assert(cancelled && applied == 0);
    std::cout << "configuration worker cancelled\n";
}
~~~

To przykład mechanizmu oczekiwania, a nie pełny system konfiguracji. Nie ma producenta zmian, walidacji danych ani rzeczywistego I/O. Odcinek pracy poza blokadą musiałby we własnym zakresie przestrzegać tokena i deadline. Jeżeli zastosowanie konfiguracji blokuje w obcej bibliotece przez minutę, przerwalne oczekiwanie na kolejne zadanie nie skróci tej minuty.

W wariancie z ręcznym `stop_callback` łatwo popełnić błąd lost wakeup. Sam callback wywołujący `notify_all()` i predykat oparty na atomowej fladze nie zawsze wystarczą, jeśli sprawdzenie warunku i rozpoczęcie oczekiwania nie są właściwie skoordynowane. Preferuj gotowe przerwalne oczekiwanie albo protokół zmiany predykatu pod tym samym mutexem. Callback utrzymuj przy życiu tak długo, jak trwa zależna od niego operacja.

## Porównanie i decyzje

Dobrą polityką usługi bywa drain do ustalonego deadline, a następnie żądanie anulowania. Nie oznacza to gwarancji końca procesu w danym terminie: C++ nie daje przenośnego, bezpiecznego sposobu zabicia dowolnego wątku. Twardy limit wymaga wsparcia od wszystkich operacji albo izolacji zawodnej pracy w osobnym procesie. Po przekroczeniu limitu nie wolno po prostu odłączyć wątku nadal używającego zwalnianych obiektów.

Kolejność zasobów powinna wynikać z zależności: zakończ workery korzystające z bazy, potem zamknij pulę bazy; zakończ emisję telemetrii, potem jej eksportery. Logowanie ostatniego błędu po usunięciu loggera jest błędem czasu życia tak samo jak użycie zwolnionego bufora. Przy projektowaniu composition root zapisuj tę kolejność jako część odpowiedzialności właściciela.

Wyjątek nieobsłużony w funkcji wątku prowadzi do zakończenia procesu. Executor powinien łapać błędy na granicy zadania, raportować wynik właścicielowi i zdecydować, czy następna praca jest nadal bezpieczna. Testuj zamknięcie pustej i pełnej kolejki, spóźnionego producenta oraz worker zablokowany na zależności. Sam poprawny wynik pracy na ścieżce sukcesu nie sprawdza shutdown.

Właściciel powinien także określić, kto może uruchamiać zamykanie. Jeżeli dwa wątki mogą wywołać shutdown, samo idempotentne ustawienie flagi nie wystarcza do bezpiecznego współbieżnego wywołania join na tym samym obiekcie. Serializuj zarządzanie cyklem życia lub wyznacz jeden wątek sterujący. Worker zgłasza potrzebę zatrzymania do właściciela; nie powinien próbować dołączyć samego siebie.

Czas zamykania mierz od decyzji o zatrzymaniu do zakończenia ostatniego workera. Pomocne są liczby zadań przyjętych, ukończonych i porzuconych oraz przyczyna przejścia z drain do anulowania. Takie dane pozwalają odróżnić za duży backlog od zadania, które ignoruje stop. Przetestuj także ponowne wywołanie close: powinno zachować stan zamknięty, a nie ponownie otworzyć kolejkę lub opublikować fałszywy sukces zakończenia.

## Ćwiczenia

1. Worker czeka na zwykłym `condition_variable`. Właściciel wywołuje tylko `request_stop()` i niszczy `jthread`. Co musi zostać poprawione?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Oczekiwanie potrzebuje mechanizmu wybudzenia i predykatu zakończenia. Zamknij kolejkę pod mutexem i powiadom oczekujących albo zastosuj przerwalne oczekiwanie z tokenem. Sam stan stop nie budzi zwykłego wait, więc destruktor może utknąć na join.

</details>

2. W trybie drain kolejka jest pusta, ale producent może dodać element za milisekundę. Czy to wystarczający warunek wyjścia?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Wymagaj jednocześnie pustej kolejki i zamkniętego wejścia. Pustość jest chwilowym stanem; close ustala, że żadna późniejsza operacja nie zostanie zaakceptowana. Oba warunki sprawdzaj w tej samej sekcji krytycznej.

</details>

## Powiązane tematy

- [Thread, jthread i stop_token](../10_wspolbieznosc/01_thread_jthread_i_stop_token.md)
- [Kolejka, backpressure i zamykanie](../10_wspolbieznosc/06_kolejka_backpressure_i_zamykanie.md)
- [Dependency injection i composition root](03_dependency_injection_i_composition_root.md)
