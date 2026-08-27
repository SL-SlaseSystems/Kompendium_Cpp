[← Spis treści](../README.md)

# Undefined behavior i model maszyny

Standard opisuje program względem C++ abstract machine. Implementacja musi zachować obserwowalne zachowanie poprawnego programu zgodnie z regułą as-if, ale może dowolnie przekształcać kod. Gdy wykonanie ma undefined behavior, standard nie nakłada wymagań na całość tego wykonania; optimizer może wykorzystać założenie, że poprawny program nie trafia w UB.

Typowe źródła UB to signed overflow, wyjście poza zakres, use-after-lifetime, dereferencja nieważnego lub źle wyrównanego wskaźnika, data race, naruszenie aliasingu, dzielenie całkowite przez zero i złamanie precondition oznaczonego w standardzie jako UB.

~~~cpp,notest
int overflow(int value) {
    return value + 1; // UB, gdy value == INT_MAX
}

int use_after_free() {
    int* pointer = new int{42};
    delete pointer;
    return *pointer; // UB
}
~~~

Nie każdy błąd to UB. Wyjątek z `vector::at`, niepowodzenie `dynamic_cast` do wskaźnika albo deadlock mają zdefiniowane konsekwencje. Zachowanie implementation-defined wymaga dokumentacji wyboru, unspecified dopuszcza kilka wyników, a ill-formed program wymaga diagnostyki, o ile nie zaznaczono inaczej.

~~~cpp
#include <cassert>
#include <limits>
#include <optional>

std::optional<int> checked_add(int left, int right) {
    if (right > 0 && left > std::numeric_limits<int>::max() - right) return std::nullopt;
    if (right < 0 && left < std::numeric_limits<int>::min() - right) return std::nullopt;
    return left + right;
}

int main() {
    assert(checked_add(20, 22) == 42);
    assert(!checked_add(std::numeric_limits<int>::max(), 1));
}
~~~

Sanitizery wykrywają część naruszeń w wykonanych ścieżkach. Analiza statyczna i testy uzupełniają obraz. Najważniejsza jest konstrukcja API: span zamiast wskaźnika z rozmiarem, RAII zamiast ręcznego cleanup i synchronizacja zamiast nadziei na kolejność.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Undefined behavior i model maszyny”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Undefined behavior pozwala implementacji zakładać, że dana sytuacja nie występuje w poprawnym programie. Skutek może pojawić się daleko od naruszenia po optymalizacji, dlatego obserwacja oczekiwanego wyniku nie stanowi dowodu poprawności.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Undefined behavior i model maszyny” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Undefined behavior i model maszyny
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Undefined behavior i model maszyny”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Lifetime i provenance](02_lifetime_aliasing_i_pointer_provenance.md)
- [Sanitizery](../09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)
- [Memory ordering](11_memory_ordering_lock_free_aba_i_reclamation.md)

