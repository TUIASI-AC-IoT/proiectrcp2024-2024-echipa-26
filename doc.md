# RIPv2 - DOCUMENTATION
---

###  1. Ce este RIP?
<mark>RIP (Routing Information Protocol)</mark> este un protocol de rutare fara clase, de tip distanta-vector, ce implica utilizarea ca metrica de rutare a numarului de pasi de rutut - <ins>"hop count"</ins>. Prin aceasta, RIP previne aparitia buclelor de rutare, utilizand o valoare limita maxima, aceasta fiind de regula **15**   (valoarea de 16 reprezinta o distanta de rutare infinita).

---

### 2. De ce RIPv2??
RIPv2 este o versiune imbunatatita a protocolului RIP original. Acesta include o serie impresionanta de dezvoltari menite sa abordeze limitarile predecesorului sau, facandu-l mai adaptabil si mai sigur pentru nevoile moderne de retea.

- [ ] **Rutarea fara clase:** 
- spre deosebire de RIPv1, RIPv2 implementeaza _VLSM (Variable Length Subnet Mask)_ si _CIDR (Classless Inter-Domain Routing)_, permitand o alocare mai eficienta si mai flexibila a adreselor IP, incluzand informatii despre masca de subretea cu actualizarile sale de rutare<br/></br>

- [ ] **Actualizari Multicast:**
- RIPv2 trimite actualizari utilizand adrese multicast (<ins>224.0.0.9</ins>), ceea ce reduce traficul inutil catre dispozitivele care nu utilizeaza router<br/></br>

- [ ] **Autentificare:**
- De asemenea, RIPv2 include suport pentru text simplu si autentificare _MD5 (functie criptografica - Message Digest Algorithm 5)_, adaugand un strat de securitate pentru a preveni actualizarile de rutare neautorizate 
--- 
### 3. Cum functioneaza RIPv2?
Acest protocol este bazat pe algoritmul **Bellman-Ford** de calcul al rutelor. Bellman-Ford este practic un algoritm ce rezolva gasirea drumului minim de la un nod sursa la celalte noduri. Acesta numara "hop"-urile, cel mai bun fiind cel mai apropiat de host (numarul maxim = 15). Daca acest numar de "hop"-uri ajunge la 16, inseamna ca acea ruta este inaccesibila, existand o potentiala bucla.
<p align="center"> 
  <img src="https://ipcisco.com/wp-content/uploads/rip/routing-with-rip.jpg" width="400" height="250" />
</p>

- **Publicarea rutelor in RIPv2** <br></br>
Rutele sunt trimise periodic, insemnand ca, intr-o retea RIP, toate routerele isi trimit tabelele de rutare vecinilor lor la fiecare **30** de secunde, prin actualizari periodice. Scopul acestui proces este de a actualiza tabelele de rutare si de a gasi drumuri cat mai bune (scurte) pentru a ajunge la destinatie.

---
 ### 4. Split Horizon si Poison Reverse
- <mark><ins>Split Horizon</ins></mark> functioneaza pe un principiu simplu dar elegant : un router nu va anunta inapoi pe o interfata informatiile de rutare pe care le-a invatat chiar prin acea interfata. Acesta abordare previne situatiile in care routerele s-ar putea insela reciproc cu informatii de rutare invechite sau chiar incorecte, care ar putea duce la formarea de bucle infinite.
<br></br>
- <mark><ins>Poison Reverse</ins></mark> adopta o abordare mai directa si agresiva. In loc sa pastreze "tacerea" asupra retelelor invatate, acest mecanism alege sa "otraveasca" explicit rutele, marcandu-le ca fiind inaccesibile atunci cand le anunta inapoi spre sursa lor. Este o tehnica deosebit de eficienta in prevenirea buclelor de rutare, intrucat **elimina orice ambiguitate privind disponibilitatea unei rute**.
<br></br>
- [ ] Este unul mai bun decat celalalt?
- Ambele mecanisme isi gasesc utilitatea in special intr-un protocol precum <mark>RIP( Routing Internet Protocol )</mark>, unde problema buclelor de rutare poate fi critica. Desi <b>Split Horizon</b> este mai conservator in abordare, <b>Poison Reverse</b> ofera o siguranta certa prin natura sa explicita. Fiecare metoda are avantajele si dezavantajele sale, alegerea intre ele depinzand de cele mai multe ori de specificul retelei si de protocoalele de rutare utilizate.

---

### 5. Formatul de mesaje specific RIPv2
- **RIP** este un protocol bazat pe <mark>UDP</mark>. Fiecare router care foloseste RIP are un proces de rutare care trimite si primeste datagrame prin portul UDP 520, desemnat pentru RIPv1/RIPv2. Toate comunicarile destinate procesului RIP de pe un alt router sunt directionate catre acest port. Mai mult, toate mesajele de actualizare a rutarii sunt trimise de la portul RIP. Mesajele de actualizare trimise ca raspuns la o cerere sunt directionate inapoi de la portul de la care a venit cererea. Desi anumite interogari specifice pot fi trimise de la alte porturi decat portul RIP, ele trebuie directionate catre portul RIP al dispozitivului tinta.
<br></br>
<div align="center">
       <ins>Formatul RIPv1</ins>
       <br></br>
        
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
<br/br>
<div align="center">
    <ins>Formatul imbunatatit <mark>RIPv2</mark></ins>
       <br></br>
  
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
  <br></br>
</div>

---
#### Bibliografie

- https://ro.wikipedia.org/wiki/RIP
- https://community.fs.com/article/the-difference-between-ripv1-and-ripv2.html
- https://ipcisco.com/lesson/routing-information-protocol/
- https://iopscience.iop.org/article/10.1088/1742-6596/1007/1/012009/pdf
- https://datatracker.ietf.org/doc/html/rfc2453#section-3.6
