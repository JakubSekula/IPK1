# Dokumentace k 1. úloze do IPP 2019/2020
* Jméno a příjmení: Jakub Sekula
* Login: xsekul01
  
## HTTP resolver doménových jmen

Po zadání příkazu make run PORT=číslo_portu, ve složce s implementací serveru, se na daném portu otevře server pro komunikaci s klientem.

## Připojení na server

Server umí zpracovávat 2 způsoby připojení. Tyto způsoby jsou:

* curl localhost:5353/resolve?name=www.fit.vutbr.cz\&type=A
* curl --data-binary @queries.txt -X POST http://localhost:5353/dns-query

1. způsob připojení se pokusí připojit na portu, v našem případě, se pokusí připojit na portu 5353. Jedná se o metodu Get.

2. způsob vezme soubor @queries.txt a ten pošle na localhost s portem 5353. Jedná se o metodu POST  

## Implementace serveru
Server jsem se rozhodl implementovat jazykem python3, zejména díky modulu socket a threading.

Modulem socket otevřu server na portu daném příkazem make. Tento server čeká na připojení ze strany klienta. Jakmile připojení nastane, tak se pro připojení otevře samostatné vlákno pomocí modulu threading. 

Následně si zjistím o jaký typ připojení se jedná a podle toho volám funkci, podle které dále zprávu parsuji.

Metodu GET parsuji podle slova name= a type= . Jakmile zjistím jestli se jedná o ip adresu nebo doménové jméno, tak kontroluji, jestli se jedná o správnou metodu.

Obdobně parsuji i metodu POST, ve které prochazím dotazy řádek po řádku a kontroluji jejich správnost.

## Chybové stavy

* Vstupní URL není správné, je jiné než /resolve či /dns-query - vrací 400 Bad Request.
* Vstupní parametry pro GET jsou nesprávné nebo chybí - vrací 400 Bad Request.
* Formát vstupu pro POST není správný - vrací 400 Bad Request.
* Operace není podporována - je použita jiná operace než GET a POST - vrací 405 Method Not Allowed.
* Pro ostatní nestandardní případy je návratová hodnota 500 Internal Server Error.
