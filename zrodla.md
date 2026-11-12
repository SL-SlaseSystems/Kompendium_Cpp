[← Spis treści](README.md)

# Źródła

Kompendium opiera się przede wszystkim na tekstach normatywnych i materiałach organizacji rozwijających język. Dokumentacja kompilatora jest źródłem prawdy o jego flagach oraz poziomie implementacji. Strony referencyjne są wygodnym indeksem, ale nie zastępują standardu.

## Standard i WG21

- [The Standard — Standard C++](https://isocpp.org/std/the-standard) — informacja, że bieżącą opublikowaną normą jest C++23, formalnie ISO/IEC 14882:2024.
- [WG21](https://www.open-std.org/jtc1/sc22/wg21/) — strona grupy standaryzacyjnej, working drafts, projekty i listy zagadnień.
- [WG21 papers](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/) — dokumenty propozycji, raporty redaktorów i mailingi.
- [N4950 — stabilny draft C++23 w HTML](https://timsong-cpp.github.io/cppwp/n4950/) — punkt odniesienia dla bazowych reguł tego kompendium; publiczny draft nie jest oficjalną publikacją ISO.
- [ISO/IEC 14882:2024](https://www.iso.org/standard/83626.html) — oficjalna informacja o opublikowanym standardzie C++23; sprawdzono 2026-11-12. Katalog nadal oznacza tę edycję jako opublikowaną, a następną jako draft.
- [WG21 P3850R0](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p3850r0.pdf) — dokument z 2026 roku, którego wprowadzenie opisuje zakończenie prac komitetu nad C++26 w Croydon w marcu 2026. Zakończenie prac, publikacja ISO i wdrożenie przez toolchainy to osobne etapy; dokument i rozróżnienie ponownie sprawdzono 2026-11-12.
- [Czytelny HTML aktualnego draftu](https://eel.is/c++draft/) — wygodna prezentacja rozwijanego tekstu; może zawierać zmiany nowsze niż baza C++23. Nie przenoś ich bez adnotacji do starszego standardu.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) — zalecenia projektowe dotyczące m.in. lifetime, ownership, concurrency i interfaces; są wytycznymi, nie tekstem normatywnym.

## Mechanizmy języka

- [Core language clauses](https://timsong-cpp.github.io/cppwp/n4950/#language) — deklaracje, wyrażenia, klasy, szablony, wyjątki i preprocessing.
- [Object lifetime](https://timsong-cpp.github.io/cppwp/n4950/basic.life) — rozpoczęcie i zakończenie lifetime, transparent replacement oraz storage reuse.
- [Memory model](https://timsong-cpp.github.io/cppwp/n4950/intro.races) — data races, happens-before i wymagania wykonania wielowątkowego.
- [Templates](https://timsong-cpp.github.io/cppwp/n4950/temp) — dedukcja, instancjacja, dependent names, constraints i specialization.
- [Coroutines](https://timsong-cpp.github.io/cppwp/n4950/dcl.fct.def.coroutine) — transformacja funkcji korutynowej, promise oraz zawieszenie.
- [Contracts support w aktualnym drafcie](https://eel.is/c++draft/support.contract) — bieżący model contracts; nie należy mieszać go ze starszą składnią eksperymentalną.
- [Reflection w aktualnym drafcie](https://eel.is/c++draft/meta.reflection) — normatywny projekt statycznej refleksji C++26.

## Biblioteka standardowa

- [Library clauses](https://timsong-cpp.github.io/cppwp/n4950/#library) — wymagania całej biblioteki, kontenery, algorytmy, concurrency i utilities.
- [Containers library](https://timsong-cpp.github.io/cppwp/n4950/containers) — kontenery i ich wymagania.
- [Algorithms library](https://timsong-cpp.github.io/cppwp/n4950/algorithms) — algorytmy klasyczne, ranges i execution policies.
- [Thread support library](https://timsong-cpp.github.io/cppwp/n4950/thread) — wątki, mutexy, atomiki, futures i koordynacja.
- [Input/output library](https://timsong-cpp.github.io/cppwp/n4950/input.output) — strumienie, filesystem i powiązane utilities.
- [cppreference](https://en.cppreference.com/w/) — użyteczny, społecznościowy indeks funkcji i tabel wsparcia; źródło pomocnicze, nie norma ani oficjalna publikacja WG21.

## Toolchain i narzędzia

- [Clang documentation](https://clang.llvm.org/docs/) — flagi, diagnostyka, sanitizery, Clang-Tidy i informacje o wsparciu języka.
- [GCC C++ documentation](https://gcc.gnu.org/onlinedocs/gcc/C_002b_002b-Dialect-Options.html) — opcje dialektu i rozszerzeń GCC.
- [Microsoft C++ documentation](https://learn.microsoft.com/cpp/) — MSVC, STL, debugger, warning levels i opcje zgodności.
- [CMake documentation](https://cmake.org/cmake/help/latest/) — target model, commands, presets i integracja testów.
- [Conan documentation](https://docs.conan.io/2/) i [vcpkg documentation](https://learn.microsoft.com/vcpkg/) — zewnętrzne systemy zależności.
- [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html) — coverage-guided fuzzing w toolchainie LLVM.

## Uzupełnienia do pogłębionej ścieżki

- [C++23: inicjalizacja listowa](https://timsong-cpp.github.io/cppwp/n4950/dcl.init.list), [wykonanie i sequencing](https://timsong-cpp.github.io/cppwp/n4950/intro.execution), [elision](https://timsong-cpp.github.io/cppwp/n4950/class.copy.elision) i [move-eligible expressions](https://timsong-cpp.github.io/cppwp/n4950/expr.prim.id.unqual) — rozdzielaj reguły C++23 od dawnych objaśnień `return`.
- [C++23: wymagania hash](https://timsong-cpp.github.io/cppwp/n4950/hash.requirements) oraz [semantyczne wymagania concepts](https://timsong-cpp.github.io/cppwp/n4950/concepts) — sprawdzalna składnia nie dowodzi praw operacji.
- [Unicode Standard](https://www.unicode.org/versions/), [UAX #15: normalizacja](https://www.unicode.org/reports/tr15/) i [UAX #29: segmentacja](https://www.unicode.org/reports/tr29/) — materiał o tekście wymaga jawnego wskazania warstwy i wersji Unicode. Przykłady nowego rozdziału korzystają z niezmiennych reprezentacji UTF-8; nie implementują kompletnego walidatora ani segmentera.
- [CMake 3.20: add_test](https://cmake.org/cmake/help/v3.20/command/add_test.html) — wersjonowana dokumentacja odpowiadająca minimalnej wersji laboratoriów.
- [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html) i [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) — zakres diagnostyki i wymagania uruchomienia; brak zgłoszenia nie jest dowodem poprawności programu.

## Jak weryfikować twierdzenie w praktyce

Najpierw ustal wersję standardu. Dla reguły języka lub biblioteki sprawdź konkretną klauzulę opublikowanej normy albo odpowiadający jej draft. Dla funkcji jeszcze nieopublikowanej zachowaj numer dokumentu i datę. Dla flagi oraz dostępności sprawdź dokumentację konkretnej wersji kompilatora i biblioteki. Na końcu potwierdź zachowanie testem na wszystkich wspieranych toolchainach; eksperyment nie zmienia jednak programu z UB w program zgodny ze standardem.

## Hierarchia źródeł

Tekst standardu i aktualne drafty odpowiadają na pytania o język oraz bibliotekę normatywną. Dokumentacja kompilatora opisuje flagi, rozszerzenia i status implementacji. Dokumentacja platformy oraz ABI wyjaśnia calling convention, layout i symbole, a cppreference jest wysokiej jakości indeksem prowadzącym do właściwych reguł, nie formalnym zamiennikiem standardu.

~~~text
pytanie o poprawność języka   -> standard / draft + core issues
pytanie o bibliotekę          -> standard + status implementacji
pytanie o flagę               -> dokumentacja konkretnego kompilatora
pytanie o ABI                 -> dokument ABI platformy
pytanie o wydajność           -> pomiar + dokumentacja procesora/narzędzia
pytanie o C++26               -> przyjęta propozycja + feature-test macro
~~~

Źródło powinno podawać wersję i warstwę. Artykuł pokazujący assembly jest dowodem dla konkretnej konfiguracji, a nie ogólną gwarancją; odpowiedź forum może wskazać trop, lecz kluczową tezę trzeba sprawdzić w źródle pierwotnym lub eksperymencie kontrolnym.

## Powiązane tematy

- [Standardy i implementacje](01_wprowadzenie/02_standardy_i_implementacje.md)
- [Feature-test macros](12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

## Narzędzia użyte w wariancie repozytorium 01–30

- [CMake Presets, wersja dokumentacji 3.21](https://cmake.org/cmake/help/v3.21/manual/cmake-presets.7.html) — format dołączonych presetów; ręczny projekt CMake ma osobno określone minimum.
- [Git bisect](https://git-scm.com/docs/git-bisect) — znaczenie good/bad/skip i kodów wyjścia używanych przez automatyczne wyszukiwanie regresji.
- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) — semantyka HTTP, metod i ponawiania; konfiguracja timeoutów konkretnego klienta wymaga jego dokumentacji.
- [PostgreSQL: izolacja transakcji](https://www.postgresql.org/docs/current/transaction-iso.html) i [SQLite: izolacja](https://www.sqlite.org/isolation.html) — odrębne kontrakty silników. Nie wolno utożsamiać nazw poziomów z identyczną implementacją.
- [Prometheus: histogramy i summaries](https://prometheus.io/docs/practices/histograms/) — znaczenie agregacji i estymacji kwantyli; reprezentacja metryk nie zastępuje interpretacji danych.
- [GitHub Actions: składnia workflow](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) — zewnętrzna automatyzacja repozytorium, nie część języka C++.

Każdy pogłębiony rozdział produkcyjny dodatkowo wskazuje źródło konkretnej reguły lub API. Podczas eksperymentów zapisuj wersję bazy, narzędzia i biblioteki; link do bieżącej dokumentacji nie utrwala zachowania każdego historycznego wydania.
