[← Spis treści](../README.md)

# Linkowanie, ODR i inline

Linkage określa, czy deklaracje w różnych zakresach i jednostkach odnoszą się do tej samej encji. Nazwa może mieć external, internal albo no linkage. Anonimowa przestrzeń nazw nadaje elementom namespace scope internal linkage i jest preferowana nad `static` dla pomocniczych nazw w pliku `.cpp`.

One Definition Rule wymaga jednej definicji odr-used funkcji lub zmiennej nieinline w całym programie. Typy, szablony, funkcje inline i inline variables mogą mieć definicje w wielu jednostkach, lecz muszą spełniać szczegółowe wymagania równoważności. Naruszenie ODR nie zawsze wymaga diagnostyki, więc program może linkować i nadal być niepoprawny.

~~~cpp
#include <cassert>

inline constexpr int protocol_version = 3;

inline int square(int value) {
    return value * value;
}

int main() {
    static_assert(protocol_version == 3);
    assert(square(5) == 25);
}
~~~

`inline` nie nakazuje kompilatorowi wstawienia ciała w miejscu wywołania. To właściwość ODR i linkage. Optymalizator podejmuje decyzję o inline niezależnie, zwłaszcza przy link-time optimization.

Błędy „undefined symbol/reference” wynikają zwykle z braku definicji, niewłaściwej biblioteki, różnicy sygnatury albo visibility. „Duplicate symbol” wskazuje wiele niedozwolonych definicji. Name mangling koduje sygnatury i zależy od ABI, dlatego C++ API nie jest bezpośrednio stabilnym C ABI.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Linkowanie, ODR i inline”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- ODR wymaga pojedynczej definicji odr-used bytu w programie, z wyjątkami dla zgodnych definicji inline i template. `inline` pozwala na definicje w wielu jednostkach; nie jest poleceniem wykonania inline przez optimizer.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Linkowanie, ODR i inline” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Linkowanie, ODR i inline
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Linkowanie, ODR i inline”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Nie definiuj zwykłych zmiennych globalnych w nagłówku bez `inline` lub `constexpr` spełniającego właściwe reguły. Trzymaj implementacyjne symbole w anonimowym namespace. Używaj narzędzi `nm`, `objdump` lub platformowych odpowiedników przy diagnozie linkera, ale interpretuj wynik zgodnie z ABI platformy.

## Powiązane tematy

- [Translation units i nagłówki](01_translation_units_headers_i_include.md)
- [ODR, moduły i FFI](../zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)

