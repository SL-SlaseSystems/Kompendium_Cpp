[← Spis treści](../README.md)

# Alokatory, PMR i new/delete

Wyrażenie `new T(args...)` łączy uzyskanie storage z konstrukcją obiektu. `delete` wywołuje destruktor i zwalnia storage. Funkcje `operator new/delete` zajmują się surową pamięcią i mogą być przeciążane globalnie lub dla klasy, lecz poprawne wsparcie rozmiaru, alignment, tablic oraz wyjątków jest złożone.

Allocator-aware containers oddzielają politykę pamięci od kontenera. Klasyczne allocators są częścią typu kontenera. Polymorphic memory resources z `<memory_resource>` przenoszą wybór strategii do runtime, a `std::pmr::vector<T>` używa `polymorphic_allocator`.

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <memory_resource>
#include <vector>

int main() {
    std::array<std::byte, 1024> buffer{};
    std::pmr::monotonic_buffer_resource arena{buffer.data(), buffer.size()};
    std::pmr::vector<int> values{&arena};

    values.assign({10, 20, 12});
    assert(values[0] + values[1] + values[2] == 42);
}
~~~

Monotonic resource przydziela szybko i zwalnia pamięć grupowo przy destrukcji zasobu; indywidualne deallocation jest zwykle no-op. Kontenery nadal wywołują destruktory elementów. Obiekt korzystający z resource nie może go przeżyć, a przenoszenie między kontenerami z różnymi resource ma szczegółowe reguły.

Pool resources pomagają dla wielu podobnych alokacji. `unsynchronized_pool_resource` nie jest bezpieczny do równoczesnego dostępu, a `synchronized_pool_resource` płaci za synchronizację. PMR nie usuwa kosztu konstrukcji ani automatycznie nie poprawia cache.

Placement new i `construct_at` wymagają ręcznego zarządzania lifetime. Implementując kontener, licz skonstruowane elementy, aby wyjątek posprzątał tylko te istniejące. Preferuj sprawdzone kontenery; własna arena ma sens dopiero po profilu i jasnym modelu zwalniania.

## Jak to działa krok po kroku

W pierwszym przykładzie kolejność deklaracji tworzy bufor, następnie zasób, a na końcu wektor. Destrukcja zachodzi odwrotnie: wektor najpierw niszczy elementy, zasób odzyskuje przydziały, a bufor kończy życie ostatni. To istotna część poprawności. Sam `polymorphic_allocator` przechowuje odniesienie do strategii pamięci, ale nie zarządza lifetime obiektu `memory_resource`.

Przy `values.assign` kontener pyta zasób o odpowiedni rozmiar i alignment. Arena próbuje obsłużyć żądanie z lokalnego bufora, uwzględniając straty wyrównania. Gdy zabraknie miejsca, domyślnie korzysta z upstream resource. Mała tablica na stosie nie jest więc gwarancją zakazu alokacji dynamicznych. Taki zakaz można wyrazić dopiero przez `null_memory_resource`, który odrzuca dodatkowe żądania wyjątkiem `bad_alloc`.

## Pogłębienie mechanizmu

Wyrażenie `new T` i funkcja `operator new` mają różne obowiązki. Pierwsze uruchamia konstruktor; druga uzyskuje storage. Jeśli konstruktor rzuci po udanej alokacji, new-expression wywołuje odpowiednią funkcję dealokującą. Kod ręcznie wywołujący `allocate` oraz `construct_at` musi odtworzyć tę ochronę sam. Przy tablicy częściowo skonstruowanej trzeba zniszczyć tylko te elementy, których konstrukcja zakończyła się sukcesem.

`allocator_traits` ujednolica interfejs alokatorów i określa zachowanie ich propagacji przy kopiowaniu, przenoszeniu i zamianie kontenerów. Przeniesienie wektora nie zawsze oznacza przejęcie trzech wskaźników: gdy alokatory nie propagują się i są nierówne, przydział należy do innego zasobu, więc elementy mogą wymagać osobnego przeniesienia. Warunki `noexcept` i złożoność wynikają z tych zasad, a nie wyłącznie z obecności `std::move`.

Dla PMR kopiowanie kontenera i jawny konstruktor z alokatorem mogą wybierać zasób inaczej. Nie zakładaj, że kopia odziedziczy arenę źródła; zachowanie `select_on_container_copy_construction` dla `polymorphic_allocator` prowadzi do domyślnego zasobu. Zamiana kontenerów z nierównymi alokatorami niepropagującymi alokatora może naruszać kontrakt. Z kolei wewnętrzne napisy użyją tej samej strategii tylko wtedy, gdy ich typ i sposób konstrukcji uczestniczą w protokole uses-allocator; zwykły `std::string` w PMR-wektorze nadal ma własny alokator.

Arena monotoniczna nie odzyskuje indywidualnych bloków. Realokacja wektora zostawia zatem poprzedni blok zajęty aż do `release` lub destrukcji zasobu. `reserve` może ograniczyć szczytowe zużycie pamięci bardziej niż sama zmiana implementacji alokatora. `release` nie wywołuje destruktorów obiektów korzystających z pamięci: najpierw trzeba zakończyć ich życie. Pozostawienie aktywnego wektora po `release` daje wiszące wskaźniki, nawet gdy jego `size()` nadal wygląda rozsądnie.

## Drugi przykład

~~~cpp
#include <array>
#include <cassert>
#include <cstddef>
#include <memory_resource>
#include <vector>

int main() {
    alignas(std::max_align_t) std::array<std::byte, 1024> bytes{};
    std::pmr::monotonic_buffer_resource arena{
        bytes.data(), bytes.size(), std::pmr::null_memory_resource()};
    {
        std::pmr::vector<int> values{&arena};
        values.reserve(8);
        values.push_back(42);
        assert(values.front() == 42);
    }
    arena.release();
}
~~~

Wektor zostaje zniszczony w wewnętrznym zakresie przed zwolnieniem całej areny. Próba przekroczenia dostępnej pojemności zasobu zgłosi `bad_alloc`; nie przejdzie ukradkiem na domyślną stertę. Rozmiar 1024 jest budżetem tego przykładu, nie wyprowadzoną przez standard uniwersalną pojemnością na osiem elementów każdego typu. Wyrównanie oraz polityka konkretnego kontenera mogą wpływać na zużycie storage.

## Porównanie i decyzje

Arena pasuje do danych o wspólnym końcu życia: drzewa składni, pojedynczego żądania serwera, fazy przetwarzania. Pool lepiej obsługuje wielokrotne zwalnianie i ponowne przydzielanie bloków podobnego rozmiaru. Zasób synchronizowany chroni własne struktury alokatora; nie czyni przechowywanego w nim wektora bezpiecznym współbieżnie. Synchronizacja kontenera pozostaje odrębnym zadaniem.

**Ćwiczenie.** Dlaczego funkcja zwracająca PMR-wektor oparty na lokalnej arenie jest błędna? **Odpowiedź:** zwraca kontener zawierający wskaźniki do pamięci i zasobu, które znikają przy wyjściu. NRVO nie przedłuża życia lokalnej areny. Dlaczego `clear()` nie zeruje wykorzystania areny? Niszczy elementy, lecz wektor zwykle zachowuje pojemność, a arena monotoniczna nie odzyskuje indywidualnych bloków.

Szczegółowe kontrakty: [N4950: memory resources](https://timsong-cpp.github.io/cppwp/n4950/mem.res) i [wymagania alokatorów](https://timsong-cpp.github.io/cppwp/n4950/allocator.requirements).

### Równość zasobów i kontrola kosztów

Dwa obiekty `memory_resource` są równe w sensie alokatora wtedy, gdy pamięć przydzieloną przez jeden można poprawnie zwolnić przez drugi zgodnie z ich kontraktem. Nie wystarcza wspólna klasa implementacji ani identyczny rozmiar bufora. Dwie odrębne areny monotoniczne zwykle nie są wymienne, choć mają tę samą strategię. Zwrócenie bezwarunkowego `true` z `do_is_equal` może skłonić kontener do przekazania bloku niewłaściwemu zasobowi.

Instrumentujący zasób powinien rozróżniać żądane bajty, udane przydziały, bieżące wykorzystanie i maksimum. Zwiększenie licznika przed wywołaniem upstream może zliczać również nieudane żądanie, co nie jest błędem samo w sobie, ale wymaga właściwej nazwy metryki. Osobną wielkością są koszty narzutu alokatora; rozmiar żądania kontenera nie musi równać się liczbie bajtów zarezerwowanych przez system.

Przeciążając globalne `operator new`, łatwo pominąć wersje wyrównane, tablicowe, sized delete lub ścieżki wyjątków. Dodatkowo logowanie wewnątrz alokatora może samo alokować i uruchomić rekurencję. Do obserwacji wybranej struktury PMR daje zwykle węższy, łatwiejszy do sprawdzenia punkt instrumentacji niż globalna ingerencja w przydziały całego procesu.

Pamiętaj również o parowaniu alokacji wyrównanych. Przekazanie pamięci uzyskanej z aligned operator new do niewłaściwego delete może naruszyć kontrakt. Własny zasób powinien traktować argument alignment jako wymaganie, nie opcjonalną sugestię; prawidłowy rozmiar bloku nie rekompensuje źle wyrównanego początku.

## Powiązane tematy

- [Dynamiczna pamięć](../03_pamiec_i_czas_zycia/02_stos_sterta_i_dynamiczna_pamiec.md)
- [Lifetime i provenance](02_lifetime_aliasing_i_pointer_provenance.md)
- [Wydajność i cache](../13_wzorce_api_i_wydajnosc/05_wydajnosc_cache_i_zero_overhead.md)

