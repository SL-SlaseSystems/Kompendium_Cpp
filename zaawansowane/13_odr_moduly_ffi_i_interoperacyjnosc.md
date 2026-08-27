[← Spis treści](../README.md)

# ODR, moduły, FFI i interoperacyjność

FFI wymaga kontraktu na poziomie języka, ABI i ownership. `extern "C"` nadaje funkcji C language linkage, zwykle upraszczając name mangling, ale nie czyni dowolnego typu C++ zgodnym z C. Przez granicę przekazuj typy o uzgodnionej reprezentacji, jawne długości i opaque handles.

~~~cpp
#include <cassert>

extern "C" int c_add(int left, int right) noexcept {
    return left + right;
}

class Calculator {
public:
    int add(int left, int right) const noexcept {
        return c_add(left, right);
    }
};

int main() {
    const Calculator calculator;
    assert(calculator.add(20, 22) == 42);
}
~~~

Wyjątek nie może bezpiecznie przekroczyć C ABI; wrapper łapie wszystko i zamienia na kod lub tagged result. Pamięć powinna być zwalniana przez tę samą bibliotekę/runtime, która ją przydzieliła. Nie przekazuj `std::string`, `std::vector`, referencji, klas z virtual ani layoutu zależnego od kompilatora jako stabilnego C ABI.

Opaque handle może być niekompletną strukturą C oraz parami `create/destroy`. Każda funkcja waliduje null, rozmiary i wersję. Callback wymaga userdata pointer, jasnej synchronizacji i zakazu wywołania po zniszczeniu kontekstu.

Moduły zmieniają model widoczności deklaracji, lecz ODR nadal obowiązuje. Module linkage i attachment decydują, czy encje należą do nazwanego modułu. Nie łącz losowo tej samej deklaracji przez header i moduł bez planu migracji. BMI nie jest przenośnym formatem dystrybucji między dowolnymi kompilatorami.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „ODR, moduły, FFI i interoperacyjność”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- ODR wymaga pojedynczej definicji odr-used bytu w programie, z wyjątkami dla zgodnych definicji inline i template. `inline` pozwala na definicje w wielu jednostkach; nie jest poleceniem wykonania inline przez optimizer.
- Granica FFI powinna używać stabilnych typów i jawnej konwencji wywołania; wyjątki, klasy STL i ownership nie powinny przechodzić przez niezgodne ABI. Moduły nie usuwają ODR ani problemu wersjonowania binarnego.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „ODR, moduły, FFI i interoperacyjność” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: ODR, moduły, FFI i interoperacyjność
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „ODR, moduły, FFI i interoperacyjność”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Moduły C++](../08_budowanie_i_organizacja/04_moduly_cpp.md)
- [Linkowanie i ODR](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
- [API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)

