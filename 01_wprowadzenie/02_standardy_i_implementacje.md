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

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Standardy i implementacje”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz przejście od tekstu źródłowego przez analizę składniową i semantyczną do artefaktu wykonywalnego. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wymaganie standardu od rozszerzenia kompilatora, ustawienia toolchainu i zachowania platformy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź pełne polecenie kompilacji, wersje narzędzi, diagnostykę oraz wynik uruchomienia w kontrolowanym środowisku. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Program C++ powstaje w łańcuchu źródło–kompilator–linker–środowisko wykonawcze. Standard opisuje zachowanie programu abstrakcyjnego, implementacja wybiera reprezentację i ABI, a system operacyjny dostarcza proces, pliki oraz biblioteki. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Dokument ISO definiuje program abstrakcyjny, a implementacja składa się z kompilatora, biblioteki standardowej i ABI platformy. Zachowanie implementation-defined musi być udokumentowane, unspecified dopuszcza wybór, a undefined behavior nie nakłada wymagań.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Standardy i implementacje” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Standardy i implementacje
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Standardy i implementacje”, oceniaj przenośność, powtarzalność budowania, jakość diagnostyki i jawne wymagania wersji standardu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Pułapki i praktyka

Flaga `-std=c++23` lub `/std:c++latest` nie dowodzi pełnej zgodności implementacji. Sprawdzaj dokumentację kompilatora, biblioteki i konkretne makro funkcji. Nie uzależniaj przenośnego kodu od rozszerzenia bez warunkowej kompilacji i testu na drugim toolchainie.

## Powiązane tematy

- [Kompilatory i toolchain](03_kompilatory_i_toolchain.md)
- [Feature-test macros](../12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

