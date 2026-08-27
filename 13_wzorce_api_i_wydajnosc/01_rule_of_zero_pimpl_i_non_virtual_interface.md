[← Spis treści](../README.md)

# Rule of zero, PImpl i Non-Virtual Interface

Rule of zero mówi, że klasa aplikacyjna nie powinna ręcznie zarządzać zasobem, jeśli może przechować gotowy typ RAII. Automatycznie generowane copy/move/destrukcja zachowują wtedy semantykę pól. Kod jest krótszy, a exception safety wynika z kompozycji.

PImpl (*pointer to implementation*) przenosi prywatną reprezentację do niekompletnego typu za `unique_ptr`. Zmniejsza zależności nagłówka i może ograniczyć część zmian ABI, ale dodaje alokację, indirection, kod boilerplate oraz konieczność zdefiniowania destruktora tam, gdzie implementacja jest kompletna.

~~~cpp
#include <cassert>

class Processor {
public:
    int process(int value) {
        validate(value);
        return do_process(value);
    }

    virtual ~Processor() = default;

private:
    static void validate(int value) {
        if (value < 0) {
            throw "negative";
        }
    }
    virtual int do_process(int value) = 0;
};

class Doubler final : public Processor {
private:
    int do_process(int value) override { return value * 2; }
};

int main() {
    Doubler doubler;
    assert(doubler.process(21) == 42);
}
~~~

Non-Virtual Interface (NVI) udostępnia publiczną niewirtualną metodę pilnującą kontraktu i wywołuje private/protected virtual customization point. Dzięki temu walidacja, logowanie i inwariant nie są duplikowane przez klasy pochodne. NVI nie jest potrzebny w każdej hierarchii; proste interface-only base może mieć publiczne pure virtual metody.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Rule of zero, PImpl i Non-Virtual Interface”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz ustanowienie kontraktu typu, rozdzielenie interfejsu od implementacji, wykonanie operacji i zmierzenie kosztu na granicy abstrakcji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie domenowe od mechanizmu implementacyjnego, publiczne ABI od prywatnego layoutu i hipotezę wydajności od pomiaru. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź przykładowe użycie API, rozmiar i layout typu, symbole biblioteki, profil CPU oraz liczbę alokacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projektowanie C++ łączy semantykę wartości, własność, stabilność ABI i koszt abstrakcji. Dobra abstrakcja utrudnia niewłaściwe użycie, ale pozostawia kompilatorowi wystarczającą informację do optymalizacji. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Wirtualne wywołanie działa przez dynamiczny typ obiektu, ale podczas konstruktora i destruktora dispatch nie przechodzi do bardziej pochodnej części. Polimorficzna baza przeznaczona do usuwania przez wskaźnik bazowy potrzebuje wirtualnego destruktora.
- PImpl przenosi reprezentację za granicę typu niekompletnego, zmniejszając zależności i chroniąc ABI kosztem alokacji oraz indirection. NVI pozostawia wirtualny punkt rozszerzenia prywatny, a publiczna metoda pilnuje kontraktu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Rule of zero, PImpl i Non-Virtual Interface” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Rule of zero, PImpl i Non-Virtual Interface
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Rule of zero, PImpl i Non-Virtual Interface”, oceniaj łatwość poprawnego użycia, value semantics, stabilność kontraktu, koszt kompilacji i zmierzona wydajność krytycznej ścieżki. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Wybierz PImpl z powodu czasu budowania lub stabilności granicy, nie jako automatyczny wzorzec. Najpierw wybieraj kompozycję i typy wartościowe. Hierarchie powinny mieć jeden jasny wymiar zmienności, a klasa bazowa musi dokumentować ownership i destrukcję.

## Powiązane tematy

- [Copy, move i rule of zero](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [virtual i RTTI](../04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
- [Projektowanie API i ABI](03_projektowanie_api_i_abi.md)

