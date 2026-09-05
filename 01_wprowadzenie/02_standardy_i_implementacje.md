[← Spis treści](../README.md)

# Standardy i implementacje

C++ jest definiowany przez normę ISO/IEC 14882, a nie przez jeden konkretny kompilator. WG21 rozwija specyfikację w cyklu mniej więcej trzyletnim. Nazwa C++23 odnosi się do roku zakończenia prac technicznych; opublikowana norma nosi formalne oznaczenie ISO/IEC 14882:2024. C++26 jest następną rewizją i do chwili publikacji należy rozróżniać working draft od obowiązującego standardu.

Standard opisuje *abstract machine*: reguły, którym musi odpowiadać obserwowalne zachowanie programu. Implementacje — przede wszystkim GCC, Clang i Microsoft Visual C++ — tłumaczą ten model na konkretne procesory, systemy i ABI. Mogą różnić się stopniem implementacji nowych funkcji, diagnostyką, rozszerzeniami oraz biblioteką standardową. Clang może używać libc++, ale często jest łączony z libstdc++; MSVC dostarcza własną implementację STL.

~~~cpp
#include <iostream>

int main() {
    std::cout << "Wersja języka: " << __cplusplus << '\n';

#if __cplusplus >= 202302L
    std::cout << "Tryb co najmniej C++23\n";
#endif
}
~~~

Makro `__cplusplus` mówi o wybranym trybie języka, nie gwarantuje jednak obecności każdej funkcji bibliotecznej. Do precyzyjnej detekcji służą feature-test macros, na przykład `__cpp_concepts` albo makra biblioteczne udostępniane po włączeniu odpowiedniego nagłówka.

W dokumentacji spotkasz kilka kategorii zachowania. *Implementation-defined* wymaga, by implementacja dokumentowała wybór, na przykład rozmiar niektórych typów. *Unspecified* pozwala wybrać jedno z dopuszczonych zachowań bez dokumentowania. *Undefined behavior* nie nakłada wymagań na wykonanie programu. W C++26 dochodzi istotniejsze formalne rozróżnienie wartości indeterminate i erroneous; nie należy przenosić go bez adnotacji do bazowego opisu C++23.

## Jak to działa krok po kroku

Przy pytaniu „czy mogę tego użyć?” ustal kolejno: wybrany standard języka, implementację kompilatora, implementację biblioteki i docelową platformę. Kompilator może rozpoznawać korutyny, podczas gdy biblioteka nie dostarcza `std::generator`. Samo zainstalowanie nowszego kompilatora nie podmienia automatycznie wszystkich nagłówków ani bibliotek znalezionych przez system budowania.

Następnie przygotuj minimalny program używający dokładnie potrzebnego API. Sprawdź makro funkcji, skompiluj i zlinkuj program. Jeżeli funkcja zależy od danych systemowych, jak baza stref czasowych, sprawdź też wykonanie. Dopiero komplet tych informacji opisuje użyteczny zakres wsparcia. Wynik zanotuj jako konfigurację, na przykład „Apple Clang + dołączona libc++ + macOS + C++23”, a nie ogólne „Clang obsługuje C++23”.

## Pogłębienie mechanizmu

Rozróżnienie kategorii zachowania decyduje, jakie wnioski wolno wyciągnąć z eksperymentu:

| Kategoria | Obowiązek i konsekwencja |
|---|---|
| Zdefiniowane | Program może polegać na podanej regule, przy spełnionych wymaganiach. |
| Implementation-defined | Wybór jest udokumentowany przez implementację; sprawdź dokumentację platformy. |
| Unspecified | Istnieje zbiór dozwolonych wyników, ale wybór nie wymaga dokumentacji. |
| Undefined behavior | Norma nie określa skutków takiego wykonania; udany test nie ustanawia gwarancji. |
| Ill-formed | Program narusza regułę; zwykle wymagana jest diagnostyka, ale istnieją przypadki „no diagnostic required”. |

Kolejność obliczania argumentów zwykłego wywołania jest dobrym przykładem unspecified. Nie należy mylić jej z pierwszeństwem operatorów, które określa grupowanie składni. Z kolei wyjście poza zakres podczas dereferencji jest problemem poprawności, a nie wyborem jednej z kilku legalnych wartości. Zobaczenie „sensownej liczby” nie legalizuje dostępu.

Standard nie definiuje jednej szerokości `int` ani jednego ABI. Gwarantuje minimalne zakresy i relacje między typami, a implementacja dokumentuje konkretne parametry. C++ jest zatem przenośny w znaczeniu możliwości napisania kodu zgodnego z kontraktami, nie identycznej reprezentacji każdego obiektu na każdej maszynie. Format pliku trzeba zaprojektować niezależnie od `sizeof` klasy.

## Drugi przykład

~~~cpp
#include <cassert>
#include <climits>
#include <limits>

int main() {
    static_assert(sizeof(char) == 1);
    static_assert(CHAR_BIT >= 8);
    static_assert(std::numeric_limits<int>::max() >= 32767);
    const unsigned maximum = std::numeric_limits<unsigned>::max();
    assert(maximum + 1u == 0u);
}
~~~

Pierwsze sprawdzenie mówi o jednostce rozmiaru języka, nie o liczbie bitów bajtu. Drugie określa minimalną liczbę bitów. Trzecie sprawdza minimalny zakres dodatni `int`. Ostatnia operacja korzysta ze zdefiniowanej arytmetyki modulo typu unsigned; analogiczne dodanie jedynki do największego `int` nie ma tej gwarancji.

## Porównanie i decyzje

Dla nauki stosuj jeden zadeklarowany punkt odniesienia, tutaj C++23. Przy czytaniu aktualnego working draft sprawdzaj, czy reguła nie została zmieniona w C++26. Numery akapitów i treść bieżącego draftu mogą się przesuwać; stabilny dokument N4950 jest użyteczny przy ustalaniu bazy C++23. Zgłoszenia błędów standardu, czyli defect reports, mogą prowadzić do poprawek wdrażanych także w starszych trybach kompilatora.

W bibliotece przeznaczonej dla wielu odbiorców wybór minimalnego standardu jest częścią kontraktu. Wyższy standard upraszcza kod, ale zmniejsza zbiór obsługiwanych konfiguracji. Warstwa zgodności ma sens dla kilku konkretnych braków; utrzymywanie własnej kopii znacznej części nowej biblioteki szybko staje się osobnym projektem.

## Ćwiczenie z odpowiedzią

Dwa kompilatory wypisują różną wartość `sizeof(long)`, ale oba akceptują kod. Czy jeden się myli? Nie: sprawdź dopuszczony zakres i dokumentację modelu danych. Czy podobne rozumowanie uzasadnia różne wyniki dostępu `array[100]` w tablicy trójelementowej? Nie: to naruszenie granic, dla którego porównywanie wyników nie daje dowodu poprawności.

Źródła: [ISO/IEC 14882:2024](https://www.iso.org/standard/83626.html), [C++23: maszyna abstrakcyjna](https://timsong-cpp.github.io/cppwp/n4950/intro.abstract).

## Powiązane tematy

- [Kompilatory i toolchain](03_kompilatory_i_toolchain.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

