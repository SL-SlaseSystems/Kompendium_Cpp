[← Spis treści](../README.md)

# Overload resolution, ADL i hidden friends

Overload resolution buduje zbiór kandydatów przez lookup, dodaje kandydatów znalezionych przez ADL, sprawdza viability, szereguje implicit conversion sequences i wybiera najlepszą funkcję. Templates przechodzą dedukcję i constraints. Jeśli nie ma jednego najlepszego kandydata, wywołanie jest niejednoznaczne.

~~~cpp
#include <cassert>

namespace units {
class Meter {
public:
    explicit constexpr Meter(int value) : value_{value} {}
    friend constexpr Meter operator+(Meter left, Meter right) {
        return Meter{left.value_ + right.value_};
    }
    friend constexpr bool operator==(Meter, Meter) = default;

private:
    int value_;
};
} // namespace units

int main() {
    using units::Meter;
    constexpr Meter total = Meter{20} + Meter{22};
    static_assert(total == Meter{42});
}
~~~

Operatory są hidden friends: nie są zwykle odnajdywane przez zwykły lookup bez argumentu powiązanego z `Meter`, lecz ADL je znajduje. Zmniejsza to liczbę kandydatów i wiąże customization z typem.

Konwersja exact match wygrywa z promotion, promotion z conversion, ale istnieją dodatkowe reguły dla referencji, initializer lists, templates i rewritten candidates operatorów porównania. `explicit` usuwa konstruktor lub conversion function z kontekstów wymagających niejawnej konwersji.

Customization point pattern często wykonuje niekwalifikowane wywołanie po wprowadzeniu standardowego fallbacku. Należy unikać niekontrolowanej rekurencji i przypadkowego ADL dla typów zależnych. C++20 customization point objects w ranges używają bardziej złożonych reguł niż zwykła funkcja.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Overload resolution, ADL i hidden friends”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- ADL dodaje do wyszukiwania funkcje z przestrzeni skojarzonych z typami argumentów. Hidden friend wykorzystuje tę regułę, udostępniając operację tylko wtedy, gdy uczestniczy odpowiedni typ.
- Hidden friend jest zdefiniowany w klasie, lecz odnajdywany głównie przez ADL, co ogranicza zanieczyszczenie zwykłego lookup. Ranking kandydatów nadal zależy od konwersji i partial ordering.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Overload resolution, ADL i hidden friends” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Overload resolution, ADL i hidden friends
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Overload resolution, ADL i hidden friends”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Funkcje i przeciążanie](../02_podstawy_jezyka/05_funkcje_i_przeciazanie.md)
- [Namespaces i ADL](../08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)
- [Concept subsumption](08_concepts_normalization_i_subsumption.md)

