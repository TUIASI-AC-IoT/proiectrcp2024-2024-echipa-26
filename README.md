# RIPv2 - DOCUMENTATION


### <ins>Ce este RIP?</ins>
<mark>RIP (Routing Information Protocol)</mark> este un protocol de rutare fara clase, de tip distanta-vector, ce implica utilizarea ca metrica de rutare a numarului de pasi de rutut - <ins>"hop count"</ins>. Prin aceasta, RIP previne aparitia buclelor de rutare, utilizand o valoare limita maxima, aceasta fiind de regula **15**   (valoarea de 16 reprezinta o distanta de rutare infinita).

---

### <ins>De ce RIPv2?</ins>
RIPv2 este o versiune imbunatatita a protocolului RIP original. Acesta include o serie impresionanta de dezvoltari menite sa abordeze limitarile predecesorului sau, facandu-l mai adaptabil si mai sigur pentru nevoile moderne de retea.

**Rutarea fara clase:**

Spre deosebire de RIPv1, RIPv2 implementeaza _VLSM (Variable Length Subnet Mask)_ si _CIDR (Classless Inter-Domain Routing)_, permitand o alocare mai eficienta si mai flexibila a adreselor IP, incluzand informatii despre masca de subretea cu actualizarile sale de rutare<br/></br>

**Actualizari Multicast:**

RIPv2 trimite actualizari utilizand adrese multicast (<ins>224.0.0.9</ins>), ceea ce reduce traficul inutil catre dispozitivele care nu utilizeaza router<br/></br>

**Autentificare:**

De asemenea, RIPv2 include suport pentru text simplu si autentificare _MD5 (functie criptografica - Message Digest Algorithm 5)_, adaugand un strat de securitate pentru a preveni actualizarile de rutare neautorizate 

--- 

### <ins>Cum functioneaza RIPv2?</ins>
Acest protocol este bazat pe algoritmul **Bellman-Ford** de calcul al rutelor. Bellman-Ford este practic un algoritm ce rezolva gasirea drumului minim de la un nod sursa la celalte noduri. Acesta numara "hop"-urile, cel mai bun fiind cel mai apropiat de host (numarul maxim = 15). Daca acest numar de "hop"-uri ajunge la 16, inseamna ca acea ruta este inaccesibila, existand o potentiala bucla.
<p align="center"> 
  <img src="https://ipcisco.com/wp-content/uploads/rip/routing-with-rip.jpg" width="400" height="250" />
</p>

**Publicarea rutelor in RIPv2**<br>
Rutele sunt trimise periodic, insemnand ca, intr-o retea RIP, toate routerele isi trimit tabelele de rutare vecinilor lor la fiecare **30** de secunde, prin actualizari periodice. Scopul acestui proces este de a actualiza tabelele de rutare si de a gasi drumuri cat mai bune (scurte) pentru a ajunge la destinatie.</br>

---

 ### <ins>Split Horizon si Poison Reverse</ins>
<mark><ins>Split Horizon</ins></mark> functioneaza pe un principiu simplu dar elegant : un router nu va anunta inapoi pe o interfata informatiile de rutare pe care le-a invatat chiar prin acea interfata. Acesta abordare previne situatiile in care routerele s-ar putea insela reciproc cu informatii de rutare invechite sau chiar incorecte, care ar putea duce la formarea de bucle infinite.
<br></br>
<mark><ins>Poison Reverse</ins></mark> adopta o abordare mai directa si agresiva. In loc sa pastreze "tacerea" asupra retelelor invatate, acest mecanism alege sa "otraveasca" explicit rutele, marcandu-le ca fiind inaccesibile atunci cand le anunta inapoi spre sursa lor. Este o tehnica deosebit de eficienta in prevenirea buclelor de rutare, intrucat **elimina orice ambiguitate privind disponibilitatea unei rute**.
<br></br>
**Este unul mai bun decat celalalt?**
<br>Ambele mecanisme isi gasesc utilitatea in special intr-un protocol precum <mark>RIP( Routing Internet Protocol )</mark>, unde problema buclelor de rutare poate fi critica. Desi <b>Split Horizon</b> este mai conservator in abordare, <b>Poison Reverse</b> ofera o siguranta certa prin natura sa explicita. Fiecare metoda are avantajele si dezavantajele sale, alegerea intre ele depinzand de cele mai multe ori de specificul retelei si de protocoalele de rutare utilizate.</br>

---

### <ins>Formatul de mesaje specific RIPv2</ins>
**RIP** este un protocol bazat pe <mark>UDP</mark>. Fiecare router care foloseste RIP are un proces de rutare care trimite si primeste datagrame prin portul UDP 520, desemnat pentru RIPv1/RIPv2. Toate comunicarile destinate procesului RIP de pe un alt router sunt directionate catre acest port. Mai mult, toate mesajele de actualizare a rutarii sunt trimise de la portul RIP. Mesajele de actualizare trimise ca raspuns la o cerere sunt directionate inapoi de la portul de la care a venit cererea. Desi anumite interogari specifice pot fi trimise de la alte porturi decat portul RIP, ele trebuie directionate catre portul RIP al dispozitivului tinta.

<div align="center">
  <ins>Formatul <mark>RIPv1</mark></ins>
  
     0                   1                   2                   3
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | address family identifier (2) |      must be zero (2)         |
    +-------------------------------+-------------------------------+
    |                        IPv4 address (4)                       |
    +---------------------------------------------------------------+
    |                        must be zero (4)                       |
    +---------------------------------------------------------------+
    |                        must be zero (4)                       |
    +---------------------------------------------------------------+
    |                           metric (4)                          |
    +---------------------------------------------------------------+
    
</div>

<div align="center">
  <ins>Formatul imbunatatit <mark>RIPv2</mark></ins>
  
     0                   1                   2                   3 
     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    | Address Family Identifier (2) |        Route Tag (2)          |
    +-------------------------------+-------------------------------+
    |                         IP Address (4)                        |
    +---------------------------------------------------------------+
    |                         Subnet Mask (4)                       |
    +---------------------------------------------------------------+
    |                         Next Hop (4)                          |
    +---------------------------------------------------------------+
    |                         Metric (4)                            |
    +---------------------------------------------------------------+
</div>

---
#### <ins>Descriere explicita a formatului de mesaje</ins> <br></br>
- ***AFI (Address Family Identifier)*** <br></br>
⇨ AFI specifica familia de adrese utilizata. Pentru RIPv1, doar **AF_INET (IPv4)** este suportat, cat si pentru RIPv2. <br></br>

- ***Route Tag*** <br></br>
⇨ Route Tag-ul are ca scop separarea rutelor RIP "interne" de cele "externe". Mai precis, prin termenul intern ne referim la rutele invatate de RIP de la el insusi, iar prin extern intelegem
  ca rutele sunt procesate prin intermediul altor protocoale, de exemplu OSPF ( Open Shortest Path First ). <br></br>

- ***IP Address*** <br></br>
⇨ Specifica adresa IP destinatie. <br></br>

- ***Subnet Mask*** <br></br>
⇨ Acest camp contine masca de retea pentru destinatie. Daca valoarea este 0, atunci inseamna ca masca nu a fost specificata. <br></br>

- ***Next Hop*** <br></br>
⇨ Indica adresa IP al celui mai aproapiat router unde ar trebui sa fie trimisa informatia pentru a ajunge pe drumul cel mai scurt la destinatie. Daca nu se poate ajunge la acest "urmator hop", atunci acesta trebuie
  tratat ca fiind 0.0.0.0 . <br></br>

- ***Metric*** <br></br>
⇨ Reprezinta o valoare utilizata ce indica numarul de "next hop-uri" pentru a ajung la destinatia dorita. Aceasta metrica poate avea o valoare intre 1 si 15 pentru rutele valide, <mark>16</mark> reprezentand rutele
  indisponibile si/sau infinite. 
  
---
### <ins>Header-ul RIPv2</ins> <br></br>
  Fiecare mesaj trimis contine un antet (header) care este alcatuit dintr-o comanda si un numar al versiunii. Campul de <mark>comanda</mark> este folosit in ambele versiuni RIP, cu scopul de a specifica intentia mesajului. <br></br>
  - 1 - ***request*** <br></br>
    O cerere pentru sistemul care raspunde sa trimita tot sau o parte din tabelul sau de rutare. <br></br>
  - 2 - ***response*** <br></br>
    Un mesaj ce contine tot sau o parte din tabelul de rutare al sistemului care a fost solicitat. Mesajul poate fi trimis in mod solicitat ca raspunsul unei cereri, sau poate fi un update nesolicitat si periodic de rutare generat de catre sursa. <br></br>

  <div align ="center">

      
  
      0                   1                   2                   3
       0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
      +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
      |  command (1)  |  version (1)  |       must be zero (2)        |
      +---------------+---------------+-------------------------------+
      |                                                               |
      ~                         RIP Entry (20)                        ~
      |                                                               |
      +---------------+---------------+---------------+---------------+
    
  
  
  </div>
  
---

### <ins>Timere</ins>
O data la 30 de secunde, fiecare router trebuie sa-si trimita tabela de rutare catre vecini. Timer-ul nu ar trebui sa fie afectat de cat de incarcat este sistemul. Fiecare timer are un offset de un numar aleator intre 0 si 5 secunde pentru a evita sincronizarea ceasurilor.

Fiecare ruta are 2 timere asociate: un timeout si un garbage-collection timer. Cand timeout-ul expira ruta nu mai este valida dar ramane in tabelul de rutare pentru a informa si vecinii. Cand expira timer-ul garbage-collection, ruta este eliminata. Timeout-ul este setat cand ruta este gasita si/sau atunci cand un mesaj de update este primit legat de ruta. Timeout-ul este de 180s. Garbage-collection este 120s.

---

### <ins>Topologia exemplificata</ins>
<div align="center">
  
![Topologie](/Images/Topologie.png)

</div>



#### <ins>Adrese IP folosite:</ins>
- R01: 192.168.1.1, 192.168.2.1
- R02: 192.168.1.2, 192.168.3.2 
- R03: 192.168.2.3, 192.168.3.3, 192.168.4.3
- R04: 192.168.4.4, 192.168.5.4, 192.168.224.4
- R05: 192.168.5.5, 172.16.48.5
- R06: 172.16.48.6, 172.16.8.6
- R07: 192.168.224.7, 172.16.8.7, 192.168.9.7
- R08: 192.168.9.8, 192.168.64.8, 10.67.192.8
- R09: 192.168.64.9, 10.3.64.9
- R10: 10.67.192.10, 10.3.64.10

Pentru facilitate, fiecare router are o adresa IP care se termina in ID-ul sau.

---

### <ins>Masina virtuala</ins>
Masina virtuala folosita este TinyCore, o distributie de Linux lightweight ce va tine locul routerului. In virtual box aceasta a fost configurata cu 64MB de RAM si 250MB disk.

In functie de numarul routerului din topologie, fiecare masina este conectata la 2-3 retele interne, o interfata fiind rezervata pentru NAT (virtualbox pune la dispozitie 8 interfete, dar doar 4 fiind accesibile prin GUI).

Pe fiecare masina a fost instalat git, openssh si Python (3.6.15) prin intermediul package manager-ului care vine preinstalat.

Pentru asignarea adreselor IP in mod static am folosit un modul de pe github, creat special pentru TinyCore.

Fiecare interfata are un fisier de config pentru a putea reasigna adresele IP.

---

### <ins>Structura programului</ins>
<div align="center">

  ![Workflow](/Images/diagrama_cod.jpg)
  
</div>

Inainte de rularea efectiva a programului este necesara configurarea adreselor statice prin modulul amintit anterior. Dupa configurare, procesul principal citeste niste configuratii de tipul: adrese IP, ID, valoare INF si creaaza un obiect de tipul Router. Obiectul porneste 3 procese copil: unul pentru trimis pachete, unul pentru receptionat si unul pentru verificat timer-e, in procesul parinte ruland interfata de terminal.

Toate cele 4 procese (incluzand parintele) au in comun un obiect de tip SharedTable care contine tabela de rutare. Obiectul SharedTable creeaza niste structuri de date prin intermediul altor obiecte oferite de modulul multiprocessing (Manager, BaseManager) ce au drept scop sincronizarea datelor. Astfel toate procesele au acces la datele din tabela de rutare.

Procesul send reactioneaza la 2 semnale: unul de update si unul de triggered update. Acesta comunica cu procesul listen printr-un pipe prin care primeste detaliile legate de request-urile primite.

Procesul listen asteapta sa primeasca mesaje multicast si unicast si raspunde in mod adecvat la acestea. De asemenea acesta este responsabil pentru mentinerea a doua dictionarea ce contin date relevante pentru Split Horizon (pentru fiecare sender este asociat adresa IP a interfetei de pe care a venit mesajul).

Procesul timerChecker verifica in mod constant timer-ele de timeout, garbage, update si triggered update. Cand un timer de timeout expira, acesta modifica entry-ul din tabela printr-o metoda oferita de SharedTable. Cand un timer de garbage expira, modificarea are loc intr-un mod similar. De asemenea, verificarea timer-elor ce tine de entry-uri este facuta prin intermediul unei metode din SharedTable. Cand timer-ul update expira, procesul trimite un semnal catre procesul de send. Cand timer-ul triggered update expira, procesul trimite un semnal catre acelasi proces send.

Obiectul SharedTable poate de asemenea sa trimita semnale de tipul triggered update catre send prin urmatorul mecanism: acesta trimite semnalul in momentul in care un flag devine CHANGED si il trimite catre procesul parinte si anume CLI. Acesta reactioneaza la semnal prin propagarea acestuia catre procesul send.

Procesul CLI pune la dispozitie 3 moduri: browse, commands si search dintre care doar browse si commands sunt functionale. Browse permite utilizatorului sa vada toate entry-urile din tabela si timer-ele asociate in timp real. Modul commands pune la dispozitie cateva comenzi ce pot fi vazute prin comanda "help". Dintre comenzile puse la dispozitie se remarca: set/get IP timeout/garbage/metric newVal care permite schimbarea parametrilor tuturor entry-urilor ce au venit pe o anumita interfata. Acest lucru se realizeaza prin apelul unor metode din SharedTable care retine de altfel si valorile pentru metrica, timeout si garbage pentru toate interfetele participante.

---

### <ins>Interfata</ins>

Interfata este realizata utilizand modulul <b>curses</b> din python. Am generat 3 meniuri din care utilizatorul poate alege:

- ***<b>BROWSE</b>***:
- ***<b>COMMANDS</b>***:
- ***<b>SEARCH</b>***:

---

### <ins>Dificultati intalnite pe parcurs<ins>

- Implementare Split Horizon: am gasit cu greu o optiune in manualul de linux ce permite socket-urilor sa receptioneze si adresa IP a interfetei de pe care a primit un mesaj. Astfel putem asocia adresa IP de pe o interfata cu adresa IP a unui vecin indiferent de tipul de mesaj si modul in care a ajuns la noi (multicast, unicast).

- Sincronizarea proceselor: am avut probleme la sincronizarea/comunicatia intre proceselor folosing obiecte de tip Manager, dar am reusit in momentul in care am inceput sa folosim doar getter-e si setter-e pentru obiectele complexe precum RIPEntry si Timer.

- Raspuns la response: am avut probleme in urmarirea RFC-ului intrucat logica din spate nu era explicata, RFC-ul doar prezentand cea mai optima abordare pe care am reusit sa o implementam.

- Masinile virtuale: din cauza naturii efemere a distributiei de Linux alese, setup-ul initial a fost anevoios.

- Utilizare sockets: a trebuit sa incercam mai multe variante de setari pana am reusit sa intelegem cum functioneaza si sa reusim sa setam socket-urile pentru a primi mesaje unicast si multicast si pentru a trimite atat multicast cat si unicast.

---

#### <ins>Bibliografie</ins>

- https://ro.wikipedia.org/wiki/RIP
- https://community.fs.com/article/the-difference-between-ripv1-and-ripv2.html
- https://ipcisco.com/lesson/routing-information-protocol/
- https://iopscience.iop.org/article/10.1088/1742-6596/1007/1/012009/pdf
- https://datatracker.ietf.org/doc/html/rfc2453
- http://tinycorelinux.net/
- https://github.com/on-prem/tinycore-network
- https://app.diagrams.net/
- https://en.wikipedia.org/wiki/Private_network
- https://github.com/github/gitignore/blob/main/Python.gitignore
- https://docs.python.org/3/howto/sockets.html
- https://linux.die.net/man/7/ip
- https://docs.python.org/3/howto/curses.html
- https://docs.python.org/3/library/curses.html
