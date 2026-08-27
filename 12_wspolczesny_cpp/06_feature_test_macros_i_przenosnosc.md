[← Spis treści](../README.md)

# Feature-test macros i przenośność

Feature-test macros pozwalają wykryć konkretną funkcję języka lub biblioteki. Makra językowe zwykle zaczynają się od `__cpp_`, biblioteczne od `__cpp_lib_`. Wartość koduje rewizję funkcji, dlatego porównanie liczbowe jest ważniejsze niż samo `#ifdef`.

~~~cpp
#include <cassert>
#include <version>

int main() {
#if defined(__cpp_consteval) && __cpp_consteval >= 201811L
    constexpr bool has_consteval = true;
#else
    constexpr bool has_consteval = false;
#endif
    assert(has_consteval);
}
~~~

`__cplusplus` wskazuje tryb języka, lecz biblioteka standardowa może mieć inny poziom kompletności. MSVC historycznie wymagał opcji `/Zc:__cplusplus`, aby makro raportowało współczesną wartość. Używaj oficjalnej dokumentacji toolchainu i testów konfiguracji.

Warunkowa kompilacja powinna mieć mały zasięg. Zamiast rozrzucać preprocesor po logice domenowej, zbuduj adapter wybierający implementację i udostępniający wspólny interfejs. Testuj obie gałęzie w macierzy CI; fallback, którego nikt nie buduje, szybko gnije.

Nie używaj wyłącznie numeru wersji kompilatora do wykrywania języka. Vendor może backportować funkcję lub używać innej biblioteki standardowej. Dla zależności systemowych CMake `try_compile`, wykrywanie target properties i pakiety config mogą być lepsze od ręcznych makr.

Przenośność obejmuje także endianess, szerokości typów, alignment, ABI, filesystem, locale i model wątków. Compile-time detekcja odpowiada tylko na część pytań; zachowanie należy testować na rzeczywistych platformach.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Feature-test macros i przenośność”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz identyfikację wymaganej funkcji, sprawdzenie feature-test macro, wybór implementacji i weryfikację na wszystkich wspieranych toolchainach. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel wersję języka ustawioną flagą od faktycznej implementacji funkcji i dostępności odpowiedniego komponentu biblioteki standardowej. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź wartość makra funkcji, wynik kompilacji minimalnego przykładu, status implementacji i test na najstarszym wspieranym narzędziu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Edycje standardu dodają język i bibliotekę, lecz ich obecność w dokumencie nie oznacza kompletnego wsparcia toolchainu. Kod produkcyjny potrzebuje macierzy kompilator–biblioteka–platforma oraz polityki fallbacku. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Makro feature-test ma wartość wersjonującą konkretną funkcję języka lub biblioteki. Sprawdzanie wyłącznie `__cplusplus` jest zbyt grube, gdy implementacja wspiera edycję standardu częściowo.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Feature-test macros i przenośność” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Feature-test macros i przenośność
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Feature-test macros i przenośność”, oceniaj wartość funkcji dla projektu, dojrzałość implementacji, koszt fallbacku, wpływ na ABI oraz termin wsparcia toolchainu. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Standardy i implementacje](../01_wprowadzenie/02_standardy_i_implementacje.md)
- [C++23](04_cpp23.md)
- [C++26](../zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

