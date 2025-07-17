# %%
import pandas as pd
import numpy as np
import datetime



# %%
columnas = ['Order \nNumber', 'Fecha Estimada De Llegada','Fecha del\nPedido','Fecha\nFactura', 'Fecha\nllegada DITEC', 'Códigos','Qty','Forma de\nenvío','Marca','Factura']


# %%
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os

# Crear la ventana principal oculta (necesaria para abrir el explorador de archivos)
root = tk.Tk()
root.withdraw()  # Ocultar la ventana principal de tkinter

# Abrir un cuadro de diálogo para seleccionar el archivo de stock
archivo_tubo = filedialog.askopenfilename(
    title="Selecciona el archivo de Panel de Control",
    filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
)

# Verificar si se seleccionó algún archivo
if archivo_tubo:
    print(f"Archivo de Control de pedidos seleccionado: {archivo_tubo}")
    dtypes={'Order \nNumber':'str','Códigos':'str'}
    
    # Leer el archivo seleccionado
    df = pd.read_excel(archivo_tubo, dtype=dtypes, sheet_name="Control de pedidos LR",usecols = columnas,header=1, parse_dates=['Fecha\nFactura'])
    print("Archivo de Control de pedidos cargado correctamente.")
else:
    print("No se seleccionó ningún archivo de Stock.")

# %%
transito = df.rename(columns={'Order \nNumber': 'Documento compras', 'Fecha\nFactura':'Fecha Factura', 'Fecha\nllegada DITEC':'Fecha ATA', 'Códigos':'Material','Qty':'Cantidad','Forma de\nenvío':'Via','Marca':'Marca' , 'Fecha del\nPedido':'Fecha Pedido'})

# %%
import pandas as pd
import numpy as np

# Assuming your DataFrame is called 'transito'

# Condition for 'Facturado': is it a number AND greater than 0?
is_numeric = pd.to_numeric(transito['Factura'], errors='coerce').notna()
is_greater_than_zero = pd.to_numeric(transito['Factura'], errors='coerce') > 0
condition_facturado = is_numeric & is_greater_than_zero

# %%
cond = [
    transito['Factura'] == "BO",
    transito['Factura'] == "Cancelado",
    transito['Factura'] == "Obsoleto",
    transito['Factura'].isna(),
    condition_facturado  # Our new condition for "Facturado"
]
opc = [
    'Back Order',
    '',
    '',
    'OC Fabrica',
    'Facturado'
]

transito['Estado'] = np.select(cond, opc, default='Otro Estado') # Added a default case

# %%
transito['Estado'].value_counts()

# %%
transito['AUX'] = transito['Documento compras'] + transito['Material']


# %%
transito['Cantidad_transito'] = 0  # Initialize the new column with 0

# Use .loc to set 'Cantidad_transito' to 'Cantidad' where 'Fecha ATA' is null
transito.loc[transito['Fecha ATA'].isna(), 'Cantidad_transito'] = transito['Cantidad']


# %%
cond = [transito['Via']=='Courrier',transito['Via']=='Aéreo', transito['Via']=='Marítimo']
opc = [10,20,90]

transito['dias_suma_vía'] = np.select(cond, opc)



# %%


# %%
transito['Fecha Pedido'] = pd.to_datetime(transito['Fecha Pedido'])
#transito['Fecha Estimada De Llegada'] = pd.to_datetime(transito['Fecha Estimada De Llegada'])

# %%
import pandas as pd
import numpy as np
import datetime

# Assuming 'transito' DataFrame is already loaded and has the necessary columns:
# 'Cantidad_transito', 'Estado', 'Fecha Estimada De Llegada',
# 'Fecha Pedido', 'dias_suma_vía', and 'fecha_estimada_llegada' (even if it's going to be overwritten)

# --- Second Code Snippet (Calculate/Recalculate 'fecha_estimada_llegada') ---
cond_estimada = [
    transito['Cantidad_transito'] == 0,
    transito['Estado'] == 'Facturado',
    (transito['Cantidad_transito'] != 0) & (transito['Fecha Estimada De Llegada'].isna())
]
opc_estimada = [
    pd.NaT,
    transito['Fecha Estimada De Llegada'], # This assumes 'Fecha Estimada De Llegada' is a separate column
    transito['Fecha Pedido'] + pd.to_timedelta(transito['dias_suma_vía'], unit='D')
]
default_option_estimada = transito['Fecha Pedido'] + pd.to_timedelta(transito['dias_suma_vía'], unit='D')

transito['fecha_estimada_llegada'] = np.select(cond_estimada, opc_estimada, default=default_option_estimada)
# Ensure this column is datetime after the operation

# %%

#transito['fecha_estimada_llegada'] = pd.to_datetime(transito['fecha_estimada_llegada'])


# --- First Code Snippet (Calculate 'Fecha Llegada Final') ---
hoy = pd.to_datetime(datetime.datetime.today().date()) # Get today's date

transito['fecha_estimada_llegada'] = pd.to_datetime(transito['fecha_estimada_llegada'])
cond_final = [hoy > transito['fecha_estimada_llegada']]


# %%
opc_final = [hoy + pd.to_timedelta(transito['dias_suma_vía'], unit='D')]

transito['Fecha Llegada Final'] = np.select(cond_final, opc_final, transito['fecha_estimada_llegada'])

# Ensure the new column is also datetime
transito['Fecha Llegada Final'] = pd.to_datetime(transito['Fecha Llegada Final'])

# %%
transito['Semana Llegada'] = transito['Fecha Llegada Final'].dt.isocalendar().week

# %%
transito['AUX'] = transito['Documento compras'] + transito['Material']

print(transito.dtypes)
print(transito.isna().sum())

# %%
transito_final = transito[(transito['Estado'].isin(['Facturado', 'Back Order', 'OC Fabrica'])) &
    (transito['Cantidad_transito'] > 0)][['AUX', 'Cantidad_transito','Fecha Llegada Final']]




# %%
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename



# Ocultar ventana principal de tkinter
root = Tk()
root.withdraw()

# Abrir cuadro de diálogo para elegir la ubicación de guardado
file_path = asksaveasfilename(
    defaultextension=".xlsx",
    filetypes=[("Excel files", "*.xlsx")],
    title="Guardar archivo como"
)

# Guardar si se seleccionó una ruta
if file_path:
    transito_final.to_excel(file_path, index=False)
    print(f"Archivo guardado en: {file_path}")
else:
    print("Guardado cancelado por el usuario.")


# %%



