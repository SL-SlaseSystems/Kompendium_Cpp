[← Spis treści](../README.md)

# mutex, lock i condition_variable

Data race występuje, gdy wątki równocześnie uzyskują konfliktujący dostęp do tej samej lokalizacji pamięci, co najmniej jeden zapisuje i brak wymaganej relacji synchronizacji. Data race w C++ jest undefined behavior. Mutex zapewnia mutual exclusion i ustanawia odpowiednie relacje happens-before między odblokowaniem a późniejszym zablokowaniem.

~~~cpp
#include <cassert>
#include <mutex>
#include <thread>
#include <vector>

int main() {
    int counter = 0;
    std::mutex mutex;
    std::vector<std::jthread> workers;

    for (int i = 0; i < 4; ++i) {
        workers.emplace_back([&] {
            for (int n = 0; n < 100; ++n) {
                std::lock_guard lock{mutex};
                ++counter;
            }
        });
    }
    workers.clear(); // destruktory jthread wykonują join
    assert(counter == 400);
}
~~~

`lock_guard` blokuje w konstruktorze i odblokowuje w destruktorze. `unique_lock` pozwala odblokowywać, przenosić własność i współpracować z condition variable. `scoped_lock` może bezpiecznie zablokować wiele mutexów, ograniczając ryzyko deadlocka wynikającego z różnej kolejności.

Condition variable czeka na zmianę predykatu. Zawsze używaj pętli lub overloadu przyjmującego predykat, ponieważ występują spurious wakeups, a powiadomienie nie przechowuje zdarzenia jak kolejka. Stan i predykat muszą być chronione tym samym mutexem.

Deadlock nie jest automatycznie UB, ale program przestaje robić postęp. Ustal globalną kolejność blokad, minimalizuj sekcje krytyczne i nie wywołuj obcego kodu pod mutexem bez kontraktu. `shared_mutex` umożliwia wielu czytelników, lecz może być wolniejszy i ma zależne od implementacji właściwości fairness.

## Jak to działa krok po kroku

W przykładzie każdy pracownik przed zwiększeniem licznika przejmuje ten sam mutex. Dzięki wzajemnemu wykluczaniu tylko jeden z nich wykonuje w danej chwili odczyt, dodanie i zapis chronionego licznika. Zwolnienie mutexa synchronizuje się z odpowiednim późniejszym przejęciem go, więc następny właściciel widzi zmiany poprzednika. Sam typ zmiennej `counter` nie potrzebuje atomic, ponieważ wszystkie konkurencyjne modyfikacje są chronione.

Zakres nazwanego `lock_guard` określa sekcję krytyczną. Tymczasowy strażnik bez nazwy, utworzony i porzucony w jednej instrukcji, odblokowałby mutex natychmiast na końcu tej instrukcji. To częsty błąd składniowy, którego programista nie zauważa, widząc pozornie poprawne użycie RAII. Strażnik musi żyć przez cały czas wykonywania operacji wymagających ochrony.

Oczekiwanie na condition variable zaczyna się od przejęcia mutexa i sprawdzenia predykatu. Jeśli jest fałszywy, `wait` atomowo zwalnia mutex i przechodzi do oczekiwania. Po obudzeniu ponownie przejmuje mutex, dopiero potem sprawdza stan. Ten protokół zapobiega luce między sprawdzeniem warunku a rozpoczęciem czekania, w której producent mógłby dostarczyć dane i wysłać zgubione powiadomienie.

## Pogłębienie mechanizmu

Powiadomienie nie jest przechowywaną wartością. Jeżeli producent zmieni stan wcześniej, późniejszy konsument zobaczy prawdziwy predykat i w ogóle nie musi czekać. Dlatego to kolejka, flaga zakończenia lub licznik reprezentuje fakty, a condition variable tylko pomaga spać do chwili możliwej zmiany. Spurious wakeup jest dodatkowym powodem używania predykatu, ale nie jedynym: inny konsument może odebrać element przed ponownym przejęciem mutexa.

Zwykle producent zmienia stan pod blokadą, wychodzi z sekcji krytycznej i dopiero powiadamia. Odbiorca po obudzeniu nie musi wtedy natychmiast czekać na ten sam mutex. Trzeba jednak zapewnić, że condition variable nadal istnieje podczas notify. Reguła czasu życia może uzasadniać inny układ. `notify_all` jest odpowiednie przy zamykaniu, gdy wszyscy oczekujący muszą sprawdzić stan końcowy; przy jednym nowym elemencie często wystarcza `notify_one`.

`unique_lock` potrafi przenosić własność i tymczasowo zwalniać blokadę. `scoped_lock` z kilkoma różnymi mutexami korzysta z protokołu unikającego deadlocka przy ich zdobywaniu. Nie naprawia jednak cyklu obejmującego blokady już trzymane gdzie indziej. Przekazanie tego samego nierekurencyjnego mutexa dwukrotnie nie jest poprawnym zamiennikiem usunięcia duplikatu.

Przy oczekiwaniu z limitem nie ponawiaj bezmyślnie pełnego `wait_for` po każdym obudzeniu, bo całkowity czas może przekroczyć budżet. Ustal termin na `steady_clock` i używaj `wait_until` z predykatem. Upływ czasu nie dowodzi, że stan jest fałszywy poza blokadą; stan należy interpretować w ramach tego samego protokołu ochrony.

## Drugi przykład

Kolejka przechowuje dane oraz trwały stan zamknięcia. Po zamknięciu konsument opróżnia pozostałe elementy, a następnie otrzymuje brak wyniku.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <deque>
#include <mutex>
#include <optional>
#include <thread>

class Queue {
    std::mutex mutex_;
    std::condition_variable changed_;
    std::deque<int> data_;
    bool closed_ = false;
public:
    bool push(int value) {
        {
            std::lock_guard lock{mutex_};
            if (closed_) return false;
            data_.push_back(value);
        }
        changed_.notify_one();
        return true;
    }
    void close() {
        {
            std::lock_guard lock{mutex_};
            closed_ = true;
        }
        changed_.notify_all();
    }
    std::optional<int> pop() {
        std::unique_lock lock{mutex_};
        changed_.wait(lock, [&] { return closed_ || !data_.empty(); });
        if (data_.empty()) return std::nullopt;
        const int result = data_.front();
        data_.pop_front();
        return result;
    }
};

int main() {
    Queue queue;
    int sum = 0;
    std::jthread consumer([&] {
        while (const auto item = queue.pop()) sum += *item;
    });
    for (int i = 1; i <= 3; ++i) queue.push(i);
    queue.close();
    consumer.join();
    assert(sum == 6);
    assert(!queue.push(4));
}
~~~

Klasa nie zwraca referencji do elementu chronionego kontenera, która mogłaby uciec poza zakres blokady. Zarówno sprawdzenie pustki, jak i usunięcie są jedną operacją pod mutexem. Właściciel zapewnia, że kolejka przeżyje konsumenta. Sam destruktor kolejki nie zamyka magicznie trwających wywołań; pełny system musi wyegzekwować zakończenie wszystkich użytkowników przed zniszczeniem.

## Porównanie i decyzje

Mutex dobrze chroni inwariant obejmujący kilka pól i złożone operacje. Atomik jest odpowiedni dla węższych protokołów, ale nie zamieni automatycznie całej kolejki w bezpieczną strukturę. Shared mutex ma sens tylko po pomiarze wzorca czytelników i pisarzy; standard nie daje uniwersalnej obietnicy sprawiedliwego harmonogramu ani braku zagłodzenia.

**Ćwiczenie.** Dlaczego osobne metody `empty()` i `pop()` nie tworzą bezpiecznej operacji nawet wtedy, gdy każda blokuje mutex? **Odpowiedź:** między wywołaniami inny konsument może usunąć ostatni element. Potrzebna jest metoda łącząca sprawdzenie i odebranie pod jedną blokadą, z jasno określonym zachowaniem dla pustej kolejki.

Źródła reguł: [C++23: mutexy](https://timsong-cpp.github.io/cppwp/n4950/thread.mutex), [condition variables](https://timsong-cpp.github.io/cppwp/n4950/thread.condition), [obiekty blokad](https://timsong-cpp.github.io/cppwp/n4950/thread.lock).

## Powiązane tematy

- [Wątki i jthread](01_thread_jthread_i_stop_token.md)
- [Atomiki](04_atomiki_i_model_pamieci.md)
- [Sanitizery i TSan](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)
