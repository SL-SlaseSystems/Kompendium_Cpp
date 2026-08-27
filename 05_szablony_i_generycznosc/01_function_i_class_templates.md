[← Spis treści](../README.md)

# Szablony funkcji i klas

Szablon opisuje rodzinę deklaracji parametryzowanych typami, wartościami lub innymi szablonami. Kompilator tworzy specjalizację podczas instancjacji. To podstawowy mechanizm statycznego polimorfizmu i implementacji biblioteki standardowej.

~~~cpp
#include <cassert>
#include <cstddef>
#include <utility>

template<class T>
T maximum(T left, T right) {
    return left < right ? std::move(right) : std::move(left);
}

template<class T, std::size_t N>
struct FixedBuffer {
    T data[N]{};

    constexpr std::size_t size() const noexcept { return N; }
};

int main() {
    assert(maximum(3, 7) == 7);
    FixedBuffer<int, 4> buffer;
    static_assert(buffer.size() == 4);
}
~~~

Parametr `class T` i `typename T` są w tym miejscu równoważne. Non-type template parameter może przenosić wartość znaną w compile time; C++20 rozszerzył zakres dopuszczalnych typów takich parametrów. Template template parameter przyjmuje szablon o pasującym kształcie.

Definicja szablonu musi być zwykle widoczna w miejscu instancjacji, dlatego znajduje się w nagłówku lub module. Alternatywą jest explicit instantiation dla zamkniętego zestawu typów, co może skrócić kompilację i ograniczyć rozrost kodu.

Szablon nie jest zwykłą funkcją ani klasą, dopóki nie powstanie specjalizacja. Błędy zależne od parametrów mogą ujawnić się dopiero przy konkretnym użyciu. Concepts poprawiają kontrakty i diagnostykę, ale nie eliminują potrzeby testowania różnych kategorii typów.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Szablony funkcji i klas”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zebranie argumentów, dedukcję parametrów, sprawdzenie ograniczeń, wybór specjalizacji i instancjację użytej postaci. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel błąd substytucji, niespełnione constraint i błąd wewnątrz już wybranej instancji. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wydedukowane typy, zbiór kandydatów, spełnione constraints oraz minimalną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Szablon jest przepisem na deklaracje zależne od argumentów, a nie kodem wykonywanym w runtime. Dedukcja, lookup, ograniczenia i instancjacja zachodzą w różnych momentach; pomieszanie tych faz prowadzi do trudnych diagnostyk. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Szablon funkcji zwykle dedukuje argumenty z wywołania, a szablon klasy przed C++17 wymagał jawnych argumentów lub fabryki. Każda użyta instancja jest odrębnym bytem, co wpływa na czas kompilacji i rozmiar kodu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Szablony funkcji i klas” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Szablony funkcji i klas
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Szablony funkcji i klas”, oceniaj czytelny kontrakt, krótka diagnostyka, ograniczona liczba instancji i brak metaprogramowania bez wartości dla użytkownika API. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Parametryzuj tylko wymaganą zmienność. Projektuj operacje na podstawie potrzebnego zachowania, nie przypadkowego dziedziczenia. Nie używaj `std::move` na argumentach referencyjnych bez jasnego kontraktu własności; prosty `maximum` powyżej przyjmuje wartości właśnie po to, by móc je przenieść do wyniku.

## Powiązane tematy

- [Dedukcja i CTAD](02_dedukcja_auto_decltype_i_ctad.md)
- [Concepts i requires](04_concepts_i_requires.md)
- [Monomorfizacja i wydajność](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

