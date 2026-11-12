[← Spis treści](../README.md)

# FFI C i stabilne ABI

ABI opisuje współpracę już skompilowanych modułów: symbole, wywołania, przekazywanie argumentów, reprezentację danych oraz odpowiedzialność za zasoby. Dwa projekty mogą poprawnie kompilować ten sam nagłówek, a mimo to nie współpracować binarnie po wymianie biblioteki. Stabilny interfejs wymaga jawnego zakresu zgodności: systemu, architektury, konwencji wywołań i wspieranych toolchainów. Nie istnieje jeden plik biblioteki działający jako ABI na wszystkich platformach.

`extern "C"` nadaje deklaracjom łączność językową C. Nie ustala uniwersalnego układu dowolnej klasy, nie wyrównuje wersji bibliotek standardowych i nie rozwiązuje własności pamięci. Reguły łączności i reprezentacji obiektów są oddzielnymi częściami języka. [N4950: §9.11 i §11.4](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4950.pdf). C ABI jest praktycznym punktem wspólnym dla wielu języków, ale nadal trzeba przyjąć ABI konkretnej platformy.

## Jak to działa krok po kroku

Na granicy publikuj proste dane i nieprzezroczyste uchwyty. Obiekt C++ może wewnątrz zawierać mutex, wektor i dziedziczenie; konsument zna tylko wskaźnik do niepełnego typu. Utworzenie i zniszczenie wykonuje moduł właściciela. Nie przekazuj przez publiczny interfejs `std::string`, wyjątków, iteratorów ani obiektów wymagających zgodnego runtime po obu stronach.

Pierwszy przykład to **trzy pliki jednego programu**. Nagłówek jest zgodny z C, implementacja jest C++23, a konsument jest C11. To statycznie zlinkowany test kontraktu FFI; ładowanie biblioteki dynamicznej, eksport symboli i opakowanie dystrybucyjne są poza przykładem. Funkcje nie zapewniają współbieżnego dostępu do tego samego uchwytu.

Plik `counter.h`:

~~~c
#ifndef COUNTER_H
#define COUNTER_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
#define COUNTER_NOEXCEPT noexcept
extern "C" {
#else
#define COUNTER_NOEXCEPT
#endif

typedef struct counter counter;
#define COUNTER_OK 0
#define COUNTER_INVALID 1
#define COUNTER_FAILURE 2

counter* counter_create(int64_t initial, char* error, size_t capacity) COUNTER_NOEXCEPT;
int32_t counter_add(counter* handle, int64_t delta, int64_t* result,
                    char* error, size_t capacity) COUNTER_NOEXCEPT;
void counter_destroy(counter* handle) COUNTER_NOEXCEPT;

#ifdef __cplusplus
}
#endif
#endif
~~~

Plik `counter.cpp`. Blok oznaczono `cpp,notest`, ponieważ wymaga nagłówka `counter.h` i połączenia z osobną jednostką klienta; weryfikujemy go jako projekt C11+C++23, a nie samodzielny program:

~~~cpp,notest
#include "counter.h"
#include <limits>
#include <new>

struct counter { int64_t value; };

static void message(char* out, size_t capacity, const char* text) noexcept {
    if (!out || capacity == 0) return;
    size_t i = 0;
    while (i + 1 < capacity && text[i] != '\0') {
        out[i] = text[i];
        ++i;
    }
    out[i] = '\0';
}

extern "C" counter* counter_create(int64_t initial, char* error,
                                    size_t capacity) noexcept {
    message(error, capacity, "");
    if (initial < 0) { message(error, capacity, "negative initial"); return nullptr; }
    try { return new counter{initial}; }
    catch (...) { message(error, capacity, "allocation failed"); return nullptr; }
}

extern "C" int32_t counter_add(counter* handle, int64_t delta, int64_t* result,
                               char* error, size_t capacity) noexcept {
    message(error, capacity, "");
    if (!handle || !result || delta < 0) {
        message(error, capacity, "invalid argument");
        return COUNTER_INVALID;
    }
    if (delta > std::numeric_limits<int64_t>::max() - handle->value) {
        message(error, capacity, "counter overflow");
        return COUNTER_FAILURE;
    }
    handle->value += delta;
    *result = handle->value;
    return COUNTER_OK;
}

extern "C" void counter_destroy(counter* handle) noexcept { delete handle; }
~~~

Plik `client.c`:

~~~c
#include "counter.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>

int main(void) {
    char error[64];
    int64_t result = -1;
    counter* handle = counter_create(10, error, sizeof error);
    assert(handle != NULL);
    int32_t status = counter_add(handle, 7, &result, error, sizeof error);
    assert(status == COUNTER_OK && result == 17);
    printf("result=%" PRId64 "\n", result);
    counter_destroy(handle);
    return 0;
}
~~~

Bufor błędu należy do klienta. Jeśli jest niepusty i ma dodatnią pojemność, funkcja zapisuje zakończenie NUL, ewentualnie skracając komunikat. Wskaźnik NULL lub pojemność zero wyłączają opis tekstowy. Kod statusu nadal ma znaczenie; tekst służy diagnostyce. Pamięć musi być zapisywalna przez całe wywołanie, ale biblioteka nie przechowuje wskaźnika po powrocie. Nie zwracamy adresu lokalnego stringa ani komunikatu zależnego od czasu życia wyjątku.

## Pogłębienie mechanizmu

`noexcept` nie przechwytuje wyjątku: ucieczka wyjątku z takiej funkcji kończy proces. Każda ścieżka mogąca zgłaszać potrzebuje tłumaczenia na status wewnątrz funkcji granicznej. W przykładzie taką ścieżką jest `new`; dodawanie po walidacji i kopiowanie opisu są niezgłaszające. Gdy implementacja zyska parser lub kontener, trzeba rozszerzyć osłonę. Obsługa błędu sama nie powinna alokować.

Alokator jest częścią kontraktu. Nie wolno zakładać, że klient może wykonać `delete` na uchwycie albo `free` na buforze pochodzącym z biblioteki. Różne kopie CRT mogą mieć różne zarządzanie stertą; Microsoft opisuje wynikające z tego błędy przy przekraczaniu granicy DLL. [Dokumentacja CRT](https://learn.microsoft.com/cpp/c-runtime-library/potential-errors-passing-crt-objects-across-dll-boundaries). Para create/destroy lub osobna funkcja release kieruje zwalnianie do właściwego modułu.

Liczby o ustalonej szerokości ograniczają niejednoznaczność, lecz nie rozwiązują wyrównania, endianowości ani rozmiaru wskaźników. `size_t` jest wygodne wewnątrz procesu o jednym ABI; nie traktuj takiej struktury jako formatu pliku lub protokołu sieciowego. Serializacja wymaga osobnego kodowania. Podobnie C enum nie musi być dobrym zamiennikiem jawnego `int32_t` w długowiecznym interfejsie binarnym.

## Drugi przykład

Rozwijający się interfejs potrzebuje negocjacji wersji i rozmiaru. Poniższy wariant dodaje nową funkcję, zachowując stare deklaracje. Struktura ma stały prefiks `size, version`, a nowe pola można dopisywać na końcu dopiero po określeniu zachowania starszych implementacji. Samo pole size nie pozwala odczytywać pamięci, której klient nie przekazał.

Do `counter.h`, **wewnątrz bloku łączności C**, dodaj:

~~~c
typedef struct counter_options {
    uint32_t size;
    uint32_t version;
    int64_t initial;
    uint32_t flags;
} counter_options;

counter* counter_create_options(const counter_options* options,
                               char* error, size_t capacity) COUNTER_NOEXCEPT;
~~~

Do `counter.cpp` dodaj poniższą definicję. Obowiązkowy prefiks zawiera `initial`; `flags` jest opcjonalne i przy braku pola przyjmuje zero. Dla uproszczenia wszelkie niezerowe flagi są nieobsługiwane. Obiekt wskazywany przez options musi faktycznie mieć deklarowaną wielkość i odpowiednie wyrównanie.

Poniższy blok `cpp,notest` jest rozszerzeniem wcześniejszej jednostki `counter.cpp`: wymaga jej funkcji `message`, definicji uchwytu i uzupełnionego nagłówka. Weryfikujemy go po połączeniu z `client_options.c`.

~~~cpp,notest
extern "C" counter* counter_create_options(const counter_options* options,
                                           char* error, size_t capacity) noexcept {
    message(error, capacity, "");
    constexpr size_t required = offsetof(counter_options, initial) + sizeof(int64_t);
    if (!options || options->size < required || options->version != 1) {
        message(error, capacity, "unsupported options prefix");
        return nullptr;
    }
    uint32_t flags = 0;
    constexpr size_t flags_end = offsetof(counter_options, flags) + sizeof(uint32_t);
    if (options->size >= flags_end) flags = options->flags;
    if (flags != 0) {
        message(error, capacity, "unsupported flags");
        return nullptr;
    }
    return counter_create(options->initial, error, capacity);
}
~~~

Drugi program konsumenta, `client_options.c`, zastępuje poprzedni plik z main:

~~~c
#include "counter.h"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>

int main(void) {
    char error[64];
    counter_options options = {0};
    options.size = (uint32_t)(offsetof(counter_options, initial) + sizeof(int64_t));
    options.version = 1;
    options.initial = 30;
    options.flags = 99; /* Poza deklarowanym prefiksem: nie należy tego czytać. */
    counter* handle = counter_create_options(&options, error, sizeof error);
    assert(handle != NULL);
    int64_t result = 0;
    int32_t status = counter_add(handle, 2, &result, error, sizeof error);
    assert(status == COUNTER_OK && result == 32);
    counter_destroy(handle);
    options.size = (uint32_t)sizeof options;
    handle = counter_create_options(&options, error, sizeof error);
    assert(handle == NULL); /* Teraz flags jest obecne i nieobsługiwane. */
    printf("result=%" PRId64 ", rejected=%s\n", result, error);
    return 0;
}
~~~

Test ma pełny obiekt w pamięci, ale celowo deklaruje krótszy prefiks. Nie dowodzi zgodności ze wszystkimi historycznymi klientami. Tę sprawdza się, kompilując rzeczywisty stary konsument i łącząc go z nową biblioteką. Odrzucenie nieznanej wersji jest świadomą polityką; ignorowanie nowych pól ma sens tylko wtedy, gdy ich pominięcie zachowuje znaczenie operacji.

## Porównanie i decyzje

Dla modułów budowanych i wdrażanych razem wewnętrzny interfejs C++ jest często najprostszy. C ABI opłaca się przy pluginach, niezależnych dostawcach i klientach w innych językach. Kosztem jest ręczny kontrakt statusów, wskaźników i czasu życia. Opakowanie RAII po stronie C++ może ukryć tę mechanikę bez zmieniania publicznego ABI.

Plugin musi pozostawać załadowany do zniszczenia jego uchwytów, zakończenia wątków i wyrejestrowania callbacków. Wskaźnik do funkcji nie utrzymuje biblioteki przy życiu. Dokumentuj też wątki wywołań callbacku i możliwość ponownego wejścia; łączność C nie zapewnia synchronizacji. Osobne kontrakty własności i współbieżności są równie ważne jak zgodność sygnatur.

Rozmiar struktury wymaga ostrożności przy paddingu. Dopisane pole może zająć miejsce, które w starszej wersji było końcowym wyrównaniem, a `sizeof` starego typu już obejmowało te bajty. Samo porównanie rozmiaru nie rozpozna wtedy obecności nowego pola. Stabilny projekt może używać jawnych długości zdefiniowanych prefiksów, wersji obejmującej taki dodatek albo zarezerwowanych pól o opisanej inicjalizacji. W przykładzie krótki prefiks świadomie kończy się po initial.

Weryfikacja size jest kontrolą kontraktu, nie ochroną przed dowolnym uszkodzonym wskaźnikiem. Biblioteka nie zna rzeczywistej wielkości obiektu na podstawie samego adresu. Klient musi przekazać poprawnie wyrównaną, dostępną pamięć, a deklarowany rozmiar musi odpowiadać udostępnionemu obszarowi. Ta sama zasada dotyczy pojemności bufora błędu; podanie dużej liczby nie powiększa alokacji.

Do testów zgodności dodaj klienta kompilowanego rzeczywistym kompilatorem C i przynajmniej jednym docelowym językiem FFI. Sprawdzaj wartości graniczne, skracanie komunikatu, NULL, złą wersję i rozmiar kończący się przed każdym polem. Test wymiany biblioteki bez rekompilacji klienta bada inną własność niż wspólne przebudowanie wszystkich plików. Oba są potrzebne przed obietnicą zgodności binarnej między wydaniami.

## Ćwiczenia

1. Implementacja zwraca `exception.what()` w polu błędu, a potem kończy blok catch. Czy klient ma trwały komunikat?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie ma takiej gwarancji po zniszczeniu obiektu wyjątku. Skopiuj ograniczony opis do bufora klienta podczas obsługi błędu albo zwróć osobny obiekt błędu z jawną funkcją zwalniania i kontraktem czasu życia.

</details>

2. Nowe pole dopisano na końcu struktury i zawsze odczytuje się je przed sprawdzeniem size. Czy to zgodne rozszerzenie?

<details>
<summary>Rozwiązanie z uzasadnieniem</summary>

Nie. Starszy klient może przekazać krótszy obiekt. Najpierw sprawdź, czy zadeklarowany rozmiar obejmuje całe pole, dopiero potem je odczytaj. Dla nieobecnego pola zdefiniuj wartość domyślną albo odrzuć żądanie.

</details>

## Powiązane tematy

- [ABI, name mangling i wyjątki](../17_runtime_kompilator_i_abi/04_abi_name_mangling_i_wyjatki.md)
- [Biblioteki dynamiczne i pluginy](03_biblioteki_dynamiczne_i_pluginy.md)
- [Wersjonowanie pluginów i capabilities](04_wersjonowanie_pluginow_i_capabilities.md)
