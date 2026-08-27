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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Iteratory i invalidacja”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Kategoria iteratora określa dozwolone operacje i liczbę przejść, a sentinel może mieć inny typ niż iterator. Reguły invalidacji zależą od kontenera i konkretnej operacji, dlatego muszą być częścią lokalnego dowodu poprawności.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Iteratory i invalidacja” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Iteratory i invalidacja
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Iteratory i invalidacja”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Nie przechowuj iteratora przez operację modyfikującą kontener bez sprawdzenia kontraktu. Używaj wyniku `erase`, gdy zwraca następny poprawny iterator. Preferuj algorytmy i ranges, które zmniejszają ręczną arytmetykę pozycji.

## Powiązane tematy

- [Kontenery sekwencyjne](02_vector_array_deque_list.md)
- [Algorytmy i lambdy](05_algorytmy_i_lambdy.md)
- [Ranges i views](06_ranges_i_views.md)

