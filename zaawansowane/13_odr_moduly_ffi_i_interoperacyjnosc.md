[← Spis treści](../README.md)

# ODR, moduły, FFI i interoperacyjność

FFI wymaga kontraktu na poziomie języka, ABI i ownership. `extern "C"` nadaje funkcji C language linkage, zwykle upraszczając name mangling, ale nie czyni dowolnego typu C++ zgodnym z C. Przez granicę przekazuj typy o uzgodnionej reprezentacji, jawne długości i opaque handles.

~~~cpp
#include <cassert>

extern "C" int c_add(int left, int right) noexcept {
    return left + right;
}

class Calculator {
public:
    int add(int left, int right) const noexcept {
        return c_add(left, right);
    }
};

int main() {
    const Calculator calculator;
    assert(calculator.add(20, 22) == 42);
}
~~~

Wyjątek nie może bezpiecznie przekroczyć C ABI; wrapper łapie wszystko i zamienia na kod lub tagged result. Pamięć powinna być zwalniana przez tę samą bibliotekę/runtime, która ją przydzieliła. Nie przekazuj `std::string`, `std::vector`, referencji, klas z virtual ani layoutu zależnego od kompilatora jako stabilnego C ABI.

Opaque handle może być niekompletną strukturą C oraz parami `create/destroy`. Każda funkcja waliduje null, rozmiary i wersję. Callback wymaga userdata pointer, jasnej synchronizacji i zakazu wywołania po zniszczeniu kontekstu.

Moduły zmieniają model widoczności deklaracji, lecz ODR nadal obowiązuje. Module linkage i attachment decydują, czy encje należą do nazwanego modułu. Nie łącz losowo tej samej deklaracji przez header i moduł bez planu migracji. BMI nie jest przenośnym formatem dystrybucji między dowolnymi kompilatorami.

## Jak to działa krok po kroku

`extern "C"` w przykładzie nadaje funkcji C language linkage. Wrapper C++ wywołuje ją zwyczajnie, bez zmiany semantyki dodawania. Zakres argumentów nadal musi gwarantować reprezentowalny wynik w `int`; językowe powiązanie C nie legalizuje przepełnienia. Klient innego języka potrzebuje deklaracji o zgodnych typach oraz zgodnej konwencji wywołania na konkretnej platformie.

W stabilniejszym interfejsie oddziela się utworzenie uchwytu, operacje na nim i jego zniszczenie. Implementacja ukrywa pola struktury, a odbiorca przechowuje jedynie wskaźnik do typu niekompletnego. Funkcja tworząca oddaje własność, funkcja niszcząca ją odbiera, a pozostałe pożyczają uchwyt. Dzięki temu zmiana wewnętrznego `vector` lub mutexa nie wymaga od klienta znajomości nowego `sizeof` klasy.

## Pogłębienie mechanizmu

One Definition Rule kontroluje tożsamość definicji w programie. Zwykła funkcja o zewnętrznym linkage powinna mieć odpowiednią pojedynczą definicję. Dla inline functions, klas i szablonów istnieją warunkowe wyjątki pozwalające na wiele definicji, ale wymagają między innymi odpowiedniej zgodności tokenów i lookup. Makro zmieniające treść klasy w różnych jednostkach translacji może złamać ODR, choć każda jednostka osobno się kompiluje i linker nie zgłasza konfliktu.

`inline` nie znaczy „linker wybierze dowolną z różnych implementacji”. Jest zobowiązaniem, że wielokrotne definicje spełniają reguły języka. LTO może ujawnić naruszenia lub umożliwić optymalizacje wykorzystujące założenie ich braku. Flagi pakowania struktur, różne ustawienia biblioteki standardowej i makra konfiguracyjne mogą naruszyć zgodność równie skutecznie jak jawna zmiana kodu.

Named modules oddzielają eksport deklaracji od tekstowego włączania nagłówków. Import nie jest kopiowaniem tekstu i nie przenosi arbitralnie makr interfejsu tak jak `#include`. Global module fragment służy między innymi do dołączania tradycyjnych nagłówków przed deklaracją modułu. Deklaracje mają attachment i reachability; definicje dołączone do nazwanego modułu podlegają innym warunkom niż tradycyjne wielokrotne definicje nagłówkowe.

BMI lub IFC jest artefaktem konkretnego kompilatora i konfiguracji. Standard nie definiuje formatu wymiany takiego pliku ani formatu dynamicznej biblioteki. Moduł może zmniejszyć zależności tekstowe i poprawić izolację, lecz nie rozwiązuje automatycznie problemów ABI, cykli zależności czy synchronizacji etapów budowania. Dystrybucja źródłowego interfejsu modułu i dystrybucja gotowego binarium wymagają osobnych polityk kompatybilności.

Na granicy FFI `noexcept` nie tłumaczy wyjątku na kod błędu. Nieprzechwycony wyjątek z takiej funkcji prowadzi do `terminate`. Wrapper powinien złapać przewidywane błędy oraz pozostałe wyjątki i zbudować reprezentację zrozumiałą dla odbiorcy. Obie strony muszą również ustalić kodowanie tekstu, długości buforów, możliwość przechowywania callbacka i wątek, na którym wolno go wywołać.

## Drugi przykład

~~~cpp
#include <cassert>
#include <new>

struct engine { int value = 42; };
extern "C" {
int engine_create(engine** out) noexcept {
    if (!out) return 1;
    *out = nullptr;
    try { *out = new engine; return 0; }
    catch (...) { return 2; }
}
int engine_read(const engine* ptr, int* out) noexcept {
    if (!ptr || !out) return 1;
    *out = ptr->value;
    return 0;
}
void engine_destroy(engine* ptr) noexcept { delete ptr; }
}
int main() {
    engine* ptr = nullptr;
    assert(engine_create(&ptr) == 0);
    int value = 0;
    assert(engine_read(ptr, &value) == 0 && value == 42);
    engine_destroy(ptr);
}
~~~

Najpierw zerujemy parametr wyjściowy, więc po niepowodzeniu klient otrzymuje znany stan. Alokacja i zwolnienie są wykonywane przez tę samą implementację. W rzeczywistym nagłówku przeznaczonym dla C należałoby oddzielić deklarację niekompletnego `struct engine`, zastosować osłonę `__cplusplus` dla linkage i dostosować składnię deklaracji. Pokazany blok jest samowystarczalną jednostką C++ demonstrującą warstwę implementacji.

## Porównanie i decyzje

Dla biblioteki budowanej razem z aplikacją bogate typy C++ mogą być właściwym interfejsem. Dla pluginów różnych dostawców mały interfejs C z numerem wersji i opaque handles zwykle daje bardziej kontrolowaną granicę. Kosztem jest ręczna reprezentacja błędów i zasobów, którą warto ponownie opakować w RAII po stronie C++.

**Ćwiczenie.** Czy sprawdzenie `ptr != nullptr` w `engine_read` dowodzi poprawności uchwytu? **Odpowiedź:** nie; klient musi przekazać żywy uchwyt właściwego pochodzenia. Czy `extern "C" std::string name()` ustanawia stabilny interfejs C? Nie; linkage funkcji nie zmienia reprezentacji ani dostępności typu. Czy poprawne linkowanie dowodzi ODR? Nie, wiele naruszeń nie wymaga diagnostyki.

Źródła: [N4950: ODR](https://timsong-cpp.github.io/cppwp/n4950/basic.def.odr), [language linkage](https://timsong-cpp.github.io/cppwp/n4950/dcl.link) oraz [moduły](https://timsong-cpp.github.io/cppwp/n4950/module).

### Wersjonowanie kontraktu binarnego

Rozszerzalna struktura opcji często zawiera pole wersji lub rozmiaru oraz jawnie określone wartości domyślne. Biblioteka może wtedy rozpoznać starszego klienta i odczytać tylko pola obecne w jego strukturze. Wymaga to dokumentacji wyrównania, szerokości typów i odpowiedniej walidacji. Samo dopisanie pola na końcu nie gwarantuje bezpieczeństwa, jeśli funkcja bezwarunkowo odczytuje nowy pełny rozmiar ze starego bufora.

Wskaźnik zwrócony jako tekst może oznaczać pamięć klienta, pamięć biblioteki lub widok ważny tylko do następnego wywołania. Te modele potrzebują różnych zasad zwalniania. Najbardziej niebezpieczny interfejs pozostawia odbiorcy zgadywanie, czy użyć `free`, `delete[]` czy żadnej operacji. Para funkcji alokującej i zwalniającej lub zapis do bufora dostarczonego przez klienta upraszcza kontrakt.

Callback przekraczający granicę języka powinien przechwycić wyjątki jeszcze przed powrotem do obcego runtime. Jego `userdata` musi pozostać żywe do zakończenia wszystkich możliwych wywołań, również tych będących już w toku. Funkcja odrejestrowania powinna wyraźnie określać, czy czeka na aktywne callbacki; bez tego klient nie wie, kiedy bezpiecznie zniszczyć kontekst.

## Powiązane tematy

- [Moduły C++](../08_budowanie_i_organizacja/04_moduly_cpp.md)
- [Linkowanie i ODR](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
- [API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)

