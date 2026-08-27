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

`compare_exchange_weak` może zawieść pozornie i dlatego zwykle działa w pętli. Parametr expected jest zapisywany aktualną wartością przy porażce. Failure ordering nie może być release ani acq_rel i nie może być silniejszy w niedozwolony sposób od success ordering.

ABA występuje, gdy wartość zmienia się z A do B i z powrotem do A. CAS widzi oczekiwane A, ale logiczny stan mógł się zmienić. Rozwiązania obejmują tagowane wskaźniki/liczniki, hazard pointers, epoch-based reclamation, RCU lub zmianę struktury. Same memory orders nie rozwiązują ABA.

Najtrudniejsze jest zwalnianie pamięci. Wątek może posiadać pointer do węzła usuniętego przez inny wątek. `shared_ptr` upraszcza lifetime, ale jego atomowe użycie i koszty mają własne kontrakty. Reclamation scheme musi gwarantować, że żaden czytelnik nie używa węzła przed `delete`.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Memory ordering, lock-free, ABA i reclamation”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Lock-free opisuje postęp systemu, nie sprawiedliwość ani szybkość. Problem ABA wynika z powrotu reprezentacji do wcześniejszej wartości, a reclamation musi zapobiec zwolnieniu węzła obserwowanego przez inny wątek.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Memory ordering, lock-free, ABA i reclamation” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Memory ordering, lock-free, ABA i reclamation
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Memory ordering, lock-free, ABA i reclamation”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Zacznij od mutexa i zmierz contention. Korzystaj z opublikowanych algorytmów oraz biblioteki reclamation zamiast improwizacji. Testy stresowe nie są dowodem, a TSan może nie rozumieć każdej niestandardowej synchronizacji.

## Powiązane tematy

- [Podstawy atomików](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
- [Undefined behavior](01_undefined_behavior_i_model_maszyny.md)
- [Sanitizery](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)

