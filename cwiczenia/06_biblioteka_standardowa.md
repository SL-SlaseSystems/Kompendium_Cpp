[← Mapa działu](../06_biblioteka_standardowa/README.md) · [Spis treści](../README.md)

# Ćwiczenia: kontenery, zakresy i znaczenie bajtów

Wybór narzędzia uzasadniaj konkretną operacją oraz kontraktem. Zapisz osobno złożoność, ważność odwołań i własność danych. Dla tekstu dopisz, czy operujesz na bajtach, punktach kodowych, czy znakach widzianych przez użytkownika.

## 1. Rejestr sesji z trwałymi odwołaniami

**Wejście:** serwer dodaje sesje według rosnącego identyfikatora; istniejące wskaźniki mają pozostać ważne podczas dodawania. Potrzebne są wyszukiwanie po identyfikatorze i usuwanie. **Oddaj:** wybór reprezentacji i kontrakt ważności wskaźnika po usunięciu sesji. Porównaj `vector<Session>` oraz `unordered_map<Id,Session>`. **Wskazówka:** invalidacja iteratora nie zawsze oznacza invalidację referencji.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wektor może realokować i unieważnić wskaźniki do elementów. W `unordered_map` rehash unieważnia iteratory, lecz nie wskaźniki i referencje do istniejących elementów; usunięcie danego elementu kończy ich ważność. Taka mapa spełnia wymaganie dodawania, przy średnim stałym koszcie wyszukiwania. Klient musi zakończyć pożyczanie przed usunięciem. [Kontenery i hash](../06_biblioteka_standardowa/03_map_set_unordered_i_hash.md).

</details>

## 2. Usuwanie podczas iteracji

**Wejście:** wektor zawiera `2,3,4,5,6`; pętla usuwa parzysty element i bezwarunkowo zwiększa stary iterator. **Oddaj:** bezpieczny wariant pętli oraz wariant biblioteczny. Kryterium: wynik `3,5`, także dla pustego wektora i wektora samych parzystych. **Wskazówka:** `erase` zwraca pozycję potrzebną do dalszego przejścia.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Przy usunięciu przypisz iterator zwrócony przez `erase`; zwiększaj go wyłącznie w gałęzi bez usuwania. Nie używaj starego `end` po zmianie wektora. Dla prostego predykatu wybierz `std::erase_if`, które wyraża całą operację i zwykle unika wielokrotnego przesuwania elementów charakterystycznego dla pojedynczych wymazań. [Invalidacja](../06_biblioteka_standardowa/04_iteratory_i_invalidacja.md).

</details>

## 3. Potok, który jeszcze niczego nie obliczył

**Wejście:** lokalny wektor jest filtrowany i transformowany przez views; funkcja zwraca potok. Klient iteruje dopiero po powrocie. **Oddaj:** diagnozę własności i dwie bezpieczne reprezentacje wyniku. Dodatkowo policz wywołania transformacji przy dwóch pełnych przejściach, gdy filtr wybiera trzy elementy. **Wskazówka:** zapamiętanie opisu operacji nie materializuje danych.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Potok utworzony z lokalnego lvalue zazwyczaj przechowuje odwołanie do tego wektora i po powrocie zwisa. Zwróć zmaterializowany kontener albo świadomie zbuduj potok posiadający przeniesione dane. Przy dwóch pełnych przejściach transformacja trzech wybranych elementów wykona się sześć razy, jeśli nie materializujesz wyniku. Efekty uboczne komplikują kontrakt. [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md).

</details>

## 4. Sortowanie rekordów bez utraty kolejności remisów

**Wejście:** rekordy `(priorytet, identyfikator)` przychodzą jako `(2,A),(1,B),(2,C),(1,D)`. Wynik ma grupować rosnące priorytety, zachowując kolejność nadejścia w grupie. **Oddaj:** algorytm, comparator i oczekiwany wynik. Sprawdź identyczne priorytety i pusty zakres. **Wskazówka:** dopisanie identyfikatora do porównania zmienia semantykę remisów.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Użyj `stable_sort` z porównaniem wyłącznie priorytetu przez `<`. Otrzymasz `(1,B),(1,D),(2,A),(2,C)`. Zwykły `sort` nie obiecuje zachowania kolejności elementów równoważnych. Comparator z `<=` jest niedozwolony, ponieważ dla elementu porównanego z samym sobą zwraca true i narusza wymagania porządku. [Algorytmy](../06_biblioteka_standardowa/05_algorytmy_i_lambdy.md).

</details>

## 5. Liczba bajtów nie jest liczbą znaków

**Wejście:** plik UTF-8 zawiera kolejno `A`, `ą` i emoji U+1F600; osobny plik kończy się pojedynczym bajtem `C4`. **Oddaj:** liczby bajtów i punktów kodowych pierwszego tekstu oraz politykę obsługi drugiego. Oceń, czy `substr(0,2)` daje poprawny UTF-8. **Wskazówka:** `std::string` nie waliduje kodowania.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Pierwszy tekst ma 7 bajtów i 3 punkty kodowe: 1+2+4 bajty. `substr(0,2)` ucina dwubajtowy zapis `ą`, więc tworzy niepoprawną sekwencję. Samotne `C4` jest niekompletne. Wybierz jawne odrzucenie z pozycją bajtową albo zastąpienie znakiem zastępczym; nie utożsamiaj punktów kodowych z grafemami. [UTF-8](../06_biblioteka_standardowa/08_unicode_utf8_i_parsowanie.md).

</details>

## 6. Parser liczby, który zjada za mało

**Wejście:** parser używa `from_chars` do `int`; testy dostają `42`, `42x`, pusty tekst, `+7` i liczbę przekraczającą zakres. **Oddaj:** tabelę akceptacji dla kontraktu „cały niepusty zapis dziesiętny ze znakiem minus, bez białych znaków”. **Wskazówka:** sukces konwersji prefiksu nie oznacza sukcesu walidacji pola.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Akceptuj `42`; odrzuć `42x`, mimo sukcesu konwersji prefiksu, sprawdzając `ptr == end`. Puste wejście i `+7` są niepoprawne dla tej konwersji całkowitej; przekroczenie zakresu daje `result_out_of_range`. Nie używaj wartości wyjściowej po błędzie. Minus jest dopuszczalny dla typu ze znakiem. [Parsowanie tekstu](../06_biblioteka_standardowa/08_unicode_utf8_i_parsowanie.md).

</details>
