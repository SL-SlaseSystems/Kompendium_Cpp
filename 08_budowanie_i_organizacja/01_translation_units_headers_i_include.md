[← Spis treści](../README.md)

# Translation units, nagłówki i include

Po preprocessing każdy plik źródłowy wraz z włączonymi nagłówkami tworzy jednostkę translacji (*translation unit*). Jednostki są kompilowane oddzielnie, dlatego deklaracje potrzebne klientowi muszą być widoczne w każdej z nich. Linker łączy powstałe pliki obiektowe.

Typowy podział umieszcza publiczną deklarację w `.hpp`, a definicję funkcji nieinline w `.cpp`:

~~~text
// math.hpp
#pragma once
int square(int value);

// math.cpp
#include "math.hpp"
int square(int value) { return value * value; }

// main.cpp
#include "math.hpp"
int main() { return square(4) == 16 ? 0 : 1; }
~~~

`#include` jest tekstowym włączeniem pliku. Include guards zapobiegają wielokrotnemu przetworzeniu tego samego nagłówka w jednej jednostce:

~~~text
#ifndef PROJECT_MATH_HPP
#define PROJECT_MATH_HPP
int square(int value);
#endif
~~~

`#pragma once` jest szeroko wspierane, lecz formalnie pozostaje mechanizmem implementacji. Guards są przenośne, o ile nazwa makra jest unikalna i nieużywa identyfikatorów zarezerwowanych.

Nagłówek powinien być samowystarczalny: po jego bezpośrednim dołączeniu dostępne są wszystkie potrzebne deklaracje. Nie polegaj na przypadkowym transitive include. Forward declaration zmniejsza zależności tylko wtedy, gdy wystarczy typ niekompletny; wiele operacji, w tym przechowywanie wartości jako pola, wymaga pełnej definicji.

Szablony i funkcje inline zwykle mają definicje w nagłówku, ponieważ muszą być widoczne przy instancjacji lub spełniać ODR w wielu jednostkach. Moduły C++ rozwiązują część problemów tekstowych nagłówków, lecz współistnienie i wsparcie build systemów nadal wymagają świadomej konfiguracji.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Translation units, nagłówki i include”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Preprocesor rozwija `#include` tekstowo przed kompilacją jednostki translacji. Include guards lub `#pragma once` zapobiegają wielokrotnemu dołączeniu w jednej jednostce, ale nie rozwiązują zależności ani ODR między jednostkami.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Translation units, nagłówki i include” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Translation units, nagłówki i include
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Translation units, nagłówki i include”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Linkowanie, ODR i inline](02_linkowanie_odr_i_inline.md)
- [Moduły C++](04_moduly_cpp.md)
- [Proces budowania](../01_wprowadzenie/05_proces_budowania.md)

