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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Atomiki i model pamięci”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz publikację danych, ustanowienie synchronizacji, wykonanie pracy przez wiele wątków i bezpieczne zakończenie lub anulowanie. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wzajemne wykluczanie, komunikację, postęp algorytmu i czas życia danych współdzielonych. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant chroniony blokadą, memory order, ownership wątku, ślad TSan i test kontrolowanego zamknięcia. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Współbieżny program opisuje relacje happens-before między operacjami. Sam czas zegarowy lub obserwowana kolejność logów nie ustanawia synchronizacji; dostęp do współdzielonego, nieatomowego obiektu bez właściwej relacji może być data race i UB. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Relaxed zapewnia atomowość bez międzywątkowego uporządkowania, release publikuje wcześniejsze zapisy, a acquire obserwujący odpowiednią wartość ustanawia synchronizes-with. Sequential consistency dodaje wspólny porządek operacji seq_cst.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Atomiki i model pamięci” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Atomiki i model pamięci
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Atomiki i model pamięci”, oceniaj najprostszy poprawny model, możliwość anulowania, brak data race, ograniczone contention i udowodniony lifetime. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Mutex i condition_variable](02_mutex_lock_i_condition_variable.md)
- [Zaawansowane memory ordering](../zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)
- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)
