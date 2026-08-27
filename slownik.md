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
- **Forwarding reference** — dedukowane `T&&`, które może wiązać lvalue i rvalue.
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
- **Lock-free** — gwarancja postępu systemowego bez blokady mutexowej; nie oznacza wait-free.
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

## Powiązane tematy

- [Ściąga](sciaga.md)
- [Zagadnienia zaawansowane](zaawansowane/README.md)
- [Źródła](zrodla.md)

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

