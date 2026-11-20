import tkinter as tk
from tkinter import messagebox, ttk

import psycopg2

DB_CONFIG = {
    "dbname": "northwind_2", #nuestra bd
    "user": "postgres",
    "password": "postgres",  # ponemos nuestra contraseña si tenemos
    "host": "127.0.0.1",
    "port": "5432",
    "client_encoding":"utf8"
}

def obtener_conexion():
    return psycopg2.connect(**DB_CONFIG)

# CLASE PRINCIPAL DE LA APLICACION 
class AppNorthwindProductos:
    def __init__(self, root):
        self.root = root
        self.root.title("Northwind - Gestión de Productos (ABM)")
        self.root.geometry("1280x720")
        self.root.configure(bg="#bfbfbf")

        self.construir_interfaz()
        self.cargar_productos()

    def construir_interfaz(self):
        # --- barra nav ---
        navbar = tk.Frame(self.root, bg="#27416B", height=75)
        navbar.pack(side="top", fill="x")
        navbar.pack_propagate(False)

        tk.Label(
            navbar, text="ABM - PRODUCTOS", fg="white", bg="#27416B",
            font=("Great Vibes", 16, "bold")
        ).pack(pady=(25, 2), padx=20, anchor="w")

        tk.Label(
            navbar, text="GESTIÓN DE PRODUCTOS", fg="#94a3b8", bg="#27416B",
            font=("Great Vibes", 10, "bold")
        ).pack(side="left", padx=25)

        tk.Label(
            navbar, text="▶  Productos (ABM)", fg="white" ,bg="#27416B",
            font=("Great Vibes", 10, "bold"), pady=10, padx=20, anchor="w"
        ).pack(side="right", padx=25)

        # --- ÁREA PRINCIPAL DERECHA ---
        main_area = tk.Frame(self.root,bg= "#bfbfbf")
        main_area.pack(side="top", fill="both", expand=True, padx=25, pady=18)

        # Encabezado
        tk.Label(
            main_area, text="Administración de Productos", fg="#0f172a", bg="#bfbfbf",
            font=("Great Vibes", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            main_area, text="Consulta, registra, modifica y da de baja productos.",
            fg="#36485f",bg= "#bfbfbf", font=("Great Vibes", 10)
        ).pack(anchor="w", pady=(2, 15))

        # --- BARRA DE BÚSQUEDA Y BOTONES DE ACCIÓN ---
        barraBusqueda = tk.Frame(main_area, bg="#bfbfbf")
        barraBusqueda.pack(fill="x", pady=(0, 12))

        self.var_buscar = tk.StringVar()
        entry_buscar = tk.Entry(barraBusqueda, textvariable=self.var_buscar, font=("Great Vibes", 10), width=35,placeholder="Buscar por nombre de producto")
        entry_buscar.pack(side="left", ipady=4, padx=(0, 8))
        entry_buscar.bind("<Return>", lambda e: self.cargar_productos())

        tk.Button(
            barraBusqueda, text="Buscar", bg="#2563eb", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=14, pady=5, cursor="hand2", command=self.cargar_productos
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            barraBusqueda, text="Limpiar", bg="#64748b", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=10, pady=5, cursor="hand2", command=self.limpiar_busqueda
        ).pack(side="left")

        # Botones ABM 
        abm_botones = tk.Frame(main_area,bg="#bfbfbf",pady=5)
        abm_botones.pack(fill="x", pady=(0, 10))
        
        contenedor_centro = tk.Frame(abm_botones, bg="#bfbfbf")
        contenedor_centro.pack(anchor="center",pady=(15, 5))


        tk.Button(
            contenedor_centro, text="+ Nuevo Producto", bg="#27416B", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=14, pady=5, cursor="hand2", command=lambda: self.abrir_formulario("A")
        ).pack(side="left", padx=(0,12))

        tk.Button(
            contenedor_centro, text="Editar Seleccionado", bg="#27416B", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=14, pady=5, cursor="hand2", command=self.preparar_edicion
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            contenedor_centro, text="Eliminar Seleccionado", bg="#27416B", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=14, pady=5, cursor="hand2", command=self.eliminar_producto
        ).pack(side="left")

        # --- GRILLA DE DATOS (TREEVIEW) ---
        frame_tabla = tk.Frame(main_area, bg="white", bd=1, relief="solid")
        frame_tabla.pack(fill="both", expand=True)

        columnas = ("id", "nombre", "proveedor", "categoria", "unidad", "precio", "stock", "orden", "reorden", "estado", "id_proveedor", "id_categoria")
        columnas_visibles= ("id", "nombre", "proveedor", "categoria", "unidad", "precio", "stock", "orden", "reorden", "estado")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", selectmode="browse", displaycolumns=columnas_visibles)

        encabezados = {
            "id": ("ID", 50),
            "nombre": ("Producto", 210),
            "proveedor": ("ID Proveedor", 65),
            "categoria": ("ID Categoria", 65),
            "unidad": ("Presentación", 135),
            "precio": ("Precio ($)", 80),
            "stock": ("Stock", 60),
            "orden": ("Unidades encargadas", 65),
            "reorden": ("Reabastecimiento", 65),
            "estado": ("Estado", 95)
        }

        for col, (texto, ancho) in encabezados.items():
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=ancho, anchor="center" if col != "nombre" else "w")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    # ==========================================================================
    # 3. MÉTODOS DE CONSULTA Y LLAMADA A LA FUNCIÓN ABM EN POSTGRESQL
    # ==========================================================================
    def limpiar_busqueda(self):
        self.var_buscar.set("")
        self.cargar_productos()

    def cargar_productos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtro = f"%{self.var_buscar.get().strip()}%"
        con = None
        try:
            con = obtener_conexion()
            cur = con.cursor()
            cur.execute("SELECT * FROM fn_buscar_productos(%s);", (filtro,))

            for fila in cur.fetchall():
                estado_txt = "Descontinuado" if fila[9] else "Activo"
                valores = (
                    fila[0], fila[1], fila[2], fila[3], fila[4],
                    f"{fila[5]:.2f}" if fila[5] is not None else "0.00",
                    fila[6], fila[7], fila[8], estado_txt, fila[10], fila[11]
                )
                self.tree.insert("", "end", values=valores)

        except Exception as e:
            messagebox.showerror("Error al cargar datos", str(e))
        finally:
            if con:
                cur.close()
                con.close()

    def invocar_funcion_abm(self, accion, p_id, nombre, id_prov, id_cat, unidad, precio, stock, orden, reorden, descontinuado):
        con = None
        try:
            con = obtener_conexion()
            cur = con.cursor()

            # ÚNICO PUNTO DE ENTRADA PARA A, B y M
            query = "SELECT fn_abm_producto(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            params = (accion, p_id, nombre, id_prov, id_cat, unidad, precio, stock, orden, reorden, descontinuado)

            cur.execute(query, params)
            mensaje_bd = cur.fetchone()[0]
            con.commit()

            messagebox.showinfo("Operación Exitosa", mensaje_bd)
            self.cargar_productos()
            return True

        except psycopg2.Error as db_err:
            if con:
                con.rollback()
            # Extraemos el mensaje limpio del RAISE EXCEPTION de PostgreSQL
            mensaje_limpio = db_err.pgerror.split("CONTEXT:")[0].replace("ERROR:", "").strip() if db_err.pgerror else str(db_err)
            messagebox.showerror("Validación de Base de Datos", mensaje_limpio)
            return False

        except Exception as e:
            if con:
                con.rollback()
            messagebox.showerror("Error", str(e))
            return False

        finally:
            if con:
                cur.close()
                con.close()

    def eliminar_producto(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, seleccioná un producto de la lista para eliminar.")
            return

        datos = self.tree.item(seleccion[0], "values")
        p_id = int(datos[0])
        nombre = datos[1]

        confirmar = messagebox.askyesno(
            "Confirmar Baja",
            f"¿Estás segura de que querés dar de baja el producto:\n\nID {p_id} - {nombre}?"
        )
        if confirmar:
            self.invocar_funcion_abm("B", p_id, None, None, None, None, None, None, None, None, None)

    def preparar_edicion(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Por favor, seleccioná un producto de la lista para editar.")
            return

        datos = self.tree.item(seleccion[0], "values")
        self.abrir_formulario("M", datos)

    # ==========================================================================
    # 4. VENTANA EMERGENTE (FORMULARIO DE ALTA Y MODIFICACIÓN)
    # ==========================================================================
    def abrir_formulario(self, accion, datos=None):
        modal = tk.Toplevel(self.root)
        modal.title("Nuevo Producto" if accion == "A" else f"Modificar Producto (ID {datos[0]})")
        modal.geometry("430x480")
        modal.configure(bg="white")
        modal.grab_set()  # Bloquea la ventana trasera hasta cerrar el formulario

        titulo = "Registrar nuevo producto" if accion == "A" else "Modificar datos del producto"
        tk.Label(modal, text=titulo, font=("Great Vibes", 14, "bold"), bg="white", fg="#0f172a").pack(pady=(15, 5))
        tk.Label(modal, text="Completá los campos y presioná Guardar", font=("Great Vibes", 9), bg="white", fg="#64748b").pack(pady=(0, 15))

        form_frame = tk.Frame(modal, bg="white")
        form_frame.pack(padx=30, fill="x")

        campos = [
            ("ID del Producto *:", "id"),
            ("Nombre del Producto *:", "nombre"),
            ("ID Proveedor (ej. 1):", "prov"),
            ("ID Categoría (ej. 1):", "cat"),
            ("Cantidad por Unidad:", "unidad"),
            ("Precio Unitario ($):", "precio"),
            ("Unidades en Stock:", "stock"),
            ("Unidades Encargadas:", "orden"),
            ("Reabastecimiento", "reorden")
        ]

        entradas = {}
        for idx, (etiqueta, clave) in enumerate(campos):
            tk.Label(form_frame, text=etiqueta, bg="white", fg="#334155", font=("Great Vibes", 9, "bold")).grid(row=idx, column=0, sticky="w", pady=5)
            ent = tk.Entry(form_frame, font=("Great Vibes", 9), width=25, bg="#f8fafc")
            ent.grid(row=idx, column=1, sticky="e", pady=5)
            entradas[clave] = ent

        var_descontinuado = tk.BooleanVar(value=False)
        chk_desc = tk.Checkbutton(
            form_frame, text="Producto Descontinuado", variable=var_descontinuado,
            bg="white", font=("Great Vibes", 9)
        )
        chk_desc.grid(row=len(campos), column=0, columnspan=2, sticky="w", pady=8)

        # Si es Modificación ('M'), precargamos los datos y bloqueamos el ID
        if accion == "M" and datos:
            entradas["id"].insert(0, datos[0])
            entradas["id"].config(state="disabled")
            entradas["nombre"].insert(0, datos[1])
            entradas["prov"].insert(0, "" if datos[10] == "None" else datos[10])
            entradas["cat"].insert(0, "" if datos[11] == "None" else datos[11])
            entradas["unidad"].insert(0, "" if datos[4] == "None" else datos[4])
            entradas["precio"].insert(0, datos[5])
            entradas["stock"].insert(0, datos[6])
            entradas["orden"].insert(0, datos[7])
            entradas["reorden"].insert(0, datos[8])
            var_descontinuado.set(datos[9] == "Descontinuado")

        def procesar_guardado():
            try:
                p_id = int(entradas["id"].get().strip())
                nombre = entradas["nombre"].get().strip()
                prov = int(entradas["prov"].get().strip()) if entradas["prov"].get().strip() else None
                cat = int(entradas["cat"].get().strip()) if entradas["cat"].get().strip() else None
                unidad = entradas["unidad"].get().strip() or None
                precio = float(entradas["precio"].get().strip()) if entradas["precio"].get().strip() else 0.0
                stock = int(entradas["stock"].get().strip()) if entradas["stock"].get().strip() else 0
                orden = int(entradas["orden"].get().strip()) if entradas["orden"].get().strip() else 0
                reorden = int(entradas["reorden"].get().strip()) if entradas["reorden"].get().strip() else 0
                desc = var_descontinuado.get()

                exito = self.invocar_funcion_abm(accion, p_id, nombre, prov, cat, unidad, precio, stock, orden, reorden, desc)
                if exito:
                    modal.destroy()

            except ValueError:
                messagebox.showerror("Error de Formato", "Verificá que ID, Proveedor, Categoría, Precio y Stock sean valores numéricos válidos.", parent=modal)

        btn_frame = tk.Frame(modal, bg="white")
        btn_frame.pack(pady=15)

        tk.Button(
            btn_frame, text="Guardar", bg="#16a34a", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=20, pady=6, cursor="hand2", command=procesar_guardado
        ).pack(side="left", padx=8)

        tk.Button(
            btn_frame, text="Cancelar", bg="#64748b", fg="white", font=("Great Vibes", 9, "bold"),
            relief="flat", padx=20, pady=6, cursor="hand2", command=modal.destroy
        ).pack(side="left", padx=8)

# ==============================================================================
# 5. PUNTO DE ARRANQUE DE LA APLICACIÓN
# ==============================================================================
if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppNorthwindProductos(ventana)
    ventana.mainloop()
