[← Spis treści](README.md)

# Ścieżka do świadomego programowania w C++

Ta trasa jest przeznaczona przede wszystkim dla osoby, która już pisze w C++. Nie musisz czytać całego kompendium od początku. Zacznij od [diagnozy](test_diagnostyczny.md), znajdź błędne założenia i przechodź dalej dopiero wtedy, gdy umiesz uzasadnić rozwiązanie. Znajomość nazw mechanizmów jest początkiem; celem jest samodzielne projektowanie i diagnozowanie programów.

## Jak pracować nad jednym tematem

1. **Przewidź.** Przed kompilacją zapisz typy, właścicieli zasobów, czas życia i dozwolone wyniki. Jeśli kod jest niepoprawny, nazwij rodzaj błędu: ill-formed, naruszenie kontraktu, UB albo błąd logiki.
2. **Uzasadnij.** Wskaż regułę, z której wynika odpowiedź. „U mnie działa” jest obserwacją konkretnego uruchomienia. Nie dowodzi poprawności językowej.
3. **Sprawdź.** Uruchom poprawny wariant, test graniczny oraz diagnostykę adekwatną do hipotezy. Programu z UB nie uruchamiaj w oczekiwaniu na jeden „właściwy wynik”. W izolowanym eksperymencie diagnostycznym traktuj wykrycie jako demonstrację narzędzia.
4. **Przenieś.** Zmień jeden warunek: typ na move-only, zakres na pusty, wartość na graniczną, właściciela na tymczasowy albo liczbę wątków. Sprawdź, czy uzasadnienie nadal działa.
5. **Wyjaśnij.** Napisz krótką notatkę: kontrakt, mechanizm, koszt, pułapka i alternatywa. Powtórz temat po kilku kolejnych sesjach, bez zaglądania do rozwiązania.

Prowadź dziennik błędnych przewidywań. Wpis „uznałem, że `std::move` zawsze przenosi; parametr był const, więc użyto kopiowania” daje więcej niż lista przeczytanych stron. Rejestruj wersję standardu i toolchainu.

## Wybór punktu startowego

| Wynik diagnozy | Punkt wejścia | Dowód gotowości do kolejnego etapu |
|---|---|---|
| Mylisz inicjalizację, dedukcję, lifetime | Etapy 1–2 | Umiesz naprawić wiszący widok i uzasadnić wybrany typ zwrotu |
| Fundamenty są pewne, ale API trudno testować | Etapy 3–4 | Tworzysz typ z niezmiennikiem i testujesz go jako konsument |
| Piszesz szablony, lecz diagnostyka zaskakuje | Etap 4 i dział zaawansowany | Oddzielasz dopasowanie składniowe od wymagań semantycznych |
| Kod działa, ale nie umiesz wykazać poprawności wątków | Etapy 6–7 | Rysujesz happens-before i opisujesz zakończenie wszystkich oczekiwań |
| Głównym problemem jest skala projektu i wydajność | Etap 8 | Odtwarzasz pomiar, śledzisz symbole i oceniasz kompromisy ABI |

Diagnoza pomaga wybrać materiał. Nie jest certyfikacją poziomu zawodowego ani dowodem, że umiesz utrzymywać dowolny system.

## Etap 1. Model języka zamiast intuicji z innych języków

Czytaj [podstawy](02_podstawy_jezyka/README.md), szczególnie nowe rozdziały o [inicjalizacji](02_podstawy_jezyka/08_inicjalizacja_i_initializer_list.md), [sequencing](02_podstawy_jezyka/09_kolejnosc_ewaluacji_i_sequencing.md) i [arytmetyce](02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md). Powiąż je z [UB i modelem maszyny](zaawansowane/01_undefined_behavior_i_model_maszyny.md).

**Praktyka:** rozwiąż zadania działu 02 i napisz własną tabelę: które konwersje są dopuszczalne, które tracą informację i które nie kompilują się w inicjalizacji listowej. Zbuduj parser z [laboratorium](praktyka/README.md), zanim zajrzysz do rozwiązania.

**Zaliczenie:** odróżniasz priorytet operatorów od kolejności ewaluacji, umiesz zabezpieczyć dodawanie przed signed overflow i rozumiesz, dlaczego rzutowanie wyniku może przyjść za późno.

## Etap 2. Ownership, lifetime i semantyka wartości

Przejdź [czas życia](03_pamiec_i_czas_zycia/README.md), a potem [zwracanie wartości i elision](03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md). Dopiero wówczas sięgnij po [aliasing i provenance](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md) oraz [value categories](zaawansowane/05_value_categories_i_perfect_forwarding.md).

**Praktyka:** przeanalizuj API zwracające `string`, `string_view`, `const string&` i `optional<string>`. Dla każdego podpisu nazwij właściciela i możliwe unieważnienie. Zapisz diagram czasu życia trzech obiektów i dwóch widoków. Przeprojektuj jeden interfejs tak, żeby błąd był trudniejszy do zapisania.

**Zaliczenie:** umiesz wyjaśnić utratę NRVO przez `return std::move(local)`, odróżniasz alias od właściciela, nie zakładasz pustego stanu każdego obiektu po move.

## Etap 3. Typ, który gwarantuje sens danych

Czytaj [klasy](04_klasy_i_model_obiektowy/README.md), [silne typy i porównania](04_klasy_i_model_obiektowy/07_silne_typy_porownania_i_hash.md) oraz [gwarancje wyjątków](07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md). Łącz reprezentację, niezmiennik, dozwolone operacje i obsługę błędów.

**Praktyka:** laboratorium `Money`. Dodaj osobny typ ilości i jawnie zdecyduj o zaokrąglaniu przy mnożeniu. Nie zaczynaj od przeciążania wszystkich operatorów. Najpierw ustal, które działania mają sens, kiedy zawodzą i czy błąd zostawia stan bez zmian.

**Zaliczenie:** błędna jednostka zostaje odrzucona podczas kompilacji, a niedozwolona wartość podczas walidacji. Umiesz ocenić równoważność kluczy, kontrakt hash i koszt obranej reprezentacji.

## Etap 4. Generyczność jako projektowanie kontraktów

Przejdź [szablony](05_szablony_i_generycznosc/README.md) i [interfejsy generyczne](05_szablony_i_generycznosc/07_projektowanie_interfejsow_generycznych.md). Pogłębiaj [lookup](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md) oraz [normalizację ograniczeń](zaawansowane/08_concepts_normalization_i_subsumption.md), gdy rozumiesz już konkretny problem API.

**Praktyka:** napisz mały algorytm z wymaganiami wobec iteratora, wartości i operacji. Użyj dwóch rzeczywistych typów, w tym move-only, i jednego typu, który ma zostać odrzucony. Dodaj komparator spełniający składnię, ale łamiący semantykę, i wyjaśnij granice diagnostyki kompilatora.

**Zaliczenie:** potrafisz uzasadnić `T`, `T&`, `const T&` i `T&&` w podpisie. Nie używasz perfect forwarding jako automatycznej optymalizacji każdego parametru.

## Etap 5. Biblioteka i granice reprezentacji

Czytaj [kontenery, algorytmy i ranges](06_biblioteka_standardowa/README.md), [Unicode i parsowanie](06_biblioteka_standardowa/08_unicode_utf8_i_parsowanie.md) oraz [I/O](11_io_i_system/README.md).

**Praktyka:** przetwarzaj dane najpierw prostą pętlą, następnie algorytmem i pipeline ranges. Porównuj własność danych, liczbę przejść, alokacje, invalidację i czytelność. Zdefiniuj, co oznacza „długość tekstu” w danym wymaganiu.

**Zaliczenie:** umiesz dobrać kontener na podstawie operacji i stabilności uchwytów. Rozpoznajesz, kiedy leniwy widok przechowuje referencję do nieistniejącego obiektu albo do stanu lambdy.

## Etap 6. Dowodzenie jakości i obsługi awarii

Przejdź [błędy i kontrakty](07_bledy_i_kontrakty/README.md) oraz [testowanie](09_testowanie_i_jakosc/README.md). Wróć do każdego projektu i dodaj test błędu, który faktycznie obala wcześniejsze założenie.

**Praktyka:** uruchom laboratoria w Debug i Release. Wprowadź kontrolowaną regresję, np. usuń kontrolę końca parsowania. Sprawdź, czy test zawodzi. Usuń regresję. Przygotuj reprodukcję błędu czasu życia i osobno demonstrację ograniczenia sanitizera.

**Zaliczenie:** rozróżniasz sukces kompilacji, test przykładu, test kontraktu i brak wykrytego problemu. Potrafisz wskazać, czego wynik testów jeszcze nie dowodzi.

## Etap 7. Współbieżność wraz z zakończeniem pracy

Czytaj [współbieżność](10_wspolbieznosc/README.md) oraz [kolejkę i backpressure](10_wspolbieznosc/06_kolejka_backpressure_i_zamykanie.md). Najpierw poprawny projekt z mutexem. [Lock-free i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md) wymagają dodatkowych argumentów, których sam atomik nie zapewnia.

**Praktyka:** laboratorium `BoundedQueue`. Zapisz stany: otwarta/pusta, otwarta/pełna, zamknięta/z danymi, zamknięta/pusta. Dla każdego opisz odpowiedź producenta i konsumenta. Wskaż punkty, w których operacja logicznie dochodzi do skutku, i uzasadnij budzenie obu stron przy zamknięciu.

**Zaliczenie:** potrafisz opisać happens-before dla udostępnianych danych. Każde oczekiwanie ma warunek zakończenia, a każdy wątek dołącza przed zniszczeniem używanych zasobów.

## Etap 8. Toolchain, ABI i wydajność

Połącz [budowanie](08_budowanie_i_organizacja/README.md), [API i wydajność](13_wzorce_api_i_wydajnosc/README.md) oraz eksperckie [ABI](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md), [ODR i FFI](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md) i [optymalizację](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md).

**Praktyka:** wydziel bibliotekę z laboratorium, zainstaluj ją do katalogu tymczasowego i zbuduj niezależnego konsumenta. Zmierz realistyczny workload. Raportuj wersję kompilatora, flagi, dane, rozrzut pomiarów i koszt pamięci. Dopiero potem zmień reprezentację.

**Zaliczenie:** umiesz wyjaśnić, dlaczego zgodność kodu źródłowego nie dowodzi zgodności ABI. Decyzję o optymalizacji uzasadniasz profilem i zmianą wyniku użytkowego.

## Projekt końcowy: indeksator danych z ograniczonymi zasobami

Zbuduj narzędzie CLI, które czyta rekordy z plików, waliduje dane, tworzy indeks i raportuje błędy. Najpierw wersja sekwencyjna, potem ograniczona kolejka zadań. Ustal limit długości rekordu, liczbę buforowanych zadań, zasady błędów, kolejność wyników i zachowanie przy przerwaniu pracy. Biblioteka standardowa C++23 nie dostarcza kompletnego frameworka sieciowego ani pełnej obsługi Unicode; dobór takich bibliotek jest osobną decyzją.

Oddaj kod, instrukcję budowania, testy graniczne, opis własności i czasu życia, strategię zakończenia oraz jeden pomiar wskazujący faktyczne wąskie gardło. Recenzent powinien móc sprawdzić projekt z samej dokumentacji. Lista użytych nowoczesnych funkcji nie jest kryterium zaliczenia.

## Dalsze pogłębianie

Wybierz [specjalizację](dalsza_nauka.md) dopiero po rozpoznaniu luk wspólnych dla wszystkich dziedzin. [150 mechanizmów](150-zaawansowanych-mechanizmow-cpp.md) traktuj jako indeks do powtórek i poszukiwań, a [dział zaawansowany](zaawansowane/README.md) jako materiał wymagający własnych eksperymentów. C++26 poznawaj przez [oddzielnie oznaczony rozdział](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md); sam nowy numer standardu nie zastępuje opanowania modeli C++23.

## Jak przejść z tej trasy do działów 14–30

| Cel | Kolejność i rezultat |
|---|---|
| Dostarczanie biblioteki | [Warsztat](14_warsztat_profesjonalisty/README.md), [pakiety](16_biblioteki_pakiety_i_dystrybucja/README.md), [runtime i ABI](17_runtime_kompilator_i_abi/README.md), [FFI](28_wieloplatformowosc_ffi_i_pluginy/README.md): niezależny konsument buduje się z zainstalowanego pakietu |
| Kod odporny na błędy | [Bezpieczeństwo](15_bezpieczny_cpp/README.md), [diagnoza](19_debugowanie_i_utrzymanie/README.md), [testy systemowe](20_testowanie_systemowe/README.md): kontrolowana awaria nie narusza zadeklarowanego niezmiennika |
| Wydajna aplikacja | [Pomiary](18_wydajnosc_i_optymalizacja/README.md), [architektura](23_architektura_aplikacji_produkcyjnych/README.md), [obserwowalność](27_obserwowalnosc_i_monitoring/README.md): pomiar uzasadnia zmianę reprezentacji albo współbieżności |
| Usługa z trwałością | [Sieć](21_sieci_protokoly_i_api/README.md), [baza](22_bazy_danych_i_trwalosc/README.md), [messaging](24_messaging_i_systemy_rozproszone/README.md): projekt ma limity, kontrakt ponawiania i test skutku częściowego |
| Wydanie i utrzymanie | [Kontenery](25_kontenery_i_produkcja/README.md), [CI i release](26_ci_cd_i_release_engineering/README.md), [supply chain](29_bezpieczenstwo_supply_chain/README.md): weryfikowalny artefakt ma wersję, pochodzenie i plan powrotu |
| Portfolio | [Projekty](30_projekty_premium/README.md) i [mapa propozycji](Projekty.md): jedna ukończona implementacja z testami, ograniczeniami i odtwarzalnym demo |

Nie przechodź przez wszystkie narzędzia tylko dlatego, że znajdują się w spisie treści. Wybierz projekt i wracaj do reguł języka, gdy nie umiesz uzasadnić lifetime, kontraktu błędu albo synchronizacji. Przykład polityki retry nie jest gotowym klientem HTTP, a ćwiczenie SQL nie zastępuje testu na wybranym silniku bazy.
