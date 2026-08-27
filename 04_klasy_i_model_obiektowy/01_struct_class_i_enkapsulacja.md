[← Spis treści](../README.md)

# struct, class i enkapsulacja

`struct` i `class` definiują ten sam rodzaj typu klasowego. Różnią się domyślnym dostępem: w `struct` elementy i dziedziczenie są publiczne, w `class` prywatne. Konwencja często używa `struct` dla prostych agregatów i `class` dla typu chroniącego inwariant, ale język nie narzuca takiego podziału.

~~~cpp
#include <cassert>
#include <stdexcept>

class Percentage {
public:
    explicit Percentage(int value) : value_{value} {
        if (value < 0 || value > 100) {
            throw std::out_of_range{"percentage"};
        }
    }

    [[nodiscard]] int value() const noexcept {
        return value_;
    }

private:
    int value_;
};

int main() {
    const Percentage progress{75};
    assert(progress.value() == 75);
}
~~~

Prywatne pole nie jest celem samym w sobie. Enkapsulacja pozwala utrzymać inwariant i zmieniać reprezentację bez zmiany publicznego kontraktu. Konstruktor weryfikuje zakres, a metoda `value()` gwarantuje odczyt poprawnej wartości. `explicit` blokuje przypadkową konwersję z `int`.

Metoda z końcowym `const` obiecuje, że nie zmieni obserwowalnego stanu przez `this`. Nie oznacza automatycznej thread safety. Element `mutable` może być modyfikowany w metodzie const, co jest użyteczne dla cache lub mutexa, ale nie powinno służyć omijaniu projektu typu.

Publiczne pola są rozsądne w pasywnym agregacie, który nie ma ukrytego inwariantu. Mechaniczne gettery i settery dla każdego pola nie zapewniają znaczącej enkapsulacji. Projektuj operacje domenowe, które utrzymują poprawny stan.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „struct, class i enkapsulacja”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- `struct` i `class` różnią się domyślnym dostępem oraz trybem dziedziczenia, nie możliwościami języka. Enkapsulacja ma chronić inwariant; gettery i settery kopiujące wszystkie pola nie tworzą użytecznej abstrakcji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „struct, class i enkapsulacja” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: struct, class i enkapsulacja
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „struct, class i enkapsulacja”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Konstruktory i destruktory](02_konstruktory_i_destruktory.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
- [Assertions i preconditions](../07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)

