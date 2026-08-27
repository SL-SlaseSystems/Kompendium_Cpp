[← Spis treści](../README.md)

# Sterowanie przepływem

Instrukcje `if`, `switch`, `while`, `do`, `for` oraz range-based `for` sterują wykonaniem. Warunek jest kontekstowo konwertowany do `bool`. C++17 pozwala umieścić inicjalizator przed warunkiem `if` i `switch`, co ogranicza zakres pomocniczej zmiennej.

~~~cpp
#include <cassert>
#include <vector>

int sum_positive(const std::vector<int>& values) {
    int total = 0;
    for (const int value : values) {
        if (value < 0) {
            continue;
        }
        total += value;
    }
    return total;
}

int main() {
    const auto values = std::vector{3, -2, 5};
    if (const int result = sum_positive(values); result > 0) {
        assert(result == 8);
    } else {
        return 1;
    }
}
~~~

Range-based `for` pobiera element zgodnie z deklaracją zmiennej pętli. `auto element` kopiuje, `auto&` daje modyfikowalną referencję, a `const auto&` odczyt bez kopiowania. Przy proxy references, np. w `std::vector<bool>`, `auto&&` może lepiej zachować semantykę elementu.

`switch` działa na typach całkowitych i enumach. Brak `break` powoduje przejście do kolejnej etykiety; jeśli jest zamierzone, zaznacz je `[[fallthrough]]`. `break` kończy najbliższą pętlę lub switch, a `continue` rozpoczyna następną iterację. `goto` istnieje, lecz zwykle przegrywa z funkcją, RAII i czytelnym przepływem; nie można nim bezkarnie omijać inicjalizacji obiektów.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Sterowanie przepływem”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Inicjalizator w `if` lub `switch` ogranicza lifetime pomocniczej wartości do instrukcji sterującej. Wczesne wyjście upraszcza happy path, ale sprzątanie powinno pozostać odpowiedzialnością RAII zamiast ręcznych gałęzi.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Sterowanie przepływem” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Sterowanie przepływem
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Sterowanie przepływem”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Preferuj range-based `for` i algorytmy, gdy indeks nie jest potrzebny. Utrzymuj warunki bez efektów ubocznych. Wyczerpująco obsługuj `enum class` i pozwól ostrzeżeniom wykrywać brak nowych wariantów; pochopne `default` może takie ostrzeżenie ukryć.

## Powiązane tematy

- [Algorytmy i lambdy](../06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
- [enum i variant](../04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)
- [Ranges i views](../06_biblioteka_standardowa/06_ranges_i_views.md)

