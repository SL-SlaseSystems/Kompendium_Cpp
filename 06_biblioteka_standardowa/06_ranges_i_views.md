[← Spis treści](../README.md)

# Ranges i views

Biblioteka ranges z C++20 opisuje zakres przez `range`, iterator i sentinel. Algorytmy `std::ranges` mają lepsze constraints, obsługują projection i mogą przyjmować cały zakres. Views są leniwymi, zwykle tanimi adaptacjami: filtrują, transformują lub ograniczają dane bez natychmiastowego tworzenia nowego kontenera.

~~~cpp
#include <cassert>
#include <ranges>
#include <vector>

int main() {
    const std::vector values{1, 2, 3, 4, 5, 6};
    auto result = values
        | std::views::filter([](int value) { return value % 2 == 0; })
        | std::views::transform([](int value) { return value * value; });

    std::vector<int> materialized;
    for (int value : result) {
        materialized.push_back(value);
    }

    assert((materialized == std::vector{4, 16, 36}));
}
~~~

Pipeline nie wykonuje pracy przy utworzeniu `result`; elementy są obliczane podczas iteracji. To może eliminować kolekcje pośrednie, ale wielokrotne przejście może ponawiać obliczenia. Nie każdy view jest common, sized lub random-access. Wymagania zależą od źródła i zastosowanych adapterów.

Lifetime jest kluczowy. View może przechowywać referencję do zakresu źródłowego albo posiadać rvalue range przez `owning_view`, zależnie od konstrukcji. `borrowed_range` pozwala określić, czy iterator wyniku może przetrwać zniszczenie obiektu range. Nie oznacza ogólnej gwarancji, że wszystkie elementy są wieczne.

C++23 dodaje kilka adapterów i usprawnień, lecz wsparcie konkretnej biblioteki standardowej trzeba sprawdzać feature-test macros. Jeśli końcowy API potrzebuje `vector`, zmaterializuj wynik jawnie; `std::ranges::to` jest C++23, ale lokalna implementacja może jeszcze go nie dostarczać.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Ranges i views”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie zakresu, wykonanie operacji zgodnie z wymaganiami iteratora i aktualizację stanu kontenera wraz z regułami invalidacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij właściciela elementów od widoku, kolejność logiczną od fizycznego układu i gwarancję złożoności od konkretnego czasu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź rozmiar i capacity, ważność iteratorów, liczbę alokacji, kolejność elementów oraz klasę złożoności. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Kontenery i algorytmy biblioteki standardowej mają kontrakty dotyczące złożoności, invalidacji, własności oraz zakresów. Poprawny wybór wynika z wymaganych operacji i stabilności adresów, nie z przyzwyczajenia do jednego kontenera. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- View jest zwykle leniwym i niewłaścicielskim opisem transformacji zakresu. Pipeline nie wykonuje pracy do chwili iteracji, a tymczasowy zakres może wymagać mechanizmu borrowed range, aby iterator nie stał się dangling.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Ranges i views” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Ranges i views
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Ranges i views”, oceniaj wzorzec dostępu, lokalność danych, stabilność referencji, koszt modyfikacji i możliwość użycia gotowego algorytmu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Iteratory](04_iteratory_i_invalidacja.md)
- [Widoki i dangling](../03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
- [Concepts](../05_szablony_i_generycznosc/04_concepts_i_requires.md)
