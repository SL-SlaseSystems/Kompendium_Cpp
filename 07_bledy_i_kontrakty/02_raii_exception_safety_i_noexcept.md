[← Spis treści](../README.md)

# RAII, exception safety i noexcept

Exception safety opisuje stan programu po rzuceniu wyjątku. Gwarancja podstawowa oznacza brak wycieków i zachowanie inwariantów, ale stan może się zmienić. Gwarancja silna zapewnia efekt transakcyjny: operacja kończy się sukcesem albo nie zmienia obserwowalnego stanu. Gwarancja no-throw mówi, że operacja nie zgłasza wyjątków.

~~~cpp
#include <cassert>
#include <string>
#include <utility>
#include <vector>

class Names {
public:
    void add(std::string name) {
        auto copy = names_;
        copy.push_back(std::move(name));
        names_.swap(copy);
    }

    [[nodiscard]] std::size_t size() const noexcept { return names_.size(); }

private:
    std::vector<std::string> names_;
};

int main() {
    Names names;
    names.add("Ada");
    assert(names.size() == 1);
}
~~~

Przykład ilustruje prostą technikę copy-and-commit dającą silną gwarancję, ale kopia może być kosztowna. Standardowe kontenery często oferują lepsze, wyspecjalizowane gwarancje. Projektuj najpierw poprawny kontrakt, a później optymalizuj na podstawie pomiaru.

`noexcept` jest częścią typu funkcji od C++17 i obietnicą: wyjątek opuszczający funkcję `noexcept` uruchamia `std::terminate`. Nie używaj go jako prośby o optymalizację. Zaznaczaj nim destruktory, operacje swap i move tylko wtedy, gdy wszystkie wykonywane operacje rzeczywiście nie rzucają. `noexcept(expression)` pozwala warunkowo przenieść własność szablonowego kodu.

`std::vector` podczas realokacji może wybrać kopiowanie zamiast potencjalnie rzucającego move, by zachować silną gwarancję. Dlatego poprawnie warunkowy `noexcept` konstruktor przenoszący ma znaczenie semantyczne i wydajnościowe.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „RAII, exception safety i noexcept”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wykrycie niespełnionego warunku, zbudowanie informacji o błędzie, propagację przez granice oraz odtworzenie prawidłowego stanu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd możliwy do obsłużenia od naruszenia precondition i zagwarantuj sprzątanie niezależnie od wybranej ścieżki. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ błędu, zachowany kontekst, stan obiektów po porażce i spełniony poziom exception safety. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Obsługa błędów zaczyna się od klasyfikacji niepowodzenia: naruszenie kontraktu programisty, spodziewany brak wyniku, błąd środowiska albo awaria uniemożliwiająca kontynuację. Mechanizm raportowania powinien odpowiadać tej kategorii. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- RAII wiąże zwolnienie zasobu z destruktorem obiektu posiadającego. Podczas stack unwinding niszczone są w pełni skonstruowane podobiekty, dlatego częściowo nieudany konstruktor nie wymaga ręcznego odwijania wcześniej utworzonych członów.
- Basic guarantee zachowuje inwariant i brak wycieku, strong guarantee pozostawia obserwowalny stan bez zmian, a nothrow gwarantuje brak wyjątku. `noexcept` wpływa także na wybór move przez kontenery.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „RAII, exception safety i noexcept” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: RAII, exception safety i noexcept
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „RAII, exception safety i noexcept”, oceniaj częstotliwość błędu, koszt ścieżki sukcesu, możliwość pominięcia wyniku, zgodność z RAII i czytelność kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Wyjątki](01_wyjatki_try_catch_throw.md)
- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)

