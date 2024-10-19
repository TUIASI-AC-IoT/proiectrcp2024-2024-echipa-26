# RIPv2 - DOCUMENTATION
---

####  1. Ce este RIP?
<mark>RIP (Routing Information Protocol)</mark> este un protocol de rutare fara clase, de tip distanta-vector, ce implica utilizarea ca metrica de rutare a numarului de pasi de rutut - <ins>"hop count"</ins>. Prin aceasta, RIP previne aparitia buclelor de rutare, utilizand o valoare limita maxima, aceasta fiind de regula **15**   (valoarea de 16 reprezinta o distanta de rutare infinita).

---

#### 2. De ce RIPv2?
RIPv2 este o versiune imbunatatita a protocolului RIP original. Acesta include o serie impresionanta de dezvoltari menite sa abordeze limitarile predecesorului sau, facandu-l mai adaptabil si mai sigur pentru nevoile moderne de retea.
<div style="text-align: center;">
  <img src="https://media.fs.com/images/community/erp/6k2R5_XCPBJhJjtp4mcF7NSFjR.jpg" width="500" height="200" />
</div><br/>

- [ ] **Rutarea fara clase:** 
- spre deosebire de RIPv1, RIPv2 _VLSM (Variable Length Subnet Mask)_ si _CIDR (Classless Inter-Domain Routing)_, permitand o alocare mai eficienta si mai flexibila a adreselor IP, incluzand informatii despre masca de subretea cu actualizarile sale de rutare<br/></br>

- [ ] **Actualizari Multicast:**
- RIPv2 trimite actualizari utilizand adrese multicast (<ins>224.0.0.9</ins>), ceea ce reduce traficul inutil catre dispozitivele care nu utilizeaza router<br/></br>

- [ ] **Autentificare:**
- De asemenea, RIPv2 include suport pentru text simplu si autentificare _MD5 (functie criptografica - Message Digest Algorithm 5)_, adaugand un strat de securitate pentru a preveni actualizarile de rutare neautorizate 
--- 
#### 3. Cum functioneaza RIPv2?
Acest protocol este bazat pe algoritmul **Bellman-Ford** de calcul al rutelor. Bellman-Ford este practic un algoritm ce rezolva gasirea drumului minim de la un nod sursa la celalte noduri. Acesta numara "hop"-urile, cel mai bun fiind cel mai apropiat de host (numarul maxim = 15). Daca acest numar de "hop"-uri ajunge la 16, inseamna ca acea ruta este inaccesibila, existand o potentiala bucla.
<div style="text-align: center;">
  <img src="https://ipcisco.com/wp-content/uploads/rip/routing-with-rip.jpg" width="400" height="250" />
</div>

- **Publicarea rutelor in RIPv2**
 Rutele sunt trimise periodic, insemnand ca, intr-o retea RIP, toate routerele isi trimit tabelele de rutare vecinilor lor la fiecare **30** de secunde, prin actualizari periodice. Scopul acestui proces este de a actualiza tabelele de rutare si de a gasi drumuri cat mai bune (scurte) pentru a ajunge la destinatie.

---
 #### 4. Split Horizon si Poison Reverse
 coming soon :)




#### Bibliografie

- https://ro.wikipedia.org/wiki/RIP
- https://community.fs.com/article/the-difference-between-ripv1-and-ripv2.html
- https://ipcisco.com/lesson/routing-information-protocol/
- https://iopscience.iop.org/article/10.1088/1742-6596/1007/1/012009/pdf