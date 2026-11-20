CREATE OR REPLACE FUNCTION fn_abm_producto (
    p_accion text,               -- 'A' (Alta), 'M' (Modificación), 'B' (Baja)
    p_productid integer,         -- ID del producto (se pasa NULL o 0 en el Alta)
    p_productname varchar(40),   -- Nombre del producto
    p_supplierid integer,        -- ID del proveedor
    p_categoryid integer,        -- ID de la categoría
    p_quantityperunit varchar,   -- Cantidad por unidad (ej: '10 boxes x 20 bags')
    p_unitprice numeric,         -- Precio unitario
    p_unitsinstock integer,      -- Stock actual
    p_unitsonorder integer,      -- Unidades encargadas
    p_reorderlevel integer,      -- Nivel de reorden
    p_discontinued boolean       -- 0: Activo, 1: Descontinuado (o boolean según tu esquema)
)
RETURNS text AS $$
DECLARE
    v_existe boolean;
    v_tiene_ventas boolean;
BEGIN
    -- 1. Validar que la acción sea una de las tres permitidas
    IF p_accion NOT IN ('A', 'M', 'B') THEN
        RAISE EXCEPTION 'Acción inválida: %. Use A (Alta), M (Modificación) o B (Baja).', p_accion;
    END IF;

    ---------------------------------------------------------------------------
    -- ALTA (INSERT)
    ---------------------------------------------------------------------------
    IF p_accion = 'A' THEN
        -- Validaciones de Entrada
		IF p_productid IS NULL OR p_productid <= 0 THEN
            RAISE EXCEPTION 'Debe ingresar un ID de producto válido (mayor a 0).';
        END IF;

		SELECT EXISTS(SELECT 1 FROM products WHERE productid = p_productid) INTO v_existe;
        IF v_existe THEN
            RAISE EXCEPTION 'El ID de producto % ya está ocupado. Elija otro número.', p_productid;
        END IF;


        IF p_productname IS NULL OR trim(p_productname) = '' THEN
            RAISE EXCEPTION 'El nombre del producto no puede estar vacío.';
        END IF;

        IF p_unitprice < 0 THEN
            RAISE EXCEPTION 'El precio unitario no puede ser negativo (Precio: %).', p_unitprice;
        END IF;

        IF p_unitsinstock < 0 THEN
            RAISE EXCEPTION 'El stock en existencia no puede ser negativo.';
        END IF;

        -- Validar Integridad Referencial de Categoría y Proveedor
        IF p_categoryid IS NOT NULL THEN
            SELECT EXISTS(SELECT 1 FROM categories WHERE categoryid = p_categoryid) INTO v_existe;
            IF NOT v_existe THEN
                RAISE EXCEPTION 'La categoría seleccionada (ID %) no existe.', p_categoryid;
            END IF;
        END IF;

        IF p_supplierid IS NOT NULL THEN
            SELECT EXISTS(SELECT 1 FROM suppliers WHERE supplierid = p_supplierid) INTO v_existe;
            IF NOT v_existe THEN
                RAISE EXCEPTION 'El proveedor seleccionado (ID %) no existe.', p_supplierid;
            END IF;
        END IF;

        -- Ejecutar el Alta 
        INSERT INTO products (productid,
            productname, supplierid, categoryid, quantityperunit, 
            unitprice, unitsinstock, unitsonorder, reorderlevel, discontinued
        )
        VALUES (
            p_productid,trim(p_productname), p_supplierid, p_categoryid, p_quantityperunit, 
            p_unitprice, COALESCE(p_unitsinstock, 0), COALESCE(p_unitsonorder, 0), 
            COALESCE(p_reorderlevel, 0), COALESCE(p_discontinued, false)
        );

        RETURN 'Producto agregado exitosamente.';

    ---------------------------------------------------------------------------
    -- MODIFICACIÓN (UPDATE)
    ---------------------------------------------------------------------------
    ELSIF p_accion = 'M' THEN
        -- Validar existencia del Producto
        SELECT EXISTS(SELECT 1 FROM products WHERE productid = p_productid) INTO v_existe;
        IF NOT v_existe THEN
            RAISE EXCEPTION 'El producto con ID % no existe.', p_productid;
        END IF;

        -- Validaciones
        IF p_productname IS NULL OR trim(p_productname) = '' THEN
            RAISE EXCEPTION 'El nombre del producto no puede estar vacío.';
        END IF;

        IF p_unitprice < 0 THEN
            RAISE EXCEPTION 'El precio unitario no puede ser negativo.';
        END IF;

        IF p_unitsinstock < 0 THEN
            RAISE EXCEPTION 'El stock en existencia no puede ser negativo.';
        END IF;

        -- Ejecutar la Modificación
        UPDATE products 
        SET productname     = trim(p_productname),
            supplierid      = p_supplierid,
            categoryid      = p_categoryid,
            quantityperunit = p_quantityperunit,
            unitprice       = p_unitprice,
            unitsinstock    = p_unitsinstock,
            unitsonorder    = p_unitsonorder,
            reorderlevel    = p_reorderlevel,
            discontinued    = COALESCE(p_discontinued, false)
        WHERE productid = p_productid;

        RETURN 'Producto modificado exitosamente.';

    ---------------------------------------------------------------------------
    -- BAJA (DELETE / LOGICAL DELETE)
    ---------------------------------------------------------------------------
    ELSIF p_accion = 'B' THEN
        -- Validar existencia del Producto
        SELECT EXISTS(SELECT 1 FROM products WHERE productid = p_productid) INTO v_existe;
        IF NOT v_existe THEN
            RAISE EXCEPTION 'No se puede eliminar: El producto con ID % no existe.', p_productid;
        END IF;

        -- Validar si el producto ya fue vendido en la tabla orderdetails
        SELECT EXISTS(SELECT 1 FROM orderdetails WHERE productid = p_productid) INTO v_tiene_ventas;

        IF v_tiene_ventas THEN
            -- Opción Recomendada: En lugar de borrarlo y romper historial, se descontinúa
            UPDATE products SET discontinued = true WHERE productid = p_productid;
            RETURN 'El producto no se eliminó físicamente porque posee ventas registradas, pero fue marcado como DESCONTINUADO.';
        ELSE
            -- Si no tiene ventas, se borra físicamente de la BD
            DELETE FROM products WHERE productid = p_productid;
            RETURN 'Producto eliminado físicamente de la base de datos.';
        END IF;

    END IF;
END;
$$ LANGUAGE plpgsql;


-- Prueba de alta
SELECT fn_abm_producto('A', 80, 'Yerba Mate Premium', 1, 1, 'Bolsa 1kg', 1200.50, 50, 0, 10, false );

-- Prueba de alta con error
SELECT fn_abm_producto('A', NULL, 'Café Torrado', 1, 1, '500g', -50.00, 10, 0, 5, 0);

-- Prueba de modificacion 
SELECT fn_abm_producto('M', 80, 'Yerba Mate Seleccionada', 1, 1, 'Bolsa 1kg', 1350.00, 45, 0, 10, 0);

-- Prueba de baja
SELECT fn_abm_producto('B', 80, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);


-- Funcion para traer y buscar productos.
CREATE OR REPLACE FUNCTION public.fn_buscar_productos(p_filtro varchar DEFAULT '')
RETURNS TABLE (
    productid int4,
    productname varchar,
    companyname varchar,
    categoryname varchar,
    quantityperunit varchar,
    unitprice numeric,
    unitsinstock int4,
    unitsonorder int4,
    reorderlevel int4,
    discontinued bool,
    supplierid int4,
    categoryid int4
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.productid,
        p.productname,
        s.companyname,
        c.categoryname,
        p.quantityperunit,
        p.unitprice,
        p.unitsinstock,
        p.unitsonorder,
        p.reorderlevel,
        p.discontinued,
        s.supplierid,
        c.categoryid
    FROM public.products p
    INNER JOIN public.suppliers s ON p.supplierid = s.supplierid
    INNER JOIN public.categories c ON p.categoryid = c.categoryid
    WHERE p.productname ILIKE '%' || COALESCE(p_filtro, '') || '%'
    ORDER BY p.productid ASC;
END;
$$;





