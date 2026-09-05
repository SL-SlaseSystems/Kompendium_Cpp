[← Spis treści](../README.md)

# Operatory i konwersje

Operatory C++ obejmują arytmetykę, porównania, logikę, operacje bitowe, przypisanie, dostęp do elementu i wywołanie. Priorytet operatorów określa grupowanie składni, lecz nie zawsze kolejność ewaluacji operandów. Jeśli poprawność zależy od kolejności efektów ubocznych, rozdziel wyrażenie na instrukcje.

~~~cpp
#include <cassert>
#include <compare>

struct Version {
    int major;
    int minor;
    auto operator<=>(const Version&) const = default;
};

int main() {
    const double value = 7.8;
    const int truncated = static_cast<int>(value);
    const unsigned flags = 0b0101u | 0b1000u;

    assert(truncated == 7);
    assert(flags == 0b1101u);
    assert((Version{1, 4} < Version{2, 0}));
}
~~~

Konwersje niejawne umożliwiają wygodny kod, ale mogą zawężać zakres, zmieniać znak lub wybierać niespodziewane przeciążenie. Inicjalizacja klamrowa odrzuca wiele konwersji zawężających. Jawny `static_cast` dokumentuje standardową konwersję, `dynamic_cast` wykonuje kontrolowaną konwersję w hierarchii polimorficznej, `const_cast` zmienia kwalifikację, a `reinterpret_cast` wykonuje konwersje niskopoziomowe o ograniczonej przenośności.

Usunięcie `const` i modyfikacja obiektu, który faktycznie utworzono jako const, jest undefined behavior. `reinterpret_cast` nie tworzy obiektu nowego typu ani nie znosi reguł aliasowania, alignment i lifetime. C-style cast może próbować kilka kategorii konwersji naraz, dlatego w nowym kodzie używaj nazwanych rzutowań.

Wbudowane operatory `&&` i `||` działają short-circuit. Operator przecinka sekwencjonuje lewy operand przed prawym, lecz przecinek oddzielający argumenty nie jest tym operatorem. Od C++17 istnieje więcej gwarancji sekwencjonowania, ale argumenty funkcji nadal nie mają powszechnie gwarantowanej kolejności między sobą.

## Jak to działa krok po kroku

Analizując `a + b * c`, najpierw odczytaj grupowanie jako `a + (b * c)`. Następnie ustal typy operandów i konwersje. Dopiero potem rozważ kolejność wykonania oraz efekty uboczne. Priorytet mnożenia nie gwarantuje, że odczyt `a` nastąpi po obliczeniu prawej strony. Dla zwykłych odczytów nie ma to znaczenia, lecz przy wywołaniach zmieniających wspólny stan staje się częścią poprawności.

W arytmetyce wbudowanej następują promocje całkowite i zwykłe konwersje arytmetyczne. Przy porównaniu `-1 < 1u` wartość ujemna zostaje skonwertowana do `unsigned int`, ponieważ operandy mają odpowiednie równe rangi. Wynik porównania jest fałszywy. Jawne rzutowanie na większy typ po całym wyrażeniu nie naprawia decyzji podjętej wcześniej. Dla porównań liczb o różnych znakach C++20 udostępnia `std::cmp_less` i pokrewne funkcje.

Konwersja `double` do `int` odrzuca część ułamkową w kierunku zera. Nie jest to zaokrąglenie do najbliższej liczby. Jeżeli obcięta wartość nie mieści się w typie docelowym, zachowanie jest niezdefiniowane. Dlatego `static_cast<int>` nie jest walidatorem danych: przed rzutowaniem trzeba sprawdzić zakres, a przy danych zmiennoprzecinkowych także odpowiednio potraktować nieskończoności i NaN.

## Pogłębienie mechanizmu

Wbudowane `&&` i `||` najpierw obliczają lewą stronę. Prawa jest pomijana, jeśli wynik jest już znany. Dzięki temu `p != nullptr && *p > 0` nie dereferencjonuje pustego wskaźnika. Przeciążone operatory logiczne wymagają obliczenia obu argumentów przed wejściem do funkcji, więc nie zachowują tej własności. To jeden z powodów, dla których rzadko warto je przeciążać.

Od C++17 inicjalizacje parametrów wywołania są względem siebie nieokreślenie sekwencjonowane: jedna kończy się przed drugą, ale standard nie wybiera kolejności. Wywołanie `f(i++, i++)` samo z tego powodu nie ma już dawnego problemu niezsekwencjonowanych modyfikacji; nadal nie należy zakładać, który parametr dostanie wcześniejszą wartość. Inne wyrażenia, na przykład `i++ + i++`, wciąż zawierają niezsekwencjonowane modyfikacje tego samego obiektu i powodują UB.

`explicit` przy konstruktorze lub operatorze konwersji pozwala ograniczyć konwersje niejawne. Szczególny przypadek to kontekstowa konwersja do `bool`, używana w `if`: bierze pod uwagę `explicit operator bool()`. Dlatego smart pointer nadaje się bezpośrednio do warunku, ale nie powinien przypadkiem zachowywać się jak dowolna liczba.

Operatory bitowe wymagają ostrożności z promocjami i szerokością typu. Dla przesunięcia liczba pozycji musi być nieujemna i mniejsza niż szerokość promowanego lewego operandu. W maskach wygodnie używać typów unsigned oraz sufiksów takich jak `1u`, a nie zakładać, że `1 << bit` zawsze tworzy poprawną maskę.

## Drugi przykład

Poniższy program łączy bezpieczne sprawdzenie opcjonalnego wskaźnika z porównaniem liczb o różnych znakach. Testy dokumentują wynik operatorów zamiast polegać na ostrzeżeniach konkretnego kompilatora.

~~~cpp
#include <cassert>
#include <utility>

bool positive(const int* value) {
    return value != nullptr && *value > 0;
}

struct Handle {
    int id;
    explicit operator bool() const noexcept { return id >= 0; }
};

int main() {
    const int number = 4;
    assert(positive(&number));
    assert(!positive(nullptr));
    assert(std::cmp_less(-1, 1u));

    const Handle handle{7};
    if (handle) {
        assert(handle.id == 7);
    }
    const unsigned mask = 1u << 3;
    assert((mask | 1u) == 9u);
    assert((mask & 1u) == 0u);
}
~~~

## Porównanie i decyzje

Wybieraj nawiasy dla czytelności, lecz nie traktuj ich jako sposobu sekwencjonowania. `f((first()), (second()))` nadal nie gwarantuje kolejności argumentów. Jeśli kolejność jest częścią wymagania, oblicz wartości w osobnych instrukcjach i potem wywołaj funkcję. Rzutowanie powinno oznaczać świadomą zmianę reprezentacji lub interfejsu; nie powinno jedynie uciszać diagnostyki.

Przy danych liczbowych rozróżnij trzy operacje: sprawdzenie, czy wartość się mieści, wybór sposobu zaokrąglenia i samą konwersję. Dla konwersji całkowitych C++20 oferuje `std::in_range`. Inicjalizacja klamrowa daje dodatkową ochronę przed zawężaniem, ale przy dynamicznych danych czasem potrzebny jest jawny warunek błędu.

**Ćwiczenie.** Czy `a != 0 & 10 / a > 1` bezpiecznie chroni przed dzieleniem przez zero?

**Odpowiedź.** Nie. Bitowe `&` nie pomija prawego operandu, więc obie strony zostaną obliczone. Należy użyć logicznego `&&`, którego prawa strona wykona się tylko po prawdziwym sprawdzeniu lewej.

Źródła: [konwersje arytmetyczne](https://timsong-cpp.github.io/cppwp/n4950/expr.arith.conv), [kolejność wyrażeń](https://timsong-cpp.github.io/cppwp/n4950/intro.execution), [konwersje zmiennoprzecinkowe do całkowitych](https://timsong-cpp.github.io/cppwp/n4950/conv.fpint).

## Powiązane tematy

- [Funkcje i przeciążanie](05_funkcje_i_przeciazanie.md)
- [Funkcje specjalne i operatory](../04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
