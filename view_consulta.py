import tkinter as tk
from tkinter import messagebox, ttk
from conexion import obtener_conexion

class PantallaConsultaVentas(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent, bg="#bfbfbf")
        self.title("Northwind - Consulta de Ventas por Empleado y Pais")
        self.geometry("1150x620")
        self.construir_interfaz()
        self.cargar_consulta_ventas()

    def construir_interfaz(self):
        area_consulta = tk.Frame(self, bg="#bfbfbf")
        area_consulta.pack(fill="both", expand=True, padx=25, pady=18)

        tk.Label(
            area_consulta, text="Consulta de Ventas por Empleado", fg="#0f172a", bg="#bfbfbf",
            font=("Great Vibes", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            area_consulta, text="Historial de órdenes atendidas por cada empleado. Filtrá por nombre de empleado y/o país del cliente.",
            fg="#36485f", bg="#bfbfbf", font=("Great Vibes", 10)
        ).pack(anchor="w", pady=(2, 15))

        # --- BARRA DE FILTROS (WHERE) ---
        filtros_bar = tk.Frame(area_consulta, bg="#bfbfbf")
        filtros_bar.pack(fill="x", pady=(0, 15))

        tk.Label(filtros_bar, text="Empleado:", bg="#bfbfbf", fg="#0f172a", font=("Great Vibes", 10, "bold")).pack(side="left", padx=(0, 6))
        self.var_filtro_emp = tk.StringVar()
        ent_emp = tk.Entry(filtros_bar, textvariable=self.var_filtro_emp, font=("Great Vibes", 10), width=25,placeholder="Ingrese nombre del empleado")
        ent_emp.pack(side="left", ipady=4, padx=(0, 15))
        ent_emp.bind("<Return>", lambda e: self.cargar_consulta_ventas())

        tk.Label(filtros_bar, text="País Destino:", bg="#bfbfbf", fg="#0f172a", font=("Great Vibes", 10, "bold")).pack(side="left", padx=(0, 6))
        self.var_filtro_pais = tk.StringVar()
        ent_pais = tk.Entry(filtros_bar, textvariable=self.var_filtro_pais, font=("Great Vibes", 10), width=25, placeholder="Ingrese nombre del pais")
        ent_pais.pack(side="left", ipady=4, padx=(0, 15))
        ent_pais.bind("<Return>", lambda e: self.cargar_consulta_ventas())

        tk.Button(
            filtros_bar, text="Filtrar Consulta", bg="#2563eb", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=14, pady=5, cursor="hand2", command=self.cargar_consulta_ventas
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            filtros_bar, text="Limpiar Filtros", bg="#64748b", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=12, pady=5, cursor="hand2", command=self.limpiar_filtros_consulta
        ).pack(side="left")

        # --- GRILLA DE RESULTADOS DE LA VISTA ---
        frame_tabla_vista = tk.Frame(area_consulta, bg="white", bd=1, relief="solid")
        frame_tabla_vista.pack(fill="both", expand=True)

        cols_vista = ("id_orden", "fecha_orden", "id_empleado", "empleado", "cargo", "cliente", "pais_destino", "cant_items", "total_orden")
        self.tree_vista = ttk.Treeview(frame_tabla_vista, columns=cols_vista, show="headings", selectmode="browse")

        encabezados_vista = {
            "id_orden": ("N° Orden", 75),
            "fecha_orden": ("Fecha", 95),
            "id_empleado": ("ID Emp.", 65),
            "empleado": ("Empleado", 160),
            "cargo": ("Cargo", 165),
            "cliente": ("Cliente", 200),
            "pais_destino": ("País Destino", 110),
            "cant_items": ("Cant. Ítems", 85),
            "total_orden": ("Total Orden ($)", 110)
        }

        for col, (texto, ancho) in encabezados_vista.items():
            self.tree_vista.heading(col, text=texto)
            alineacion = "w" if col in ("empleado", "cargo", "cliente") else "center"
            self.tree_vista.column(col, width=ancho, anchor=alineacion)

        scroll_y_vista = ttk.Scrollbar(frame_tabla_vista, orient="vertical", command=self.tree_vista.yview)
        self.tree_vista.configure(yscrollcommand=scroll_y_vista.set)

        self.tree_vista.pack(side="left", fill="both", expand=True)
        scroll_y_vista.pack(side="right", fill="y")

    def limpiar_filtros_consulta(self):
        self.var_filtro_emp.set("")
        self.var_filtro_pais.set("")
        self.cargar_consulta_ventas()

    def cargar_consulta_ventas(self):
        for item in self.tree_vista.get_children():
            self.tree_vista.delete(item)

        filtro_emp = f"%{self.var_filtro_emp.get().strip()}%"
        filtro_pais = f"%{self.var_filtro_pais.get().strip()}%"

        con = None
        cur = None
        try:
            con = obtener_conexion()
            cur = con.cursor()

            cur.execute("SELECT * FROM fn_buscar_ventas_empleados(%s, %s);",
            (filtro_emp, filtro_pais)
)

            for fila in cur.fetchall():
                valores = (
                    fila[0],
                    str(fila[1]),
                    fila[2],
                    fila[3],
                    fila[4],
                    fila[5],
                    fila[6],
                    fila[7],
                    f"$ {fila[8]:.2f}" if fila[8] is not None else "$ 0.00"
                )
                self.tree_vista.insert("", "end", values=valores)

        except Exception as e:
            messagebox.showerror("Error al consultar la vista", str(e))
        finally:
            if cur:
                cur.close()
            if con:
                con.close()