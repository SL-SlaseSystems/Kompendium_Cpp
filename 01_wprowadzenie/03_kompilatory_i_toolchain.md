[← Spis treści](../README.md)

# Kompilatory i toolchain

Typowy toolchain C++ składa się z kompilatora, implementacji biblioteki standardowej, linkera, debuggera i systemu budowania. Na Linuksie najczęściej spotyka się GCC lub Clang, na Windows MSVC, Clang-cl albo MinGW, a na macOS Apple Clang. Wybór kompilatora nie powinien być ukrytym założeniem biblioteki, jeśli projekt deklaruje przenośność.

Minimalna kompilacja pojedynczej jednostki translacji wygląda następująco:

~~~text
clang++ -std=c++23 -Wall -Wextra -Wpedantic main.cpp -o app
./app
~~~

`-std=c++23` wybiera dialekt, `-Wall -Wextra -Wpedantic` włącza wartościowy zestaw ostrzeżeń, a `-o` nadaje nazwę wynikowi. Ostrzeżenia są częścią procesu jakości, ale nie zastępują analizy statycznej ani sanitizerów. W projekcie MSVC analogiczne intencje wyrażają między innymi `/std:c++latest`, `/W4` i `/permissive-`.

~~~cpp
#include <cstdlib>
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Użycie: program NAZWA\n";
        return EXIT_FAILURE;
    }
    std::cout << "Witaj, " << argv[1] << "!\n";
    return EXIT_SUCCESS;
}
~~~

Debug build powinien zachowywać symbole i ułatwiać diagnostykę, na przykład `-g -O0` lub `-Og`. Release build włącza optymalizację, zwykle `-O2` albo `-O3`, ale dokładny profil należy kontrolować w systemie budowania. Sanitizery dodaje się do kompilacji i linkowania, np. `-fsanitize=address,undefined`.

## Dobra konfiguracja

W CI warto kompilować co najmniej Clangiem i GCC, a kod przenośny na Windows również MSVC. Ustal wersję minimalną kompilatora, standard języka i politykę ostrzeżeń. Nie wpisuj globalnych flag platformowych w kodzie; konfiguruj je per target w CMake. Narzędzia `clang-format`, `clang-tidy`, `lldb` i `gdb` rozwiązują inne problemy i powinny mieć osobne kroki w pipeline.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Kompilatory i toolchain”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz przejście od tekstu źródłowego przez analizę składniową i semantyczną do artefaktu wykonywalnego. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie standardu od rozszerzenia kompilatora, ustawienia toolchainu i zachowania platformy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź pełne polecenie kompilacji, wersje narzędzi, diagnostykę oraz wynik uruchomienia w kontrolowanym środowisku. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Program C++ powstaje w łańcuchu źródło–kompilator–linker–środowisko wykonawcze. Standard opisuje zachowanie programu abstrakcyjnego, implementacja wybiera reprezentację i ABI, a system operacyjny dostarcza proces, pliki oraz biblioteki. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Frontend parsuje i sprawdza język, optimizer przekształca reprezentację pośrednią, backend generuje kod, a linker scala symbole. Flagi ostrzeżeń, tryb standardu, standard library i linker są częścią reprodukowalnej konfiguracji.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Kompilatory i toolchain” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Kompilatory i toolchain
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Kompilatory i toolchain”, oceniaj przenośność, powtarzalność budowania, jakość diagnostyki i jawne wymagania wersji standardu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Proces budowania](05_proces_budowania.md)
- [Ostrzeżenia i analiza statyczna](../09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md)
- [CMake](../08_budowanie_i_organizacja/05_cmake.md)

