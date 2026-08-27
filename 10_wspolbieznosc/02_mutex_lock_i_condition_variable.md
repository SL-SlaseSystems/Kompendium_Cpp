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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „mutex, lock i condition_variable”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz publikację danych, ustanowienie synchronizacji, wykonanie pracy przez wiele wątków i bezpieczne zakończenie lub anulowanie. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wzajemne wykluczanie, komunikację, postęp algorytmu i czas życia danych współdzielonych. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant chroniony blokadą, memory order, ownership wątku, ślad TSan i test kontrolowanego zamknięcia. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Współbieżny program opisuje relacje happens-before między operacjami. Sam czas zegarowy lub obserwowana kolejność logów nie ustanawia synchronizacji; dostęp do współdzielonego, nieatomowego obiektu bez właściwej relacji może być data race i UB. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Mutex chroni inwariant współdzielonego stanu, a lock guard koduje zwolnienie przez RAII. Condition variable może obudzić się pozornie, dlatego czekanie zawsze powtarza predykat pod tą samą blokadą.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „mutex, lock i condition_variable” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: mutex, lock i condition_variable
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „mutex, lock i condition_variable”, oceniaj najprostszy poprawny model, możliwość anulowania, brak data race, ograniczone contention i udowodniony lifetime. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wątki i jthread](01_thread_jthread_i_stop_token.md)
- [Atomiki](04_atomiki_i_model_pamieci.md)
- [Sanitizery i TSan](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)

