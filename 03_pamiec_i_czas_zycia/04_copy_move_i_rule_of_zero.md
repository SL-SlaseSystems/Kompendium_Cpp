[← Spis treści](../README.md)

# Copy, move i rule of zero

C++ ma semantykę wartości: obiekt można kopiować, przenosić, przypisywać i niszczyć zgodnie z jego funkcjami specjalnymi. Kopia tworzy niezależny stan logiczny. Przeniesienie może przejąć zasoby z obiektu źródłowego, który pozostaje ważny, ale zwykle ma nieokreślony stan opisany przez kontrakt typu.

~~~cpp
#include <cassert>
#include <string>
#include <utility>
#include <vector>

struct Document {
    std::string title;
    std::vector<int> pages;
};

int main() {
    Document original{"Guide", {1, 2, 3}};
    Document copy = original;
    Document moved = std::move(original);

    assert(copy.title == "Guide");
    assert(moved.pages.size() == 3);
    original = Document{}; // obiekt nadal można przypisać
}
~~~

`std::move` niczego sam nie przenosi; wykonuje rzutowanie do xvalue, umożliwiając wybór przeciążenia przyjmującego rvalue. Jeśli typ lub kontekst nie oferuje ruchu, może nadal nastąpić kopia. Nie czytaj stanu moved-from poza operacjami dozwolonymi przez kontrakt.

*Rule of zero* mówi, by zasoby reprezentować elementami, które same zarządzają swoim lifetime. Wtedy kompilator może wygenerować poprawne copy/move/destrukcję. Jeśli klasa bezpośrednio posiada surowy zasób i musi definiować destruktor, zwykle trzeba świadomie rozważyć pięć funkcji: copy constructor, copy assignment, move constructor, move assignment i destructor — to rule of five.

Zadeklarowanie niektórych funkcji specjalnych wpływa na automatyczne generowanie pozostałych. `= default` jawnie prosi o domyślne zachowanie, a `= delete` zakazuje operacji. Konstruktor przenoszący oznaczony `noexcept` pozwala kontenerom częściej przenosić elementy podczas realokacji z zachowaniem silnej gwarancji wyjątków.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Copy, move i rule of zero”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz rozpoczęcie lifetime, ustanowienie inwariantu, przekazywanie własności lub widoku oraz zakończenie lifetime w dokładnie określonym miejscu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel storage od obiektu, właściciela od obserwatora oraz semantykę przeniesienia od zwykłego kopiowania bitów. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź miejsce konstrukcji i destrukcji, graf właścicieli, ważność referencji oraz zachowanie sanitizerów. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Poprawność pamięci w C++ wynika z czasu życia obiektów i własności zasobów. Adres jest tylko reprezentacją położenia; nie dowodzi, że obiekt nadal istnieje ani że wolno uzyskać przez niego dostęp do przechowywanej wartości. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Operacja move może przejąć zasób, lecz źródło musi pozostać ważne i zniszczalne. Rule of zero preferuje człony zarządzające własnymi zasobami, dzięki czemu kompilator może poprawnie wygenerować funkcje specjalne klasy złożonej.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Copy, move i rule of zero” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Copy, move i rule of zero
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Copy, move i rule of zero”, oceniaj jednoznaczna własność, automatyczne sprzątanie, brak dangling i możliwie mała liczba ręcznych operacji na pamięci. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Funkcje specjalne](../04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
- [Value categories i forwarding](../zaawansowane/05_value_categories_i_perfect_forwarding.md)
- [Rule of zero i PImpl](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)

