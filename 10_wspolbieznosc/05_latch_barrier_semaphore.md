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

Latch zaczyna z licznikiem dwóch oczekiwanych zgłoszeń. Każdy pracownik zapisuje własny wynik, a następnie zmniejsza licznik. `wait` w głównym wątku kończy się dopiero po osiągnięciu zera i zapewnia potrzebną synchronizację, więc można wtedy odczytać oba wyniki. Pracownicy zapisują różne obiekty, dlatego nie rywalizują ze sobą o tę samą zmienną. Latch koordynuje zakończenie etapu, a nie chroni wspólnego licznika przed jednoczesnym zapisem.

`count_down` tylko zgłasza dojście i nie musi czekać na innych. `arrive_and_wait` łączy zgłoszenie z oczekiwaniem. Licznik latch nie może zejść poniżej zera i nie można go ponownie naładować do kolejnego zadania. Ustawiona liczba powinna odpowiadać faktycznym zgłoszeniom również wtedy, gdy uruchomienie któregoś pracownika się nie powiedzie. Sama obecność RAII w uchwycie wątku nie uzupełni brakującego zgłoszenia.

Barrier w każdej fazie czeka na odpowiednią liczbę przybyć, wykonuje krok zakończenia, a następnie przygotowuje następną fazę. Uczestnik może zgłosić przybycie i osobno czekać z użyciem otrzymanego tokena. `arrive_and_drop` zmniejsza wymagania także dla przyszłych faz. Jest to decyzja o trwałym opuszczeniu grupy, nie zwykły sposób pominięcia jednego oczekiwania bez konsekwencji.

## Pogłębienie mechanizmu

Krok zakończenia barrier może agregować dane opublikowane w fazie. Zakończenie tego kroku poprzedza powrót odblokowanych oczekiwań zgodnie z gwarancjami synchronizacji. Funkcja completion musi spełniać wymagania niezgłaszania wyjątków. Nie zakładaj, że wykona ją zawsze wskazany pracownik lub wątek główny; projektuj ją tak, aby nie zależała od konkretnej tożsamości wykonawcy.

Jedna bariera po zapisach nie zawsze wystarczy dla algorytmu iteracyjnego. Szybki pracownik może rozpocząć nadpisywanie tablicy dla następnej rundy, kiedy wolny nadal czyta dane poprzedniej. Potrzebujesz drugiej fazy po odczytach albo rozdzielenia buforów z odpowiednim protokołem zamiany. To problem czasu życia wartości i relacji między etapami, a nie brak atomowości pojedynczego licznika barrier.

Semaphore przechowuje liczbę dostępnych pozwoleń. `acquire` zużywa jedno lub czeka, a `release` dodaje określoną liczbę. W przeciwieństwie do mutexa release może wykonać inny wątek niż ten, który wcześniej zrobił acquire. To pozwala używać go do sygnalizacji producent–konsument. `try_acquire` może zawieść pozornie, więc wynik false nie jest trwałą informacją o stanie całego systemu.

Maksymalna liczba pozwoleń jest ograniczona. Parametr szablonu określa co najmniej wymagane maksimum, a implementacja może wspierać większe, dostępne przez `max()`. Nie wolno wykonywać release tak, aby przekroczyć dopuszczalny licznik. Jeśli semafor ogranicza pulę zasobów, przejęcie pozwolenia powinno być połączone z oddaniem przez strażnika RAII, także przy wyjątku. Pozwolenie nie mówi jednak, który konkretnie obiekt puli został przydzielony; to może wymagać dodatkowej chronionej struktury.

## Drugi przykład

Dwie fazy bariery na rundę oddzielają zapisy, odczyty i następne nadpisanie. Każdy pracownik ma własny slot, lecz podczas agregacji czyta wszystkie sloty.

~~~cpp
#include <array>
#include <barrier>
#include <cassert>
#include <numeric>
#include <thread>
#include <vector>

int main() {
    constexpr int count = 3;
    std::array<int, count> slots{};
    std::barrier phase{count};
    std::vector<std::jthread> workers;
    for (int id = 0; id < count; ++id) {
        workers.emplace_back([&, id] {
            for (int round = 1; round <= 2; ++round) {
                slots[static_cast<std::size_t>(id)] = round;
                phase.arrive_and_wait();
                const int sum = std::accumulate(slots.begin(), slots.end(), 0);
                assert(sum == round * count);
                phase.arrive_and_wait();
            }
        });
    }
    for (auto& worker : workers) worker.join();
    assert((slots == std::array<int, count>{2, 2, 2}));
}
~~~

Pierwsze oczekiwanie zapewnia, że wszystkie zapisy rundy nastąpiły przed odczytami. Drugie zapewnia, że wszystkie odczyty skończyły się przed zapisami kolejnej rundy. Usunięcie drugiego oczekiwania mogłoby spowodować data race, choć pierwsza bariera nadal poprawnie liczyłaby przybycia. Przykład zakłada skuteczne utworzenie grupy; produkcyjny właściciel musi obsłużyć częściową porażkę startu, zanim inni utkną na oczekiwaniu brakujących uczestników.

## Porównanie i decyzje

Latch pasuje do jednorazowego oczekiwania na gotowość, barrier do powtarzalnych etapów współpracującej grupy, a semaphore do liczby dostępnych zasobów lub przekazywanych pozwoleń. Condition variable jest bardziej elastyczna, gdy warunek obejmuje kilka pól i zamknięcie. Żaden z tych mechanizmów sam nie ustala polityki anulowania, sprawiedliwości ani bezpiecznego zniszczenia obiektu, na którym ktoś nadal czeka.

**Ćwiczenie.** Czy `binary_semaphore` można zawsze zastąpić mutexem? **Odpowiedź:** nie. Jeśli producent wykonuje release, a konsument acquire, nie występuje własność blokady przypisana temu samemu wątkowi. Mutex wymaga odblokowania przez właściciela. Semafor może przekazywać sygnał między różnymi wykonawcami, co stanowi inny protokół.

Źródła reguł: [C++23: latch](https://timsong-cpp.github.io/cppwp/n4950/thread.latch), [barrier](https://timsong-cpp.github.io/cppwp/n4950/thread.barrier), [semaphore](https://timsong-cpp.github.io/cppwp/n4950/thread.sema).

## Powiązane tematy

- [Wątki i jthread](01_thread_jthread_i_stop_token.md)
- [Atomiki](04_atomiki_i_model_pamieci.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
