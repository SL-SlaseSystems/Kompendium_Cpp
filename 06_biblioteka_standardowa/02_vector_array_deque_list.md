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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „vector, array, deque i list”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `vector` zapewnia ciągłość pamięci i dobrą lokalność, ale realokacja invaliduje wskaźniki oraz iteratory. `deque` segmentuje storage, `list` stabilizuje węzły kosztem lokalności, a `array` ma rozmiar w typie.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „vector, array, deque i list” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: vector, array, deque i list
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „vector, array, deque i list”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Iteratory i invalidacja](04_iteratory_i_invalidacja.md)
- [Dynamiczna pamięć](../03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

