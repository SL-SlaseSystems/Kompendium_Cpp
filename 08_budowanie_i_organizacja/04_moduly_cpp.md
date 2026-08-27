[← Spis treści](../README.md)

# Moduły C++

Moduły wprowadzone w C++20 pozwalają eksportować deklaracje bez tekstowego kopiowania całego interfejsu przez `#include`. Mogą poprawić izolację makr i czas budowania, ale wymagają współpracy kompilatora oraz systemu budowania, który zna zależności między module interface units.

~~~text
// math.cppm — module interface unit
export module math;

export int square(int value) {
    return value * value;
}

// main.cpp
import math;

int main() {
    return square(4) == 16 ? 0 : 1;
}
~~~

Przykład pozostaje blokiem `text`, ponieważ sposób kompilowania modułów w Clang, GCC i MSVC oraz format artefaktów BMI/CMI nie ma jednolitego ręcznego interfejsu. Standard opisuje semantykę języka, nie polecenia toolchainu. W praktyce powierz obsługę nowoczesnemu CMake lub natywnemu systemowi środowiska i testuj każdą wspieraną konfigurację.

Jednostka może mieć global module fragment przed deklaracją modułu, część eksportowaną, implementacyjną i private module fragment. `export import` reeksportuje zależność. Header units pozwalają importować pewne nagłówki, ale nie zamieniają automatycznie każdego legacy header w dobry moduł.

Moduły nie rozwiązują stabilności ABI, dystrybucji bibliotek binarnych ani wszystkich naruszeń ODR. Makra nie są eksportowane jak zwykłe deklaracje, co jest zaletą izolacji, ale może komplikować biblioteki konfigurowane preprocesorem. Migrację warto zaczynać od dobrze odseparowanych targetów, nie od mechanicznego zastąpienia wszystkich include.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Moduły C++”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Moduł eksportuje deklaracje semantycznie zamiast tekstowego wklejania nagłówka. BMI jest artefaktem zależnym od kompilatora i opcji, dlatego jego budowanie musi być częścią grafu, a nie ręcznie kopiowanym plikiem.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Moduły C++” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Moduły C++
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Moduły C++”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Translation units i nagłówki](01_translation_units_headers_i_include.md)
- [CMake](05_cmake.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)

