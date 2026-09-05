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

W `maximum(3, 7)` kompilator porównuje oba argumenty z parametrami typu `T` i dedukuje `T = int`. Następnie sprawdza, czy powstała funkcja może uczestniczyć w wywołaniu. Gdy potrzebna jest jej definicja, instancjonuje ciało dla tego typu. Porównanie i konstrukcja wyniku muszą być wtedy poprawne. Szablon nie gwarantuje, że każde podstawienie z dowolnym typem ma sens.

Wywołanie `maximum(3, 7.0)` nie wybiera automatycznie jednego szerszego typu. Pierwszy argument sugeruje `int`, a drugi `double`, więc dedukcja wspólnego `T` nie jest spójna. Jawne `maximum<double>(3, 7.0)` najpierw ustala typ i dopiero pozwala konwertować argumenty. Alternatywny szablon z niezależnymi `T` i `U` wymaga świadomego zaprojektowania wspólnego typu wyniku.

`FixedBuffer<int, 4>` tworzy specjalizację klasy z typem elementu i stałą długością. `FixedBuffer<int, 8>` jest innym typem, nawet jeśli ma takie same nazwy metod. Wartość `N` staje się częścią tożsamości typu. Pętla działająca na takiej klasie może znać długość podczas kompilacji, lecz sam parametr szablonu nie wymusza konkretnej optymalizacji.

## Pogłębienie mechanizmu

Nazwy niezależne od parametrów są zwykle wyszukiwane przy definicji szablonu. Nazwy zależne wymagają uwzględnienia argumentów podczas instancjacji. Brak deklaracji zwykłej pomocniczej funkcji przy definicji nie jest zawsze naprawiany przez dopisanie jej później. Ten podział, często omawiany jako two-phase lookup, pozwala ograniczyć zależność znaczenia szablonu od przypadkowej kolejności dołączania nagłówków.

Zależną nazwę typu może być trzeba poprzedzić `typename`, na przykład `typename T::value_type`. Przy zależnym wywołaniu szablonu składowego może być potrzebne słowo `template`. Te słowa pomagają parserowi rozpoznać składnię, zanim pozna konkretny `T`; nie tworzą nowego typu ani nowego szablonu. W klasie dziedziczącej z bazy zależnej często potrzebne jest `this->member`, aby wyszukiwanie właściwie uwzględniało tę bazę.

Instancjacja specjalizacji klasy nie musi instancjonować definicji wszystkich jej metod. Zwykle ciało metody jest potrzebne dopiero, gdy użycie go wymaga. Dlatego szablon klasy może mieć operację sensowną tylko dla części typów, choć jawne constraints dają czytelniejszy interfejs niż późny błąd z wnętrza metody. Wirtualne funkcje i wybrane szczególne sytuacje mają dodatkowe reguły instancjacji.

Parametry wartościowe mogą obejmować liczby, wskaźniki i określone typy strukturalne. Nie oznacza to, że dowolny obiekt `std::string` nadaje się jako argument szablonu. Argument musi spełniać reguły typu parametru i stałego wyrażenia. `template<auto Value>` dedukuje typ argumentu, dzięki czemu wartości takie jak `3` i `3u` mogą tworzyć różne specjalizacje.

Zwykle definicja szablonu jest udostępniona wraz z deklaracją w nagłówku. Przy zamkniętym zbiorze obsługiwanych typów można użyć jawnych instancjacji w pliku implementacji oraz deklaracji `extern template` ograniczających powtarzaną pracę. To decyzja o architekturze biblioteki: nowy nieprzewidziany typ może wtedy wymagać nowej dostarczonej instancjacji.

## Drugi przykład

Dwa bufory o różnej długości są różnymi typami. `std::array` obsługuje także rozmiar zero, czego wbudowana tablica `T[N]` z pierwszego przykładu nie zapewnia w standardowym C++.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <type_traits>

template<class T, std::size_t N>
struct Buffer {
    std::array<T, N> values{};
    constexpr std::size_t size() const noexcept { return N; }
};

template<class T, std::size_t N>
T total(const Buffer<T, N>& buffer) {
    T result{};
    for (const auto& value : buffer.values) result += value;
    return result;
}

int main() {
    Buffer<int, 3> numbers{{2, 3, 4}};
    Buffer<int, 0> empty;
    static_assert(!std::is_same_v<decltype(numbers), decltype(empty)>);
    assert(total(numbers) == 9);
    assert(total(empty) == 0);
}
~~~

`total` dedukuje jednocześnie typ elementu i długość. Wymaga wartości początkowej `T{}` oraz odpowiedniego `+=`. Dla liczb oznacza to sumowanie, lecz dla własnego typu neutralność wartości domyślnej jest już wymaganiem semantycznym, którego sama poprawna składnia nie dowodzi.

## Porównanie i decyzje

Szablon pasuje do algorytmu o wspólnej strukturze i zachowaniu zależnym od typu. Zwykła przeciążona funkcja jest prostsza, gdy obsługujesz kilka z góry znanych przypadków o odmiennych kontraktach. Wartość runtime pasuje do liczby zmieniającej się podczas pracy; parametr szablonu do informacji, która naprawdę ma definiować typ lub dostępność operacji.

**Ćwiczenie.** Czy wywołanie `maximum<int>(2.9, 3.1)` porównuje pierwotne wartości zmiennoprzecinkowe?

**Odpowiedź.** Nie. Jawny argument ustala parametry funkcji jako `int`, więc argumenty są konwertowane przed wejściem do ciała. Porównywane są dwa i trzy. To pokazuje różnicę między dedukowaniem typu a świadomym wymuszeniem konwersji.

Źródła: [parametry szablonów](https://timsong-cpp.github.io/cppwp/n4950/temp.param), [instancjacja](https://timsong-cpp.github.io/cppwp/n4950/temp.inst), [dedukcja argumentów wywołania](https://timsong-cpp.github.io/cppwp/n4950/temp.deduct.call).

## Powiązane tematy

- [Dedukcja i CTAD](02_dedukcja_auto_decltype_i_ctad.md)
- [Concepts i requires](04_concepts_i_requires.md)
- [Monomorfizacja i wydajność](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

