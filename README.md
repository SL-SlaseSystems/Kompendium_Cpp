# Kompendium języka C++

Polskojęzyczna ścieżka od reguł języka do projektowania i utrzymywania systemów. Bazą przykładów jest C++23; C++26 jest oznaczone osobno. Ten wariant repozytorium obejmuje **30 działów, 179 rozdziałów głównych i 15 eksperckich** oraz katalog 150 mechanizmów.

**Już piszesz w C++:** zacznij od [24 problemów diagnostycznych](test_diagnostyczny.md), następnie wybierz etap ze [ścieżki pogłębionej nauki](sciezka_nauki.md). Ćwicz analizę kontraktów, czasu życia i przypadków granicznych. Wynik kompilacji oraz jedno udane uruchomienie nie są dowodem poprawności całego projektu.

Rozbudowa z 12 listopada 2026 łączy osiem nowych rozdziałów fundamentów, 78 zadań z rozwiązaniami i trzy uruchamiane laboratoria z istniejącą ścieżką 01–30. Dodatkowo pogłębia wybrane rozdziały warsztatowe i produkcyjne, zastępując ogólne checklisty konkretnymi regułami, przykładami i przypadkami awarii.

## Jak korzystać

- **Ścieżka językowa:** działy 01–13; osoba znająca C++ wybiera rozdziały według diagnozy, zamiast obowiązkowo zaczynać od początku.
- **Ścieżka zawodowa:** warsztat i bezpieczeństwo 14–20, następnie wybrana specjalizacja 21–29 oraz jeden projekt z działu 30.
- **Ścieżka ekspercka:** lifetime, value categories, templates, model pamięci, ABI i pomiary w [dziale zaawansowanym](zaawansowane/README.md).
- **Praktyka:** istniejące zestawy przy każdym dziale uzupełnia [78 scenariuszy z rozwiązaniami](cwiczenia/README.md) oraz [laboratoria z testami](praktyka/README.md).
- **Portfolio:** [mapa trzydziestu projektów](Projekty.md) pomaga wybrać jeden kompletny projekt, wraz z testami błędów i dowodami decyzji.

## Oznaczenia przykładów

- `cpp`: samowystarczalna jednostka translacji sprawdzana składniowo jako C++23.
- `cpp,notest`: przykład zależny od kontekstu, platformy, nieobsługiwanej funkcji albo celowo niepoprawny; przy przykładzie opisano powód.
- `text`, `cmake`, `sql`, `yaml`, `json`: polecenia, konfiguracja lub fragment wymagający wskazanego kontekstu. Nie są automatycznie uruchamiane przez walidator Markdown.

Kompilacja wszystkich bloków jest odrębna od uruchamiania programów, testów laboratoriów i testów adapterów zewnętrznych. [Raport](RAPORT_KONCOWY.md) opisuje rzeczywiście wykonane kontrole i ich granice.

## 01. Wprowadzenie do C++

[Mapa i wymagania](01_wprowadzenie/README.md) · [Zestaw ćwiczeń](01_wprowadzenie/ZESTAW-CWICZEN.md)

1. [Czym jest C++](01_wprowadzenie/01_czym_jest_cpp.md)
2. [Standardy i implementacje](01_wprowadzenie/02_standardy_i_implementacje.md)
3. [Kompilatory i toolchain](01_wprowadzenie/03_kompilatory_i_toolchain.md)
4. [Pierwszy program](01_wprowadzenie/04_pierwszy_program.md)
5. [Proces budowania](01_wprowadzenie/05_proces_budowania.md)

## 02. Podstawy języka C++

[Mapa i wymagania](02_podstawy_jezyka/README.md) · [Zestaw ćwiczeń](02_podstawy_jezyka/ZESTAW-CWICZEN.md)

1. [Leksemy, deklaracje i zakresy](02_podstawy_jezyka/01_leksemy_deklaracje_i_zakresy.md)
2. [Typy podstawowe i literały](02_podstawy_jezyka/02_typy_podstawowe_i_literaly.md)
3. [Zmienne, const i constexpr](02_podstawy_jezyka/03_zmienne_const_i_constexpr.md)
4. [Operatory i konwersje](02_podstawy_jezyka/04_operatory_i_konwersje.md)
5. [Funkcje i przeciążanie](02_podstawy_jezyka/05_funkcje_i_przeciazanie.md)
6. [Sterowanie przepływem](02_podstawy_jezyka/06_sterowanie_przeplywem.md)
7. [Referencje, wskaźniki i tablice](02_podstawy_jezyka/07_referencje_wskazniki_i_tablice.md)
8. [Inicjalizacja i initializer_list](02_podstawy_jezyka/08_inicjalizacja_i_initializer_list.md)
9. [Kolejność ewaluacji i sequencing](02_podstawy_jezyka/09_kolejnosc_ewaluacji_i_sequencing.md)
10. [Arytmetyka, przepełnienia i float](02_podstawy_jezyka/10_arytmetyka_przepelnienia_i_float.md)

## 03. Pamięć i czas życia

[Mapa i wymagania](03_pamiec_i_czas_zycia/README.md) · [Zestaw ćwiczeń](03_pamiec_i_czas_zycia/ZESTAW-CWICZEN.md)

1. [Storage duration i lifetime](03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
2. [Stos, sterta i dynamiczna pamięć](03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
3. [RAII i destruktory](03_pamiec_i_czas_zycia/03_raii_i_destruktory.md)
4. [Copy, move i rule of zero](03_pamiec_i_czas_zycia/04_copy_move_i_rule_of_zero.md)
5. [Smart pointery](03_pamiec_i_czas_zycia/05_smart_pointery.md)
6. [Widoki, span, string_view i dangling](03_pamiec_i_czas_zycia/06_widoki_span_string_view_i_dangling.md)
7. [Zwracanie wartości, elision i lifetime](03_pamiec_i_czas_zycia/07_zwracanie_wartosci_elision_i_lifetime.md)

## 04. Klasy i model obiektowy

[Mapa i wymagania](04_klasy_i_model_obiektowy/README.md) · [Zestaw ćwiczeń](04_klasy_i_model_obiektowy/ZESTAW-CWICZEN.md)

1. [struct, class i enkapsulacja](04_klasy_i_model_obiektowy/01_struct_class_i_enkapsulacja.md)
2. [Konstruktory i destruktory](04_klasy_i_model_obiektowy/02_konstruktory_i_destruktory.md)
3. [Funkcje specjalne i operatory](04_klasy_i_model_obiektowy/03_funkcje_specjalne_i_operatory.md)
4. [Dziedziczenie i polimorfizm](04_klasy_i_model_obiektowy/04_dziedziczenie_i_polimorfizm.md)
5. [virtual, override i RTTI](04_klasy_i_model_obiektowy/05_virtual_override_i_rtti.md)
6. [enum, union i variant](04_klasy_i_model_obiektowy/06_enum_union_i_variant.md)
7. [Silne typy, znaczenie porównań i kontrakt hash](04_klasy_i_model_obiektowy/07_silne_typy_porownania_i_hash.md)

## 05. Szablony i generyczność

[Mapa i wymagania](05_szablony_i_generycznosc/README.md) · [Zestaw ćwiczeń](05_szablony_i_generycznosc/ZESTAW-CWICZEN.md)

1. [Szablony funkcji i klas](05_szablony_i_generycznosc/01_function_i_class_templates.md)
2. [Dedukcja, auto, decltype i CTAD](05_szablony_i_generycznosc/02_dedukcja_auto_decltype_i_ctad.md)
3. [Specialization i SFINAE](05_szablony_i_generycznosc/03_specialization_i_sfinAE.md)
4. [Concepts i requires](05_szablony_i_generycznosc/04_concepts_i_requires.md)
5. [Variadic templates i fold expressions](05_szablony_i_generycznosc/05_variadic_templates_i_fold.md)
6. [constexpr, consteval i metaprogramowanie](05_szablony_i_generycznosc/06_constexpr_consteval_i_metaprogramowanie.md)
7. [Projektowanie interfejsów generycznych](05_szablony_i_generycznosc/07_projektowanie_interfejsow_generycznych.md)

## 06. Biblioteka standardowa

[Mapa i wymagania](06_biblioteka_standardowa/README.md) · [Zestaw ćwiczeń](06_biblioteka_standardowa/ZESTAW-CWICZEN.md)

1. [string, string_view i tekst](06_biblioteka_standardowa/01_string_string_view_i_tekst.md)
2. [vector, array, deque i list](06_biblioteka_standardowa/02_vector_array_deque_list.md)
3. [map, set, unordered i hash](06_biblioteka_standardowa/03_map_set_unordered_i_hash.md)
4. [Iteratory i invalidacja](06_biblioteka_standardowa/04_iteratory_i_invalidacja.md)
5. [Algorytmy i lambdy](06_biblioteka_standardowa/05_algorytmy_i_lambdy.md)
6. [Ranges i views](06_biblioteka_standardowa/06_ranges_i_views.md)
7. [tuple, pair, variant i any](06_biblioteka_standardowa/07_tuple_pair_variant_any.md)
8. [Unicode, UTF-8 i ścisłe parsowanie](06_biblioteka_standardowa/08_unicode_utf8_i_parsowanie.md)

## 07. Błędy i kontrakty

[Mapa i wymagania](07_bledy_i_kontrakty/README.md) · [Zestaw ćwiczeń](07_bledy_i_kontrakty/ZESTAW-CWICZEN.md)

1. [Wyjątki: try, catch i throw](07_bledy_i_kontrakty/01_wyjatki_try_catch_throw.md)
2. [RAII, exception safety i noexcept](07_bledy_i_kontrakty/02_raii_exception_safety_i_noexcept.md)
3. [optional, expected i kody błędów](07_bledy_i_kontrakty/03_optional_expected_i_kody_bledow.md)
4. [Assertions, preconditions i contracts](07_bledy_i_kontrakty/04_assertions_preconditions_i_contracts.md)

## 08. Budowanie i organizacja

[Mapa i wymagania](08_budowanie_i_organizacja/README.md) · [Zestaw ćwiczeń](08_budowanie_i_organizacja/ZESTAW-CWICZEN.md)

1. [Translation units, nagłówki i include](08_budowanie_i_organizacja/01_translation_units_headers_i_include.md)
2. [Linkowanie, ODR i inline](08_budowanie_i_organizacja/02_linkowanie_odr_i_inline.md)
3. [Namespaces, visibility i ADL](08_budowanie_i_organizacja/03_namespaces_visibility_i_adl.md)
4. [Moduły C++](08_budowanie_i_organizacja/04_moduly_cpp.md)
5. [CMake](08_budowanie_i_organizacja/05_cmake.md)
6. [Conan, vcpkg i zależności](08_budowanie_i_organizacja/06_conan_vcpkg_i_zaleznosci.md)

## 09. Testowanie i jakość

[Mapa i wymagania](09_testowanie_i_jakosc/README.md) · [Zestaw ćwiczeń](09_testowanie_i_jakosc/ZESTAW-CWICZEN.md)

1. [Testy jednostkowe i integracyjne](09_testowanie_i_jakosc/01_testy_jednostkowe_i_integracyjne.md)
2. [Ostrzeżenia i analiza statyczna](09_testowanie_i_jakosc/02_ostrzezenia_i_analiza_statyczna.md)
3. [Sanitizery i debuggery](09_testowanie_i_jakosc/03_sanitizery_i_debuggery.md)
4. [Benchmarki i profilowanie](09_testowanie_i_jakosc/04_benchmarki_i_profilowanie.md)
5. [Fuzzing i property-based testing](09_testowanie_i_jakosc/05_fuzzing_i_property_based_testing.md)

## 10. Współbieżność

[Mapa i wymagania](10_wspolbieznosc/README.md) · [Zestaw ćwiczeń](10_wspolbieznosc/ZESTAW-CWICZEN.md)

1. [thread, jthread i stop_token](10_wspolbieznosc/01_thread_jthread_i_stop_token.md)
2. [mutex, lock i condition_variable](10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)
3. [future, promise i async](10_wspolbieznosc/03_future_promise_async.md)
4. [Atomiki i model pamięci](10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
5. [latch, barrier i semaphore](10_wspolbieznosc/05_latch_barrier_semaphore.md)
6. [Ograniczona kolejka, backpressure i zamykanie](10_wspolbieznosc/06_kolejka_backpressure_i_zamykanie.md)

## 11. I/O i system

[Mapa i wymagania](11_io_i_system/README.md) · [Zestaw ćwiczeń](11_io_i_system/ZESTAW-CWICZEN.md)

1. [Strumienie i formatowanie](11_io_i_system/01_strumienie_i_formatowanie.md)
2. [Pliki i filesystem](11_io_i_system/02_pliki_i_filesystem.md)
3. [chrono i czas](11_io_i_system/03_chrono_i_czas.md)
4. [random i numeryka](11_io_i_system/04_random_i_numeryka.md)
5. [Sieć, serializacja i granice std](11_io_i_system/05_siec_serializacja_i_granice_std.md)

## 12. Współczesny C++

[Mapa i wymagania](12_wspolczesny_cpp/README.md) · [Zestaw ćwiczeń](12_wspolczesny_cpp/ZESTAW-CWICZEN.md)

1. [C++11 i C++14](12_wspolczesny_cpp/01_cpp11_14.md)
2. [C++17](12_wspolczesny_cpp/02_cpp17.md)
3. [C++20](12_wspolczesny_cpp/03_cpp20.md)
4. [C++23](12_wspolczesny_cpp/04_cpp23.md)
5. [Korutyny](12_wspolczesny_cpp/05_korutyny.md)
6. [Feature-test macros i przenośność](12_wspolczesny_cpp/06_feature_test_macros_i_przenosnosc.md)

## 13. Wzorce, API i wydajność

[Mapa i wymagania](13_wzorce_api_i_wydajnosc/README.md) · [Zestaw ćwiczeń](13_wzorce_api_i_wydajnosc/ZESTAW-CWICZEN.md)

1. [Rule of zero, PImpl i Non-Virtual Interface](13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md)
2. [Value semantics i type erasure](13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md)
3. [Projektowanie API i ABI](13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md)
4. [Architektura i dependency injection](13_wzorce_api_i_wydajnosc/04_architektura_i_dependency_injection.md)
5. [Wydajność, cache i zero-overhead](13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

## 14. Warsztat profesjonalisty

[Mapa i wymagania](14_warsztat_profesjonalisty/README.md) · [Zestaw ćwiczeń](14_warsztat_profesjonalisty/ZESTAW-CWICZEN.md)

1. [Formatowanie: clang-format i EditorConfig](14_warsztat_profesjonalisty/01_formatowanie_clang_format_editorconfig.md)
2. [Analiza statyczna: clang-tidy i Cppcheck](14_warsztat_profesjonalisty/02_analiza_statyczna_clang_tidy_cppcheck.md)
3. [CMake Presets i Ninja](14_warsztat_profesjonalisty/03_cmake_presets_i_ninja.md)
4. [Dokumentacja: Doxygen i diagramy](14_warsztat_profesjonalisty/04_dokumentacja_doxygen_i_diagramy.md)
5. [Git i praca z repozytorium](14_warsztat_profesjonalisty/05_git_i_praca_z_repozytorium.md)
6. [Automatyzacja lokalna i pre-commit](14_warsztat_profesjonalisty/06_automatyzacja_lokalna_i_pre_commit.md)

## 15. Bezpieczny C++

[Mapa i wymagania](15_bezpieczny_cpp/README.md) · [Zestaw ćwiczeń](15_bezpieczny_cpp/ZESTAW-CWICZEN.md)

1. [Model zagrożeń i granice zaufania](15_bezpieczny_cpp/01_model_zagrozen_i_granice_zaufania.md)
2. [Bezpieczne API i typy](15_bezpieczny_cpp/02_bezpieczne_api_i_typy.md)
3. [Walidacja danych i arytmetyka](15_bezpieczny_cpp/03_walidacja_danych_i_arytmetyka.md)
4. [Bezpieczeństwo pamięci i lifetime](15_bezpieczny_cpp/04_bezpieczenstwo_pamieci_i_lifetime.md)
5. [Pliki ścieżki i procesy](15_bezpieczny_cpp/05_pliki_sciezki_i_procesy.md)
6. [Hardening i sanitizery](15_bezpieczny_cpp/06_hardening_i_sanitizery.md)

## 16. Biblioteki, pakiety i dystrybucja

[Mapa i wymagania](16_biblioteki_pakiety_i_dystrybucja/README.md) · [Zestaw ćwiczeń](16_biblioteki_pakiety_i_dystrybucja/ZESTAW-CWICZEN.md)

1. [Typy bibliotek i struktura pakietu](16_biblioteki_pakiety_i_dystrybucja/01_typy_bibliotek_i_struktura_pakietu.md)
2. [CMake install export i find package](16_biblioteki_pakiety_i_dystrybucja/02_cmake_install_export_i_find_package.md)
3. [Conan w praktyce](16_biblioteki_pakiety_i_dystrybucja/03_conan_w_praktyce.md)
4. [Vcpkg w praktyce](16_biblioteki_pakiety_i_dystrybucja/04_vcpkg_w_praktyce.md)
5. [Wersjonowanie ABI i publikacja artefaktów](16_biblioteki_pakiety_i_dystrybucja/05_wersjonowanie_abi_i_publikacja_artefaktow.md)

## 17. Runtime, kompilator i ABI

[Mapa i wymagania](17_runtime_kompilator_i_abi/README.md) · [Zestaw ćwiczeń](17_runtime_kompilator_i_abi/ZESTAW-CWICZEN.md)

1. [Od main do procesu](17_runtime_kompilator_i_abi/01_od_main_do_procesu.md)
2. [Fazy kompilacji i IR](17_runtime_kompilator_i_abi/02_fazy_kompilacji_i_ir.md)
3. [Symbole linker i ładowanie dynamiczne](17_runtime_kompilator_i_abi/03_symbole_linker_i_ladowanie_dynamiczne.md)
4. [ABI name mangling i wyjątki](17_runtime_kompilator_i_abi/04_abi_name_mangling_i_wyjatki.md)
5. [Diagnostyka kompilatora i linkera](17_runtime_kompilator_i_abi/05_diagnostyka_kompilatora_i_linkera.md)

## 18. Wydajność i optymalizacja

[Mapa i wymagania](18_wydajnosc_i_optymalizacja/README.md) · [Zestaw ćwiczeń](18_wydajnosc_i_optymalizacja/ZESTAW-CWICZEN.md)

1. [Metodologia benchmarków](18_wydajnosc_i_optymalizacja/01_metodologia_benchmarkow.md)
2. [Profilowanie CPU](18_wydajnosc_i_optymalizacja/02_profilowanie_cpu.md)
3. [Profilowanie pamięci i alokacji](18_wydajnosc_i_optymalizacja/03_profilowanie_pamieci_i_alokacji.md)
4. [Cache lokalność i layout danych](18_wydajnosc_i_optymalizacja/04_cache_lokalnosc_i_layout_danych.md)
5. [I/O streaming i backpressure](18_wydajnosc_i_optymalizacja/05_io_streaming_i_backpressure.md)
6. [Wektoryzacja PGO i LTO](18_wydajnosc_i_optymalizacja/06_wektoryzacja_pgo_i_lto.md)

## 19. Debugowanie i utrzymanie

[Mapa i wymagania](19_debugowanie_i_utrzymanie/README.md) · [Zestaw ćwiczeń](19_debugowanie_i_utrzymanie/ZESTAW-CWICZEN.md)

1. [Strategia debugowania i MRE](19_debugowanie_i_utrzymanie/01_strategia_debugowania_i_mre.md)
2. [GDB i LLDB](19_debugowanie_i_utrzymanie/02_gdb_i_lldb.md)
3. [Core dump i crash report](19_debugowanie_i_utrzymanie/03_core_dump_i_crash_report.md)
4. [Regresje git bisect i reprodukcja](19_debugowanie_i_utrzymanie/04_regresje_git_bisect_i_reprodukcja.md)
5. [Diagnostyka wielowątkowości](19_debugowanie_i_utrzymanie/05_diagnostyka_wielowatkowosci.md)
6. [Refaktoryzacja starego kodu](19_debugowanie_i_utrzymanie/06_refaktoryzacja_starego_kodu.md)

## 20. Testowanie systemowe

[Mapa i wymagania](20_testowanie_systemowe/README.md) · [Zestaw ćwiczeń](20_testowanie_systemowe/ZESTAW-CWICZEN.md)

1. [Strategia i piramida testów](20_testowanie_systemowe/01_strategia_i_piramida_testow.md)
2. [Testy integracyjne i E2E](20_testowanie_systemowe/02_testy_integracyjne_i_e2e.md)
3. [Testy kontraktowe](20_testowanie_systemowe/03_testy_kontraktowe.md)
4. [Fake mock stub i seams](20_testowanie_systemowe/04_fake_mock_stub_i_seams.md)
5. [Fixtures builders i dane testowe](20_testowanie_systemowe/05_fixtures_builders_i_dane_testowe.md)
6. [Flaky tests i testy niefunkcjonalne](20_testowanie_systemowe/06_flaky_tests_i_testy_niefunkcjonalne.md)

## 21. Sieci, protokoły i API

[Mapa i wymagania](21_sieci_protokoly_i_api/README.md) · [Zestaw ćwiczeń](21_sieci_protokoly_i_api/ZESTAW-CWICZEN.md)

1. [Modele sieci TCP UDP i DNS](21_sieci_protokoly_i_api/01_modele_sieci_tcp_udp_i_dns.md)
2. [HTTP i REST](21_sieci_protokoly_i_api/02_http_i_rest.md)
3. [TLS certyfikaty i zaufanie](21_sieci_protokoly_i_api/03_tls_certyfikaty_i_zaufanie.md)
4. [Serializacja JSON Protobuf i schema](21_sieci_protokoly_i_api/04_serializacja_json_protobuf_i_schema.md)
5. [Klient HTTP: timeouty, retry i pooling](21_sieci_protokoly_i_api/05_klient_http_timeouty_retry_i_pooling.md)
6. [Serwer API limity i testy](21_sieci_protokoly_i_api/06_serwer_api_limity_i_testy.md)

## 22. Bazy danych i trwałość

[Mapa i wymagania](22_bazy_danych_i_trwalosc/README.md) · [Zestaw ćwiczeń](22_bazy_danych_i_trwalosc/ZESTAW-CWICZEN.md)

1. [SQL i model relacyjny](22_bazy_danych_i_trwalosc/01_sql_i_model_relacyjny.md)
2. [SQLite i RAII połączenia](22_bazy_danych_i_trwalosc/02_sqlite_i_raii_polaczenia.md)
3. [Transakcje i poziomy izolacji](22_bazy_danych_i_trwalosc/03_transakcje_i_poziomy_izolacji.md)
4. [Prepared statements i bezpieczeństwo](22_bazy_danych_i_trwalosc/04_prepared_statements_i_bezpieczenstwo.md)
5. [Migracje pooling i odporność](22_bazy_danych_i_trwalosc/05_migracje_pooling_i_odpornosc.md)
6. [Repozytoria i case study](22_bazy_danych_i_trwalosc/06_repozytoria_i_case_study.md)

## 23. Architektura aplikacji produkcyjnych

[Mapa i wymagania](23_architektura_aplikacji_produkcyjnych/README.md) · [Zestaw ćwiczeń](23_architektura_aplikacji_produkcyjnych/ZESTAW-CWICZEN.md)

1. [Granice modułów i zależności](23_architektura_aplikacji_produkcyjnych/01_granice_modulow_i_zaleznosci.md)
2. [Konfiguracja i sekrety](23_architektura_aplikacji_produkcyjnych/02_konfiguracja_i_sekrety.md)
3. [Dependency injection i composition root](23_architektura_aplikacji_produkcyjnych/03_dependency_injection_i_composition_root.md)
4. [Obsługa błędów i odporność](23_architektura_aplikacji_produkcyjnych/04_obsluga_bledow_i_odpornosc.md)
5. [Zadania w tle i shutdown](23_architektura_aplikacji_produkcyjnych/05_zadania_w_tle_i_shutdown.md)
6. [Case study usługa produkcyjna](23_architektura_aplikacji_produkcyjnych/06_case_study_usluga_produkcyjna.md)

## 24. Messaging i systemy rozproszone

[Mapa i wymagania](24_messaging_i_systemy_rozproszone/README.md) · [Zestaw ćwiczeń](24_messaging_i_systemy_rozproszone/ZESTAW-CWICZEN.md)

1. [Kolejki brokerzy i delivery](24_messaging_i_systemy_rozproszone/01_kolejki_brokerzy_i_delivery.md)
2. [Retry backoff i idempotencja](24_messaging_i_systemy_rozproszone/02_retry_backoff_i_idempotencja.md)
3. [Eventual consistency i sagi](24_messaging_i_systemy_rozproszone/03_eventual_consistency_i_sagi.md)
4. [RabbitMQ Kafka i NATS](24_messaging_i_systemy_rozproszone/04_rabbitmq_kafka_i_nats.md)
5. [Outbox inbox i deduplication](24_messaging_i_systemy_rozproszone/05_outbox_inbox_i_deduplication.md)
6. [Case study system zamówień](24_messaging_i_systemy_rozproszone/06_case_study_system_zamowien.md)

## 25. Kontenery i produkcja

[Mapa i wymagania](25_kontenery_i_produkcja/README.md) · [Zestaw ćwiczeń](25_kontenery_i_produkcja/ZESTAW-CWICZEN.md)

1. [Kontenery i proces C++](25_kontenery_i_produkcja/01_kontenery_i_proces_cpp.md)
2. [Dockerfile wieloetapowy i hardening](25_kontenery_i_produkcja/02_dockerfile_wieloetapowy_i_hardening.md)
3. [Docker compose i zależności](25_kontenery_i_produkcja/03_docker_compose_i_zaleznosci.md)
4. [Konfiguracja limity i sygnały](25_kontenery_i_produkcja/04_konfiguracja_limity_i_sygnaly.md)
5. [Healthcheck debugowanie i case study](25_kontenery_i_produkcja/05_healthcheck_debugowanie_i_case_study.md)

## 26. CI/CD i release engineering

[Mapa i wymagania](26_ci_cd_i_release_engineering/README.md) · [Zestaw ćwiczeń](26_ci_cd_i_release_engineering/ZESTAW-CWICZEN.md)

1. [Pipeline build test analyze](26_ci_cd_i_release_engineering/01_pipeline_build_test_analyze.md)
2. [Macierze kompilatorów i platform](26_ci_cd_i_release_engineering/02_macierze_kompilatorow_i_platform.md)
3. [Quality gates i cache](26_ci_cd_i_release_engineering/03_quality_gates_i_cache.md)
4. [Artefakty SBOM i podpisy](26_ci_cd_i_release_engineering/04_artefakty_sbom_i_podpisy.md)
5. [Wersjonowanie changelog i release](26_ci_cd_i_release_engineering/05_wersjonowanie_changelog_i_release.md)
6. [Deployment rollback i hotfix](26_ci_cd_i_release_engineering/06_deployment_rollback_i_hotfix.md)

## 27. Obserwowalność i monitoring

[Mapa i wymagania](27_obserwowalnosc_i_monitoring/README.md) · [Zestaw ćwiczeń](27_obserwowalnosc_i_monitoring/ZESTAW-CWICZEN.md)

1. [Logi strukturalne i korelacja](27_obserwowalnosc_i_monitoring/01_logi_strukturalne_i_korelacja.md)
2. [Metryki i histogramy](27_obserwowalnosc_i_monitoring/02_metryki_i_histogramy.md)
3. [Tracing i OpenTelemetry](27_obserwowalnosc_i_monitoring/03_tracing_i_opentelemetry.md)
4. [Health readiness i liveness](27_obserwowalnosc_i_monitoring/04_health_readiness_i_liveness.md)
5. [Crash reporting i symbole](27_obserwowalnosc_i_monitoring/05_crash_reporting_i_symbole.md)
6. [Case study incydent produkcyjny](27_obserwowalnosc_i_monitoring/06_case_study_incydent_produkcyjny.md)

## 28. Wieloplatformowość, FFI i pluginy

[Mapa i wymagania](28_wieloplatformowosc_ffi_i_pluginy/README.md) · [Zestaw ćwiczeń](28_wieloplatformowosc_ffi_i_pluginy/ZESTAW-CWICZEN.md)

1. [Warstwy platformowe i porty](28_wieloplatformowosc_ffi_i_pluginy/01_warstwy_platformowe_i_porty.md)
2. [FFI C i stabilne ABI](28_wieloplatformowosc_ffi_i_pluginy/02_ffi_c_i_stabilne_abi.md)
3. [Biblioteki dynamiczne i pluginy](28_wieloplatformowosc_ffi_i_pluginy/03_biblioteki_dynamiczne_i_pluginy.md)
4. [Wersjonowanie pluginów i capabilities](28_wieloplatformowosc_ffi_i_pluginy/04_wersjonowanie_pluginow_i_capabilities.md)
5. [Cross compilation i toolchain files](28_wieloplatformowosc_ffi_i_pluginy/05_cross_compilation_i_toolchain_files.md)
6. [Dystrybucja windows linux macos](28_wieloplatformowosc_ffi_i_pluginy/06_dystrybucja_windows_linux_macos.md)

## 29. Bezpieczeństwo supply chain

[Mapa i wymagania](29_bezpieczenstwo_supply_chain/README.md) · [Zestaw ćwiczeń](29_bezpieczenstwo_supply_chain/ZESTAW-CWICZEN.md)

1. [Model zagrożeń secure SDLC i sekrety](29_bezpieczenstwo_supply_chain/01_model_zagrozen_secure_sdlc_i_sekrety.md)
2. [Zależności CVE i SCA](29_bezpieczenstwo_supply_chain/02_zaleznosci_cve_i_sca.md)
3. [SBOM podpisy i proweniencja](29_bezpieczenstwo_supply_chain/03_sbom_podpisy_i_proweniencja.md)
4. [Fuzzing parsowanie i protokoły](29_bezpieczenstwo_supply_chain/04_fuzzing_parsowanie_i_protokoly.md)
5. [Incydenty patchowanie i case study](29_bezpieczenstwo_supply_chain/05_incydenty_patchowanie_i_case_study.md)

## 30. Projekty premium

[Mapa i wymagania](30_projekty_premium/README.md) · [Zestaw ćwiczeń](30_projekty_premium/ZESTAW-CWICZEN.md)

1. [Narzędzia CLI i automatyzacja](30_projekty_premium/01_narzedzia_cli_i_automatyzacja.md)
2. [Systemy plikowe i wyszukiwanie](30_projekty_premium/02_systemy_plikowe_i_wyszukiwanie.md)
3. [Parsery, interpretery i silniki](30_projekty_premium/03_parsery_interpretery_i_silniki.md)
4. [Sieć, bazy i usługi](30_projekty_premium/04_siec_bazy_i_uslugi.md)
5. [Współbieżność, runtime i obserwowalność](30_projekty_premium/05_wspolbieznosc_runtime_i_obserwowalnosc.md)
6. [Systemy rozproszone i capstone](30_projekty_premium/06_systemy_rozproszone_i_capstone.md)

## Zagadnienia zaawansowane

[Mapa i wymagania wstępne](zaawansowane/README.md)

1. [Undefined behavior i model maszyny](zaawansowane/01_undefined_behavior_i_model_maszyny.md)
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

- [Ścieżka pogłębionej nauki](sciezka_nauki.md)
- [24 problemy diagnostyczne](test_diagnostyczny.md)
- [78 zadań z rozwiązaniami](cwiczenia/README.md)
- [Trzy laboratoria i instrukcja uruchomienia](praktyka/README.md)
- [Dwanaście rozszerzeń laboratoriów](praktyka/ZADANIA.md)
- [Mapa trzydziestu projektów portfolio](Projekty.md)
- [150 zaawansowanych mechanizmów](150-zaawansowanych-mechanizmow-cpp.md)
- [Ściąga](sciaga.md), [słownik](slownik.md), [specjalizacje](dalsza_nauka.md)
- [Źródła](zrodla.md), [zasady redakcyjne](CONTRIBUTING.md), [raport](RAPORT_KONCOWY.md)

## Weryfikacja

Z katalogu głównego repozytorium:

~~~text
python3 -m unittest discover -s scripts -p 'test_*.py' -v
bash scripts/verify.sh
python3 scripts/verify_content.py --metadata-only --metrics
cmake -S praktyka -B build/praktyka-debug -DCMAKE_BUILD_TYPE=Debug
cmake --build build/praktyka-debug --config Debug
ctest --test-dir build/praktyka-debug -C Debug --output-on-failure
~~~

Opcje `--section`, presety Debug/Release/UBSan i różnice generatorów opisano w [laboratoriach](praktyka/README.md) i zasadach redakcyjnych. Konfiguracja CI znajduje się w [workflow](.github/workflows/verify.yml); dodanie pliku nie oznacza, że wykonano już zdalny przebieg.
