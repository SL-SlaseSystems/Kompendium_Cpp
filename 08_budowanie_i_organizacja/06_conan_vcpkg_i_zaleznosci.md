[← Spis treści](../README.md)

# Conan, vcpkg i zależności

C++ nie ma jednego standardowego menedżera pakietów. Conan i vcpkg są popularnymi narzędziami ekosystemu, ale mają inne modele wersji, binariów, rejestrów i integracji. CMake potrafi odnaleźć lub budować zależności, lecz sam nie rozwiązuje wszystkich problemów zarządzania wersjami i wariantami ABI.

~~~text
# Przykładowa intencja w CMake po dostarczeniu pakietu przez menedżer:
find_package(fmt CONFIG REQUIRED)
target_link_libraries(app PRIVATE fmt::fmt)
~~~

Imported target `fmt::fmt` powinien nieść include paths, wymagane definicje i właściwości linkowania. To bezpieczniejsze niż ręczne składanie ścieżek do plików. Dokładne polecenie instalacji i nazwa targetu zależą od pakietu oraz wybranego menedżera.

Zależność binarna musi pasować pod względem architektury, kompilatora, runtime library, trybu debug/release, opcji ABI i często wersji biblioteki standardowej. Sam zgodny numer semantyczny nie gwarantuje zgodności binarnej. Reproducible build wymaga zablokowania wersji receptur, źródeł, opcji i toolchainu.

Biblioteka header-only usuwa krok linkowania, ale nie jest pozbawiona kosztów: może zwiększać czas kompilacji, liczbę instancjacji i ryzyko ODR przy niespójnych makrach konfiguracyjnych. FetchContent upraszcza małe projekty, lecz pobieranie podczas konfiguracji utrudnia środowiska hermetyczne i audyt supply chain.

## Jak to działa krok po kroku

1. **Zapisz kontrakt.** Określ, jakie wartości i typy wchodzą do mechanizmu „Conan, vcpkg i zależności”, jaki stan jest poprawny oraz co wywołujący może obserwować po sukcesie i porażce.
2. **Prześledź fazę języka.** Rozpisz odnalezienie deklaracji, przetworzenie zależności, utworzenie plików obiektowych, rozwiązanie symboli i złożenie końcowego artefaktu. Pozwala to wskazać, czy decyzja zapada w preprocessing, podczas kompilacji, linkowania czy dopiero w runtime.
3. **Ustal granice odpowiedzialności.** Dla tego zagadnienia trzeba oddziel zależność źródłową, wymaganie użycia biblioteki, szczegół ABI oraz ustawienie prywatne konkretnego targetu. Szczególnie ważne są ownership, lifetime i miejsce, w którym obowiązuje inwariant.
4. **Zbierz dowód.** Sprawdź graf targetów, pełne komendy kompilacji, tablicę symboli, kolejność linkowania i zawartość pakietu. Jeden poprawny output nie wystarcza, jeśli program mógł wcześniej wykonać undefined behavior albo zależy od niejawnej konfiguracji.

Model dla tej części kompendium jest następujący: Projekt C++ jest grafem jednostek translacji, modułów, bibliotek i artefaktów. Kompilator analizuje jednostki osobno, linker łączy definicje, a system budowania musi odtworzyć zależności i opcje w sposób powtarzalny. W praktyce warto narysować małą oś czasu obiektu lub artefaktu: utworzenie, wszystkie miejsca przekazania, moment ostatniego legalnego użycia i zakończenie. Taki zapis często ujawnia błąd wcześniej niż analiza samej składni.

## Pogłębienie mechanizmu

- Menedżer zależności rozwiązuje wersje, warianty ABI i źródła artefaktów, lecz system budowania nadal definiuje targety projektu. Lockfile lub manifest musi być częścią reprodukcji wraz z profilem kompilatora.

Pojęcia wymienione wyżej współdziałają, lecz nie powinny być zlewane w jedną regułę. Dla „Conan, vcpkg i zależności” osobno sprawdź poprawność programu wobec standardu, wymagania używanego API oraz koszt konkretnej implementacji. Dzięki temu optymalizacja nie ukryje naruszenia kontraktu, a szczegół jednego kompilatora nie zostanie przedstawiony jako przenośna gwarancja C++.

## Drugi przykład

Poniższy scenariusz jest przykładem diagnostycznym. Uzupełnia kompilowalny kod z początku rozdziału o przypadek graniczny i sposób weryfikacji założenia.

~~~text
Temat: Conan, vcpkg i zależności
Przypadek podstawowy: minimalne poprawne dane i jeden właściciel zasobu
Zmiana kontrolna: pusty zakres, przeniesiony obiekt, wyjątek albo konkurencyjny dostęp
Pytanie: który kontrakt przestaje obowiązywać i w którym momencie?
Dowód: diagnostyka kompilatora + sanitizer/test + stan przed i po operacji
Decyzja: wybór prostszego wariantu, który jawnie koduje ownership i lifetime
~~~

Najpierw uruchom przypadek podstawowy, potem zmień dokładnie jeden warunek. Jeśli problem dotyczy typów, zachowaj te same dane; jeśli lifetime, zachowaj typy i przesuń moment zniszczenia. Przy współbieżności dodaj prawdziwą synchronizację zamiast opóźnień czasowych. Taki eksperyment rozdziela przyczynę od przypadkowej zmiany layoutu, optymalizacji lub harmonogramu.

## Porównanie i decyzje

Wybierając rozwiązanie dla „Conan, vcpkg i zależności”, oceniaj hermetyczność, szybkość przebudowy, przenośność konfiguracji, kontrola publicznych zależności i zgodność ABI. Wariant bardziej ogólny nie jest automatycznie lepszy: szablon może wydłużyć kompilację, polimorfizm dynamiczny może utrudnić value semantics, a współdzielona własność może ukryć cykl. Preferuj najmniejszy interfejs, który wyraża wymagany kontrakt i uniemożliwia typowe błędne stany.

Przed zatwierdzeniem API odpowiedz: kto posiada zasób, jak długo obowiązuje każdy widok, co dzieje się przy częściowym niepowodzeniu i czy zachowanie zależy od ABI lub wersji standardu? Następnie sprawdź wariant prostszy — wartość zamiast wskaźnika, RAII zamiast ręcznego cleanup, algorytm standardowy zamiast pętli albo mutex zamiast lock-free. Bardziej złożony mechanizm jest uzasadniony dopiero wtedy, gdy wymaganie lub pomiar odrzuca prostsze rozwiązanie.

## Dobre praktyki

Wybierz jeden główny model zależności dla projektu. Utrzymuj lockfile lub manifest, weryfikuj sumy i pochodzenie artefaktów, skanuj licencje oraz podatności. Publiczna biblioteka powinna minimalizować zależności widoczne w interfejsie, bo stają się częścią wymagań klientów.

## Powiązane tematy

- [CMake](05_cmake.md)
- [Projektowanie API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
- [Testowanie](../09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)

