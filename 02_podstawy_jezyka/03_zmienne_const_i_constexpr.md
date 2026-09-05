[← Spis treści](../README.md)

# Zmienne, const i constexpr

Zmienna wiąże nazwę z obiektem. `const` zabrania modyfikacji przez daną ścieżkę dostępu, lecz nie zawsze oznacza, że wartość powstała podczas kompilacji. `constexpr` deklaruje obiekt albo funkcję możliwą do użycia w constant expression, jeśli argumenty i wykonana ścieżka spełniają wymagania. `consteval` wymaga ewaluacji wywołania w czasie kompilacji.

~~~cpp
#include <array>
#include <cassert>

constexpr int square(int value) {
    return value * value;
}

consteval int checked_size(int value) {
    return value > 0 ? value : 1;
}

int main() {
    constexpr int count = checked_size(4);
    std::array<int, count> values{1, 2, 3, 4};
    const int runtime_sum = values[0] + values[1];

    static_assert(square(count) == 16);
    assert(runtime_sum == 3);
}
~~~

`constinit` nie czyni obiektu niezmiennym. Wymusza statyczną inicjalizację zmiennej o static lub thread storage duration i pomaga uniknąć części problemów kolejności inicjalizacji. `volatile` również nie służy do synchronizacji wątków; opisuje szczególne dostępy istotne dla implementacji, np. niektóre rejestry sprzętowe. Do komunikacji między wątkami używa się atomików i synchronizacji.

`auto` dedukuje typ z inicjalizatora i usuwa najwyższy poziom `const` oraz referencję według reguł podobnych do dedukcji szablonów. `const auto&` zachowuje dostęp referencyjny i często jest dobrym wyborem dla odczytu dużej wartości. Nie używaj `auto` do ukrywania istotnej konwersji lub niejasnej własności.

## Jak to działa krok po kroku

Najpierw oddziel kwalifikację obiektu od kontekstu obliczenia. `const int n = read();` zabrania późniejszego przypisania do `n`, lecz może wymagać odczytu danych podczas działania programu. `constexpr int n = expression;` wymaga odpowiedniego stałego inicjalizatora i również czyni obiekt stałym. Gdy inicjalizator nie spełnia wymagań, program jest niepoprawny i kompilator powinien zgłosić błąd; nie przechodzi po cichu do obliczenia runtime.

W początkowym programie `checked_size(4)` jest obliczane w wymaganym kontekście stałym. Wynik staje się argumentem szablonu `std::array`, czyli częścią typu. `square(count)` w `static_assert` również musi zostać wyliczone jako stała. Ta sama funkcja może przyjąć wartość odczytaną podczas wykonania, jeśli jej wynik nie służy jako wymagane stałe wyrażenie. Specyfikator funkcji daje możliwość, a miejsce wywołania określa obowiązek.

Stałość jest płytka. `const int* p` pozwala zmieniać adres w `p`, ale nie wartość przez `*p`. `int* const p` blokuje zmianę adresu, lecz pozwala modyfikować wskazany `int`. W szczególności `constexpr int*` jest stałym wskaźnikiem, nie automatycznie wskaźnikiem do stałego `int`. Analogicznie stały obiekt przechowujący wskaźnik nie zamraża wskazywanego zasobu.

## Pogłębienie mechanizmu

`const` na referencji do obiektu modyfikowalnego ogranicza tylko tę drogę dostępu. Inny alias może legalnie zmienić obiekt i kolejny odczyt przez stałą referencję zobaczy zmianę. Inna sytuacja zachodzi, gdy sam obiekt utworzono jako stały: próba jego modyfikacji po usunięciu kwalifikacji przez `const_cast` prowadzi do UB. Rzutowanie nie zmienia historii utworzenia obiektu.

Stała całkowita z inicjalizatorem będącym odpowiednim stałym wyrażeniem, na przykład `const int n = 4`, może nadawać się do rozmiaru tablicy bez słowa `constexpr`. Nie należy z tego wyciągać ogólnego wniosku o wszystkich obiektach `const`. `constexpr` wyraża zamierzenie wyraźniej i kompilator sprawdza jego wymagania od razu przy deklaracji.

`constinit` stosuje się do zmiennych o statycznym lub wątkowym czasie przechowywania. Odrzuca konieczność dynamicznej inicjalizacji takiej zmiennej, lecz nie zabrania jej późniejszych modyfikacji. Nie można używać go jako zamiennika `const` dla lokalnego automatycznego obiektu. Nie rozwiązuje też wyścigów danych ani wszystkich zależności występujących podczas kończenia programu.

Warto rozróżniać regułę języka i optymalizację. Kompilator może zastąpić wynikiem obliczenie zwykłej funkcji, gdy zachowuje obserwowalne zachowanie programu. Taka optymalizacja nie sprawia, że wyrażenie wolno wpisać jako argument szablonu. Legalność stałego wyrażenia wynika ze standardu, a nie z tego, czy asembler zawiera jeszcze mnożenie.

## Drugi przykład

W tym programie odczyt przez stałą referencję obserwuje zmianę dokonaną przez właściciela. Stała tablica ma rozmiar znany podczas kompilacji, a licznik inicjalizowany statycznie nadal pozostaje modyfikowalny.

~~~cpp
#include <array>
#include <cassert>
#include <type_traits>

constinit int requests = 0;
constexpr int twice(int value) { return value * 2; }

int main() {
    int value = 3;
    const int& observed = value;
    auto snapshot = observed;
    value = 9;
    assert(observed == 9);
    assert(snapshot == 3);
    static_assert(std::is_same_v<decltype(snapshot), int>);

    constexpr int size = twice(3);
    std::array<int, size> buffer{};
    ++requests;
    assert(requests == 1);
    assert(buffer.size() == 6);
}
~~~

`auto snapshot` tworzy niezależny obiekt typu `int`. Brak najwyższego `const` w tym typie nie jest obejściem zakazu: kopiowanie wartości było dozwolone. Gdyby deklaracja brzmiała `const auto& snapshot`, wynik byłby aliasem i zmiana źródła stałaby się widoczna również przez tę nazwę.

## Porównanie i decyzje

Używaj `const`, kiedy obiekt nie powinien się zmieniać po inicjalizacji. Wybieraj `constexpr` dla stałych potrzebnych kompilatorowi i funkcji mających sens zarówno dla stałych, jak i danych runtime. `consteval` nadaje się do walidowanych konstruktorów danych konfiguracyjnych obliczanych wyłącznie podczas kompilacji. `constinit` jest narzędziem kontroli inicjalizacji stanu o długim czasie przechowywania, nie modelem jego niezmienności.

**Ćwiczenie.** Czy `const std::unique_ptr<int>` chroni wskazaną liczbę przed zmianą? Jaki typ przekazać, aby odbiorca miał wyłącznie dostęp do odczytu tej liczby?

**Odpowiedź.** Stały smart pointer blokuje zmianę własności przez tę instancję, ale jego dereferencja nadal może dać modyfikowalny `int&`. Do niewłaścicielskiego odczytu zwykle wystarczy `const int&` lub `const int*`. Jeśli sam model własności ma obejmować stały obiekt, odpowiednim typem jest `std::unique_ptr<const int>`.

Źródła: [kwalifikatory const i volatile](https://timsong-cpp.github.io/cppwp/n4950/dcl.type.cv), [constexpr](https://timsong-cpp.github.io/cppwp/n4950/dcl.constexpr), [constinit](https://timsong-cpp.github.io/cppwp/n4950/dcl.constinit).

## Powiązane tematy

- [Dedukcja, auto i decltype](../05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
- [Compile time](../zaawansowane/09_constexpr_consteval_i_compile_time.md)
- [Atomiki](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)

