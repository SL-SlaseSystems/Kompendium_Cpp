[← Spis treści](../README.md)

# Funkcje i przeciążanie

Funkcja ma typ zwracany, nazwę, listę parametrów i opcjonalne specyfikatory. Argument przekazywany przez wartość tworzy osobny obiekt parametru. `const T&` pozwala czytać bez kopiowania i może wiązać temporary, `T&` oznacza modyfikowalny argument istniejący, a `T&&` ma różne role zależnie od kontekstu. Dla małych typów wartościowych przekazanie przez wartość jest zwykle najprostsze.

~~~cpp
#include <cassert>
#include <string>
#include <string_view>

std::string greet(std::string_view name) {
    return "Witaj, " + std::string{name};
}

int area(int side) {
    return side * side;
}

int area(int width, int height) {
    return width * height;
}

int main() {
    assert(greet("Ada") == "Witaj, Ada");
    assert(area(4) == 16);
    assert(area(4, 5) == 20);
}
~~~

Przeciążenia mają tę samą nazwę, ale różne listy parametrów. Typ zwracany sam nie rozróżnia przeciążenia. Kompilator tworzy zbiór kandydatów, odrzuca niewykonalne, porównuje sekwencje konwersji i wybiera najlepszą funkcję. Niejawne konwersje i parametry domyślne mogą spowodować niejednoznaczność.

Parametry domyślne są dołączane w miejscu wywołania, dlatego ich zmiana w publicznym nagłówku może wymagać przebudowania klientów. Funkcja `inline` pozwala na identyczne definicje w wielu jednostkach translacji; nie jest poleceniem optymalizacji. `[[nodiscard]]` ostrzega, gdy wynik o istotnym znaczeniu został pominięty.

Zwracanie referencji lub wskaźnika wymaga, aby wskazywany obiekt żył wystarczająco długo. Nigdy nie zwracaj referencji do zwykłej zmiennej lokalnej. Return value optimization i move semantics sprawiają, że zwracanie obiektów przez wartość jest naturalnym i często wydajnym wyborem.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Funkcje i przeciążanie”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Overload resolution buduje kandydatów, odrzuca funkcje niewykonalne i porównuje sekwencje konwersji. Wartość domyślna argumentu jest wybierana w miejscu wywołania, natomiast funkcja wybrana po typach nadal ma jedną definicję.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Funkcje i przeciążanie” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Funkcje i przeciążanie
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Funkcje i przeciążanie”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Copy, move i rule of zero](../03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
- [Szablony funkcji](../05_szablony_i_generycznosc/01_function_i_class_templates.md)
- [Overload resolution](../zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)

