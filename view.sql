
CREATE OR REPLACE VIEW public.vw_ventas_empleados AS
SELECT 
    o.orderid AS id_orden,
    o.orderdate::date AS fecha_orden,
    e.employeeid AS id_empleado,
    (e.lastname || ', ' || e.firstname) AS empleado,
    e.title AS cargo,
    c.companyname AS cliente,
    c.country AS pais_destino,
    COUNT(od.productid) AS cant_items,
    ROUND(SUM(od.quantity * od.unitprice * (1 - od.discount))::numeric, 2) AS total_orden
FROM public.employees e
INNER JOIN public.orders o ON e.employeeid = o.employeeid
INNER JOIN public.customers c ON o.customerid = c.customerid
INNER JOIN public.orderdetails od ON o.orderid = od.orderid
GROUP BY 
    o.orderid, o.orderdate, e.employeeid, e.lastname, 
    e.firstname, e.title, c.companyname, c.country;