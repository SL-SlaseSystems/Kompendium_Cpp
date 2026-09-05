[← Spis treści](../README.md)

# Czym jest C++

C++ jest wieloparadygmatowym językiem ogólnego przeznaczenia. Pozwala pisać kod proceduralny, obiektowy, generyczny i funkcyjny, a jednocześnie daje bezpośredni dostęp do reprezentacji danych oraz zasobów systemu. Projekt języka opiera się na zasadzie *zero-overhead*: nie powinno się płacić za mechanizm, którego się nie używa, a użyta abstrakcja ma być możliwa do zaimplementowania równie wydajnie ręcznie. To cel projektowy, nie obietnica, że każdy abstrakcyjny kod będzie automatycznie szybki.

C++ nie ma garbage collectora narzuconego przez język. Czas życia obiektów jest deterministyczny, dlatego podstawowym idiomem jest RAII: zasób wiąże się z obiektem, a jego zwolnienie następuje w destruktorze. Dzięki temu pamięcią, plikami i blokadami można zarządzać bez ręcznego sprzątania na każdej ścieżce sterowania. Język nadal dopuszcza operacje niskopoziomowe, więc poprawność zależy również od przestrzegania reguł czasu życia, aliasowania i synchronizacji.

~~~cpp
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> languages{"C++", "Rust", "Python"};
    for (const auto& name : languages) {
        std::cout << name << '\n';
    }
}
~~~

Przykład korzysta z typu wartościowego `std::vector`: kolekcja sama zarządza pamięcią elementów. Referencja `const auto&` pozwala czytać każdy napis bez kopiowania. Po wyjściu z `main` destruktory automatycznie sprzątają zasoby.

C++ jest używany w systemach operacyjnych, silnikach gier, przeglądarkach, bazach danych, systemach wbudowanych, aplikacjach czasu rzeczywistego i bibliotekach wymagających kontroli nad kosztami. Ceną za elastyczność jest złożony model języka oraz możliwość undefined behavior. Współczesny styl C++ ogranicza tę powierzchnię przez typy wartościowe, standardowe kontenery, smart pointery, algorytmy i silne kontrakty interfejsów.

## Jak to działa krok po kroku

Prześledź pierwszy program na trzech poziomach. Podczas kompilacji nazwa `std::vector<std::string>` określa konkretny typ kontenera; kompilator sprawdza, czy napis można skonstruować z każdego literału. Podczas wykonania powstaje obiekt `languages` i jego trzy elementy. Kontener organizuje przechowywanie elementów, a każdy napis sam obsługuje własną reprezentację. Nie trzeba znać rozmiaru wewnętrznego bufora napisu, aby legalnie go używać.

W pętli `const auto& name` jest kolejną referencją do elementu. Zastąpienie jej przez `auto name` oznacza utworzenie kopii przy każdej iteracji. Wynik na ekranie pozostanie taki sam, lecz program może wykonywać więcej pracy. Po wyjściu z zakresu niszczony jest kontener i jego elementy. Zasada RAII działa także przy zwykłym wcześniejszym `return` i odwijaniu stosu po wyjątku; nie gwarantuje sprzątania po przerwaniu procesu przez system.

## Pogłębienie mechanizmu

Najważniejszym nawykiem jest oddzielenie **reguły języka**, **kontraktu biblioteki** i **wyboru implementacji**. Język mówi, kiedy wywołać destruktor. Biblioteka określa, że `vector` przechowuje zwykłe elementy ciągle w pamięci. Konkretna implementacja wybiera współczynnik wzrostu pojemności. Pierwsze dwa poziomy mogą być podstawą przenośnego programu; trzeciego nie należy zakodować jako założenia aplikacji.

System typów C++ jest statyczny, ale nie oznacza to, że wszystkie wartości są znane podczas kompilacji. Typ `int` może być znany, a jego wartość pochodzić z pliku. Szablon pozwala wybrać implementację na podstawie typu; funkcja wirtualna pozwala wybrać ją na podstawie rzeczywistego obiektu podczas wykonania. Oba mechanizmy mają inne zastosowania i mogą występować w tym samym programie.

Semantyka wartości to kolejny fundament: przypisanie `b = a` dla wektora kopiuje jego elementy, podczas gdy przypisanie wskaźnika kopiuje adres. „Dwie zmienne” nie musi oznaczać „dwóch niezależnych danych”. Zanim przeanalizujesz trudny kod, ustal typ każdej zmiennej oraz to, czy reprezentuje wartość, właściciela czy obserwatora. To wyjaśnia więcej niż sam wygląd operatora `=`.

## Drugi przykład

~~~cpp
#include <cassert>
#include <vector>

int main() {
    std::vector<int> original{1, 2, 3};
    auto copy = original;
    auto& alias = original;
    copy[0] = 100;
    alias[1] = 20;
    assert(original[0] == 1);
    assert(original[1] == 20);
    assert(copy[1] == 2);
}
~~~

`copy` ma własny zestaw elementów. `alias` nie jest drugim wektorem: daje dostęp do `original`. Zmiana pierwszego elementu kopii nie zmienia oryginału, ale zmiana przez referencję jest zmianą oryginału. Obie kolekcje zostaną posprzątane automatycznie. Sama referencja nie ma operacji zwalniającej cudzą pamięć.

## Porównanie i decyzje

Ucz się C++ od poprawnego modelu obiektów, a następnie dodawaj kontrolę nad kosztami. Do kolekcji o zmiennym rozmiarze zacznij od `vector`, do tekstu od `string`, a do wyłącznej własności dynamicznego obiektu od `unique_ptr`. Surowa pamięć, niestandardowy allocator i ręczna synchronizacja przydadzą się później, gdy potrafisz określić brakującą gwarancję albo zmierzyć ograniczenie prostszej wersji.

Nie utożsamiaj zaawansowania z liczbą użytych mechanizmów. Dobrze zaprojektowana biblioteka ukrywa trudne reguły wewnątrz niewielu typów i udostępnia łatwy do użycia kontrakt. Warto umieć wyjaśnić zarówno implementację właściciela zasobu, jak i powód, dla którego kod aplikacji powinien korzystać z gotowego właściciela.

## Ćwiczenie z odpowiedzią

Zmień `auto& alias` na `auto alias`. Które sprawdzenie przestanie być prawdziwe? Sprawdzenie `original[1] == 20`, ponieważ teraz `alias` również jest niezależną kopią. Następnie użyj `const auto& alias`: odczyty pozostaną legalne, ale przypisanie do `alias[1]` zostanie odrzucone podczas kompilacji. To trzy różne kontrakty zapisane przez niewielką zmianę deklaracji.

Źródło idei kosztu abstrakcji: [Bjarne Stroustrup, Abstraction and the C++ machine model](https://www.stroustrup.com/abstraction-and-machine.pdf).

## Powiązane tematy

- [Standardy i implementacje](02_standardy_i_implementacje.md)
- [RAII i destruktory](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)

