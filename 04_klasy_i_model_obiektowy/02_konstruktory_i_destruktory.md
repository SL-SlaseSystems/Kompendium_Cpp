[← Spis treści](../README.md)

# Konstruktory i destruktory

Konstruktor rozpoczyna życie kompletnego obiektu po skonstruowaniu klas bazowych i pól. Elementy są inicjalizowane w kolejności deklaracji w klasie, nie w kolejności listy inicjalizacyjnej. Destrukcja zachodzi odwrotnie: najpierw ciało destruktora, potem pola i klasy bazowe.

~~~cpp
#include <cassert>
#include <string>
#include <utility>

class Account {
public:
    Account(std::string owner, int balance = 0)
        : owner_{std::move(owner)}, balance_{balance} {}

    Account() : Account{"anonymous", 0} {}

    [[nodiscard]] const std::string& owner() const noexcept { return owner_; }
    [[nodiscard]] int balance() const noexcept { return balance_; }

private:
    std::string owner_;
    int balance_{};
};

int main() {
    const Account named{"Ada", 100};
    const Account guest;
    assert(named.balance() == 100);
    assert(guest.owner() == "anonymous");
}
~~~

Delegating constructor pozwala jednej wersji wywołać inną, ograniczając powtarzanie inwariantów. In-class member initializers zapewniają wartości domyślne. Konstruktor jednoargumentowy powinien zwykle być `explicit`, chyba że konwersja jest naturalną i bezpieczną częścią semantyki typu.

Obiekt nie jest jeszcze kompletnym obiektem najbardziej pochodnej klasy podczas budowania bazy. Wywołania wirtualne w konstruktorze lub destruktorze nie dispatchują do nieistniejącej już części pochodnej. Nie publikuj `this` przed zakończeniem konstrukcji.

Destruktor jest generowany automatycznie, jeśli nie trzeba specjalnego zachowania. W hierarchii usuwanej polimorficznie destruktor klasy bazowej musi być public virtual albo należy uniemożliwić takie usuwanie, np. przez chroniony niewirtualny destruktor.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Konstruktory i destruktory”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz wybór konstruktora, inicjalizację podobiektów, wykonanie operacji publicznej i destrukcję w odwrotnej kolejności. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba odróżnij relację typu, współdzielenie implementacji i dynamiczny polimorfizm od zwykłej kompozycji obiektów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź inwariant przed i po metodzie, wygenerowane funkcje specjalne, wywołany override oraz koszt reprezentacji. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Klasa definiuje inwariant i zestaw operacji, które mogą go zachować. Ukrywanie pól jest środkiem, nie celem: interfejs powinien utrudniać utworzenie stanu nieważnego, a destrukcja i kopiowanie muszą odpowiadać semantyce reprezentowanego obiektu. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Podobiekty są inicjalizowane według kolejności deklaracji w klasie, niezależnie od kolejności na liście inicjalizacyjnej. Delegating constructor pozwala skupić ustanowienie inwariantu w jednym miejscu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Konstruktory i destruktory” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Konstruktory i destruktory
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Konstruktory i destruktory”, oceniaj siła inwariantu, value semantics, prostota własności, testowalność i stabilność publicznego kontraktu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [RAII i destruktory](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Funkcje specjalne](03_funkcje_specjalne_i_operatory.md)
- [Dziedziczenie i polimorfizm](04_dziedziczenie_i_polimorfizm.md)

