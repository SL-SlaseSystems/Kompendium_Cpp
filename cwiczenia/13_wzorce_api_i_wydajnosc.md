[← Mapa działu](../13_wzorce_api_i_wydajnosc/README.md) · [Spis treści](../README.md)

# Ćwiczenia: koszt decyzji projektowej

Zapisuj alternatywy, wymagany kontrakt i dowód wyboru. Uzasadnienie „to popularny wzorzec” nie wystarcza. Rozwiązania oceniaj także według wpływu na klienta, testowalność, kopiowanie, alokacje i możliwość przyszłych zmian.

## 1. PImpl, który przestał się przenosić

**Wejście:** `Connection` przechowuje `unique_ptr<Impl>`, deklaruje własny destruktor i ma być move-only. Po dodaniu destruktora klient nie może powiększyć `vector<Connection>`. **Oddaj:** listę funkcji specjalnych oraz ich miejsca definicji. Ustal legalne operacje na obiekcie po przeniesieniu. **Wskazówka:** własny destruktor wpływa na niejawne generowanie przenoszenia.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Jawnie usuń kopiowanie i zadeklaruj konstruktor oraz przypisanie przenoszące. Destruktor i odpowiednie operacje zdefiniuj poza nagłówkiem po kompletnej definicji `Impl`, gdzie deleter może usuwać obiekt. Uzasadnij noexcept operacji przenoszenia. Dopuść zniszczenie i ponowne przypisanie pustej instancji, a zachowanie metod korzystających z implementacji opisz jawnie. [PImpl](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md).

</details>

## 2. Callback posiadający niekopiowalny zasób

**Wejście:** zadanie przechwytuje `unique_ptr<Job>` przez przeniesienie; scheduler tylko przenosi zadania i wykonuje je raz. Obecny magazyn to `std::function<void()>`. **Oddaj:** diagnozę oraz reprezentację C++23 zgodną z wymaganiami. Zdefiniuj zachowanie pustego zadania i zakaz powtórnego wykonania. **Wskazówka:** type erasure ma własne wymagania dotyczące kopiowania celu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Cel takiej lambdy nie jest kopiowalny, a `std::function` wymaga kopiowalnego celu. Użyj `std::move_only_function<void()>` albo własnego interfejsu move-only. Sprawdzaj obecność zadania przed wywołaniem; pustej `move_only_function` nie wolno wywoływać. Jednorazowość nie wynika automatycznie z move-only: scheduler musi usunąć lub skonsumować zadanie po wykonaniu. [Type erasure](../13_wzorce_api_i_wydajnosc/02_value_semantics_i_type_erasure.md).

</details>

## 3. Prywatne pole zmienia publiczne ABI

**Wejście:** dostawca biblioteki dodaje `int cache_` do publicznie zdefiniowanej klasy i podmienia bibliotekę bez rekompilacji klientów. Metody oraz publiczne sygnatury pozostają takie same. **Oddaj:** ocenę zgodności źródłowej i binarnej oraz strategię ograniczania podobnych zmian. Uwzględnij klienta tworzącego tablicę obiektów. **Wskazówka:** prywatność kontroluje dostęp w języku, nie wiedzę klienta o rozmiarze.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Stary klient zna poprzedni rozmiar i układ klasy; dodatkowe pole może zmienić oba, psując alokacje, przesunięcia i krok tablicy. Zgodność źródeł po przebudowaniu nie gwarantuje binarnej. PImpl może ukrywać zmiany reprezentacji, lecz stabilność wymaga także określenia ABI toolchainu, eksportu symboli i typów na granicy. [API i ABI](../13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md).

</details>

## 4. Wygaśnięcie bez zegara globalnego

**Wejście:** cache uznaje wpis za ważny, gdy `now < deadline`; testy śpią sekundę i sporadycznie zawodzą. **Oddaj:** interfejs zależności czasu i trzy deterministyczne testy. Zdecyduj, czy potrzebujesz metody wirtualnej, parametru funkcji czy szablonu. **Wskazówka:** test powinien sterować przyczyną decyzji, a nie tempem działania systemu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Przekazuj źródło czasu przez konstruktor albo bieżący punkt do czystej operacji. Testuj `deadline-1`, dokładnie `deadline` i `deadline+1` w jednostce przyjętego zegara: tylko pierwszy wpis jest ważny. Dla timeoutów wybierz czas monotoniczny. Sposób wstrzyknięcia zależy od granicy API i kosztu wywołania; prosta funkcja często wystarcza. [Dependency injection](../13_wzorce_api_i_wydajnosc/04_architektura_i_dependency_injection.md).

</details>

## 5. Profil wskazuje ruch pamięci

**Wejście:** dziesięć milionów rekordów po 256 bajtów jest skanowanych tylko po to, aby zsumować jedno pole `double`. Aktualizacje całych rekordów są rzadkie. **Oddaj:** hipotezę zmiany reprezentacji i eksperyment z zachowaniem identycznych danych. Uwzględnij koszt aktualizacji i dodatkową pamięć. **Wskazówka:** skrócenie ciała pętli nie usuwa niepotrzebnego ruchu linii cache.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Porównaj AoS z wydzielonym zwartym polem lub SoA. Zmiana może poprawić lokalność skanu i wektoryzację, ale wymaga utrzymywania zgodności kolumn oraz mierzenia całego scenariusza. Kontroluj rozgrzanie, rozmiar, optymalizację i konsumowanie wyniku; sprawdź poprawność sumy z przyjętą tolerancją. Nie obiecuj przyspieszenia przed pomiarem na docelowym sprzęcie. [Cache i wydajność](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md).

</details>

## 6. Rozszerzenia omijające wspólną walidację

**Wejście:** trzy klasy eksportera implementują publiczne wirtualne `export_data`; jedna zapomina sprawdzić limit rozmiaru. Każda ma identycznie obsługiwać limit i rejestrować udane operacje. **Oddaj:** projekt NVI oraz politykę wyjątku specjalistycznego etapu. **Wskazówka:** wspólny wrapper powinien kontrolować również moment uznania sukcesu.

<details><summary>Rozwiązanie i uzasadnienie</summary>

Publiczna niewirtualna metoda sprawdza limit, wywołuje prywatny lub chroniony wirtualny etap, a po sukcesie rejestruje wynik. Klasy pochodne dostarczają tylko etap specjalistyczny. Po błędzie etapu propaguj wyjątek, pomiń wpis sukcesu i traktuj wyjście jako potencjalnie niekompletne. Błąd późniejszej rejestracji oznacza „eksport wykonany, diagnostyka nieudana”; nie udawaj cofnięcia eksportu. NVI centralizuje politykę, lecz nie czyni zewnętrznego I/O automatyczną transakcją. [Non-Virtual Interface](../13_wzorce_api_i_wydajnosc/01_rule_of_zero_pimpl_i_non_virtual_interface.md).

</details>
