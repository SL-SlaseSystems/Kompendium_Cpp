[← Spis treści](../README.md)

# Ograniczona kolejka, backpressure i zamykanie

**Wymagania wstępne:** mutex, `unique_lock`, zmienne warunkowe, `jthread` i czas życia współdzielonych obiektów. Przykłady używają C++23.

Kolejka między producentem a konsumentem jest protokołem zarządzania pracą. Musi określać nie tylko kolejność elementów, ale też zachowanie po zapełnieniu, zakończenie dopływu oraz moment bezpiecznego zniszczenia. Nieograniczony wzrost bufora przenosi problem wolnego konsumenta na pamięć i opóźnienie. Pojemność ograniczona wprowadza backpressure: producent czeka albo otrzymuje informację, że chwilowo nie może dodać pracy.

W tym rozdziale pełny bufor blokuje producenta. Zamknięcie jest trwałą zmianą stanu: dalsze dodawanie zostaje odrzucone, lecz konsumenci odbierają już przyjęte elementy. Dopiero zamknięta i pusta kolejka oznacza koniec strumienia. To semantyka opróżnienia, często nazywana drain. Przerwanie pojedynczego oczekiwania jest inną operacją i nie powinno niejawnie zmieniać tego kontraktu.

## Jak to działa krok po kroku

Przykład celowo przechowuje wyłącznie `int`. Bufor kołowy alokuje pamięć w konstruktorze; kopiowanie elementu podczas `push` i `pop` nie rzuca wyjątków. Dzięki temu nie trzeba ukrywać problemów wyjątków ruchu dowolnego `T`. Konstrukcja może zgłosić błąd alokacji lub nieprawidłową pojemność, a operacje synchronizacji zachowują swoje standardowe możliwości zgłoszenia błędu systemowego.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <cstddef>
#include <mutex>
#include <optional>
#include <stdexcept>
#include <thread>
#include <vector>

class IntQueue {
    std::mutex mutex_;
    std::condition_variable readable_;
    std::condition_variable writable_;
    std::vector<int> ring_;
    std::size_t head_ = 0;
    std::size_t tail_ = 0;
    std::size_t count_ = 0;
    bool closed_ = false;

    std::size_t next(std::size_t index) const noexcept {
        return index + 1 == ring_.size() ? 0 : index + 1;
    }
public:
    explicit IntQueue(std::size_t capacity) : ring_(capacity) {
        if (capacity == 0) {
            throw std::invalid_argument{"zero capacity"};
        }
    }

    bool push(int value) {
        std::unique_lock lock{mutex_};
        writable_.wait(lock, [&] { return closed_ || count_ < ring_.size(); });
        if (closed_) {
            return false;
        }
        ring_[tail_] = value;
        tail_ = next(tail_);
        ++count_;
        lock.unlock();
        readable_.notify_one();
        return true;
    }

    std::optional<int> pop() {
        std::unique_lock lock{mutex_};
        readable_.wait(lock, [&] { return closed_ || count_ != 0; });
        if (count_ == 0) {
            return std::nullopt;
        }
        const int value = ring_[head_];
        head_ = next(head_);
        --count_;
        lock.unlock();
        writable_.notify_one();
        return value;
    }

    void close() {
        {
            std::lock_guard lock{mutex_};
            closed_ = true;
        }
        readable_.notify_all();
        writable_.notify_all();
    }
};

int main() {
    IntQueue queue{2};
    int total = 0;
    std::jthread consumer{[&] {
        while (const auto item = queue.pop()) {
            total += *item;
        }
    }};
    for (int value = 1; value <= 100; ++value) {
        const bool accepted = queue.push(value);
        assert(accepted);
    }
    queue.close();
    queue.close(); // Zamknięcie jest idempotentne.
    consumer.join();
    assert(total == 5050);
    assert(!queue.pop());
    const bool accepted = queue.push(101);
    assert(!accepted);
}
~~~

Wszystkie pola opisujące stan kolejki są chronione jednym mutexem. Niezmiennik brzmi: liczba elementów mieści się między zerem a pojemnością. Producent może wykonać zapis tylko przy wolnym miejscu i otwartej kolejce. Konsument może wykonać odczyt przy dodatniej liczbie elementów, również po zamknięciu. Indeksy wskazują kolejne pozycje odczytu i zapisu, a zawijanie zachodzi w obrębie zaalokowanego bufora.

Predykat producenta zawiera `closed_`, aby zamknięcie pozwoliło wyjść również z oczekiwania na pełnym buforze. Analogicznie predykat konsumenta musi reagować na zamknięcie pustej kolejki. Obudzenie nie oznacza przyznania elementu ani miejsca: po ponownym przejęciu mutexa stan mógł już zmienić inny wątek. Overload `wait` z predykatem wykonuje potrzebną pętlę i obsługuje także pozorne przebudzenia. [N4950: `condition_variable`](https://timsong-cpp.github.io/cppwp/n4950/thread.condition.condvar).

Po skutecznym dodaniu wystarczy powiadomić jednego konsumenta; po odebraniu jednego producenta. Zamknięcie zmienia warunek zakończenia dla wszystkich oczekujących po obu stronach, więc wymaga dwóch `notify_all`. Powiadomienie poza sekcją krytyczną ogranicza natychmiastowe odbijanie się obudzonego wątku od mutexa. Poprawność wynika jednak ze stanu chronionego blokadą, a nie z samej pozycji wywołania `notify`.

## Pogłębienie mechanizmu

Rozstrzygnięcie wyścigu między `push` i `close` następuje pod mutexem. Jeżeli dodanie nastąpi pierwsze, element należy do pracy przeznaczonej do opróżnienia. Jeżeli pierwsze nastąpi zamknięcie, `push` zwraca `false`. Nie ma stanu „prawie przyjętego”. Podobnie `pop` zwraca brak wartości wyłącznie po zaobserwowaniu zamknięcia i pustego bufora. To punkty, w których operacje otrzymują jednoznaczny skutek w historii współbieżnej.

Przy wielu producentach właściciel musi również określić, kto zamyka strumień. Pierwszy producent, który skończy własną porcję, nie powinien automatycznie odcinać pozostałych. Może to robić koordynator po dołączeniu wszystkich producentów albo ostatni producent według osobnego protokołu licznika. Samo `close` nie zna liczby źródeł pracy. Po stronie odbiorców odebranie elementu oznacza tylko przeniesienie go z bufora do konsumenta; nie potwierdza zakończenia przetwarzania. Oczekiwanie na wykonanie wszystkich zadań wymaga dołączenia pracowników lub dodatkowego mechanizmu potwierdzeń.

Brak elementu i koniec strumienia nie mogą być tym samym wynikiem w API nieblokującym. Jeśli dodasz `try_pop`, pusty otwarty bufor powinien dawać stan „jeszcze brak”, a zamknięty pusty „koniec”. W API blokującym różnicę ukrywa oczekiwanie. Analogicznie producent może potrzebować odrębnych wyników pełnego bufora, upływu terminu, zamknięcia i anulowania. Sam `bool` wystarcza tutaj dzięki wąskiemu kontraktowi.

Uogólnienie na `T` wymaga analizy wyjątków. Ruch może zmienić element źródłowy, a następnie rzucić; pop nie odzyska wtedy automatycznie poprzedniej wartości. Kontener dynamiczny może także alokować pod blokadą. Rozsądnym wariantem prostego bufora jest jawne wymaganie bezwyjątkowej konstrukcji przenoszącej i destrukcji oraz wcześniejsza alokacja. Inny projekt może oferować słabszą gwarancję, ale musi ją nazwać i zadbać o postęp oczekujących po błędzie. Zastąpienie `int` przez `T` bez tych decyzji nie daje poprawnej biblioteki generycznej.

`jthread` nie rozwiązuje protokołu zakończenia. Jego destruktor dla aktywnego wątku prosi o zatrzymanie i wykonuje `join`, lecz zwykła `condition_variable` nie jest automatycznie budzona przez `stop_token`. Konsument pierwszego przykładu nie sprawdza tokenu: kończy dzięki `close`. Zniszczenie aktywnego pracownika przed zamknięciem mogłoby więc utknąć na oczekiwaniu. [N4950: `jthread`](https://timsong-cpp.github.io/cppwp/n4950/thread.jthread.class).

## Drugi przykład

Poniższy mały obiekt pokazuje samo przerwalne oczekiwanie na zamknięcie. Nie zastępuje pełnej kolejki. `condition_variable_any` ma overload przyjmujący `stop_token`, który obsługuje żądanie przychodzące zarówno przed rozpoczęciem czekania, jak i podczas niego. Dzięki temu przykład nie potrzebuje `sleep`, aby „trafić” w moment blokowania.

~~~cpp
#include <cassert>
#include <condition_variable>
#include <mutex>
#include <stop_token>
#include <thread>

enum class WaitResult { closed, cancelled };

class ClosingSignal {
    std::mutex mutex_;
    std::condition_variable_any changed_;
    bool closed_ = false;
public:
    WaitResult wait(std::stop_token token) {
        std::unique_lock lock{mutex_};
        const bool closed = changed_.wait(lock, token, [&] { return closed_; });
        return closed ? WaitResult::closed : WaitResult::cancelled;
    }
    void close() {
        {
            std::lock_guard lock{mutex_};
            closed_ = true;
        }
        changed_.notify_all();
    }
    bool is_closed() {
        std::lock_guard lock{mutex_};
        return closed_;
    }
};

int main() {
    ClosingSignal signal;
    WaitResult result = WaitResult::closed;
    std::jthread worker{[&](std::stop_token token) {
        result = signal.wait(token);
    }};
    worker.request_stop();
    worker.join();
    assert(result == WaitResult::cancelled);
    assert(!signal.is_closed());
    signal.close();
    assert(signal.wait(std::stop_token{}) == WaitResult::closed);
}
~~~

Wynik overloadu opisuje spełnienie predykatu, a nie sam fakt nadejścia sygnału. Jeśli zamknięcie i anulowanie zachodzą blisko siebie, kontrakt powyżej daje pierwszeństwo zaobserwowanemu stanowi zamknięcia. Rozszerzając kolejkę o token, trzeba analogicznie ustalić pierwszeństwo dostępnego elementu, zamknięcia i anulowania. Anulowanie jednego konsumenta nie powinno samo zamykać kanału pozostałym. [N4950: przerwalne oczekiwania](https://timsong-cpp.github.io/cppwp/n4950/thread.condvarany.intwait).

Backpressure działa tylko wtedy, gdy producent może się zatrzymać bez blokowania zasobów potrzebnych konsumentowi. Wywołanie blokującego `push` z zajętym mutexem aplikacji, którego potrzebuje odbiorca, tworzy możliwość zakleszczenia niezależnie od poprawności kolejki. Podobny problem pojawia się w puli, gdy wszystkie jej wątki produkują do pełnego kanału, a konsument ma dopiero dostać wątek tej samej puli.

## Porównanie i decyzje

Pojemność dobieraj do tolerowanego opóźnienia i ilości pracy w toku, a nie tylko do liczby dostępnych megabajtów. Ograniczenie liczby elementów nie ogranicza łącznego rozmiaru ich zewnętrznych zasobów. Przy zadaniach o różnej wadze potrzebny może być budżet bajtów albo kosztu. Zwykłe mutexy i powiadomienia nie zapewniają też sprawiedliwej kolejności obsługi oczekujących.

Kolejka musi żyć do zakończenia wszystkich operacji jej użytkowników. Poprawna sekwencja właściciela to zatrzymanie dopływu pracy, `close`, dołączenie producentów i konsumentów, a dopiero potem zniszczenie kolejki. `close` nie jest `join` i nie dowodzi, że obudzony wątek przestał korzystać z mutexa lub bufora. Deklarowanie kolejki przed pracownikami pomaga przy zwykłym niszczeniu w odwrotnej kolejności, ale nie zastępuje protokołu zamknięcia ani obsługi ścieżek błędów.

**Ćwiczenie 1.** Dlaczego samo `readable_.notify_all()` w `close` może zawiesić program?

<details>
<summary>Rozwiązanie</summary>

Producent może czekać na `writable_`, bo bufor był pełny. Zamknięcie ma pozwolić mu zwrócić odmowę, lecz powiadomienie innej zmiennej warunkowej go nie obudzi. Trzeba ustawić wspólny stan pod mutexem i powiadomić wszystkich oczekujących po obu stronach.

</details>

**Ćwiczenie 2.** Czy anulowanie ostatniego konsumenta gwarantuje zakończenie zablokowanych producentów?

<details>
<summary>Rozwiązanie</summary>

Nie. Kanał może pozostać otwarty i pełny. Właściciel musi podjąć decyzję o dalszym losie pracy, zamknąć kanał albo zapewnić innego odbiorcę. Anulowanie pracownika i zamknięcie wspólnego strumienia to odrębne przejścia stanu.

</details>

Źródło uzupełniające: [N4950: mutex i synchronizacja](https://timsong-cpp.github.io/cppwp/n4950/thread.mutex.requirements).

## Powiązane tematy

- [thread, jthread i stop_token](01_thread_jthread_i_stop_token.md)
- [mutex, lock i condition_variable](02_mutex_lock_i_condition_variable.md)
- [RAII, exception safety i noexcept](../07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md)
