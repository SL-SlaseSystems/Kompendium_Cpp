[← Spis treści](../README.md)

# Iteratory i invalidacja

Iterator uogólnia pozycję w zakresie. Para `[first, last)` opisuje półotwarty przedział: `first` wskazuje pierwszy element, a `last` pozycję za końcem. Standardowe algorytmy mogą dzięki temu działać na różnych kontenerach i widokach.

Kategorie iteratorów wyrażają dostępne operacje: input, output, forward, bidirectional, random access i contiguous. W C++20 concepts iteratorowe oraz ranges precyzyjniej rozdzielają iterator od sentinel. Algorytm wymaga określonej minimalnej kategorii; np. sortowanie potrzebuje random access.

~~~cpp
#include <algorithm>
#include <cassert>
#include <iterator>
#include <vector>

int main() {
    std::vector values{2, 4, 6, 8};
    const auto found = std::ranges::find(values, 6);
    assert(found != values.end());
    assert(std::distance(values.begin(), found) == 2);

    values.erase(std::remove(values.begin(), values.end(), 4), values.end());
    assert((values == std::vector{2, 6, 8}));
}
~~~

Przykład pokazuje klasyczny erase-remove idiom. Od C++20 `std::erase` i `std::erase_if` upraszczają wiele takich operacji. `remove` sam nie zmniejsza kontenera: przesuwa zachowane elementy i zwraca nowy logiczny koniec.

Iterator zostaje unieważniony, gdy operacja kontenera sprawia, że nie odnosi się już do prawidłowej pozycji. Reguły są zależne od kontenera i operacji. Realokacja wektora unieważnia wszystkie iteratory; usunięcie elementu mapy zwykle tylko iterator do tego elementu. Dereferencja iteratora końcowego lub unieważnionego może być UB.

## Jak to działa krok po kroku

`find` rozpoczyna na pierwszym elemencie i przesuwa iterator, aż porównanie zwróci prawdę albo osiągnie sentinel końcowy. Zwrócone `end()` jest poprawnym wynikiem „nie znaleziono”, ale nie wskazuje elementu. Sprawdzenie wyniku musi poprzedzać dereferencję. Pusty zakres ma `begin() == end()`, dzięki czemu ten sam algorytm działa bez osobnej gałęzi dla pustego kontenera.

W erase-remove algorytm `remove` zachowuje względną kolejność pozostawionych elementów, przypisując je na wcześniejsze miejsca. Zwraca pierwszy iterator ogona do usunięcia. Rozmiar wektora jeszcze się nie zmienia, a wartości w ogonie są poprawne, lecz nieokreślone jako konkretny wynik użytkowy. Dopiero `erase` niszczy te elementy i aktualizuje rozmiar. Nie przetwarzaj ogona jako listy usuniętych wartości.

Odejmowanie iteratorów wektora jest stałoczasowe, ale `std::distance` na liście musi przejść po węzłach. Zapis wyglądający tak samo może więc mieć różną złożoność. Nie porównuj ani nie odejmuj dowolnych iteratorów różnych kontenerów: operacje mają wymagania dotyczące wspólnego zakresu. Naruszenie tych wymagań nie jest przenośnym sposobem sprawdzania, czy dwa elementy pochodzą z tej samej kolekcji.

## Pogłębienie mechanizmu

Iterator input gwarantuje odczyt w modelu pojedynczego przejścia. Skopiowanie iteratora strumieniowego nie tworzy niezależnego kursora pliku; odczyt jednym może zmienić sytuację drugiego. Forward dodaje wieloprzejściowość, bidirectional umożliwia `--`, a random access skoki i arytmetykę w stałym czasie. Contiguous dodaje związek między nawigacją a sąsiednimi adresami rzeczywistych elementów. `deque` ma random access, ale nie contiguous.

W ranges sentinel może mieć inny typ niż iterator. Wystarczy móc stwierdzić, czy osiągnięto koniec; sentinel nie musi nadawać się do dereferencji ani cofania. `std::ranges::distance` może skorzystać ze znanego rozmiaru zakresu, natomiast zwykła pętla potrzebuje tylko warunku zakończenia. Concepts sprawdzają dostępność wyrażeń, ale wiele wymagań semantycznych, takich jak wieloprzejściowość, pozostaje odpowiedzialnością autora typu.

Unieważnienie to utrata prawa do używania pozycji zgodnie z dawnym kontraktem. Wektor po wstawieniu bez realokacji zachowuje iteratory przed miejscem wstawienia, ale unieważnia te od tego miejsca do starego końca. `erase` unieważnia od miejsca usuwania dalej. Nawet jeśli liczbowy adres pamięci się nie zmienił, stary iterator może być już niedozwolony. Zapamiętane `end()` także podlega unieważnieniu.

Odróżniaj stałość iteratora od stałości elementu. `const auto it = values.begin()` nie pozwala przesunąć samego it, ale dla mutowalnego wektora może pozwalać zmienić `*it`. Iterator otrzymany z `cbegin()` można przesuwać, lecz nie można przez niego przypisać nowej wartości elementu. Jeszcze innym przypadkiem jest obiekt pośredniczący, np. referencja bitowa `vector<bool>`. Kod generyczny powinien używać właściwych traits lub concepts, zamiast zakładać, że każdy wynik dereferencji jest zwykłym T&.

## Drugi przykład

Podczas usuwania w pętli korzystaj z iteratora zwracanego przez kontener. Pozycja następnego elementu zależy od przeprowadzonej modyfikacji.

~~~cpp
#include <cassert>
#include <vector>

int main() {
    std::vector<int> values{1, 2, 4, 5, 6};
    for (auto it = values.begin(); it != values.end();) {
        if (*it % 2 == 0) {
            it = values.erase(it);
        } else {
            ++it;
        }
    }
    assert((values == std::vector<int>{1, 5}));

    std::vector<int> output;
    output.reserve(values.size());
    for (int value : values) {
        output.push_back(value * 10);
    }
    assert((output == std::vector<int>{10, 50}));
}
~~~

Po usunięciu liczby dwa dawna pozycja następnego elementu jest nieaktualna, ale wynik `erase` wskazuje aktualną liczbę cztery. Dodatkowe `++it` w tej gałęzi pominęłoby ją. Dla wektora powtarzane usuwanie może być kwadratowe; kiedy warunek jest prostym filtrem, `std::erase_if` zwykle lepiej wyraża całą operację i ogranicza przesuwanie elementów.

## Porównanie i decyzje

Iterator nie jest automatycznie bezpieczniejszy od indeksu. Oba są pozycjami, których interpretacja może zmienić się po modyfikacji. Indeks przetrwa realokację jako liczba, ale po usunięciu wcześniejszego elementu może oznaczać inną wartość. Jeśli potrzebujesz trwałej tożsamości, stosuj identyfikator domenowy albo obiekt o odpowiednio stabilnym czasie życia.

**Ćwiczenie.** Czy `reserve(100)` wystarczy, aby bezpiecznie robić `push_back` wewnątrz zakresowej pętli po tym samym wektorze, dopóki rozmiar nie przekroczy stu? **Odpowiedź:** nie. Pętla zachowuje iterator końcowy, a dodanie elementu unieważnia dawny `end()` również bez realokacji. Jeśli przetwarzasz tylko pierwotne elementy, zapisz początkowy rozmiar i używaj indeksów, pilnując osobno stabilności ewentualnych referencji.

Źródła reguł: [C++23: wymagania iteratorów](https://timsong-cpp.github.io/cppwp/n4950/iterator.requirements), [modyfikatory wektora](https://timsong-cpp.github.io/cppwp/n4950/vector.modifiers), [remove](https://timsong-cpp.github.io/cppwp/n4950/alg.remove).

## Powiązane tematy

- [Kontenery sekwencyjne](02_vector_array_deque_list.md)
- [Algorytmy i lambdy](05_algorytmy_i_lambdy.md)
- [Ranges i views](06_ranges_i_views.md)
