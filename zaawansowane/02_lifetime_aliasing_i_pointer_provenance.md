[← Spis treści](../README.md)

# Lifetime, aliasing i pointer provenance

Adres pamięci nie wystarcza do legalnego dostępu. Musi istnieć żywy obiekt właściwego typu, pointer musi spełniać alignment, a operacja musi respektować reguły aliasowania. Pointer provenance opisuje związek wskaźnika z obiektem i storage, z którego pochodzi; formalny model jest rozwijany i nie powinien być upraszczany do „wskaźnik to liczba”.

~~~cpp
#include <cassert>
#include <memory>
#include <new>

struct Value {
    int number;
};

int main() {
    alignas(Value) unsigned char storage[sizeof(Value)];
    Value* value = std::construct_at(reinterpret_cast<Value*>(storage), Value{42});
    assert(value->number == 42);
    std::destroy_at(value);
}
~~~

Przykład ręcznie rozpoczyna i kończy lifetime w odpowiednio wyrównanym storage. `reinterpret_cast` sam nie konstruuje obiektu. W kodzie aplikacyjnym lepszy jest zwykły obiekt lub kontener; ten wzorzec należy do implementacji alokatorów i struktur o ręcznym storage.

Type-accessible glvalue może odczytać obiekt przez dozwolony typ, m.in. zgodny typ, odpowiednio cv-qualified, odpowiadający signed/unsigned lub typ znakowy/`std::byte` w określonych operacjach reprezentacji. Naruszenie reguł daje UB i pozwala optimizerowi zakładać brak pewnych aliasów.

`std::launder` nie jest uniwersalnym „napraw wskaźnik”. Ma wąskie zastosowanie po utworzeniu nowego obiektu w tym samym storage, gdy stary pointer nie może automatycznie wskazywać nowego obiektu z powodu reguł transparent replacement. Najpierw zrozum dokładny lifetime.

Konwersja pointer–integer–pointer ma implementacyjne i standardowe ograniczenia; operacje na liczbie mogą utracić związek wymagany przez model implementacji. Do przesunięć wewnątrz obiektu używaj reguł pointer arithmetic i `std::byte`, nie arbitralnej arytmetyki adresów.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Lifetime, aliasing i pointer provenance”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz zapisanie założeń, wskazanie reguły standardu, prześledzenie konsekwencji dla programu i potwierdzenie hipotezy narzędziem właściwym dla implementacji. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oznacz gwarancję normatywną, ograniczenie platformy, konwencję ABI i aktualną strategię optymalizatora jako osobne źródła wiedzy. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź minimalny przykład, diagnostykę wielu kompilatorów, sanitizer, assembly lub profil oraz odniesienie do używanej wersji standardu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Tematy eksperckie trzeba analizować na trzech poziomach: reguły abstract machine, obserwowalne zachowanie programu i szczegół implementacyjny kompilatora lub ABI. Optymalizacja może wykorzystywać gwarancje standardu, ale nie zamienia heurystyki w kontrakt języka. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Reguły aliasingu określają, przez jakie glvalue wolno uzyskać dostęp do obiektu, a provenance wiąże wskaźnik z pochodzeniem storage. Kopiowanie adresu do liczby i z powrotem nie zawsze zachowuje wszystkie gwarancje dostępu.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Lifetime, aliasing i pointer provenance” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Lifetime, aliasing i pointer provenance
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Lifetime, aliasing i pointer provenance”, oceniaj poprawność wobec abstract machine, przenośność, koszt dowodu, stabilność założenia i realny wpływ na wymaganie użytkownika. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Powiązane tematy

- [Storage duration i lifetime](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Layout i alignment](03_layout_alignment_padding_i_triviality.md)
- [Alokatory](04_allocatory_pmr_i_new_delete.md)

