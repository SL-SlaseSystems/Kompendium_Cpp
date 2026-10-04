[← Główny spis treści](../README.md)

# 08. Budowanie i organizacja

Program C++ powstaje z wielu translation units, a granice między nimi wpływają na czas kompilacji, ODR, widoczność symboli i możliwość ponownego użycia biblioteki. Dział łączy reguły języka z praktyką CMake i zarządzania zależnościami.

## Wymagania wstępne

Wymagana jest znajomość pierwszego procesu budowania, deklaracji, definicji, klas, templates i obsługi błędów linkera.

## Efekty uczenia się

- rozdzielasz deklarację, definicję i zależność tekstową;
- diagnozujesz naruszenia ODR i brakujące symbole;
- projektujesz przestrzenie nazw oraz kontrolujesz ADL;
- rozumiesz cele i ograniczenia modułów C++;
- budujesz target-based projekt CMake;
- rozróżniasz rolę CMake, Conan i vcpkg.

## Kolejność rozdziałów

1. [Translation units, nagłówki i include](01_translation_units_headers_i_include.md)
2. [Linkowanie, ODR i inline](02_linkowanie_odr_i_inline.md)
3. [Namespaces, visibility i ADL](03_namespaces_visibility_i_adl.md)
4. [Moduły C++](04_moduly_cpp.md)
5. [CMake](05_cmake.md)
6. [Conan, vcpkg i zależności](06_conan_vcpkg_i_zaleznosci.md)
7. [Zestaw ćwiczeń](ZESTAW-CWICZEN.md)

## Jak pracować

Obserwuj polecenia generowane przez system budowania. Dla każdego targetu określ źródła, publiczne nagłówki, wymagania użycia i zależności prywatne. Błędy ODR reprodukuj na minimalnym projekcie co najmniej dwóch translation units.

## Pułapki

- globalne `include_directories` i `link_libraries` zamiast właściwości targetu;
- definicje nie-`inline` w nagłówku;
- include zależny od przypadkowej kolejności innych include;
- ukrywanie cyklicznych zależności przez jeden wielki target;
- mylenie generatora buildsystemu z menedżerem pakietów.

## Samoocena

Potrafisz utworzyć bibliotekę i program, poprawnie propagować wymagania użycia, wyjaśnić błąd linkera na poziomie symboli oraz zbudować projekt poza katalogiem źródeł bez ręcznie wpisanych ścieżek maszyny autora.

## Co dalej

Przejdź do [testowania i jakości](../09_testowanie_i_jakosc/README.md), aby budowanie stało się powtarzalną bramką jakości.
