[← Spis treści](../README.md)

# Algorytmy i lambdy

Biblioteka `<algorithm>` oddziela operację od kontenera. Algorytmy wyrażają intencję — wyszukanie, transformację, partycję, sortowanie — i ograniczają ręczne zarządzanie indeksami. Wersje `std::ranges` przyjmują zakres bez osobnego `begin/end`, używają concepts i często obsługują projection.

~~~cpp
#include <algorithm>
#include <cassert>
#include <numeric>
#include <string>
#include <vector>

struct User {
    std::string name;
    int score;
};

int main() {
    std::vector<User> users{{"Ada", 7}, {"Bjarne", 10}, {"Linus", 5}};
    std::ranges::sort(users, std::greater{}, &User::score);

    const int total = std::accumulate(
        users.begin(), users.end(), 0,
        [](int sum, const User& user) { return sum + user.score; });

    assert(users.front().name == "Bjarne");
    assert(total == 22);
}
~~~

Lambda może przechwytywać przez wartość `[=]`, referencję `[&]` lub jawnie `[limit, &result]`. Domyślne przechwytywanie bywa wygodne, lecz ukrywa lifetime i koszt kopii. Lambda `mutable` może zmieniać własne kopie przechwyconych wartości. Przechwycenie `this` nie wydłuża życia obiektu; zadanie asynchroniczne może później użyć wiszącego wskaźnika.

`std::sort` nie zachowuje kolejności równoważnych elementów; do tego służy `std::stable_sort`. Komparator musi spełniać strict weak ordering. Użycie `<=` zamiast `<` łamie kontrakt i może powodować dowolne skutki w obrębie wymagań algorytmu.

Algorytmy równoległe z execution policies mogą zmieniać kolejność i kontekst wykonania; funkcje użytkownika muszą spełniać odpowiednie wymagania bezpieczeństwa. Nie zakładaj, że polityka zawsze przyniesie przyspieszenie.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Algorytmy i lambdy”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Algorytmy oddzielają sposób przejścia od operacji na elementach. Lambda przechwytująca przez referencję dziedziczy ograniczenie lifetime, a `mutable` zmienia constness operatora wywołania, nie obiektu źródłowego.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Algorytmy i lambdy” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Algorytmy i lambdy
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Algorytmy i lambdy”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Iteratory](04_iteratory_i_invalidacja.md)
- [Ranges](06_ranges_i_views.md)
- [Współbieżność](../10_wspolbieznosc/01_thread_jthread_i_stop_token.md)

