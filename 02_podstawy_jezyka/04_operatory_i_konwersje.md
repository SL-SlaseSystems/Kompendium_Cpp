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

Operator `&&` i `||` działa short-circuit. Operator przecinka sekwencjonuje lewy operand przed prawym, lecz przecinek oddzielający argumenty nie jest tym operatorem. Od C++17 istnieje więcej gwarancji sekwencjonowania, ale argumenty funkcji nadal nie mają powszechnie gwarantowanej kolejności między sobą.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Operatory i konwersje”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Konwersje integralne mogą zmieniać znak i zakres, a zwykłe konwersje arytmetyczne ustalają wspólny typ operandów. `static_cast` dokumentuje konwersję dozwoloną przez język, lecz nie dowodzi braku utraty informacji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Operatory i konwersje” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Operatory i konwersje
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Operatory i konwersje”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Funkcje i przeciążanie](05_funkcje_i_przeciazanie.md)
- [Funkcje specjalne i operatory](../04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
