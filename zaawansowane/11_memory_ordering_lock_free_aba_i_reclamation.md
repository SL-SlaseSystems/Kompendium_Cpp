[← Spis treści](../README.md)

# Memory ordering, lock-free, ABA i reclamation

Lock-free oznacza gwarancję postępu systemowego: w skończonej liczbie kroków jakiś wątek robi postęp. Nie oznacza wait-free dla każdego wątku, braku starvation ani większej szybkości. Algorytm wymaga jednocześnie poprawnego porządku pamięci i bezpiecznego lifetime węzłów.

~~~cpp
#include <atomic>
#include <cassert>

bool increment_below(std::atomic<int>& value, int limit) {
    int current = value.load(std::memory_order_relaxed);
    while (current < limit) {
        if (value.compare_exchange_weak(
                current, current + 1,
                std::memory_order_relaxed,
                std::memory_order_relaxed)) {
            return true;
        }
        // Po porażce current zawiera nową zaobserwowaną wartość.
    }
    return false;
}

int main() {
    std::atomic<int> value{0};
    assert(increment_below(value, 1));
    assert(!increment_below(value, 1));
}
~~~

`compare_exchange_weak` może zawieść pozornie i dlatego zwykle działa w pętli. Parametr expected jest zapisywany aktualną wartością przy porażce. Failure ordering nie może być release ani acq_rel; w C++23 obowiązują reguły właściwe dla odczytu po nieudanym CAS.

ABA występuje, gdy wartość zmienia się z A do B i z powrotem do A. CAS widzi oczekiwane A, ale logiczny stan mógł się zmienić. Rozwiązania obejmują tagowane wskaźniki/liczniki, hazard pointers, epoch-based reclamation, RCU lub zmianę struktury. Same memory orders nie rozwiązują ABA.

Najtrudniejsze jest zwalnianie pamięci. Wątek może posiadać pointer do węzła usuniętego przez inny wątek. `shared_ptr` upraszcza lifetime, ale jego atomowe użycie i koszty mają własne kontrakty. Protokół reclamation musi odroczyć `delete` do chwili, gdy żaden czytelnik nie może już uzyskać dostępu do zwalnianego węzła; normalny dostęp przed jego usunięciem pozostaje dozwolony.

## Jak to działa krok po kroku

`increment_below` najpierw odczytuje bieżący licznik. Jeżeli wartość osiągnęła limit, nie próbuje zapisu. W przeciwnym razie CAS porównuje licznik z `current` i atomowo zastępuje go `current + 1`, tylko jeśli oczekiwanie nadal odpowiada rzeczywistości. Ta udana operacja jest punktem linearyzacji: chwilą, w której zwiększenie można umieścić w hipotetycznym wykonaniu sekwencyjnym.

Przy porażce CAS aktualizuje `current`, więc następna iteracja ponownie sprawdza limit dla zaobserwowanej wartości. Nie wolno bez zastanowienia przenosić obliczenia nowej wartości poza pętlę. `weak` może zawieść także bez zmiany licznika; pętla obsługuje ten przypadek. Arytmetyka jest bezpieczna, ponieważ `current < limit`, a `limit` mieści się w `int`, więc zwiększana wartość jest mniejsza od maksimum typu.

## Pogłębienie mechanizmu

Każdy atomik ma własny modification order. `relaxed` zachowuje niepodzielność i wymagania spójności dla tego obiektu, ale nie publikuje automatycznie zwykłych pól znajdujących się obok. Jeżeli licznik służy tylko do zliczania i ograniczania przydziałów, może to wystarczyć. Jeżeli oznacza „dane gotowe”, potrzebna jest relacja synchronizacji pomiędzy zapisami danych a odczytami odbiorcy.

Release synchronizuje się z acquire, który odczytuje odpowiednią wartość z tego samego atomika albo z właściwej release sequence. Samo wystąpienie słów release i acquire w dwóch wątkach nie wystarcza. Po połączeniu tej relacji z kolejnością operacji wewnątrz wątków otrzymujemy happens-before dla danych nieatomowych. Acquire odczytujące wcześniejsze `false` nie uprawnia jeszcze do czytania opublikowanego payloadu.

Release sequence w C++23 obejmuje następujący po operacji release odpowiedni ciąg operacji read-modify-write. Nie przenoś bez sprawdzenia starszego opisu, który obejmował dodatkowe zwykłe zapisy przez pierwotny wątek. Dla CAS porządek porażki opisuje tylko odczyt: nie może być `release` ani `acq_rel`. Dodatkowe reguły zależności success/failure zmieniały się historycznie; w C++23 nie należy powtarzać dawnego ogólnego zakazu „failure nigdy nie może być silniejsze niż success”.

ABA jest problemem historii logicznej, nie atomowości samego słowa. Usunięty węzeł może zostać zwolniony, a nowa alokacja otrzymać ten sam adres. CAS porównujący wyłącznie adres uzna go za niezmieniony. Tag ogranicza takie pomyłki, lecz trzeba rozważyć przepełnienie licznika i dostępność atomowego porównania całej pary. Hazard pointers wymagają protokołu publikacji ochrony oraz ponownego sprawdzenia wskaźnika; samo zapisanie go w tablicy po dereferencji przychodzi za późno.

## Drugi przykład

~~~cpp
#include <atomic>
#include <cassert>
#include <thread>

int main() {
    int payload = 0;
    std::atomic<bool> ready{false};
    std::jthread producer([&] {
        payload = 42;
        ready.store(true, std::memory_order_release);
        ready.notify_one();
    });
    while (!ready.load(std::memory_order_acquire))
        ready.wait(false, std::memory_order_relaxed);
    assert(payload == 42);
}
~~~

Odczyt acquire w warunku, który zobaczy `true`, ustanawia widoczność wcześniejszego zapisu `payload`. `wait` może jedynie uśpić oczekujący wątek; użyto dla niego relaxed, ponieważ dowód publikacji opiera się na ponownym odczycie warunku. `notify_one` nie jest samodzielnym zastępnikiem release. Przykład ma jednego producenta i jednorazową zmianę flagi, więc nie wymaga protokołu ponownego wykorzystania bufora.

## Porównanie i decyzje

Mutex upraszcza ochronę złożonych inwariantów i zwalnianie pamięci, a biblioteczne kolejki często dają lepszy wynik niż własny lock-free. Nawet jeśli CAS na liczniku jest lock-free, alokacja węzła, destruktor danych albo systemowy alokator mogą blokować cały algorytm. `is_lock_free` i `is_always_lock_free` odnoszą się do operacji danego typu atomowego, nie do dowolnej funkcji, która go używa.

**Ćwiczenie.** Czy zamiana wszystkich porządków na `seq_cst` naprawi dereferencję zwolnionego węzła? **Odpowiedź:** nie; silniejszy porządek nie przedłuża lifetime. Czy usunięcie `notify_one` z przykładu zachowuje gwarantowany postęp oczekiwania? Nie należy na to liczyć; zmiana wartości nie zastępuje wymaganego powiadomienia śpiących obserwatorów. Czy lock-free gwarantuje szybkie zakończenie każdemu wątkowi? Nie, pojedynczy wątek może wielokrotnie przegrywać CAS.

Źródła: [N4950: memory ordering](https://timsong-cpp.github.io/cppwp/n4950/atomics.order), [CAS](https://timsong-cpp.github.io/cppwp/n4950/atomics.types.operations) oraz [happens-before](https://timsong-cpp.github.io/cppwp/n4950/intro.races).

### Postęp i publikacja złożonego stanu

Relacja synchronizacji nie blokuje przyszłych modyfikacji payloadu. W jednorazowym przykładzie producent kończy zapis przed publikacją i nie zmienia danych ponownie. Gdyby po ustawieniu `ready` zaczął wpisywać kolejną wiadomość do tego samego pola, odbiorca mógłby z nim konkurować. Potrzebny byłby dodatkowy protokół zwrotu własności bufora, mutex albo struktura z osobnymi generacjami danych.

Atomowy `shared_ptr` upraszcza ochronę lifetime przez przejmowanie udziału we własności, lecz nie chroni pól wskazywanego obiektu przed równoczesną modyfikacją. Wskaźnik może być bezpiecznie opublikowany, a jego payload nadal wymagać mutexa. Operacje takiego atomika nie muszą być lock-free, a ostatnie zwolnienie udziału może uruchomić kosztowny destructor. Ocena czasu najgorszego przypadku musi objąć również te efekty.

Testy obciążeniowe pozwalają znajdować błędy, ale brak awarii przez milion iteracji nie jest dowodem ordering. Dla małego protokołu rozpisz zdarzenia zapisów i odczytów, wartości odczytywane przez atomiki oraz krawędzie happens-before. Jeżeli po usunięciu przypadkowej kolejności harmonogramu pozostają konflikty bez synchronizacji, algorytm wymaga poprawki niezależnie od wyniku benchmarka.

Porównanie wykonywane przez CAS nie jest domenowym operatorem równości T. Dla odpowiednich specjalizacji porównywana jest reprezentacja wartości według reguł atomika. Typy z wieloma reprezentacjami tej samej semantycznej wartości, w szczególności liczby zmiennoprzecinkowe, wymagają ostrożności. Projektowanie protokołu na prostym indeksie lub liczniku często ułatwia zarówno dowód, jak i dobór dostępnej instrukcji procesora.

## Powiązane tematy

- [Podstawy atomików](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
- [Undefined behavior](01_undefined_behavior_i_model_maszyny.md)
- [Sanitizery](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)

