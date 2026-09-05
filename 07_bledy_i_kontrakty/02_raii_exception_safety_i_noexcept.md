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

W `Names::add` najpierw powstaje kopia istniejącej kolekcji. Jeśli kopiowanie napisu lub alokacja zawiedzie, oryginalne `names_` pozostaje nietknięte. Następnie dopisujemy nowy element do kopii; także tutaj porażka niszczy tylko stan roboczy. Dopiero `swap` zatwierdza zmianę. Stara kolekcja trafia do `copy` i jest zwalniana przy wyjściu z funkcji. Granicą zatwierdzenia jest więc konkretna operacja, która nie może już zawieść.

Gwarancję należy opisywać względem obserwowalnego stanu. Jeśli funkcja przed wykonaniem kopii wysłała wiadomość do sieci lub zwiększyła zewnętrzny licznik, wymiana wektorów nie cofnie tych efektów. Silna gwarancja dla obiektu `Names` nie oznacza transakcji całego otoczenia. Dla danych zewnętrznych potrzebne są osobne mechanizmy: transakcja bazy, plik tymczasowy i zamiana albo operacja kompensująca.

RAII zapewnia sprzątanie zasobów, lecz samo nie gwarantuje wycofania zmian logicznych. Dwa kontenery mogą nie wyciekać, a mimo to po wyjątku zawierać niespójne dane. Przykładowo zapis rekordu w pierwszej mapie i nieudana aktualizacja indeksu w drugiej łamią wspólny inwariant. Trzeba zmienić kolejność, pracować na stanie tymczasowym lub zastosować poprawny rollback.

## Pogłębienie mechanizmu

Operator `noexcept(expr)` sprawdza statyczną informację, czy wyrażenie jest potencjalnie rzucające; nie wykonuje go i nie analizuje wszystkich ścieżek na podstawie znanych danych. Funkcja może zawsze poprawnie kończyć się dla konkretnego argumentu, a nadal dawać `false`, jeśli jej deklaracja dopuszcza wyjątek. Z kolei zadeklarowanie nieprawdziwego `noexcept` nie powoduje automatycznej obsługi: wyjątek opuszczający tę granicę kończy proces.

Wyjątek może zostać rzucony i złapany wewnątrz funkcji `noexcept`, o ile nie wydostanie się poza nią. To pozwala implementować niezgłaszający interfejs, który tłumaczy porażki na kod wyniku. Trzeba jednak sprawdzić, czy sama ścieżka tłumaczenia, tworzenie komunikatu i logowanie również nie rzucają. W destruktorze najbezpieczniejsze jest sprzątanie, które nie wymaga nowych zasobów.

Standardowy wektor przy realokacji często korzysta z idei `move_if_noexcept`: kopiuje, gdy kopia jest dostępna, a move może rzucić. Nie wolno upraszczać tego do twierdzenia, że każdy wektor zawsze ma silną gwarancję. Jeśli element jest niekopiowalny i ma rzucający konstruktor przenoszący, wyjątek podczas takiego przenoszenia może oznaczać słabsze, określone dla danej operacji gwarancje. `noexcept` elementu wpływa więc na możliwą strategię kontenera.

Niejawna specyfikacja destruktora zależy od destruktorów jego pól i baz. Zwykle jest niezgłaszająca, lecz pole z destruktorem `noexcept(false)` może zmienić ten wynik. Deklarując własny destruktor, sprawdź również wpływ na automatyczne generowanie operacji przenoszących. Czasem najlepszym rozwiązaniem jest rule of zero: kontener i smart pointer już kodują poprawne niszczenie, kopiowanie lub zakaz kopii. Dodatkowy pusty destruktor może zmienić własności typu bez jakiejkolwiek korzyści dla sprzątania.

## Drugi przykład

Silną gwarancję można przetestować przez kontrolowaną porażkę przed punktem zatwierdzenia. Wartość zależy od danych, a nie od manipulowania globalnym allocatorem.

~~~cpp
#include <cassert>
#include <stdexcept>
#include <utility>
#include <vector>

class Scores {
    std::vector<int> data_{1, 2};
public:
    void append_checked(int score) {
        auto candidate = data_;
        candidate.push_back(score);
        if (score < 0) {
            throw std::invalid_argument{"negative score"};
        }
        data_.swap(candidate);
    }
    const std::vector<int>& values() const noexcept { return data_; }
};

int main() {
    Scores scores;
    const auto before = scores.values();
    bool rejected = false;
    try {
        scores.append_checked(-1);
    } catch (const std::invalid_argument&) {
        rejected = true;
    }
    assert(rejected && scores.values() == before);
    scores.append_checked(3);
    assert((scores.values() == std::vector<int>{1, 2, 3}));
    static_assert(noexcept(scores.values()));
}
~~~

W rzeczywistym kodzie sprawdzenie ujemnego argumentu należałoby wykonać przed kopiowaniem. Tutaj jest celowo później, aby unaocznić, że częściowo zmieniony stan roboczy można porzucić. Test sprawdza nie tylko złapanie wyjątku, ale także zachowanie starej wartości. Osobno warto testować każdą operację mogącą rzucić, używając kontrolowanego typu elementu lub wstrzykiwanego źródła porażki.

## Porównanie i decyzje

Copy-and-swap lub copy-and-commit jest prosty do udowodnienia, ale może kopiować zbyt wiele. Operacja wyspecjalizowana potrafi osiągnąć to samo, rezerwując miejsce przed modyfikacją i dopiero potem wykonując niezgłaszające kroki. Rollback jest dobry tylko wtedy, gdy sam nie zawiedzie i rzeczywiście odtworzy wszystkie istotne własności. Nie obiecuj silnej gwarancji bez wskazania punktu zatwierdzenia.

**Ćwiczenie.** Czy dodanie `noexcept` do `append_checked` uczyni ją bezpieczniejszą? **Odpowiedź:** nie. Przy ujemnym wyniku zewnętrzny handler nie otrzyma wyjątku, bo zostanie wywołane `terminate`. Deklaracja `noexcept` opisuje zapewnienie implementacji, a nie polecenie, aby kompilator automatycznie naprawiał błędy. Klient musi nadal znać strategię zgłaszania niepowodzenia.

Źródła reguł: [C++23: specyfikacje wyjątków](https://timsong-cpp.github.io/cppwp/n4950/except.spec), [operator noexcept](https://timsong-cpp.github.io/cppwp/n4950/expr.unary.noexcept), [gwarancje modyfikatorów vector](https://timsong-cpp.github.io/cppwp/n4950/vector.modifiers).

## Powiązane tematy

- [Wyjątki](01_wyjatki_try_catch_throw.md)
- [Copy i move](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [RAII](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
