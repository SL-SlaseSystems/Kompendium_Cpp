[← Spis treści](../README.md)

# Proces budowania

Plik źródłowy C++ nie staje się programem w jednym logicznym kroku. Preprocesor obsługuje dyrektywy, takie jak `#include`, `#define` i warunkowa kompilacja. Następnie kompilator analizuje wynik jako jednostkę translacji, sprawdza typy i generuje kod obiektowy. Linker łączy obiekty oraz biblioteki, rozwiązuje symbole i tworzy program lub bibliotekę.

~~~text
clang++ -std=c++23 -E main.cpp -o main.ii
clang++ -std=c++23 -c main.cpp -o main.o
clang++ main.o -o app
~~~

Opcja `-E` zatrzymuje proces po preprocessing, a `-c` tworzy plik obiektowy bez linkowania. W rzeczywistym projekcie system budowania pilnuje zależności i uruchamia tylko potrzebne kroki. Polecenia ręczne są jednak dobrym narzędziem diagnostycznym.

~~~cpp
#include <numeric>
#include <vector>

int sum(const std::vector<int>& values) {
    return std::accumulate(values.begin(), values.end(), 0);
}

int main() {
    return sum({1, 2, 3}) == 6 ? 0 : 1;
}
~~~

Deklaracja mówi kompilatorowi, że nazwa istnieje i jaki ma typ. Definicja dostarcza byt lub ciało funkcji. Ta sama funkcja nieinline powinna mieć dokładnie jedną definicję w całym programie; to część One Definition Rule. Szablony i funkcje `inline` mają inne warunki i dlatego ich definicje często znajdują się w nagłówkach.

Biblioteka statyczna jest kopiowana przez linker do wyniku na poziomie potrzebnych obiektów, natomiast dynamiczna pozostaje osobnym artefaktem ładowanym podczas startu lub działania programu. Szczegóły nazw plików, wyszukiwania bibliotek i ABI są platformowe.

## Typowe pułapki

Błąd „undefined reference” zwykle oznacza brak definicji albo brak biblioteki przy linkowaniu, a „multiple definition” naruszenie ODR. Zmiana ABI bez przebudowania zależnych obiektów może dać trudne błędy. Czyść build directory po zmianie kompilatora, istotnych flag ABI albo wersji biblioteki standardowej.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Proces budowania”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz przejście od tekstu źródłowego przez analizę składniową i semantyczną do artefaktu wykonywalnego. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie standardu od rozszerzenia kompilatora, ustawienia toolchainu i zachowania platformy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź pełne polecenie kompilacji, wersje narzędzi, diagnostykę oraz wynik uruchomienia w kontrolowanym środowisku. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Program C++ powstaje w łańcuchu źródło–kompilator–linker–środowisko wykonawcze. Standard opisuje zachowanie programu abstrakcyjnego, implementacja wybiera reprezentację i ABI, a system operacyjny dostarcza proces, pliki oraz biblioteki. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Preprocessing, kompilacja, generowanie pliku obiektowego i linkowanie to odrębne fazy z innymi błędami. Błąd undefined reference oznacza zwykle brak pasującej definicji podczas linkowania, nie problem parsera.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Proces budowania” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Proces budowania
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Proces budowania”, oceniaj przenośność, powtarzalność budowania, jakość diagnostyki i jawne wymagania wersji standardu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Translation units i nagłówki](../08_budowanie_i_organizacja/01_translation_units_headers_i_include.md)
- [Linkowanie, ODR i inline](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
- [CMake](../08_budowanie_i_organizacja/05_cmake.md)

