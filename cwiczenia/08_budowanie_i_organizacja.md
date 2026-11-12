[← Mapa działu](../08_budowanie_i_organizacja/README.md) · [Spis treści](../README.md)

# Ćwiczenia: od źródeł do odtwarzalnego programu

Przy każdym zadaniu zaznacz, jaki etap posiada potrzebną informację: preprocesor, kompilator, linker czy system budowania. Udane linkowanie nie jest automatycznym dowodem spełnienia wszystkich reguł programu.

## 1. Dwie wersje tej samej funkcji inline

**Wejście:** nagłówek definiuje `inline int limit(){ return LIMIT; }`. Dwie jednostki translacji włączają go z `LIMIT` równym odpowiednio 10 i 20. Linkowanie się udaje. **Oddaj:** diagnozę ODR i naprawę konfiguracji. Kryterium: wynik nie zależy od wyboru definicji przez linker. **Wskazówka:** inline pozwala na wielokrotne definicje tylko pod określonymi warunkami.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Po preprocessingu definicje mają inne sekwencje tokenów, więc naruszają wymagania ODR. Diagnoza takiego naruszenia między jednostkami nie zawsze jest wymagana. Ustal jedną publiczną konfigurację dla wszystkich klientów albo reprezentuj różne polityki jako różne typy lub nazwane funkcje. Nie naprawiaj problemu przez liczenie na kolejność plików. [ODR](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md).

</details>

## 2. Archiwa statyczne i kolejność

**Wejście:** linker przegląda archiwa jednokrotnie od lewej do prawej. `main.o` potrzebuje funkcji z `libA.a`, a ta funkcji z `libB.a`. Polecenie podaje `main.o libB.a libA.a`. **Oddaj:** wyjaśnienie brakującego symbolu i poprawną kolejność. Uwzględnij cykl zależności jako osobny przypadek. **Wskazówka:** archiwum nie musi zostać włączone w całości.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Przy przeglądaniu B nie ma jeszcze zapotrzebowania ujawnianego dopiero przez A, więc odpowiedni obiekt B nie zostaje wybrany. Dla podanego modelu użyj `main.o libA.a libB.a`. Cykl może wymagać grupowania lub ponownego skanowania właściwego danemu linkerowi, a często wskazuje potrzebę podziału bibliotek. To zadanie dotyczy jawnie określonego modelu linkera. [Linkowanie](../08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md).

</details>

## 3. Ukryty przyjaciel i ADL

**Wejście:** `Token` w przestrzeni `api` definiuje przyjacielską funkcję `equal(Token,Token)` wewnątrz klasy, bez osobnej deklaracji na poziomie przestrzeni. **Oddaj:** ocenę `equal(a,b)` i `api::equal(a,b)` dla argumentów `Token`. Zaproponuj zmianę umożliwiającą kwalifikowane wywołanie. **Wskazówka:** ADL i zwykłe wyszukiwanie nazw nie są tym samym.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wywołanie niekwalifikowane może znaleźć ukrytego przyjaciela przez przestrzenie i klasy skojarzone z argumentami. Sama definicja przyjacielska nie udostępnia nazwy zwykłemu kwalifikowanemu wyszukiwaniu `api::equal`. Dodaj zgodną deklarację funkcji na poziomie przestrzeni, jeśli taki sposób wywołania jest częścią API. Nie przenoś jej do globalnej przestrzeni. [ADL](../08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md).

</details>

## 4. PUBLIC to obietnica dla klienta

**Wejście:** publiczny nagłówek biblioteki `engine` włącza nagłówek biblioteki `geometry`; wewnętrzny plik implementacji używa `logger`. Osobna biblioteka szablonowa nie ma kompilowanych źródeł. **Oddaj:** przypisanie wymagań użycia do PUBLIC, PRIVATE i INTERFACE. Kryterium: czysty klient otrzymuje potrzebne ścieżki bez ręcznego ich kopiowania. **Wskazówka:** opisuj zależności celu, nie globalne ustawienia katalogu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Wymagania `geometry` używane przez publiczny nagłówek muszą docierać do klientów `engine`, zwykle przez zależność PUBLIC. Implementacyjny `logger` jest PRIVATE. Wymagania biblioteki wyłącznie nagłówkowej ustaw przez cel INTERFACE. To opis widoczności wymagań; szczegóły linkowania prywatnych zależności archiwów statycznych dodatkowo obsługuje model celów CMake. [CMake](../08_budowanie_i_organizacja/05_cmake.md).

</details>

## 5. Ta sama nazwa zależności, inne binarium

**Wejście:** menedżer pakietów pobiera „najnowszą zgodną” bibliotekę, a dwóch autorów używa różnych kompilatorów i opcji ABI. Programy mają ten sam numer wersji projektu. **Oddaj:** manifest danych potrzebnych do odtworzenia oraz plan czystego budowania bez pobierania przypadkowych aktualizacji. **Wskazówka:** pin źródeł nie opisuje całej konfiguracji binarnej.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Utrwal wersje i rewizje zależności, źródła pakietów, profil kompilatora, bibliotekę standardową, architekturę, tryb budowania i istotne opcje. Korzystaj z lockfile lub baseline odpowiedniego menedżera. Oddziel katalogi budowania niezgodnych konfiguracji i weryfikuj manifest w CI. Nie mieszaj dowolnie binariów tylko dlatego, że udostępniają te same nagłówki. [Zależności](../08_budowanie_i_organizacja/06_conan_vcpkg_i_zaleznosci.md).

</details>

## 6. Moduł nie jest nagłówkiem z nową nazwą

**Wejście:** projekt zamienia wszystkie `#include` na `import`, zachowując dotychczasowe makra konfiguracyjne i ręczną kolejność kompilacji plików. **Oddaj:** trzy kwestie do rozwiązania przed migracją i mały pilotaż. Kryterium: czyste budowanie nie wymaga wcześniej pozostawionych artefaktów modułów. **Wskazówka:** kompilacja importera zależy od interfejsu modułu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Ustal obsługę modułów przez kompilator i system budowania, graf zależności interfejsów oraz granice makr i kompatybilności nagłówków. Pilotaż obejmuje jeden mały moduł i importera, budowane od zera. Artefakty pośrednie modułu są zależne od narzędzia i konfiguracji; nie traktuj ich jak przenośnej biblioteki binarnej. [Moduły](../08_budowanie_i_organizacja/04_moduly_cpp.md).

</details>
