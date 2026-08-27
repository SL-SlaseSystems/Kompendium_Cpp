# Kompendium języka C++ — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stworzyć kompletne, polskojęzyczne kompendium C++ w modularnych plikach Markdown, prowadzące od pierwszego programu do mechanizmów eksperckich.

**Architecture:** Numerowane katalogi wyznaczają kolejność nauki, a małe pliki tematyczne pozwalają używać materiału jak referencji. Przykłady są osadzone w Markdown i, gdy są samowystarczalne, kompilowane przez wspólny walidator jako C++23. Osobny katalog `zaawansowane` izoluje tematy wymagające dobrej znajomości modelu obiektów, szablonów, współbieżności i ABI.

**Tech Stack:** Markdown, ISO C++23, informacje uzupełniające o C++26, lokalny Clang 17, powłoka POSIX, Python 3 w skrypcie walidującym, źródła WG21 i C++ Core Guidelines.

## Global Constraints

- Język treści: polski, z angielskim terminem przy pierwszym użyciu.
- Format: opisowe pliki Markdown i przykłady w tekście; brak osobnych projektów demonstracyjnych.
- Projekt nie może zawierać repozytorium Git ani wymagać operacji Git.
- Bazą jest opublikowany C++23; C++26, rozszerzenia i biblioteki zewnętrzne muszą być jawnie oznaczone.
- Każdy zwykły rozdział ma link do głównego indeksu, przykład lub uzasadnienie jego braku, pułapki, dobre praktyki i sekcję „Powiązane tematy”.
- Testowalne bloki `cpp` muszą kompilować się przez `clang++ -std=c++23 -Wall -Wextra -Wpedantic`; szkice i przykłady niebezpieczne używają `cpp,notest` albo `text`.
- Walidator ma ignorować składnię linków wewnątrz bloków kodu i nigdy nie wykonywać przykładów UB.

---

## Mapa plików

### Nawigacja i materiały przekrojowe

- `README.md`
- `CONTRIBUTING.md`
- `slownik.md`
- `sciaga.md`
- `dalsza_nauka.md`
- `zrodla.md`
- `scripts/verify.sh`

### 01 — Wprowadzenie

- `01_wprowadzenie/01_czym_jest_cpp.md`
- `01_wprowadzenie/02_standardy_i_implementacje.md`
- `01_wprowadzenie/03_kompilatory_i_toolchain.md`
- `01_wprowadzenie/04_pierwszy_program.md`
- `01_wprowadzenie/05_proces_budowania.md`

### 02 — Podstawy języka

- `02_podstawy_jezyka/01_leksemy_deklaracje_i_zakresy.md`
- `02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md`
- `02_podstawy_jezyka/03_zmienne_const_i_constexpr.md`
- `02_podstawy_jezyka/04_operatory_i_konwersje.md`
- `02_podstawy_jezyka/05_funkcje_i_przeciazanie.md`
- `02_podstawy_jezyka/06_sterowanie_przeplywem.md`
- `02_podstawy_jezyka/07_referencje_wskazniki_i_tablice.md`

### 03 — Pamięć i czas życia

- `03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md`
- `03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md`
- `03_pamiec_i_czas_zycia/03_raii_i_destruktory.md`
- `03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md`
- `03_pamiec_i_czas_zycia/05_smart_pointery.md`
- `03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md`

### 04 — Klasy i model obiektowy

- `04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md`
- `04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md`
- `04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md`
- `04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md`
- `04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md`
- `04_klasy_i_model_obiektowy/06_enum_union_i_variant.md`

### 05 — Szablony i programowanie generyczne

- `05_szablony_i_generycznosc/01_function_i_class_templates.md`
- `05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md`
- `05_szablony_i_generycznosc/03_specialization_i_sfinAE.md`
- `05_szablony_i_generycznosc/04_concepts_i_requires.md`
- `05_szablony_i_generycznosc/05_variadic_templates_i_fold.md`
- `05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md`

### 06 — Biblioteka standardowa, kontenery i ranges

- `06_biblioteka_standardowa/01_string_string_view_i_tekst.md`
- `06_biblioteka_standardowa/02_vector_array_deque_list.md`
- `06_biblioteka_standardowa/03_map_set_unordered_i_hash.md`
- `06_biblioteka_standardowa/04_iteratory_i_invalidacja.md`
- `06_biblioteka_standardowa/05_algorytmy_i_lambdy.md`
- `06_biblioteka_standardowa/06_ranges_i_views.md`
- `06_biblioteka_standardowa/07_tuple_pair_variant_any.md`

### 07 — Błędy i kontrakty

- `07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md`
- `07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md`
- `07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md`
- `07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md`

### 08 — Organizacja, kompilacja i zależności

- `08_budowanie_i_organizacja/01_translation_units_headers_i_include.md`
- `08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md`
- `08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md`
- `08_budowanie_i_organizacja/04_moduly_cpp.md`
- `08_budowanie_i_organizacja/05_cmake.md`
- `08_budowanie_i_organizacja/06_conan_vcpkg_i_zaleznosci.md`

### 09 — Testowanie i jakość

- `09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md`
- `09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md`
- `09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md`
- `09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md`
- `09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md`

### 10 — Współbieżność

- `10_wspolbieznosc/01_thread_jthread_i_stop_token.md`
- `10_wspolbieznosc/02_mutex_lock_i_condition_variable.md`
- `10_wspolbieznosc/03_future_promise_async.md`
- `10_wspolbieznosc/04_atomiki_i_model_pamieci.md`
- `10_wspolbieznosc/05_latch_barrier_semaphore.md`

### 11 — I/O, system i narzędzia biblioteczne

- `11_io_i_system/01_strumienie_i_formatowanie.md`
- `11_io_i_system/02_pliki_i_filesystem.md`
- `11_io_i_system/03_chrono_i_czas.md`
- `11_io_i_system/04_random_i_numeryka.md`
- `11_io_i_system/05_siec_serializacja_i_granice_std.md`

### 12 — Współczesny C++ i ewolucja

- `12_wspolczesny_cpp/01_cpp11_14.md`
- `12_wspolczesny_cpp/02_cpp17.md`
- `12_wspolczesny_cpp/03_cpp20.md`
- `12_wspolczesny_cpp/04_cpp23.md`
- `12_wspolczesny_cpp/05_korutyny.md`
- `12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md`

### 13 — Wzorce, API i wydajność

- `13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md`
- `13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md`
- `13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md`
- `13_wzorce_api_i_wydajnosc/04_architektura_i_dependency_injection.md`
- `13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md`

### Zagadnienia zaawansowane

- `zaawansowane/README.md`
- `zaawansowane/01_undefined_behavior_i_model_maszyny.md`
- `zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md`
- `zaawansowane/03_layout_alignment_padding_i_triviality.md`
- `zaawansowane/04_allocatory_pmr_i_new_delete.md`
- `zaawansowane/05_value_categories_i_perfect_forwarding.md`
- `zaawansowane/06_overload_resolution_adl_i_hidden_friends.md`
- `zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md`
- `zaawansowane/08_concepts_normalization_i_subsumption.md`
- `zaawansowane/09_constexpr_consteval_i_compile_time.md`
- `zaawansowane/10_type_erasure_vtables_abi_i_visibility.md`
- `zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md`
- `zaawansowane/12_korutyny_promise_awaitery_i_frame.md`
- `zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md`
- `zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md`
- `zaawansowane/15_cpp26_i_nadchodzace_funkcje.md`

---

### Task 1: Fundament, indeks i walidator

**Files:** `README.md`, `CONTRIBUTING.md`, `scripts/verify.sh`.

- [ ] Zbuduj pełny indeks z legendą `cpp`, `cpp,notest` i `text`, trzema ścieżkami nauki oraz wszystkimi pozycjami z mapy plików.
- [ ] Zapisz kontrakt redakcyjny rozdziału i reguły oznaczania C++23, C++26, rozszerzeń oraz bibliotek zewnętrznych.
- [ ] Zaimplementuj walidator sprawdzający puste Markdown, ogrodzenia kodu, lokalne linki, nawigację i kompilowalne bloki `cpp`.
- [ ] Uruchom `bash scripts/verify.sh`; na tym etapie akceptowalne są wyłącznie zgłoszenia brakujących, jeszcze niezapisanych celów indeksu.

### Task 2: Wprowadzenie i składnia

**Files:** wszystkie pliki w `01_wprowadzenie` i `02_podstawy_jezyka`.

- [ ] Opisz charakter języka, standardy i implementacje, GCC/Clang/MSVC, pierwszy program, etapy preprocessing–kompilacja–linkowanie oraz podstawowe komendy.
- [ ] Opisz deklaracje, zakresy, typy, literały, `const`, `constexpr`, operatory, konwersje, funkcje, przeciążanie, sterowanie, referencje, wskaźniki i tablice.
- [ ] Skompiluj wszystkie testowalne fragmenty z tych katalogów w C++23.

### Task 3: Pamięć, RAII i model obiektowy

**Files:** wszystkie pliki w `03_pamiec_i_czas_zycia` i `04_klasy_i_model_obiektowy`.

- [ ] Opisz storage duration, lifetime, dynamiczną pamięć, RAII, destruktory, copy/move, rule of zero/five, smart pointery oraz niewłaścicielskie widoki.
- [ ] Opisz klasy, konstruktory, funkcje specjalne, operatory, dziedziczenie, wirtualność, RTTI, enumy, uniony i `variant`.
- [ ] Zaznacz wszystkie przypadki dangling, slicing, double delete i UB; skompiluj bezpieczne przykłady.

### Task 4: Szablony i programowanie generyczne

**Files:** wszystkie pliki w `05_szablony_i_generycznosc`.

- [ ] Opisz templates funkcji i klas, dedukcję, `auto`, `decltype`, CTAD, specialization, SFINAE, concepts, variadics, fold expressions, `constexpr` i `consteval`.
- [ ] Wyjaśnij różnicę między instancjacją, przeciążeniem, specjalizacją i ograniczaniem szablonu.
- [ ] Skompiluj przykłady; funkcje C++26 oznacz jako nietestowalne na lokalnym Clang 17, jeśli brak wsparcia.

### Task 5: Biblioteka standardowa i ranges

**Files:** wszystkie pliki w `06_biblioteka_standardowa`.

- [ ] Porównaj tekst, kontenery sekwencyjne i asocjacyjne, iteratory oraz reguły invalidacji.
- [ ] Pokaż algorytmy, lambdy, projections, ranges, views, `tuple`, `pair`, `variant` i `any`.
- [ ] Każdy rozdział zakończ regułą wyboru abstrahującą od konkretnej implementacji; skompiluj przykłady C++23.

### Task 6: Błędy, kontrakty, organizacja i budowanie

**Files:** wszystkie pliki w `07_bledy_i_kontrakty` i `08_budowanie_i_organizacja`.

- [ ] Opisz wyjątki, gwarancje exception safety, `noexcept`, `optional`, `expected`, `error_code`, assertions i stan kontraktów.
- [ ] Opisz translation units, nagłówki, include guards, linkowanie, ODR, namespaces, ADL, moduły, CMake, Conan i vcpkg.
- [ ] Odróżnij mechanizmy ISO od narzędzi ekosystemowych i skompiluj samowystarczalne fragmenty.

### Task 7: Testowanie i jakość

**Files:** wszystkie pliki w `09_testowanie_i_jakosc`.

- [ ] Opisz testy bez frameworka i z frameworkami, warning policy, clang-tidy, sanitizery, debugowanie, benchmarki, profilowanie, fuzzing i property-based testing.
- [ ] Podaj przenośne komendy dla Clang/GCC oraz oznacz narzędzia zależne od platformy.
- [ ] Dodaj przykłady kodu z testowalnymi funkcjami i wyjaśnij ograniczenia mikrobenchmarków.

### Task 8: Współbieżność

**Files:** wszystkie pliki w `10_wspolbieznosc`.

- [ ] Opisz `thread`, `jthread`, cooperative cancellation, mutexy, condition variables, futures, promises, `async`, atomiki oraz model happens-before.
- [ ] Opisz latch, barrier i semaphore, deadlock, races, false sharing i zasady wyboru synchronizacji.
- [ ] Kompiluj przykłady; nie uruchamiaj kodu niedeterministycznego podczas walidacji.

### Task 9: I/O, system i ewolucja języka

**Files:** wszystkie pliki w `11_io_i_system` i `12_wspolczesny_cpp`.

- [ ] Opisz strumienie, formatowanie, pliki, filesystem, chrono, random i numerykę oraz brak standardowej sieci i serializacji w C++23.
- [ ] Zbuduj przekrój C++11/14, C++17, C++20 i C++23; opisz korutyny i feature-test macros.
- [ ] Wyraźnie oddziel składnię języka, bibliotekę standardową, funkcje opcjonalne implementacji i biblioteki zewnętrzne.

### Task 10: Wzorce, projektowanie API i wydajność

**Files:** wszystkie pliki w `13_wzorce_api_i_wydajnosc`.

- [ ] Opisz rule of zero, PImpl, NVI, value semantics, type erasure, projektowanie stabilnego API/ABI, dependency injection i composition root.
- [ ] Opisz zero-overhead principle, alokacje, cache locality, branch prediction, wektoryzację i zasadę pomiaru przed optymalizacją.
- [ ] Skompiluj przykłady i unikaj obietnic wydajności bez pomiaru.

### Task 11: Zaawansowany model pamięci i typów

**Files:** `zaawansowane/README.md` oraz rozdziały 01–09 w `zaawansowane`.

- [ ] Zbuduj mapę wymagań wstępnych i ostrzeżenie o przeniesieniu obowiązku dowodu na programistę.
- [ ] Opisz UB, abstract machine, lifetime, aliasing, provenance, layout, alignment, allocators/PMR, value categories, forwarding, overload resolution, ADL, dependent names, two-phase lookup, SFINAE, concepts i compile time.
- [ ] Kod potencjalnie powodujący UB umieść wyłącznie w `cpp,notest` albo `text`; bezpieczne fragmenty skompiluj.

### Task 12: ABI, lock-free, korutyny, interoperacyjność i C++26

**Files:** rozdziały 10–15 w `zaawansowane`.

- [ ] Opisz type erasure, vtables, ABI, visibility, memory ordering, lock-free, ABA, reclamation, frame korutyny, promise/awaiter, ODR, moduły, FFI, SIMD i diagnostykę optymalizacji.
- [ ] W rozdziale C++26 przedstaw tylko funkcje przyjęte do właściwego working draftu, podaj datę weryfikacji i wymagaj feature-test macros zamiast zgadywania wsparcia.
- [ ] Skompiluj fragmenty C++23; przykłady C++26 i zależne od ABI oznacz jako nietestowalne.

### Task 13: Materiały przekrojowe i pełna kontrola jakości

**Files:** `slownik.md`, `sciaga.md`, `dalsza_nauka.md`, `zrodla.md`, wszystkie rozdziały i `scripts/verify.sh`.

- [ ] Napisz słownik polsko-angielski, składniową ściągę, ścieżki dla CLI/backendu/systemów/embedded/gier/bibliotek oraz bibliografię źródeł pierwotnych.
- [ ] Zamknij graf nawigacji: każdy materiał użytkowy jest osiągalny z `README.md`, a każdy rozdział wraca do indeksu i ma 2–5 powiązanych tematów.
- [ ] Uruchom `bash scripts/verify.sh` i popraw wszystkie błędy do kodu wyjścia 0.
- [ ] Sprawdź brak `.git`, placeholderów, pustych szkieletów i plików merytorycznych krótszych niż 200 słów.
- [ ] Zbierz liczbę plików, słów i testowalnych przykładów do raportu końcowego.

