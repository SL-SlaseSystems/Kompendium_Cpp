[← Spis treści](../README.md)

# Leksemy, deklaracje i zakresy

Kod C++ składa się z tokenów: słów kluczowych, identyfikatorów, literałów, operatorów i znaków interpunkcyjnych. Komentarze `//` trwają do końca wiersza, a `/* ... */` mogą obejmować wiele wierszy, lecz nie zagnieżdżają się. Wielkość liter ma znaczenie, więc `value` i `Value` są innymi nazwami.

Deklaracja wprowadza nazwę i opisuje jej typ. Definicja dodatkowo tworzy obiekt, ciało funkcji albo inną encję wymagającą definicji. Zakres (*scope*) określa, gdzie nazwa jest widoczna; czas życia obiektu to osobne zagadnienie i nie zawsze pokrywa się z zakresem nazwy.

~~~cpp
#include <cassert>

int twice(int value); // deklaracja

int twice(int value) { // definicja
    return value * 2;
}

int main() {
    int result = twice(4);
    {
        int result = 10; // przesłania zewnętrzną nazwę
        assert(result == 10);
    }
    assert(result == 8);
}
~~~

Blok `{}` tworzy zakres blokowy. Parametry funkcji, elementy klasy, przestrzenie nazw, inicjalizatory instrukcji `if` i `for` mają własne reguły zakresu. Przesłanianie (*shadowing*) jest legalne, ale może utrudniać czytanie. Ostrzeżenia kompilatora pomagają wykryć przypadkowe przesłonięcia.

Identyfikatory rozpoczynające się podkreśleniem i wielką literą oraz nazwy zawierające podwójne podkreślenie są zarezerwowane dla implementacji. W globalnej przestrzeni nazw zarezerwowane są także nazwy zaczynające się od pojedynczego podkreślenia. Nie używaj takich nazw we własnym API.

## Inicjalizacja

Deklaracja lokalnej zmiennej typu podstawowego bez inicjalizatora może pozostawić wartość indeterminate. Czytanie jej może prowadzić do błędnego programu lub UB zależnie od kontekstu i wersji standardu. Inicjalizuj obiekty przy deklaracji, najlepiej nawiasami klamrowymi, gdy chcesz blokować konwersje zawężające.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Leksemy, deklaracje i zakresy”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz utworzenie deklaracji, ustalenie typu, wybór operacji i ocenę wyrażenia zgodnie z regułami języka. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba sprawdź, które informacje istnieją w czasie kompilacji, a które zależą od danych i stanu programu podczas wykonania. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź typ wyrażenia, wybrany overload, zakres nazwy, wartość wyniku i ewentualną diagnostykę kompilatora. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Podstawowe konstrukcje C++ trzeba czytać jako operacje na typach, wartościach i zakresach, a nie tylko jako składnię. Istotne są konwersje, kategorie wartości, kolejność ewaluacji oraz to, czy dana nazwa oznacza obiekt, funkcję czy typ. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Deklaracja wprowadza nazwę i jej znaczenie, a definicja dodatkowo dostarcza obiekt lub ciało wymagane przez program. Zakres określa widoczność nazwy, natomiast linkage decyduje, czy deklaracje z różnych jednostek mogą oznaczać ten sam byt.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Leksemy, deklaracje i zakresy” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Leksemy, deklaracje i zakresy
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Leksemy, deklaracje i zakresy”, oceniaj jawność intencji, brak niebezpiecznych konwersji, minimalny zakres nazw i możliwość wykrycia błędu podczas kompilacji. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Typy i literały](02_typy_podstawowe_i_literaly.md)
- [Storage duration i lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Namespaces](../08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)

