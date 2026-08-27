[← Spis treści](../README.md)

# Zagadnienia zaawansowane

Ten dział zakłada swobodne rozumienie lifetime obiektów, RAII, copy/move, szablonów, concepts, ODR i modelu współbieżności. Nie jest listą sztuczek. Jego celem jest pokazanie kontraktów, na których zbudowane są bezpieczne abstrakcje biblioteczne i wydajny kod systemowy.

Operacja niskopoziomowa może się skompilować, a mimo to naruszać standard. W C++ nie ma jednego bloku `unsafe`, który oznacza wszystkie miejsca wymagające dowodu. Obowiązek może wynikać z dereferencji wskaźnika, lifetime, aliasowania, data race, precondition biblioteki, ABI lub inline assembly. Każda otoczka powinna lokalizować ryzyko, nazywać inwariant i testować granice sanitizerami oraz wieloma kompilatorami.

Każdy rozdział oddziela gwarancję abstract machine od konwencji ABI i heurystyki implementacji. Czytając materiał, najpierw nazwij normatywny kontrakt, następnie wskaż obserwowalny skutek, a dopiero na końcu analizuj assembly, layout lub profil. Wynik jednego kompilatora jest dowodem dla konkretnej konfiguracji, nie nową regułą języka.

## Zalecana kolejność

1. [Undefined behavior i abstract machine](01_undefined_behavior_i_model_maszyny.md)
2. [Lifetime, aliasing i pointer provenance](02_lifetime_aliasing_i_pointer_provenance.md)
3. [Layout, alignment, padding i triviality](03_layout_alignment_padding_i_triviality.md)
4. [Alokatory, PMR i new/delete](04_allocatory_pmr_i_new_delete.md)
5. [Value categories i perfect forwarding](05_value_categories_i_perfect_forwarding.md)
6. [Overload resolution, ADL i hidden friends](06_overload_resolution_adl_i_hidden_friends.md)
7. [Dependent names, two-phase lookup i SFINAE](07_dependent_names_two_phase_lookup_i_sfinae.md)
8. [Concept normalization i subsumption](08_concepts_normalization_i_subsumption.md)
9. [constexpr, consteval i compile time](09_constexpr_consteval_i_compile_time.md)
10. [Type erasure, vtables, ABI i visibility](10_type_erasure_vtables_abi_i_visibility.md)
11. [Memory ordering, lock-free, ABA i reclamation](11_memory_ordering_lock_free_aba_i_reclamation.md)
12. [Korutyny: promise, awaitery i frame](12_korutyny_promise_awaitery_i_frame.md)
13. [ODR, moduły, FFI i interoperacyjność](13_odr_moduly_ffi_i_interoperacyjnosc.md)
14. [SIMD, wektoryzacja, cache i optymalizacja](14_simd_wektoryzacja_cache_i_optymalizacja.md)
15. [C++26 i nadchodzące funkcje](15_cpp26_i_nadchodzace_funkcje.md)

## Jak czytać przykłady

Bloki `cpp` są bezpiecznymi, samowystarczalnymi jednostkami C++23 kompilowanymi przez walidator. `cpp,notest` pokazuje fragment zależny od ABI, przyszłego standardu albo celowo błędny przypadek i nie jest wykonywany ani kompilowany. Nigdy nie kopiuj takiego fragmentu bez odtworzenia jego założeń w swoim środowisku.

## Powiązane tematy

- [Pamięć i czas życia](../03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md)
- [Szablony i generyczność](../05_szablony_i_generycznosc/01_function_i_class_templates.md)
- [Współbieżność](../10_wspolbieznosc/04_atomiki_i_model_pamieci.md)
