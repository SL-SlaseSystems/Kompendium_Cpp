[← Spis treści](../README.md)

# Atomiki i model pamięci

`std::atomic<T>` zapewnia niepodzielne operacje na wspieranym typie i uczestniczy w modelu pamięci. Atomowość odpowiada na pytanie, czy operacja może zostać rozerwana; memory ordering określa relacje widoczności i kolejności między wątkami. Sam atomic counter nie chroni inwariantu obejmującego kilka niezależnych pól.

~~~cpp
#include <atomic>
#include <cassert>
#include <thread>

int main() {
    int data = 0;
    std::atomic<bool> ready{false};

    std::jthread producer([&] {
        data = 42;
        ready.store(true, std::memory_order_release);
    });

    std::jthread consumer([&] {
        while (!ready.load(std::memory_order_acquire)) {
        }
        assert(data == 42);
    });
}
~~~

Release store zsynchronizowany z acquire load tworzy happens-before: zapis `data` staje się widoczny dla konsumenta. `data` nie musi być atomic, ponieważ dostęp jest uporządkowany; bez tej synchronizacji równoczesny odczyt i zapis byłby data race.

`memory_order_relaxed` zapewnia atomowość i porządek modyfikacji pojedynczego atomika, ale nie publikuje innych danych. Acquire, release i acq_rel tworzą kierunkowe bariery, a seq_cst dodaje jeden globalny porządek operacji seq_cst. Najsłabszy poprawny ordering wymaga dowodu; domyślny seq_cst jest często właściwym punktem startowym.

Atomic nie musi być lock-free. Sprawdza to `is_lock_free`, a gwarancje dla konkretnych specjalizacji zależą od standardu i platformy. `volatile` nie zastępuje atomika.

`std::atomic_ref<T>` pozwala wykonywać atomowe operacje na istniejącym, właściwie wyrównanym obiekcie. Wszystkie równoczesne dostępy do tego obiektu muszą być wtedy zgodne z wymaganiami `atomic_ref`; mieszanie zwykłego zapisu z dostępem atomowym nadal może tworzyć data race.

## Jak to działa krok po kroku

W pierwszym przykładzie producent zapisuje `data`, a potem wykonuje store z release. Konsument odczytuje ten sam atomik z acquire i przechodzi dalej dopiero po zobaczeniu wartości true z publikującego zapisu. Ten odczyt ustanawia synchronizes-with, a wcześniejszy zapis danych happens-before ich późniejszy odczyt. Ważne jest powiązanie z zaobserwowanym zapisem, a nie samo występowanie słów acquire i release gdziekolwiek w programie.

Zastąpienie obu porządków przez relaxed zachowałoby atomowość flagi, lecz nie ustanowiłoby potrzebnej relacji dla `data`. Program mógłby mieć data race na zwykłej zmiennej. Długi czas od zapisu, `sleep_for` i widoczna kolejność logów nie zastępują tej relacji. Model pamięci określa legalność wykonania niezależnie od tego, co zwykle dzieje się na danym procesorze.

Po udanej publikacji producent nie modyfikuje już danych. To istotne ograniczenie: flaga ready nie tworzy trwałej blokady. Jeśli producent zacznie nadpisywać `data`, gdy konsument jeszcze czyta, potrzebny jest kolejny etap protokołu potwierdzający zakończenie odczytu albo inny model, np. mutex lub przekazanie niezmiennego obiektu.

## Pogłębienie mechanizmu

Każdy atomik ma własny porządek modyfikacji. Relaxed zachowuje niepodzielność oraz reguły spójności dla tego obiektu, ale nie tworzy globalnego obrazu wszystkich atomików. Dwa niezależne liczniki atomic mogą być odczytane w stanach z różnych momentów. Inwariant „saldo A plus saldo B pozostaje stałe” wymaga wspólnej operacji lub blokady, a nie tylko zmiany obu pól na atomic.

Operacja read-modify-write, np. `fetch_add`, atomowo łączy odczyt starej wartości z zapisem nowej. `counter = counter + 1` wykonuje oddzielny odczyt i zapis nawet wtedy, gdy counter jest atomic, więc dwa wątki mogą zgubić aktualizację. Brak data race nie oznacza poprawności algorytmicznej. Do inkrementacji licznika używaj odpowiedniej operacji RMW.

`compare_exchange_weak(expected, desired)` zapisuje desired, jeśli bieżąca wartość odpowiada expected. Przy porażce aktualizuje expected wartością odczytaną z atomika i może zawieść pozornie, dlatego zwykle działa w pętli. Porządek porażki dotyczy odczytu, więc nie może być release ani acq_rel. Obliczenie desired może wymagać powtórzenia po zmianie expected; efektów ubocznych nie wolno bezmyślnie wykonywać wiele razy wewnątrz pętli.

`seq_cst` zapewnia dodatkowy wspólny porządek operacji sekwencyjnie spójnych, ale nie zwalnia z analizy czasów życia i danych nieatomowych. `memory_order_consume` w C++23 ma szczególny model zależności i problematyczne wsparcie praktyczne; typowy kod publikacji powinien preferować dobrze rozumiany acquire. Lock-free oznacza określony rodzaj postępu bez blokady implementacyjnej, nie automatycznie wait-free ani brak zagłodzenia pojedynczego wątku.

Dla `atomic_ref` przestrzegaj wymaganego wyrównania i ograniczeń dostępu przez cały czas życia referencji atomowych. W tym czasie dostęp do objętego nimi obiektu ma odbywać się zgodnie z protokołem `atomic_ref`, a nie naprzemiennie zwykłymi odczytami. Dla istniejącego bufora może to być wygodna adaptacja, lecz nie usuwa obowiązku zapewnienia żywego i właściwie wyrównanego obiektu.

## Drugi przykład

Atomowe maksimum można obliczyć pętlą CAS. Relaxed wystarcza, ponieważ atomik reprezentuje tylko liczbę, a wyniki odczytujemy po zakończeniu wszystkich pracowników.

~~~cpp
#include <atomic>
#include <cassert>
#include <thread>
#include <vector>

void update_max(std::atomic<int>& maximum, int candidate) {
    int observed = maximum.load(std::memory_order_relaxed);
    while (observed < candidate &&
           !maximum.compare_exchange_weak(observed, candidate,
               std::memory_order_relaxed, std::memory_order_relaxed)) {
    }
}

int main() {
    std::atomic<int> maximum{0};
    std::vector<std::jthread> workers;
    for (int candidate : {4, 20, 7, 12}) {
        workers.emplace_back([&, candidate] { update_max(maximum, candidate); });
    }
    for (auto& worker : workers) worker.join();
    assert(maximum.load(std::memory_order_relaxed) == 20);
}
~~~

Jeśli inny wątek podniesie maksimum do większej liczby, nieudany CAS przepisze tę liczbę do observed i pętla może się zakończyć bez zapisu. Jeśli wartość nadal jest mniejsza od candidate, próbujemy ponownie. Nie ma tu dodatkowego rekordu „zwycięskiego zadania” publikowanego razem z liczbą; dodanie go zmieniłoby wymagania synchronizacji i atomowości całego protokołu.

## Porównanie i decyzje

Mutex jest często prostszym rozwiązaniem dla kilku powiązanych pól i skomplikowanego czasu życia. Atomiki są użyteczne dla liczników, flag i starannie zaprojektowanych struktur. C++20 `wait/notify` pozwala unikać ciągłego aktywnego odpytywania, ale trzeba nadal zmienić wartość i ustalić właściwe porządki; notify samo nie publikuje dowolnych danych ani nie przechowuje historii wszystkich zmian.

**Ćwiczenie.** Dlaczego zamiana dwóch pól na `atomic<int>` nie czyni operacji przelewu atomową? **Odpowiedź:** każda modyfikacja jest niepodzielna osobno. Obserwator może odczytać stan po odjęciu, ale przed dodaniem. Potrzebna jest wspólna transakcja logiczna chroniona mutexem albo specjalnie zaprojektowany algorytm obejmujący oba pola.

Źródła reguł: [C++23: model pamięci](https://timsong-cpp.github.io/cppwp/n4950/intro.races), [porządki atomowe](https://timsong-cpp.github.io/cppwp/n4950/atomics.order), [operacje atomików](https://timsong-cpp.github.io/cppwp/n4950/atomics.types.operations).

## Powiązane tematy

- [Mutex i condition_variable](02_mutex_lock_i_condition_variable.md)
- [Zaawansowane memory ordering](../zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)
- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)
