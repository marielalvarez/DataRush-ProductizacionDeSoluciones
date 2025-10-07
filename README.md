# DataRush: Productización de Soluciones

<p align="center">
  <img width="525" height="303" alt="Screenshot 2025-10-07 at 10 26 07" src="https://github.com/user-attachments/assets/503da566-882f-46ae-9041-3f4f57407df4" />
</p>

### Objetivo
Aplicar EDA y visualización/algoritmos para detectar patrones en **viajes de taxi y limosina en Nueva York (NYC)** y traducirlos en **recomendaciones accionables** listas para producto (MVPs, dashboards o scripts reutilizables).

- **Datos**: se consumen **directo desde la nube** (AWS Open Data): https://registry.opendata.aws/nyc-tlc-trip-records-pds/

---

## Estructura del repositorio
```
reto/
│
├── README.md                 # uso del repositorio
└── solucion-equipo/         # entregables por equipo (en su propia carpeta)
```
---

## Reglas de colaboración
1. Cada equipo debe hacer _fork_ de este repositorio
2. Dentro del fork, crear su carpeta  con el formato:  
   `solucion-<nombre_equipo>`
3. Subir todos sus archivos únicamente dentro de su carpeta de equipo.
4. No modifiques la rama `main` del repo original. Trabaja en tu fork.
---

## Flujo de trabajo (equipos)
1) Hacer fork desde GitHub  
2) Clonar el fork en local:
```bash
git clone https://github.com/<tu_usuario>/<tu_fork>.git
cd <tu_fork>
```
3) **Crear la carpeta del equipo** y agregar contenido:
```bash
mkdir -p solucion-<nombre_equipo> # puedes añadir notebooks, scripts, dashboards exportables y un README propio.
```
4) **Commit & push** a tu fork:
```bash
git add .
git commit -m "Inicial: solucion-<nombre_equipo>"
git push origin main
```

---


¡Éxito en el reto! 💡  
— Data Science Club at Tec
