[← Spis treści](../README.md)

# Smart pointery

Smart pointer reprezentuje własność dynamicznego obiektu przez RAII. `std::unique_ptr<T>` oznacza jednego właściciela, jest niekopiowalny i przenoszalny. `std::shared_ptr<T>` współdzieli własność przez blok kontrolny z licznikami. `std::weak_ptr<T>` obserwuje obiekt zarządzany przez `shared_ptr`, ale nie przedłuża jego życia.

~~~cpp
#include <cassert>
#include <memory>
#include <string>

struct User {
    std::string name;
};

int main() {
    auto owner = std::make_shared<User>(User{"Ada"});
    std::weak_ptr<User> observer = owner;

    if (auto user = observer.lock()) {
        assert(user->name == "Ada");
    }

    owner.reset();
    assert(observer.expired());
}
~~~

Preferuj `std::make_unique` i `std::make_shared`, ponieważ łączą konstrukcję z przejęciem własności i upraszczają exception safety. `make_shared` zwykle umieszcza obiekt i blok kontrolny w jednej alokacji, ale pamięć obiektu może pozostać zarezerwowana, dopóki istnieją słabe referencje.

`shared_ptr` nie czyni samego obiektu bezpiecznym wątkowo. Niezależne instancje smart pointerów mogą współdzielić blok kontrolny, lecz równoczesny dostęp do pól `T` nadal wymaga synchronizacji. Cykle silnych referencji nie znikają automatycznie: co najmniej jedna krawędź w cyklu powinna być słaba albo model własności powinien zostać uproszczony.

Surowy wskaźnik uzyskany przez `.get()` jest niewłaścicielski. Nie wolno tworzyć z niego drugiego niezależnego `unique_ptr` lub `shared_ptr`. Jeśli obiekt ma żyć dokładnie w jednym zakresie, zwykła wartość jest prostsza niż dynamiczna alokacja.

## Jak to działa krok po kroku

`make_unique<T>` konstruuje dynamiczny obiekt i oddaje pojedynczy przenoszalny uchwyt. Destruktor `unique_ptr` uruchamia jego deleter, jeśli posiada zasób. `reset` zastępuje posiadany obiekt i sprząta poprzedni, natomiast `release` oddaje surowy wskaźnik bez zwalniania. Po `release` odpowiedzialność musi przejąć konkretny odbiorca; zignorowanie wyniku zwykle tworzy wyciek.

W przykładzie z `shared_ptr` pierwszy właściciel tworzy grupę współwłasności. Skopiowanie właściciela zwiększyłoby liczbę silnych odniesień. Utworzenie `weak_ptr` zachowuje możliwość sprawdzenia grupy, lecz nie utrzymuje obiektu. `lock` próbuje uzyskać nowy silny uchwyt. Gdy się powiedzie, obiekt pozostaje żywy przez czas tego lokalnego uchwytu, nawet jeśli inni właściciele w międzyczasie zrezygnują.

Kiedy znika ostatni silny właściciel, niszczony jest zarządzany obiekt. Blok kontrolny może przetrwać do zaniku słabych odniesień. Są więc dwa odrębne czasy życia. Przy połączonej alokacji `make_shared` destruktor obiektu wykona się odpowiednio wcześnie, ale cały przydzielony blok może zostać zwolniony dopiero później. Ma to znaczenie dla dużych obiektów długo obserwowanych przez `weak_ptr`.

## Pogłębienie mechanizmu

Tożsamość grupy własności nie jest tym samym co przechowywany adres. Konstruktor aliasujący `shared_ptr` pozwala współdzielić własność większego obiektu, jednocześnie wskazując jego pole. Taki wskaźnik jest poprawny, dopóki wskazywany podobiekt pozostaje ważny w czasie życia właściciela. Aliasing nie unieruchamia elementu wektora, który może później zostać przeniesiony przez realokację.

Zbudowanie `shared_ptr<T>{existing.get()}` tworzy nowy blok kontrolny. Oba niezależne bloki będą uważać się za właściciela tego samego adresu, co może skończyć się podwójnym usunięciem. Do współdzielenia używaj kopii istniejącego `shared_ptr` lub jego rzutowań bibliotecznych. `enable_shared_from_this` pozwala obiektowi uzyskać udział w już istniejącej grupie, ale wymaga poprawnie ustanowionej współwłasności; użycie zbyt wcześnie w konstruktorze jej nie zapewnia.

`weak_ptr::expired()` jest tylko obserwacją chwili. Sekwencja „sprawdź, a potem uzyskaj surowy dostęp” nie zabezpiecza życia przed konkurencyjnym zniknięciem właścicieli. `lock()` łączy próbę wzmocnienia z uzyskaniem uchwytu. Również `use_count() == 1` nie jest ogólnym protokołem bezpiecznej wyłącznej modyfikacji współdzielonych danych.

Niezależne instancje `shared_ptr` mogą być bezpiecznie kopiowane i niszczone równolegle, współdzieląc blok kontrolny. Modyfikacja tej samej instancji uchwytu z wielu wątków wymaga synchronizacji albo `std::atomic<std::shared_ptr<T>>` od C++20. Dostęp do obiektu `T` pozostaje osobnym problemem; licznik własności nie blokuje jego pól.

Cykl właścicielski utrzymuje dodatnie liczniki mimo braku dostępu z zewnątrz. W drzewie dzieci mogą posiadać kolejne dzieci, a odnośnik do rodzica zwykle powinien być obserwacją. Dobór `weak_ptr` wynika z kierunku odpowiedzialności, a nie z chęci losowego przerwania dowolnej krawędzi grafu.

## Drugi przykład

Aliasujący właściciel wskazuje pole, ale utrzymuje cały obiekt. Dzięki temu lokalna rezygnacja z głównego uchwytu nie unieważnia odczytu imienia.

~~~cpp
#include <cassert>
#include <memory>
#include <string>

struct Profile {
    std::string name;
    int age;
};

int main() {
    auto profile = std::make_shared<Profile>(Profile{"Ada", 36});
    std::weak_ptr<Profile> observer = profile;
    std::shared_ptr<std::string> name{profile, &profile->name};
    profile.reset();
    assert(!observer.expired());
    assert(*name == "Ada");
    name.reset();
    assert(observer.expired());
    assert(!observer.lock());
}
~~~

`name` nie usuwa samodzielnie pola `std::string`. Współdzieli blok kontrolny, którego operacja sprzątania dotyczy `Profile`. Wskaźnik do pola i zarządzany zasób są powiązane umową konstruktora aliasującego, choć mają różne typy i mogą mieć różne adresy.

## Porównanie i decyzje

Typ deletera należy do typu `unique_ptr`, a stanowy deleter może zwiększać rozmiar uchwytu. Pozwala to obsługiwać zasoby wymagające własnej funkcji zwalniającej, na przykład obiekt biblioteki C. Nie zakładaj, że każdy `unique_ptr` ma zawsze rozmiar jednego wskaźnika. Ta częsta optymalizacja dla pustego deletera jest właściwością konkretnej reprezentacji, nie uniwersalnym kontraktem interfejsu.

Przekazuj `unique_ptr` przez wartość, gdy funkcja przejmuje wyłączną własność. Przekazuj `shared_ptr` przez wartość, gdy ma zachować własny udział. Dla samego odczytu lub modyfikacji obiektu używaj `const T&`, `T&` lub wskaźnika, zależnie od nullowalności. Wymuszanie smart pointera na odbiorcy, który nie zarządza życiem, niepotrzebnie wiąże interfejs z konkretnym modelem alokacji.

**Ćwiczenie.** Czy `std::move(shared)` jest potrzebne, aby przekazać funkcji kolejnego współwłaściciela i zachować dotychczasowy uchwyt?

**Odpowiedź.** Nie. Kopia tworzy dodatkowy udział i zachowuje źródło. Ruch przekazuje istniejący uchwyt, pozostawiając źródło puste. Obie operacje mogą mieć tę samą wartość adresu u odbiorcy, ale wyrażają inne wymagania wobec nadawcy.

Źródła: [unique_ptr](https://timsong-cpp.github.io/cppwp/n4950/unique.ptr), [shared_ptr](https://timsong-cpp.github.io/cppwp/n4950/util.smartptr.shared), [obserwacja weak_ptr](https://timsong-cpp.github.io/cppwp/n4950/util.smartptr.weak.obs).

## Powiązane tematy

- [Dynamiczna pamięć](02_stos_sterta_i_dynamiczna_pamiec.md)
- [RAII](03_raii_i_destruktory.md)
- [Współbieżność i mutex](../10_wspolbieznosc/02_mutex_lock_i_condition_variable.md)

