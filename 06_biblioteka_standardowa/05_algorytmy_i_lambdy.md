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

Sortowanie użytkowników otrzymuje trzy oddzielne informacje: zakres obiektów, relację `greater` i projekcję `&User::score`. Algorytm wywołuje projekcję, aby uzyskać klucze porównania, a następnie przekazuje je relacji. Dzięki temu nie trzeba pisać osobnej lambdy porównującej struktury. Obiekty są przestawiane w oryginalnym wektorze; projekcja nie tworzy osobnego wektora wyników.

`accumulate` zaczyna od wartości początkowej i aktualizuje akumulator w kolejności zakresu. Typ wartości początkowej wpływa na typ akumulatora: start od `0` oznacza `int`, nawet gdy elementy są szersze lub zmiennoprzecinkowe. Aby sumować do `double`, użyj `0.0`. Dla dużych liczb całkowitych wybierz odpowiednio szeroki typ i nadal uwzględniaj możliwość przepełnienia; szerszy typ nie daje nieograniczonej arytmetyki.

Algorytm `transform` zapisujący przez iterator wyjściowy nie powiększa automatycznie kontenera. Pusty `output.begin()` nie daje miejsca do zapisu. Potrzebujesz uprzedniego `resize` albo adaptera `back_inserter`, który tłumaczy przypisanie na `push_back`. `reserve` zapewnia pamięć, lecz nie tworzy elementów. Zwracane przez ranges struktury wynikowe często zawierają końcowe pozycje wejścia i wyjścia, ułatwiając kontynuację pracy.

## Pogłębienie mechanizmu

Lambda jest obiektem unikalnego, anonimowego typu domknięcia. Przechwycenia przez wartość stają się jego stanem. Domyślnie operator wywołania nie pozwala zmieniać tych kopii; `mutable` usuwa to ograniczenie, ale nie zamienia kopii w referencje do oryginałów. Init-capture, np. `[data = std::move(data)]`, pozwala przenieść właściciela do domknięcia. Taka lambda może być niekopiowalna, co wpływa na zgodność z odbierającym ją API.

Algorytmy mogą kopiować obiekty funkcyjne. Nie używaj licznika przechowywanego w lokalnej kopii predykatu jako wiarygodnego raportu liczby wywołań. Również konkretna kolejność porównań w sortowaniu nie jest gwarantowana. Komparator powinien określać relację, a nie sterować logiką programu efektami ubocznymi. Dla predykatów wymagających regularnej semantyki powtarzane wywołanie dla tych samych argumentów powinno dawać ten sam wynik.

`lower_bound` wymaga zakresu podzielonego względem używanej relacji; posortowanie tą samą relacją jest zwykłym sposobem spełnienia warunku. `unique` usuwa logicznie tylko sąsiadujące duplikaty. Aby usunąć wszystkie powtórzenia, często najpierw sortuje się dane, ale traci się wtedy ich pierwotną kolejność. Dobór algorytmu zaczyna się więc od oczekiwanego zachowania, a nie od nazwy brzmiącej podobnie do celu.

Sprawdzaj także dopuszczalne nakładanie zakresów. Standardowe algorytmy kopiowania i transformacji nie mają jednej wspólnej reguły dla wszystkich konfiguracji wejścia i wyjścia. Przesuwanie fragmentu w prawo wymaga odpowiednio wybranego kierunku, np. `copy_backward`, aby nie nadpisywać danych przed ich odczytem. Osobną pułapką jest algorytm dopisujący do tego samego wektora, z którego czyta: realokacja może unieważnić wejściowe iteratory. Rozdzielenie kontenera wynikowego często upraszcza dowód poprawności bardziej niż skomplikowane sterowanie pojemnością.

## Drugi przykład

Połączenie filtrowania i transformacji można zapisać w kilku prostych krokach bez ukrytego założenia o rozmiarze wyjścia.

~~~cpp
#include <algorithm>
#include <cassert>
#include <iterator>
#include <vector>

int main() {
    const std::vector<int> raw{3, -2, 3, 1, -1, 2};
    std::vector<int> positive;
    std::ranges::copy_if(raw, std::back_inserter(positive),
                         [](int n) { return n > 0; });
    std::ranges::sort(positive);
    const auto duplicates = std::ranges::unique(positive);
    positive.erase(duplicates.begin(), duplicates.end());

    std::vector<int> doubled;
    std::ranges::transform(positive, std::back_inserter(doubled),
                           [](int n) { return 2 * n; });
    assert((positive == std::vector<int>{1, 2, 3}));
    assert((doubled == std::vector<int>{2, 4, 6}));
}
~~~

Po `unique` rozmiar wciąż wynosi cztery. Dopiero usunięcie zwróconego podzakresu skraca wektor do trzech elementów. Wynik jest posortowany, co stanowi świadomą część tego przykładu. Gdyby wymagano zachowania pierwszej kolejności wystąpień, potrzebna byłaby inna strategia, np. dodatkowy zbiór już widzianych wartości.

## Porównanie i decyzje

Pętla jest dobrym wyborem, gdy pojedynczy algorytm nie opisuje przepływu czytelnie, występuje kilka zależnych stanów albo potrzebujesz wczesnego zakończenia o nietypowych regułach. Algorytm daje z kolei gotowy kontrakt, deklarowaną złożoność i mniej ręcznych pozycji. Polityki równoległe stosuj dopiero po sprawdzeniu wymagań funkcji użytkownika; wyjątek z takiej funkcji dla standardowych polityk może prowadzić do `terminate`.

**Ćwiczenie.** Czy `reduce` może zawsze zastąpić `accumulate` dla liczb zmiennoprzecinkowych? **Odpowiedź:** nie, może inaczej grupować działania. Dodawanie zmiennoprzecinkowe nie jest matematycznie łączne w arytmetyce maszyny, więc wynik może się różnić. Wybór dotyczy również wymagań dotyczących powtarzalności, a nie tylko szybkości.

Źródła reguł: [C++23: wymagania algorytmów](https://timsong-cpp.github.io/cppwp/n4950/algorithms.requirements), [domknięcia lambd](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.lambda.closure), [algorytmy numeryczne](https://timsong-cpp.github.io/cppwp/n4950/numeric.ops).

## Powiązane tematy

- [Iteratory](04_iteratory_i_invalidacja.md)
- [Ranges](06_ranges_i_views.md)
- [Współbieżność](../10_wspolbieznosc/01_thread_jthread_i_stop_token.md)
