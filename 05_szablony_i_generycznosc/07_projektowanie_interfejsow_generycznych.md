[← Spis treści](../README.md)

# Projektowanie interfejsów generycznych

**Wymagania wstępne:** dedukcja szablonów, concepts, kategorie wartości, referencje i czas życia. Przykłady używają C++23.

Dobry interfejs generyczny akceptuje różne reprezentacje mające potrzebne zachowanie. Nie polega to na zastąpieniu każdego typu przez `auto`. Trzeba zdecydować, które operacje algorytm wykonuje, jakie prawa umożliwiają rozumowanie o wyniku oraz kto jest właścicielem wejścia i wyjścia. Dopiero te decyzje przekładają się na ograniczenia szablonu i typ zwracany.

Najłatwiejsza pułapka to zaprojektowanie funkcji pod jeden `std::vector<int>`, a następnie dopisanie conceptu o podobnie brzmiącej nazwie. Szablon pozostaje wtedy przypadkowo zależny od kopiowania, wielokrotnego przechodzenia albo prawdziwej referencji. Weryfikacja wymaga konsumentów różniących się właśnie tymi własnościami, których algorytm rzekomo nie potrzebuje.

## Jak to działa krok po kroku

Zaprojektujmy transformację zwracającą właścicielski wektor wyników. Czyta każdy element raz, nie wymaga indeksowania i nie zachowuje referencji do zakresu. Funkcja transformująca ma zachowywać znaczenie dla równych wejść oraz nie modyfikować siebie ani argumentów. Z tego powodu wybieramy `regular_invocable`, świadomie przyjmując również jego wymagania semantyczne.

~~~cpp
#include <cassert>
#include <concepts>
#include <functional>
#include <list>
#include <ranges>
#include <sstream>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

template<class F, class R>
using Mapped = std::remove_cvref_t<
    std::invoke_result_t<F&, std::ranges::range_reference_t<R>>>;

template<class R, class F>
concept Collectable = std::ranges::input_range<R> &&
    std::regular_invocable<F&, std::ranges::range_reference_t<R>> &&
    std::is_object_v<Mapped<F, R>> &&
    std::move_constructible<Mapped<F, R>> &&
    std::constructible_from<Mapped<F, R>,
        std::invoke_result_t<F&, std::ranges::range_reference_t<R>>>;

template<class R, class F>
    requires Collectable<R, F>
auto collect(R&& source, F transform) -> std::vector<Mapped<F, R>> {
    std::vector<Mapped<F, R>> result;
    for (auto&& item : source) {
        result.emplace_back(std::invoke(
            transform, std::forward<decltype(item)>(item)));
    }
    return result;
}

struct AsText {
    std::string operator()(int value) const {
        return std::to_string(value);
    }
};

int main() {
    const std::list<int> values{2, 4, 6};
    const auto text = collect(values, AsText{});
    assert((text == std::vector<std::string>{"2", "4", "6"}));

    auto once = std::views::iota(1, 4) |
        std::views::transform([](int value) { return value * 10; });
    const auto doubled = collect(once, [](int value) { return value * 2; });
    assert((doubled == std::vector<int>{20, 40, 60}));
    std::istringstream input{"5 6"};
    const auto streamed = collect(std::ranges::istream_view<int>{input}, AsText{});
    assert((streamed == std::vector<std::string>{"5", "6"}));
    static_assert(!Collectable<std::vector<int>&, decltype([](int) {})>);
}
~~~

Najpierw sprawdzamy, czy wejście jest zakresem. Potem badamy wywołanie dokładnie w takiej kategorii, w jakiej nastąpi w ciele funkcji. Transformacja jest nazwaną zmienną, a więc lvalue: wymaganie dotyczy `F&`. Typ argumentu wynika z dereferencji iteratora, nie z arbitralnie wybranego `value_type`. To ważne dla iteratorów zwracających proxy albo wartości obliczane na żądanie.

Kolejne warunki określają możliwość utworzenia i przechowywania wyniku. Usuwamy kwalifikatory i referencję z rezultatu wywołania, ponieważ wektor ma przechowywać własne obiekty. Jeśli transformacja zwraca `const std::string&`, rezultat kolekcji zawiera kopie napisów. Samo usunięcie referencji z `std::string_view` nie tworzy natomiast własności znaków: wynik pozostaje wektorem widoków. Kontrakt elementu wyjściowego trzeba rozpatrywać osobno.

Wymaganie niemodyfikowania dotyczy samego wywołania transformacji. Jeżeli zwróci ona referencję rvalue do wejściowego obiektu, późniejsze tworzenie elementu wektora może go przenieść. Gwarancja pełnego odczytu bez zmian wymagałaby dodatkowego kontraktu wykluczającego taki alias. Ten szczegół pokazuje granicę conceptu: sprawdzenie wywołania nie opisuje automatycznie wszystkich dalszych skutków użycia jego wyniku.

Wymagamy jedynie `input_range`. Rezerwowanie pojemności na podstawie odległości iteratorów mogłoby zużyć zakres jednokrotnego przejścia. Optymalizacja przez `size()` wymagałaby osobnej ścieżki dla `sized_range`, a nie podniesienia podstawowego wymagania do każdego wygodnego conceptu. Koszt reallokacji wektora jest tu świadomym kompromisem na rzecz prostszego interfejsu.

## Pogłębienie mechanizmu

Syntaktyczne spełnienie conceptu oznacza, że kompilator potrafi sprawdzić wymagane wyrażenia i typy. Modelowanie obejmuje także prawa semantyczne. `regular_invocable` ma taki sam sprawdzalny warunek jak `invocable`, ale dodatkowo wymaga zachowania równości oraz braku modyfikowania obiektu wywoływalnego i argumentów. Licznik zwiększający swój stan przy każdym wywołaniu może przejść kontrolę składniową, a nie modelować tego conceptu. [Specyfikacja `regular_invocable`](https://timsong-cpp.github.io/cppwp/n4950/concept.regularinvocable) wyraźnie rozdziela te poziomy.

Nie traktuj więc `requires` jak dowodu poprawności algorytmu. Relacji równoważności, stabilności obserwacji czy ograniczeń złożoności zwykle nie da się dowieść podczas kompilacji. Dokumentuj je i sprawdzaj przez dobrane dane oraz przegląd implementacji. Dla standardowych szablonów użycie argumentu niespełniającego wymaganych praw może wykraczać poza gwarancje biblioteki, mimo braku komunikatu kompilatora. [N4950: concepts](https://timsong-cpp.github.io/cppwp/n4950/concepts) opisuje wymagania składniowe i semantyczne.

Forwarding służy zachowaniu kategorii wartości tam, gdzie ta kategoria należy do kontraktu. W przykładzie element jest przekazywany do transformacji raz i z kategorią odpowiadającą dereferencji. Obiekt transformacji pozostaje lvalue podczas całej pętli. Bezmyślne `std::forward<F>(transform)` w każdym obiegu mogłoby wielokrotnie wybierać przeciążenie `operator() &&`, którego autor przeznaczył do jednorazowego zużycia stanu. `std::forward` nie analizuje takich intencji i niczego nie zabezpiecza przed drugim użyciem. [Definicja forward](https://timsong-cpp.github.io/cppwp/n4950/forward) jest w istocie odpowiednim rzutowaniem.

Podobnie `decltype(auto)` nie oznacza automatycznie właściwego wyniku. Zachowuje kategorię i referencje wyrażenia, co może wyeksportować referencję do lokalnego obiektu. Zwykłe `auto` może zaś nieoczekiwanie skopiować element albo zachować wartość proxy, która nadal zależy od obcego bufora. Najpierw ustal kontrakt własności, potem wybierz składnię dedukcji. W interfejsie publicznym jawny typ wyniku bywa czytelniejszy od pozornej pełnej ogólności.

## Drugi przykład

Druga funkcja celowo zwraca referencję. Odrzuca tymczasowy kontener będący właścicielem oraz zakresy zwracające proxy przez wartość. Akceptuje tymczasowy `span`, ponieważ czas życia tego widoku nie wyznacza czasu życia elementów. Użytkownik nadal odpowiada za rzeczywiste źródło danych.

Tym razem wymagamy `forward_range`, mimo że odczytujemy tylko pierwszy element. Iterator wejściowy może przechowywać odczytaną wartość we własnym buforze; referencja uzyskana z lokalnej kopii iteratora mogłaby umrzeć wraz z nią. Iteratory forward zapewniają silniejszą stabilność odwołań do zakresu. Wymaganie wynika więc z życia wyniku, a nie z liczby przebiegów pętli. To przykład sytuacji, w której pozornie nadmiarowy concept faktycznie chroni kontrakt. [N4950: iterator forward](https://timsong-cpp.github.io/cppwp/n4950/iterator.concept.forward).

~~~cpp
#include <cassert>
#include <concepts>
#include <ranges>
#include <span>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <vector>

template<class R>
concept BorrowableFirst = std::ranges::forward_range<R> &&
    std::ranges::borrowed_range<R> &&
    std::is_lvalue_reference_v<std::ranges::range_reference_t<R>>;

template<BorrowableFirst R>
auto first_ref(R&& source) -> std::ranges::range_reference_t<R> {
    auto first = std::ranges::begin(source);
    if (first == std::ranges::end(source)) {
        throw std::out_of_range{"empty range"};
    }
    return *first;
}

template<class R>
concept CanReadFirst = requires(R&& source) {
    first_ref(std::forward<R>(source));
};

int main() {
    static_assert(CanReadFirst<std::vector<int>&>);
    static_assert(!CanReadFirst<std::vector<int>>);
    static_assert(!CanReadFirst<std::vector<bool>&>);
    static_assert(CanReadFirst<std::span<int>>);

    std::vector<int> values{3, 4};
    static_assert(std::same_as<decltype(first_ref(values)), int&>);
    static_assert(std::same_as<decltype(first_ref(std::as_const(values))),
                               const int&>);
    first_ref(values) = 9;
    assert(values.front() == 9);
    int data[]{7, 8};
    int& borrowed = first_ref(std::span{data});
    assert(&borrowed == &data[0]);
    bool rejected = false;
    try {
        std::vector<int> empty;
        (void)first_ref(empty);
    } catch (const std::out_of_range&) {
        rejected = true;
    }
    assert(rejected);
}
~~~

`borrowed_range` jest informacją o zależności iteratorów od obiektu zakresu, a nie uniwersalnym certyfikatem życia pamięci. Nazwany wektor spełnia warunek przy dedukcji parametru jako referencji. Jego zniszczenie albo operacja unieważniająca elementy nadal może unieważnić wynik. Tymczasowy `span` jest poprawny tylko wtedy, gdy wskazywana tablica żyje odpowiednio długo. [Definicja zakresu pożyczonego](https://timsong-cpp.github.io/cppwp/n4950/range.range) określa właśnie tę granicę.

Wymagania negatywne są częścią projektu, nie dodatkiem do testów. Odrzucenie tymczasowego wektora chroni przed częstym wiszącym odwołaniem. Odrzucenie `vector<bool>` wynika z obietnicy prawdziwej referencji, a nie z oceny przydatności tego kontenera. Test konsumenta sprawdza wywołanie publicznej funkcji, zachowanie `const`, możliwość modyfikacji oraz zachowanie pustego zakresu. Sam test conceptu nie wykazałby pomyłki w zwracanym typie funkcji.

Pozytywne przykłady też powinny łamać wygodne założenia autora. Lista sprawdza brak zależności od indeksowania, widok transformujący dostarcza obliczane wartości, a strumień wymusza pojedyncze przejście. Takie testy są bardziej informacyjne niż kilkanaście podobnych wektorów. Nie dowodzą wszystkich praw semantycznych, ale trafiają w konkretne granice zadeklarowanej ogólności.

## Porównanie i decyzje

Gdy wynik ma przetrwać źródło, wybierz właścicielską wartość. Gdy funkcja daje dostęp do elementu istniejącego obiektu, pokaż pożyczanie w typie i ograniczeniach. Jeśli potrzebujesz operacji zużywającej elementy, zaprojektuj ją osobno i nazwij ten skutek. Uniwersalna referencja nie powinna ukrywać decyzji, czy funkcja czyta, kopiuje, czy przejmuje zasób.

**Ćwiczenie 1.** Dlaczego dodanie `std::copyable<F>` do `collect` byłoby nadmiarowe?

<details>
<summary>Rozwiązanie</summary>

Pętla nie kopiuje transformacji. Parametr przez wartość można utworzyć z przenoszalnego obiektu tymczasowego, a potem wywoływać go jako lvalue. Wymaganie kopiowalności odrzuciłoby taki poprawny przypadek bez potrzeby wynikającej z implementacji.

</details>

**Ćwiczenie 2.** Czy pozytywny test `first_ref(std::span{data})` uzasadnia zwrócenie tego wyniku z funkcji, w której `data` jest lokalną tablicą?

<details>
<summary>Rozwiązanie</summary>

Nie. Widok i referencja nie przedłużają życia tablicy. Warunek chroni przed zależnością od krótkotrwałego obiektu zakresu, lecz nie analizuje całego łańcucha własności. W takim przypadku funkcja powinna zwrócić wartość albo właścicielski kontener.

</details>

Źródło uzupełniające: [N4950: requires-expression](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.req).

## Powiązane tematy

- [Concepts i requires](04_concepts_i_requires.md)
- [Perfect forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md)
