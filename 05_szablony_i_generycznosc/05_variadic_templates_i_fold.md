[← Spis treści](../README.md)

# Variadic templates i fold expressions

Parameter pack reprezentuje zero lub więcej argumentów typowych albo wartościowych. Rozwinięcie packa powtarza wzorzec dla każdego elementu. Mechanizm pozwala budować heterogeniczne struktury, forwardować argumenty i tworzyć interfejsy o zmiennej liczbie parametrów bez C-style variadic functions.

~~~cpp
#include <cassert>
#include <string>
#include <utility>

template<class... Numbers>
auto sum(Numbers... numbers) {
    return (numbers + ... + 0);
}

template<class... Parts>
std::string join(Parts&&... parts) {
    std::string result;
    (result.append(std::forward<Parts>(parts)), ...);
    return result;
}

int main() {
    assert(sum(1, 2, 3, 4) == 10);
    assert(join("C", "+", "+") == "C++");
}
~~~

Fold expression od C++17 może być lewo- lub prawostronne oraz unary lub binary. Wartość inicjalna `0` sprawia, że `sum()` działa również dla pustego packa, choć ograniczenia typu wyniku nadal wymagają przemyślenia. Operator przecinka w drugim foldzie sekwencjonuje wywołania `append` od lewej do prawej.

`sizeof...(Parts)` zwraca liczbę elementów packa. Pack może zostać rozwinięty w listach argumentów, inicjalizatorach, bazach klasy i wielu innych kontekstach. Rekurencyjne rozpakowywanie było popularne przed fold expressions, ale dziś bywa niepotrzebnie skomplikowane.

Przy forwardowaniu używa się `T&&` w kontekście dedukowanym oraz `std::forward<T>`. Samo nazwane `argument` jest lvalue niezależnie od typu deklaracji. Nie forwarduj tej samej wartości wielokrotnie, jeśli pierwsze użycie mogło ją przenieść.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Variadic templates i fold expressions”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Parameter pack reprezentuje zero lub więcej argumentów, a fold expression redukuje rozwinięcie przez operator z określoną łącznością. Przypadek pustego packa zależy od operatora i obecności wartości początkowej.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Variadic templates i fold expressions” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Variadic templates i fold expressions
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Variadic templates i fold expressions”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Szablony funkcji](01_function_i_class_templates.md)
- [Value categories i perfect forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [tuple i pair](../06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
