[← Spis treści](../README.md)

# vector, array, deque i list

`std::vector<T>` jest domyślnym kontenerem sekwencyjnym: przechowuje elementy ciągle, zapewnia szybki dostęp indeksowany i dobrą lokalność cache. `std::array<T, N>` ma stały rozmiar należący do typu. `std::deque<T>` umożliwia efektywne dodawanie na obu końcach bez gwarancji jednego ciągłego bufora. `std::list<T>` jest listą dwukierunkową i powinien być wybierany tylko wtedy, gdy jego stabilność iteratorów oraz operacje splice rzeczywiście przeważają nad kosztami alokacji i słabą lokalnością.

~~~cpp
#include <algorithm>
#include <array>
#include <cassert>
#include <deque>
#include <vector>

int main() {
    std::vector<int> values{3, 1, 2};
    values.reserve(8);
    values.push_back(4);
    std::ranges::sort(values);

    std::array fixed{10, 20, 30};
    std::deque<int> queue{2, 3};
    queue.push_front(1);

    assert(values.front() == 1 && values.back() == 4);
    assert(fixed.size() == 3);
    assert(queue.front() == 1);
}
~~~

`vector::size()` to liczba elementów, a `capacity()` liczba możliwa bez realokacji. `reserve` zmienia pojemność, nie rozmiar; `resize` zmienia rozmiar i konstruuje lub niszczy elementy. `shrink_to_fit` jest niewiążącą prośbą.

Realokacja wektora unieważnia wszystkie wskaźniki, referencje i iteratory do jego elementów. Wstawienie bez realokacji ma bardziej lokalne zasady invalidacji. `deque` i `list` mają inne reguły; zawsze sprawdzaj kontrakt konkretnej operacji.

## Wybór

Zacznij od `vector`. Wybierz `array`, gdy rozmiar jest compile-time i wartość ma być przechowywana inline. Wybierz `deque` dla kolejki z operacjami na obu końcach. Nie wybieraj listy tylko dlatego, że wstawienie ma formalnie O(1): odnalezienie miejsca, alokacje i cache często dominują.

## Jak to działa krok po kroku

Początkowy wektor zawiera trzy skonstruowane liczby. `reserve(8)` zapewnia miejsce na co najmniej osiem elementów; jeśli dotychczasowy bufor jest za mały, następują alokacja, konstrukcja elementów w nowym miejscu i zwolnienie starej pamięci. Nie wolno odczytywać `values[7]`, ponieważ rozmiar nadal wynosi trzy. Dopiero `push_back(4)` konstruuje czwarty element i zwiększa rozmiar. Posortowanie zmienia wartości na pozycjach, nie rozmiar ani pojemność.

Amortyzowane O(1) dla dodawania na koniec oznacza koszt uśredniony nad sekwencją operacji. Pojedyncze dodanie może kosztować O(n), gdy wymaga realokacji. Standard nie nakazuje konkretnego współczynnika wzrostu pojemności. Wywoływanie `reserve(size()+1)` przed każdym dodaniem może zniszczyć korzystny wzorzec wzrostu i spowodować kwadratową sumę przenosin. Rezerwuj raz na podstawie oszacowania całego zadania.

`array` przechowuje dokładnie N elementów wewnątrz siebie, więc jego kopiowanie kopiuje elementy. Nie musi leżeć na stosie: może być polem obiektu zaalokowanego dynamicznie. `array<int, 0>` jest poprawnym pustym kontenerem, ale `front()` i `back()` nie stają się przez to dozwolone. Dostęp przez `at` sprawdza granicę i rzuca, podczas gdy `operator[]` wymaga prawidłowego indeksu.

## Pogłębienie mechanizmu

`deque` gwarantuje dostęp losowy w stałym czasie, jednak nie ciągłość całego zakresu. Nie można przekazać adresu pierwszego elementu i rozmiaru do API oczekującego jednej tablicy. Wstawienie na którymkolwiek końcu unieważnia iteratory, ale pozostawia referencje do dotychczasowych elementów. Wstawienie w środku ma surowsze skutki. Ta różnica pokazuje, że iterator może przechowywać dodatkowy stan nawigacji, niezależny od adresu elementu.

`list` gwarantuje stabilność iteratorów i referencji przy wstawianiu, a usunięcie unieważnia te odnoszące się do usuniętych elementów. `splice` przekazuje istniejące elementy pomiędzy listami bez kopiowania ich wartości. Warunki obejmują zgodność allocatorów; nie wolno zakładać, że dowolne dwa zasobniki pamięci są wymienne. Złożoność zależy od przeciążenia: przeniesienie pojedynczego elementu jest stałe, a przekazanie zakresu między różnymi listami może wymagać jego policzenia.

`emplace_back(args...)` konstruuje element z argumentów bez obowiązkowego zewnętrznego obiektu tymczasowego. Nie gwarantuje jednak braku realokacji ani braku przenoszenia wcześniejszych elementów. Gdy istnieje już wartość typu T, `push_back(std::move(value))` zwykle wyraża intencję wystarczająco jasno. Dla `vector<bool>` obowiązuje szczególna reprezentacja bitowa: wynik indeksowania jest obiektem pośredniczącym, więc nie traktuj go jak zwykłego `bool&`.

`resize(n)` dla wektora liczb z domyślnym allocatorem tworzy brakujące elementy o wartości zero, a zmniejszenie rozmiaru niszczy końcowe elementy. Nie oznacza to obowiązkowego oddania pojemności systemowi. Dzięki temu późniejsza rozbudowa może wykorzystać istniejący bufor. Wywołanie `clear` także usuwa elementy, pozostawiając pojemność wektora; stare referencje do zniszczonych elementów nie odzyskują ważności tylko dlatego, że pamięć jeszcze pozostaje zaalokowana. Własność storage i czas życia poszczególnych T to różne warstwy.

## Drugi przykład

Lista jest uzasadniona, gdy aplikacja już posiada pozycję elementu i chce zmienić jego przynależność do kolejki przy zachowaniu tożsamości.

~~~cpp
#include <cassert>
#include <iterator>
#include <list>
#include <string>

int main() {
    std::list<std::string> waiting{"compile", "test", "package"};
    std::list<std::string> running;
    const auto job = std::next(waiting.begin());
    const auto* address = &*job;

    running.splice(running.end(), waiting, job);

    assert(waiting.size() == 2 && running.size() == 1);
    assert(*job == "test");
    assert(&running.front() == address);
    running.erase(job);
    assert(running.empty());
}
~~~

Po `splice` iterator `job` nadal odnosi się do tego samego elementu, który należy już do `running`. Dlatego przekazujemy go do `running.erase`, a nie do `waiting.erase`. Po usunięciu nie wolno go dereferencjonować. Sam brak zmiany wartości nie tłumaczy poprawności: istotne jest zachowanie czasu życia i adresu obiektu podczas przekazania.

## Porównanie i decyzje

Dla intensywnego przeglądania danych lokalność wektora często wygrywa ze stałym kosztem wstawiania listy. Jeśli potrzebujesz stabilnych adresów obiektów i zwartej tablicy uchwytów, rozważ `vector<unique_ptr<T>>`: realokacja przesuwa właścicieli, ale nie wskazywane obiekty. Płacisz wtedy za osobne alokacje i pośredni dostęp, co trzeba uwzględnić w pomiarze.

**Ćwiczenie.** Kolejka usuwa pierwszy element i dodaje na końcu milion razy. Dlaczego `vector.erase(begin())` może być złym wyborem? **Odpowiedź:** każde usunięcie przesuwa pozostałe elementy, więc koszt rośnie z długością kolejki. `deque::pop_front` odpowiada temu wzorcowi; dla ograniczonej pojemności można również zaprojektować bufor cykliczny z jawnymi zasadami przepełnienia.

Źródła reguł: [C++23: vector](https://timsong-cpp.github.io/cppwp/n4950/vector), [deque](https://timsong-cpp.github.io/cppwp/n4950/deque), [list i splice](https://timsong-cpp.github.io/cppwp/n4950/list.ops).

## Powiązane tematy

- [Iteratory i invalidacja](04_iteratory_i_invalidacja.md)
- [Dynamiczna pamięć](../03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)
