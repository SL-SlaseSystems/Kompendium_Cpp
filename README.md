# Kompendium języka C++

Polskojęzyczny przewodnik po współczesnym C++: od pierwszego programu, przez czas życia obiektów, klasy, szablony i bibliotekę standardową, aż po model pamięci, ABI, lock-free i mechanikę korutyn. Bazą jest C++23. Materiał dotyczący C++26 jest oznaczony osobno. Kompendium obejmuje 73 rozdziały główne, 15 eksperckich oraz katalog 150 zaawansowanych mechanizmów. Opisy łączą intuicję, precyzyjne reguły, analizę przykładów i ćwiczenia z odpowiedziami.

Każdy rozdział przechodzi od podstawowego modelu do mechaniki konkretnego zagadnienia. Sekcja „Jak to działa krok po kroku” śledzi rzeczywiste operacje, „Pogłębienie mechanizmu” precyzuje reguły i przypadki brzegowe, „Drugi przykład” pozwala je przećwiczyć, a „Porównanie i decyzje” pomaga dobrać rozwiązanie. Ćwiczenia zawierają odpowiedzi i uzasadnienia; linki do źródeł pozwalają sprawdzić regułę w odpowiedniej wersji standardu.

## Jak korzystać

Do przekrojowej powtórki służy [150 zaawansowanych mechanizmów](150-zaawansowanych-mechanizmow-cpp.md); każda pozycja rozwija działanie, zastosowanie i pułapkę.

- **Od zera:** czytaj kolejno katalogi `01`–`13`, a dopiero potem `zaawansowane`.
- **Znasz inny język:** zacznij od podstaw, czasu życia, klas, szablonów i biblioteki standardowej; później wybierz interesujące działy.
- **Szukasz konkretu:** użyj poniższego indeksu, [ściągi](sciaga.md) albo [słownika](slownik.md).
- **Powtarzasz materiał:** zacznij od pogłębienia, drugiego przykładu, pułapek i sekcji decyzyjnej, a następnie spróbuj obalić własne założenie sanitizerem lub drugim kompilatorem.

## Oznaczenia przykładów

- `cpp` — samowystarczalny fragment kompilowany przez walidator jako C++23;
- `cpp,notest` — kod ilustracyjny, celowo błędny albo wymagający osobnej konfiguracji, platformy, funkcji C++26 lub API niedostępnego w lokalnym toolchainie; przy takim przykładzie opisano powód;
- `text` — pseudokod, polecenia lub fragment wymagający większego projektu.

Kompilowalność nie oznacza automatycznie poprawności projektu ani braku undefined behavior. Rozdziały wyjaśniają wymagane kontrakty i czas życia danych.

## 01. Wprowadzenie

1. [Czym jest C++](01_wprowadzenie/01_czym_jest_cpp.md)
2. [Standardy i implementacje](01_wprowadzenie/02_standardy_i_implementacje.md)
3. [Kompilatory i toolchain](01_wprowadzenie/03_kompilatory_i_toolchain.md)
4. [Pierwszy program](01_wprowadzenie/04_pierwszy_program.md)
5. [Proces budowania](01_wprowadzenie/05_proces_budowania.md)

## 02. Podstawy języka

1. [Leksemy, deklaracje i zakresy](02_podstawy_jezyka/01_leksemy_deklaracje_i_zakresy.md)
2. [Typy podstawowe i literały](02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
3. [Zmienne, const i constexpr](02_podstawy_jezyka/03_zmienne_const_i_constexpr.md)
4. [Operatory i konwersje](02_podstawy_jezyka/04_operatory_i_konwersje.md)
5. [Funkcje i przeciążanie](02_podstawy_jezyka/05_funkcje_i_przeciazanie.md)
6. [Sterowanie przepływem](02_podstawy_jezyka/06_sterowanie_przeplywem.md)
7. [Referencje, wskaźniki i tablice](02_podstawy_jezyka/07_referencje_wskazniki_i_tablice.md)

## 03. Pamięć i czas życia

1. [Storage duration i lifetime](03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
2. [Stos, sterta i dynamiczna pamięć](03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
3. [RAII i destruktory](03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
4. [Copy, move i rule of zero](03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
5. [Smart pointery](03_pamiec_i_czas_zycia/05_smart_pointery.md)
6. [Widoki, span, string_view i dangling](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)

## 04. Klasy i model obiektowy

1. [struct, class i enkapsulacja](04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md)
2. [Konstruktory i destruktory](04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md)
3. [Funkcje specjalne i operatory](04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
4. [Dziedziczenie i polimorfizm](04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)
5. [virtual, override i RTTI](04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
6. [enum, union i variant](04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)

## 05. Szablony i generyczność

1. [Szablony funkcji i klas](05_szablony_i_generycznosc/01_function_i_class_templates.md)
2. [Dedukcja, auto, decltype i CTAD](05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
3. [Specialization i SFINAE](05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
4. [Concepts i requires](05_szablony_i_generycznosc/04_concepts_i_requires.md)
5. [Variadic templates i fold expressions](05_szablony_i_generycznosc/05_variadic_templates_i_fold.md)
6. [constexpr, consteval i metaprogramowanie](05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md)

## 06. Biblioteka standardowa

1. [string, string_view i tekst](06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
2. [vector, array, deque i list](06_biblioteka_standardowa/02_vector_array_deque_list.md)
3. [map, set, unordered i hash](06_biblioteka_standardowa/03_map_set_unordered_i_hash.md)
4. [Iteratory i invalidacja](06_biblioteka_standardowa/04_iteratory_i_invalidacja.md)
5. [Algorytmy i lambdy](06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
6. [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)
7. [tuple, pair, variant i any](06_biblioteka_standardowa/07_tuple_pair_variant_any.md)

## 07. Błędy i kontrakty

1. [Wyjątki: try, catch i throw](07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md)
2. [RAII, exception safety i noexcept](07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md)
3. [optional, expected i kody błędów](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)
4. [Assertions, preconditions i contracts](07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)

## 08. Budowanie i organizacja

1. [Translation units, nagłówki i include](08_budowanie_i_organizacja/01_translation_units_headers_i_include.md)
2. [Linkowanie, ODR i inline](08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
3. [Namespaces, visibility i ADL](08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)
4. [Moduły C++](08_budowanie_i_organizacja/04_moduly_cpp.md)
5. [CMake](08_budowanie_i_organizacja/05_cmake.md)
6. [Conan, vcpkg i zależności](08_budowanie_i_organizacja/06_conan_vcpkg_i_zaleznosci.md)

## 09. Testowanie i jakość

1. [Testy jednostkowe i integracyjne](09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
2. [Ostrzeżenia i analiza statyczna](09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md)
3. [Sanitizery i debuggery](09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)
4. [Benchmarki i profilowanie](09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
5. [Fuzzing i property-based testing](09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)

## 10. Współbieżność

1. [thread, jthread i stop_token](10_wspolbieznosc/01_thread_jthread_i_stop_token.md)
2. [mutex, lock i condition_variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)
3. [future, promise i async](10_wspolbieznosc/03_future_promise_async.md)
4. [Atomiki i model pamięci](10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
5. [latch, barrier i semaphore](10_wspolbieznosc/05_latch_barrier_semaphore.md)

## 11. I/O i system

1. [Strumienie i formatowanie](11_io_i_system/01_strumienie_i_formatowanie.md)
2. [Pliki i filesystem](11_io_i_system/02_pliki_i_filesystem.md)
3. [chrono i czas](11_io_i_system/03_chrono_i_czas.md)
4. [random i numeryka](11_io_i_system/04_random_i_numeryka.md)
5. [Sieć, serializacja i granice std](11_io_i_system/05_siec_serializacja_i_granice_std.md)

## 12. Współczesny C++

1. [C++11 i C++14](12_wspolczesny_cpp/01_cpp11_14.md)
2. [C++17](12_wspolczesny_cpp/02_cpp17.md)
3. [C++20](12_wspolczesny_cpp/03_cpp20.md)
4. [C++23](12_wspolczesny_cpp/04_cpp23.md)
5. [Korutyny](12_wspolczesny_cpp/05_korutyny.md)
6. [Feature-test macros i przenośność](12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)

## 13. Wzorce, API i wydajność

1. [Rule of zero, PImpl i NVI](13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)
2. [Value semantics i type erasure](13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
3. [Projektowanie API i ABI](13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
4. [Architektura i dependency injection](13_wzorce_api_i_wydajnosc/04_architektura_i_dependency_injection.md)
5. [Wydajność, cache i zero-overhead](13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

## Zagadnienia zaawansowane

Osobna [mapa działu zaawansowanego](zaawansowane/README.md) podaje wymagania wstępne i zalecaną kolejność.

1. [Undefined behavior i abstract machine](zaawansowane/01_undefined_behavior_i_model_maszyny.md)
2. [Lifetime, aliasing i pointer provenance](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md)
3. [Layout, alignment, padding i triviality](zaawansowane/03_layout_alignment_padding_i_triviality.md)
4. [Alokatory, PMR i new/delete](zaawansowane/04_allocatory_pmr_i_new_delete.md)
5. [Value categories i perfect forwarding](zaawansowane/05_value_categories_i_perfect_forwarding.md)
6. [Overload resolution, ADL i hidden friends](zaawansowane/06_overload_resolution_adl_i_hidden_friends.md)
7. [Dependent names, two-phase lookup i SFINAE](zaawansowane/07_dependent_names_two_phase_lookup_i_sfinae.md)
8. [Concept normalization i subsumption](zaawansowane/08_concepts_normalization_i_subsumption.md)
9. [constexpr, consteval i compile time](zaawansowane/09_constexpr_consteval_i_compile_time.md)
10. [Type erasure, vtables, ABI i visibility](zaawansowane/10_type_erasure_vtables_abi_i_visibility.md)
11. [Memory ordering, lock-free, ABA i reclamation](zaawansowane/11_memory_ordering_lock_free_aba_i_reclamation.md)
12. [Korutyny: promise, awaitery i frame](zaawansowane/12_korutyny_promise_awaitery_i_frame.md)
13. [ODR, moduły, FFI i interoperacyjność](zaawansowane/13_odr_moduly_ffi_i_interoperacyjnosc.md)
14. [SIMD, wektoryzacja, cache i optymalizacja](zaawansowane/14_simd_wektoryzacja_cache_i_optymalizacja.md)
15. [C++26 i nadchodzące funkcje](zaawansowane/15_cpp26_i_nadchodzace_funkcje.md)

## Materiały przekrojowe

- [150 zaawansowanych mechanizmów C++](150-zaawansowanych-mechanizmow-cpp.md)
- [Słownik polsko-angielski](slownik.md)
- [Ściąga składni i biblioteki](sciaga.md)
- [Dalsza nauka i specjalizacje](dalsza_nauka.md)
- [Źródła](zrodla.md)
- [Zasady rozwijania materiału](CONTRIBUTING.md)

## Weryfikacja

~~~text
python3 -m unittest scripts/test_verify.py -v
bash scripts/verify.sh
~~~

Testy potwierdzają działanie reguł głębokości. Główny skrypt sprawdza strukturę Markdown, linki, minimalną liczbę słów i przykładów oraz kompilowalne bloki C++23. Nie uruchamia kodu, więc nie zastępuje testów zachowania programu ani sanitizerów.
