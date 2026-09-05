[← Spis treści](README.md)

# Słownik C++

Poniższe definicje łączą polskie wyjaśnienia z terminami spotykanymi w standardzie, diagnostyce i dokumentacji bibliotek.

- **Abstract machine** — model semantyczny programu zdefiniowany przez standard, niezależny od konkretnego procesora.
- **ABI (Application Binary Interface)** — umowa binarna obejmująca m.in. calling convention, layout, symbole i wyjątki.
- **ADL (argument-dependent lookup)** — wyszukiwanie funkcji w przestrzeniach powiązanych z typami argumentów.
- **Aggregate** — typ spełniający warunki agregatu i możliwy do inicjalizacji agregatowej.
- **Aliasing** — dostęp do tego samego obiektu przez różne glvalues/wskaźniki; legalność zależy od typów i lifetime.
- **Alignment** — wymagane wyrównanie adresu obiektu danego typu.
- **Allocator** — obiekt/polityka dostarczająca kontenerowi storage.
- **Atomic operation** — operacja obserwowana jako niepodzielna względem innych wątków.
- **Awaiter** — obiekt definiujący `await_ready`, `await_suspend` i `await_resume` dla `co_await`.
- **Borrowed range** — range, którego iterator może w określonych warunkach przetrwać zniszczenie obiektu range.
- **Cache locality** — bliskość czasowa i przestrzenna dostępów korzystna dla pamięci podręcznej.
- **Class template argument deduction (CTAD)** — dedukcja parametrów szablonu klasy z inicjalizatora.
- **Concept** — nazwany predykat compile-time opisujący wymagania typu lub wartości.
- **Constant expression** — wyrażenie spełniające reguły ewaluacji stałej.
- **Constructor** — funkcja specjalna rozpoczynająca poprawny stan obiektu.
- **Coroutine frame** — storage maszyny stanów korutyny, promise i danych żyjących przez zawieszenie.
- **Copy elision** — pominięcie kopii/przeniesienia; w części przypadków gwarantowane przez standard.
- **Data race** — niezsynchronizowane konfliktujące dostępy wątków; powoduje UB.
- **Dangling** — wskaźnik, referencja, iterator lub widok odnoszący się do zakończonego lifetime/unieważnionej pozycji.
- **Declaration** — wprowadzenie nazwy i jej właściwości.
- **Definition** — deklaracja dostarczająca wymagany byt, ciało lub pełny opis.
- **Dependent name** — nazwa w szablonie, której znaczenie zależy od parametrów.
- **Destructor** — funkcja specjalna kończąca używanie zasobów obiektu.
- **Dynamic dispatch** — wybór implementacji runtime, zwykle przez funkcję wirtualną albo type erasure.
- **Exception safety** — gwarancje dotyczące stanu po rzuceniu wyjątku.
- **Feature-test macro** — makro informujące o obecności i rewizji funkcji języka/biblioteki.
- **Forwarding reference** — referencja rvalue do dedukowanego, niekwalifikowanego cv parametru szablonu typu; w odpowiednich kontekstach także `auto&&`. `const T&&` nie jest forwarding reference, a inicjalizacja `auto&&` z listy ma odrębne reguły.
- **Glvalue** — kategoria wyrażenia reprezentująca tożsamość obiektu lub funkcji.
- **Happens-before** — relacja modelu pamięci określająca widoczność efektów między wykonaniami.
- **Header unit** — nagłówek importowany w mechanizmie modułów według odpowiednich reguł.
- **Hidden friend** — friend zdefiniowany w klasie, zwykle odnajdywany przez ADL.
- **Ill-formed** — program naruszający wymagania składniowe lub semantyczne; diagnostyka zależy od kategorii reguły.
- **Implementation-defined behavior** — wybór implementacji, który musi zostać udokumentowany.
- **Indeterminate value** — kategoria wartości o szczególnych regułach odczytu; nie upraszczaj automatycznie do losowej liczby.
- **Inline** — właściwość ODR pozwalająca na zgodne definicje w wielu jednostkach; nie rozkaz optymalizacji.
- **Instance / instantiation** — utworzenie specjalizacji szablonu dla argumentów.
- **Invariant** — warunek zachowany przez poprawne obserwowalne stany typu.
- **Iterator invalidation** — utrata ważności iteratora wskutek operacji na kontenerze/zakresie.
- **Lifetime** — okres, w którym obiekt istnieje i można legalnie odwoływać się do jego wartości zgodnie z regułami.
- **Linkage** — związek tej samej nazwy/encji między zakresami i jednostkami translacji.
- **Lock-free** — gwarancja postępu systemowego: opóźnienie jednego uczestnika nie zatrzymuje wszystkich operacji. Nie zapewnia ukończenia każdej konkretnej operacji w ograniczonej liczbie jej kroków, czyli wait-free.
- **Lvalue** — glvalue, które nie jest xvalue; typowo nazwany, istniejący obiekt.
- **Memory ordering** — reguły kolejności i widoczności operacji atomowych.
- **Module** — mechanizm eksportu/importu deklaracji bez klasycznego tekstowego include.
- **Move** — operacja mogąca przejąć zasoby z obiektu źródłowego.
- **Name mangling** — kodowanie sygnatury C++ w nazwie symbolu zgodnie z ABI.
- **Object slicing** — utrata części pochodnej przy kopiowaniu obiektu do wartości typu bazowego.
- **ODR (One Definition Rule)** — zbiór reguł dotyczących liczby i zgodności definicji w programie.
- **Overload resolution** — wybór najlepszego wykonalnego przeciążenia.
- **Ownership** — odpowiedzialność za zakończenie lifetime/zwolnienie zasobu; w C++ wyrażana konwencją i typami RAII.
- **Padding** — bajty reprezentacji dodane m.in. dla alignment; nie są automatycznie formatem serializacji.
- **Partial specialization** — specjalizacja szablonu klasy/zmiennej dla podzbioru argumentów.
- **Perfect forwarding** — zachowanie kategorii wartości i cv/ref argumentu przez `std::forward`.
- **Pointer provenance** — związek wskaźnika z obiektem/storage i historią jego uzyskania.
- **Postcondition** — warunek zapewniany po poprawnym zakończeniu operacji.
- **Precondition** — warunek wymagany od klienta przed operacją.
- **Promise type** — typ sterujący protokołem transformacji i wynikiem korutyny.
- **Prvalue** — wyrażenie inicjujące wartość bez tożsamości glvalue.
- **RAII** — związanie zasobu z lifetime obiektu i zwalnianie w destruktorze.
- **RTTI** — runtime type information wspierające `typeid` i `dynamic_cast`.
- **Rvalue** — prvalue lub xvalue; wyrażenie mogące wiązać rvalue reference.
- **SFINAE** — usunięcie kandydata po nieudanym podstawieniu w immediate context zamiast twardego błędu.
- **Storage duration** — okres dostępności storage: automatic, static, thread lub dynamic.
- **Strict weak ordering** — relacja porządku wymagana m.in. od komparatorów sortowania i map.
- **Subsumption** — relacja constraints używana do wyboru bardziej ograniczonego przeciążenia.
- **Translation unit** — wynik preprocessing jednego źródła, kompilowany oddzielnie.
- **Trivially copyable** — klasa typów o szczególnych gwarancjach kopiowania reprezentacji bajtowej.
- **Type erasure** — ukrycie konkretnego typu za wspólnym interfejsem runtime.
- **Undefined behavior (UB)** — zachowanie, dla którego standard nie nakłada wymagań.
- **Unspecified behavior** — jeden z dozwolonych wyników, którego implementacja nie musi dokumentować.
- **Value semantics** — zachowanie typu jak niezależnej wartości logicznej.
- **Vtable** — typowa, ale ABI-zależna implementacja dynamic dispatch.
- **View** — lekka, zwykle niewłaścicielska lub leniwa reprezentacja danych.
- **Xvalue** — glvalue oznaczające obiekt, z którego można potencjalnie odzyskać zasoby.

## Pojęcia potrzebne do precyzyjnego rozumowania

- **Storage duration / okres przechowywania** — czas dostępności pamięci. Nie jest tożsamy z lifetime obiektu, który można w tej pamięci utworzyć i zniszczyć. [Przykłady](03_pamiec_i_czas_zycia/01_storage_duration_i_lifetime.md).
- **Full-expression / pełne wyrażenie** — granica istotna między innymi dla niszczenia tymczasowych obiektów. Zwykle jest nią całe wyrażenie instrukcji, a nie każde podwyrażenie osobno.
- **Materializacja obiektu tymczasowego** — konwersja odpowiedniego prvalue prowadząca do uzyskania xvalue oznaczającego obiekt tymczasowy; pomaga wyjaśnić wiązanie referencji.
- **Reference collapsing / składanie referencji** — reguły łączenia referencji przy podstawianiu typów; tylko połączenie dwóch referencji rvalue pozostaje referencją rvalue, pozostałe dają lvalue reference. [Analiza](zaawansowane/05_value_categories_i_perfect_forwarding.md).
- **User-declared a user-provided** — deklaracja funkcji przez użytkownika i dostarczenie jej według reguł tej kategorii to różne pojęcia. `= default` przy pierwszej deklaracji nadal jest user-declared, ale nie user-provided; różnica wpływa między innymi na funkcje specjalne i inicjalizację.
- **Trivial a trivially copyable** — różne właściwości typu; nazwa „prosty typ” nie zastępuje sprawdzenia dokładnego traitu. Trivially copyable nie oznacza przenośnej serializacji reprezentacji. [Layout](zaawansowane/03_layout_alignment_padding_i_triviality.md).
- **Potentially-overlapping subobject** — podobiekt bazowy lub pole oznaczone `[[no_unique_address]]`; jego status ma znaczenie dla reguł reprezentacji i zastępowania obiektów.
- **Transparent replacement** — zastąpienie obiektu spełniające warunki, przy których stare nazwy i odwołania mogą zacząć odnosić się do nowego obiektu. Sam ten sam adres nie wystarcza. [Lifetime](zaawansowane/02_lifetime_aliasing_i_pointer_provenance.md).
- **Immediate context** — kontekst, w którym konkretne niepowodzenia podstawienia mogą podlegać SFINAE; błędy głębiej w instancjowanym ciele nie muszą być w ten sposób usuwane. [SFINAE](05_szablony_i_generycznosc/03_specialization_i_sfinAE.md).
- **Constraint satisfaction a modeling** — spełnienie sprawdzanych ograniczeń składniowych nie dowodzi wszystkich semantycznych praw conceptu. [Concepts](05_szablony_i_generycznosc/04_concepts_i_requires.md).
- **Strict weak ordering / ścisły słaby porządek** — relacja wymagana przez wiele algorytmów sortowania i kontenerów uporządkowanych. Musi spełniać właściwe prawa, a nie jedynie zwracać `bool`.
- **Projection / projekcja** — operacja wybierająca lub przeliczająca cechę elementu przed porównaniem w algorytmie ranges, na przykład wskaźnik do pola rekordu.
- **Sentinel / wartownik końca** — obiekt wyznaczający koniec zakresu; nie musi mieć tego samego typu co iterator. [Iteratory](06_biblioteka_standardowa/04_iteratory_i_invalidacja.md).
- **Amortized complexity / złożoność amortyzowana** — koszt rozłożony na sekwencję operacji. Amortyzowane O(1) nie wyklucza pojedynczej drogiej realokacji.
- **Valid but unspecified state** — stan spełniający inwarianty i kontrakty typu, którego konkretna wartość nie jest określona. Nie oznacza stanu indeterminate ani prawa do wywołania operacji z niespełnionymi preconditions.
- **Strong exception guarantee** — niepowodzenie zachowuje określony poprzedni stan operacji; nie oznacza, że każda operacja jest bezwyjątkowa.
- **Modification order** — porządek modyfikacji jednego obiektu atomowego. Nie jest sam w sobie wspólnym porządkiem wszystkich zwykłych odczytów i zapisów programu.
- **Synchronizes-with** — relacja powstająca przy określonym dopasowaniu operacji synchronizacji; uczestniczy w uzasadnianiu happens-before. [Model pamięci](10_wspolbieznosc/04_atomiki_i_model_pamieci.md).
- **Spurious wakeup** — przebudzenie oczekującego wątku bez spełnienia warunku aplikacji; predykat trzeba ponownie sprawdzić. Nie należy mylić z pozorną porażką `compare_exchange_weak`.
- **Linearization point** — punkt, w którym operacja współbieżnej struktury daje się logicznie traktować jako wykonana atomowo. Poprawność całej struktury wymaga czegoś więcej niż atomowości pojedynczego CAS.
- **Backpressure** — ograniczanie napływu pracy, gdy odbiorca nie nadąża; zapobiega nieograniczonemu narastaniu kolejek. [Transport i bufory](11_io_i_system/05_siec_serializacja_i_granice_std.md).
- **Framing** — reguła wydzielania wiadomości ze strumienia bajtów; TCP sam nie zachowuje granic wywołań zapisu aplikacji.
- **TOCTOU** — zmiana stanu między sprawdzeniem a użyciem, na przykład podmiana pliku po `exists()`. [Filesystem](11_io_i_system/02_pliki_i_filesystem.md).
- **Source compatibility a binary compatibility** — możliwość rekompilacji klienta a możliwość współpracy istniejących artefaktów binarnych. [API i ABI](13_wzorce_api_i_wydajnosc/03_projektowanie_api_i_abi.md).

## Jak korzystać ze słownika

Termin C++ należy zawsze wiązać z warstwą: językiem standardowym, biblioteką, ABI albo narzędziem. „Obiekt” w standardzie nie oznacza wyłącznie instancji klasy, „stos” jest uproszczeniem implementacyjnym, a „wątek bezpieczny” nie mówi jeszcze, które operacje można wykonywać równocześnie. Przy każdej definicji sprawdź więc, czy opisuje gwarancję normatywną, typową implementację czy praktykę projektową.

~~~text
lifetime      -> okres istnienia obiektu
storage       -> pamięć zdolna przechować obiekt
ownership     -> odpowiedzialność za zakończenie użycia zasobu
view          -> dostęp bez przejęcia własności
UB            -> brak wymagań wobec zachowania programu
ABI           -> binarny kontrakt implementacji i platformy
~~~

Najczęściej mylone pary to scope/lifetime, address/object, copy/bitwise copy, concurrency/parallelism oraz API/ABI. Rozstrzygaj je przez pytanie o moment obowiązywania i właściciela odpowiedzialności, a następnie przejdź do rozdziału wskazanego w odsyłaczu.

## Powiązane tematy

- [Ściąga](sciaga.md)
- [Zagadnienia zaawansowane](zaawansowane/README.md)
- [Źródła](zrodla.md)
