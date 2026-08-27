[← Spis treści](../README.md)

# virtual, override i RTTI

Wirtualna funkcja składowa umożliwia dynamic dispatch. Standard opisuje zachowanie semantycznie; typowy vtable i ukryty vptr są detalem ABI, nie obowiązkową reprezentacją języka. Koszt obejmuje zwykle pośrednie wywołanie i możliwość utrudnienia inline, ale decyzję wydajnościową należy oprzeć na profilu.

~~~cpp
#include <cassert>
#include <string_view>

struct Event {
    virtual ~Event() = default;
    [[nodiscard]] virtual std::string_view kind() const noexcept = 0;
};

struct Click final : Event {
    [[nodiscard]] std::string_view kind() const noexcept override {
        return "click";
    }
};

int main() {
    Click click;
    Event& event = click;
    assert(event.kind() == "click");
    assert(dynamic_cast<Click*>(&event) != nullptr);
}
~~~

`dynamic_cast` może bezpiecznie wykonać downcast w polimorficznej hierarchii. Dla wskaźnika niepowodzenie daje `nullptr`, dla referencji rzuca `std::bad_cast`. Częste downcasty mogą sugerować, że brakuje operacji w interfejsie albo lepszy byłby `variant`.

`typeid` i `dynamic_cast` tworzą RTTI. Niektóre projekty wyłączają RTTI flagą implementacji, ale wtedy nie jest to już standardowy, niezmieniony model C++. Nie zastępuj systemu typów ręcznymi liczbowymi identyfikatorami bez konkretnej potrzeby ABI lub serializacji.

Domyślny argument funkcji wirtualnej jest wybierany statycznie na podstawie typu wyrażenia, podczas gdy ciało funkcji — dynamicznie. To zaskakujące połączenie, dlatego unikaj domyślnych argumentów w wirtualnym API. Private virtual jest dozwolone i wspiera idiom NVI, w którym publiczna niewirtualna metoda pilnuje kontraktu.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „virtual, override i RTTI”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Wirtualne wywołanie działa przez dynamiczny typ obiektu, ale podczas konstruktora i destruktora dispatch nie przechodzi do bardziej pochodnej części. Polimorficzna baza przeznaczona do usuwania przez wskaźnik bazowy potrzebuje wirtualnego destruktora.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „virtual, override i RTTI” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: virtual, override i RTTI
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „virtual, override i RTTI”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Dziedziczenie i polimorfizm](04_dziedziczenie_i_polimorfizm.md)
- [NVI](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)
- [ABI i visibility](../zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)

