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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Czym jest C++”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz przejście od tekstu źródłowego przez analizę składniową i semantyczną do artefaktu wykonywalnego. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie standardu od rozszerzenia kompilatora, ustawienia toolchainu i zachowania platformy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź pełne polecenie kompilacji, wersje narzędzi, diagnostykę oraz wynik uruchomienia w kontrolowanym środowisku. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Program C++ powstaje w łańcuchu źródło–kompilator–linker–środowisko wykonawcze. Standard opisuje zachowanie programu abstrakcyjnego, implementacja wybiera reprezentację i ABI, a system operacyjny dostarcza proces, pliki oraz biblioteki. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- C++ jest językiem wieloparadygmatowym z bezpośrednim modelem obiektów i deterministyczną destrukcją. Model zero-overhead nie obiecuje zerowego kosztu każdej konstrukcji; wymaga, aby nie płacić za mechanizm, którego program nie używa.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Czym jest C++” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Czym jest C++
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Czym jest C++”, oceniaj przenośność, powtarzalność budowania, jakość diagnostyki i jawne wymagania wersji standardu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Ucz się najpierw nowoczesnego C++23, a składnię historyczną traktuj jako wiedzę potrzebną przy utrzymaniu istniejącego kodu. Preferuj bibliotekę standardową i RAII. Surowy wskaźnik powinien zwykle oznaczać niewłaścicielski dostęp, nie obowiązek wykonania `delete`.

## Powiązane tematy

- [Standardy i implementacje](02_standardy_i_implementacje.md)
- [RAII i destruktory](../03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
- [Undefined behavior](../zaawansowane/01_undefined_behavior_i_model_maszyny.md)

