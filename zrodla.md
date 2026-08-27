[← Spis treści](README.md)

# Źródła

Kompendium opiera się przede wszystkim na tekstach normatywnych i materiałach organizacji rozwijających język. Dokumentacja kompilatora jest źródłem prawdy o jego flagach oraz poziomie implementacji. Strony referencyjne są wygodnym indeksem, ale nie zastępują standardu.

## Standard i WG21

- [The Standard — Standard C++](https://isocpp.org/std/the-standard) — informacja, że bieżącą opublikowaną normą jest C++23, formalnie ISO/IEC 14882:2024.
- [WG21](https://www.open-std.org/jtc1/sc22/wg21/) — strona grupy standaryzacyjnej, working drafts, projekty i listy zagadnień.
- [WG21 papers](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/) — dokumenty propozycji, raporty redaktorów i mailingi.
- [N5054 — Working Draft, Programming Languages — C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/n5054.pdf) — najnowszy publiczny working draft C++26 w mailingu WG21 dostępny podczas weryfikacji 2026-08-27.
- [Czytelny HTML aktualnego draftu](https://eel.is/c++draft/) — wygodna prezentacja tekstu working draft; numerowaną wersję WG21 warto zachować dla trwałego cytowania.
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) — zalecenia projektowe dotyczące m.in. lifetime, ownership, concurrency i interfaces; są wytycznymi, nie tekstem normatywnym.

## Mechanizmy języka

- [Core language clauses](https://eel.is/c++draft/#language) — deklaracje, wyrażenia, klasy, szablony, wyjątki i preprocessing.
- [Object lifetime](https://eel.is/c++draft/basic.life) — rozpoczęcie i zakończenie lifetime, transparent replacement oraz storage reuse.
- [Memory model](https://eel.is/c++draft/intro.races) — data races, happens-before i wymagania wykonania wielowątkowego.
- [Templates](https://eel.is/c++draft/temp) — dedukcja, instancjacja, dependent names, constraints i specialization.
- [Coroutines](https://eel.is/c++draft/dcl.fct.def.coroutine) — transformacja funkcji korutynowej, promise oraz zawieszenie.
- [Contracts support w aktualnym drafcie](https://eel.is/c++draft/support.contract) — bieżący model contracts; nie należy mieszać go ze starszą składnią eksperymentalną.
- [Reflection w aktualnym drafcie](https://eel.is/c++draft/meta.reflection) — normatywny projekt statycznej refleksji C++26.

## Biblioteka standardowa

- [Library clauses](https://eel.is/c++draft/#library) — wymagania całej biblioteki, kontenery, algorytmy, concurrency i utilities.
- [Containers library](https://eel.is/c++draft/containers) — kontenery i ich wymagania.
- [Algorithms library](https://eel.is/c++draft/algorithms) — algorytmy klasyczne, ranges i execution policies.
- [Thread support library](https://eel.is/c++draft/thread) — wątki, mutexy, atomiki, futures i koordynacja.
- [Input/output library](https://eel.is/c++draft/input.output) — strumienie, filesystem i powiązane utilities.
- [cppreference](https://en.cppreference.com/w/) — użyteczny, społecznościowy indeks funkcji i tabel wsparcia; źródło pomocnicze, nie norma ani oficjalna publikacja WG21.

## Toolchain i narzędzia

- [Clang documentation](https://clang.llvm.org/docs/) — flagi, diagnostyka, sanitizery, Clang-Tidy i informacje o wsparciu języka.
- [GCC C++ documentation](https://gcc.gnu.org/onlinedocs/gcc/C_002b_002b-Dialect-Options.html) — opcje dialektu i rozszerzeń GCC.
- [Microsoft C++ documentation](https://learn.microsoft.com/cpp/) — MSVC, STL, debugger, warning levels i opcje zgodności.
- [CMake documentation](https://cmake.org/cmake/help/latest/) — target model, commands, presets i integracja testów.
- [Conan documentation](https://docs.conan.io/2/) i [vcpkg documentation](https://learn.microsoft.com/vcpkg/) — zewnętrzne systemy zależności.
- [LLVM libFuzzer](https://llvm.org/docs/LibFuzzer.html) — coverage-guided fuzzing w toolchainie LLVM.

## Jak weryfikować twierdzenie

Najpierw ustal wersję standardu. Dla reguły języka lub biblioteki sprawdź konkretną klauzulę opublikowanej normy albo odpowiadający jej draft. Dla funkcji jeszcze nieopublikowanej zachowaj numer dokumentu i datę. Dla flagi oraz dostępności sprawdź dokumentację konkretnej wersji kompilatora i biblioteki. Na końcu potwierdź zachowanie testem na wszystkich wspieranych toolchainach; eksperyment nie zmienia jednak programu z UB w program zgodny ze standardem.

## Powiązane tematy

- [Standardy i implementacje](01_wprowadzenie/02_standardy_i_implementacje.md)
- [Feature-test macros](12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)
- [C++26](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

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
