[← Spis treści](../README.md)

# Value semantics i type erasure

Typ ma value semantics, gdy jego kopia zachowuje się jak niezależna wartość, porównanie opisuje znaczenie logiczne, a zasoby są szczegółem implementacji. `std::string` i `std::vector` są typowymi przykładami. Value semantics upraszcza lokalne rozumowanie, testy i współbieżność, bo ownership jest jasny.

~~~cpp
#include <cassert>
#include <functional>
#include <string>
#include <utility>

class Formatter {
public:
    template<class F>
    Formatter(F function) : function_{std::move(function)} {}

    std::string operator()(int value) const {
        return function_(value);
    }

private:
    std::function<std::string(int)> function_;
};

int main() {
    Formatter formatter{[](int value) { return std::to_string(value); }};
    assert(formatter(42) == "42");
}
~~~

`std::function` wykonuje type erasure: klient widzi jednolitą sygnaturę, a konkretny typ lambdy jest ukryty. Może używać small-buffer optimization, ale standard nie gwarantuje dokładnego progu ani braku alokacji. Type erasure daje runtime polymorphism bez wymagania wspólnej klasy bazowej.

Alternatywy mają inne koszty. Template parametr zachowuje typ statyczny i pozwala inline, ale rozprzestrzenia implementację do nagłówków. Wirtualna hierarchia współdzieli kontrakt przez dziedziczenie. `variant` ma zamknięty zbiór typów i wyczerpujący visitor. Ręczny erasure może obsługiwać move-only wartości, niestandardową alokację i konkretny ABI, lecz łatwo popełnić błąd lifetime.

Nie myl value semantics z kopiowalnością za wszelką cenę. Typ reprezentujący pojedynczy uchwyt może być move-only. Ważne, by operacje odpowiadały znaczeniu domenowemu i nie ujawniały przypadkowego współdzielenia.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Value semantics i type erasure”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz ustanowienie kontraktu typu, rozdzielenie interfejsu od implementacji, wykonanie operacji i zmierzenie kosztu na granicy abstrakcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie domenowe od mechanizmu implementacyjnego, publiczne ABI od prywatnego layoutu i hipotezę wydajności od pomiaru. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź przykładowe użycie API, rozmiar i layout typu, symbole biblioteki, profil CPU oraz liczbę alokacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projektowanie C++ łączy semantykę wartości, własność, stabilność ABI i koszt abstrakcji. Dobra abstrakcja utrudnia niewłaściwe użycie, ale pozostawia kompilatorowi wystarczającą informację do optymalizacji. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Value semantics oznacza, że kopia reprezentuje niezależną wartość z przewidywalną równością. Type erasure ukrywa konkretny typ za wspólnym kontraktem przez wskaźnik funkcji, vtable lub mały bufor.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Value semantics i type erasure” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Value semantics i type erasure
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Value semantics i type erasure”, oceniaj łatwość poprawnego użycia, value semantics, stabilność kontraktu, koszt kompilacji i zmierzona wydajność krytycznej ścieżki. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Smart pointery](../03_pamiec_i_czas_zycia/05_smart_pointery.md)
- [Dziedziczenie i polimorfizm](../04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)
- [Type erasure, vtables i ABI](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)
