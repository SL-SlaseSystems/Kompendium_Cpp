[← Spis treści](../README.md)

# Assertions, preconditions i contracts

Precondition opisuje warunek, który klient musi spełnić przed wywołaniem. Postcondition opisuje zapewnienie po sukcesie, a inwariant własność utrzymywaną przez poprawne stany typu. Kontrakt istnieje niezależnie od sposobu sprawdzania: dokumentacja, typy, assertions i walidacja wejścia pełnią różne role.

~~~cpp
#include <cassert>
#include <optional>
#include <span>

std::optional<double> average(std::span<const int> values) {
    if (values.empty()) {
        return std::nullopt;
    }
    long long total = 0;
    for (int value : values) {
        total += value;
    }
    return static_cast<double>(total) / static_cast<double>(values.size());
}

int main() {
    const int values[]{2, 4, 6};
    const auto result = average(values);
    assert(result && *result == 4.0);
}
~~~

Makro `assert` jest usuwane, gdy zdefiniowano `NDEBUG`. Nie używaj go do walidacji niezaufanego wejścia, wykonywania niezbędnych efektów ubocznych ani obsługi błędu, który może legalnie zdarzyć się w produkcji. Assertion jest odpowiednie dla naruszenia wewnętrznego założenia programisty.

Silniejsze typy mogą uczynić niedozwolony stan niereprezentowalnym, np. `NonEmptySpan` skonstruowany przez walidującą fabrykę. To przenosi sprawdzenie na granicę i upraszcza wnętrze. Nie każdy warunek daje się jednak zakodować w typie bez nieproporcjonalnej złożoności.

Kontrakty językowe były proponowane i zmieniały się w toku standaryzacji. Nie opisuj wcześniejszych eksperymentalnych składni jako części C++23. W nowszym standardzie użycie contracts zależy od ostatecznie opublikowanej specyfikacji i wsparcia implementacji; bazowy kod powinien mieć własną strategię niezależną od przyszłego mechanizmu.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Assertions, preconditions i contracts”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wykrycie niespełnionego warunku, zbudowanie informacji o błędzie, propagację przez granice oraz odtworzenie prawidłowego stanu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd możliwy do obsłużenia od naruszenia precondition i zagwarantuj sprzątanie niezależnie od wybranej ścieżki. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ błędu, zachowany kontekst, stan obiektów po porażce i spełniony poziom exception safety. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Obsługa błędów zaczyna się od klasyfikacji niepowodzenia: naruszenie kontraktu programisty, spodziewany brak wyniku, błąd środowiska albo awaria uniemożliwiająca kontynuację. Mechanizm raportowania powinien odpowiadać tej kategorii. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Assertion wykrywa założenie programisty w konfiguracji, w której jest aktywne; nie zastępuje walidacji niezaufanego wejścia. Precondition należy udokumentować tak, aby wywołujący mógł je spełnić przed wejściem do funkcji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Assertions, preconditions i contracts” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Assertions, preconditions i contracts
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Assertions, preconditions i contracts”, oceniaj częstotliwość błędu, koszt ścieżki sukcesu, możliwość pominięcia wyniku, zgodność z RAII i czytelność kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [optional i expected](03_optional_expected_i_kody_bledow.md)
- [Enkapsulacja](../04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

