#Primero, agregamos el folder al terminal de la computadora
# instalamos un entorno virtual en tu computadora -- python -m venv .venv
# instalamos Streamlit y las librerías a utilizar en nuestro entorno virtual.
# pip install streamlit - pip install streamlit pandas (para la base de datos) y plotly
# ejecutamos en la terminal python -m streamlit run your_script.py
# pip install openpyxl
# pip install folium
# pip install streamlit-folium

# Importamos las librerías necesarias
import streamlit as st #Usada para crear el interfaz en donde podremos hacer la página
import pandas as pd #Utilizada para la manipulación y análisis de datos, se usará para manejar la base de datos
import numpy as np #Librería para trabajar con arrays y matrices (por si acaso)
from PIL import Image
import folium
from streamlit_folium import st_folium

#Para personalizar nuestra página, cambiaremos la apariencia principal
st.set_page_config(
    page_title="Fonkilla", #Configuramos el título que aparecerá en la pestaña de la página (es decir, en la parte superior). En este caso, será "Películas Peruanas".
    page_icon="🍽️", #Usamos un emoji que aparecerá junto al título.
    layout="wide") #Hacemos que todo el contenido de la app se extienda en la pantalla.

#creamos la barra lateral
paginas = ["Inicio", "Mapa", "Recomendaciones", "Ranking", "¿Sin tiempo de elegir?"]
# Creamos botones de navegación tomando la lista de páginas
pagina_seleccionada = st.sidebar.selectbox('Selecciona una página', paginas)

# Página de Inicio
if pagina_seleccionada == "Inicio":
    # La función st.markdown permite centrar y agrandar la letra del título de la web en Streamlit.
    st.markdown("<h1 style='text-align: center;'>Fonkilla: ¿Dónde comer en PUCP?🍔</h1>", unsafe_allow_html=True)
    #Agregamos una portada en la página principal, st. image es una función que se utiliza para mostrar imágenes. 
    st.image('Foto_1.jpg')
    st.markdown("""
    Bienvenido a FONKILLA: la guía interactiva de comida dentro de la PUCP. 
Esta plataforma te ayuda a encontrar los kioskos, restaurantes y máquinas expendedoras dentro del campus. 
Descubre los productos más vendidos, compara precios, revisa sus características y ubícalos fácilmente en nuestro mapa interactivo. 
Además, podrás dejar tu opinión y ver las calificaciones de otros estudiantes. ¡Todo lo que necesitas para comer bien y sin perder tiempo!
    """) #agregamos una pequeña intro
    st.success("Usa el menú de la izquierda para empezar a explorar.")

# usamos elif para llamar a cada página
elif pagina_seleccionada == "Mapa":
    st.title("Mapa de Kioskos y Restaurantes PUCP🗺️") #st.title para el título de la página
    st.info("Aquí se mostrará un mapa interactivo con los lugares para comer.") #st.info para remarcar la info importante

    # Cargamos la base de datos
    df = pd.read_excel("base.xlsx")

    # Agrupar por coordenadas y combinar nombres de locales
    lugares = (
        df.groupby(['latitud', 'longitud']).agg({
          'lugar': lambda x: ', '.join(sorted(set(x))),
          'producto': 'count'  # o cualquier columna que te dé idea del total
          }).reset_index().rename(columns={'producto': 'total_productos'}))

    # Centramos el mapa en la PUCP
    centro_pucp = [-12.068, -77.080]
    m = folium.Map(location=centro_pucp, zoom_start=17)

    # agregamos los marcadores y editamos para que hagan alusión a restaurantes
    for _, row in lugares.iterrows():
        popup_text = f"<b>Lugares:</b> {row['lugar']}<br><b>Total de productos:</b> {row['total_productos']}"
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='cutlery', prefix='fa') #con icon editamos color, iconos, etc
        ).add_to(m)

    # Mostrar en Streamlit
    st_folium(m, width=700, height=500)

    #debajo del mapa añadiremos un listado de todos los points con info relevante
    # Cargamos la base de datos
    df = pd.read_excel("base.xlsx") 

    # Agrupar por lugar (una fila por local)
    df_lugares = df.groupby('lugar').first().reset_index()

    # añadimos un filtro para facilitar la búsqueda
    zonas = ["Todas"] + sorted(df_lugares["zona pucp"].dropna().unique().tolist())
    zona_sel = st.selectbox("Filtrar por zona:", zonas)

    medios = ["Todos"] + sorted(set(m.strip() for sub in df_lugares["Medio de pago"].dropna() for m in sub.split(",")))

    # aplicamos el fintro, para que sea interactivo
    df_filtrado = df_lugares.copy()
    if zona_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["zona pucp"] == zona_sel]

    if not df_filtrado.empty:
        st.subheader("🍴 Lista de establecimientos:")
        st.dataframe(
            df_filtrado[['lugar', 'zona pucp', 'horario', 'Medio de pago']].reset_index(drop=True), #con ello decidimos qué info mostrar
            use_container_width=True)
    else:
        st.warning("No se encontraron lugares con esos filtros.")

elif pagina_seleccionada == "Recomendaciones":
    st.title("Recomendaciones personalizadas⭐")
    st.info("Responde unas preguntas y te diremos qué podrías comer hoy😋")

    # Cargar base
    df = pd.read_excel("base.xlsx")

    # Convertimos las columnas numéricas correctamente
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")

    # estandarizamos el contenido de la base de datos para evitar errores y omisiones
    df["zona pucp"] = df["zona pucp"].astype(str).str.strip().str.lower()
    df["tipo_general"] = df["tipo_general"].astype(str).str.strip().str.lower()
    df["subtipo"] = df["subtipo"].astype(str).str.strip().str.lower()
    df["proteína"] = df["proteína"].astype(str).str.strip().str.lower()
    df["temperatura"] = df["temperatura"].astype(str).str.strip().str.lower()

    # para el cuestionario
    # Pregunta 1: establecemos en qué Zona PUCP se encuentra
    zona = st.selectbox(
        "¿En qué zona de la PUCP te encuentras?",
        ["Selecciona una zona", "Tinkuy", "Sociales", "Librería", "Letras", "Pabellón V", "Gastronomía", "FCI", "Ciencias", "Mc Gregor", "Facultad de Arte y Diseño"]
    ) #escribimos las opciones de zonas que se encuentran en la base de datos

    # Pregunta 2: Tipo de comida
    tipo_general = st.selectbox("¿Qué te provoca hoy?", ["Selecciona una opción", "Plato de fondo", "Snack", "Bebida", "Postre"])

    # Pregunta 3: Presupuesto máximo
    precio_max = st.number_input("¿Cuál es tu presupuesto máximo (S/.)?", min_value=1.0, step=0.5) #colocamos mínimo valor para que no puedan colocar valores negativos

    # Filtro inicial por precio
    filtro = df[df["precio"] <= precio_max]

    # Filtro por zona
    if zona != "Selecciona una zona":
        filtro = filtro[filtro["zona pucp"] == zona.lower()]

    # creamos filtros más específicos para cada opción
    if tipo_general == "Plato de fondo":
        filtro = filtro[filtro["tipo_general"] == "plato de fondo"]

        menu_o_plato = st.radio("¿Deseas un menú, plato a la carta o buffet?", ["Menú", "Plato a la carta", "Buffet"])
        filtro = filtro[filtro["subtipo"] == menu_o_plato.lower()]

        opcion_veg = st.radio("¿Prefieres opción vegana o con proteína?", ["Vegano", "Con proteína"])
        if opcion_veg == "Vegano":
            filtro = filtro[filtro["vegano"] == 1]  # 1 ya que colocamos en nuestra base valores booleanos
        else:
            proteina = st.selectbox("¿Qué proteína prefieres?", ["Res", "Pollo", "Cerdo", "Pescado"])
            filtro = filtro[filtro["proteína"] == proteina.lower()]

    elif tipo_general == "Snack":
        filtro = filtro[filtro["tipo_general"] == "snack"]
        snack_tipo = st.radio("¿Dulce o salado?", ["Dulce", "Salado"])
        dulce_bool = 1 if snack_tipo == "Dulce" else 0
        filtro = filtro[filtro["dulce"] == dulce_bool]

    elif tipo_general == "Bebida":
        filtro = filtro[filtro["tipo_general"] == "bebida"]
    
        bebida_tipo = st.radio("¿Frío o caliente?", ["Frío", "Caliente"])
        filtro = filtro[filtro["temperatura"].str.lower() == bebida_tipo.lower()]

    elif tipo_general == "Postre":
        filtro = filtro[filtro["tipo_general"] == "postre"]

# Mostramos resultados
    if tipo_general != "Selecciona una opción" and zona != "Selecciona una zona" and not filtro.empty:
        st.subheader("🎯 Te recomendamos:")
        resultados = filtro[['producto', 'descripción', 'lugar', 'zona pucp', 'precio',
                             'Foto del lugar', 'temperatura', 'Tiempo de preparación/atención aproximado en min', 'gluten']].head(5)

        for i, row in resultados.iterrows():
            st.markdown("---")  # Separador visual
            st.image(row['Foto del lugar'], width=300, caption=row['lugar'])  # Imagen del lugar

            st.write(f"🍴 **Producto:** {row['producto']}")
            st.write(f"📍 **Lugar:** {row['lugar']} ({row['zona pucp']})")
            st.write(f"📝 **Descripción:** {row['descripción']}")
            st.write(f"💰 **Precio:** S/. {row['precio']:.2f}")
            st.write(f"🌡️ **Temperatura:** {row['temperatura'].capitalize() if pd.notna(row['temperatura']) else 'No especificado'}")
            st.write(f"⏱️ **Tiempo aprox. de preparación:** {int(row['Tiempo de preparación/atención aproximado en min']) if pd.notna(row['Tiempo de preparación/atención aproximado en min']) else 'No disponible'} min")
            st.write(f"🌾 **¿Contiene gluten?:** {'Sí' if row['gluten'] == 1 else 'No'}")

    elif tipo_general != "Selecciona una opción" and zona != "Selecciona una zona" and filtro.empty:
        st.warning("No se encontraron productos con esas características 😢") #por si no hay ningún producto que se ajuste a los filtros

elif pagina_seleccionada == "Ranking":
    st.title("Ranking de lugares 🏆")
    st.info("Rankea tus points favoritos.")

    # Lista de todos los establecimientos
    lugares = ["De afuera pa dentro", "Pollería Cocotte", "Ntx", "Bembos", "Street Attitud", "Tiendita Marva",
               "Juan Valdez Café", "Frutilla", "Elemar", "Gelarti", "Kilomío", "Diodo", 'Kiosco Sociales "Isalia y Enrique"',
               "Comedor central", "Máquina vendomática", "Máquinas Coca Cola", "Máquina Lavazza", "Comedor de letras",
               "Charlotte", "El Puesto", "Comedor artes"]

    lugar_seleccionado = st.selectbox("Selecciona un lugar para puntuar:", lugares)
    estrellas = st.slider("¿Cuántas estrellas le das?", 1, 5)
    comentario = st.text_area("Deja un comentario (opcional):")

    # Creamos un espacio de almacenamiento temporal
    if 'calificaciones' not in st.session_state:
        st.session_state.calificaciones = {}

    # Solo se guarda cuando se presiona el botón
    if st.button("Enviar puntuación"):
        if lugar_seleccionado not in st.session_state.calificaciones:
            st.session_state.calificaciones[lugar_seleccionado] = []

        st.session_state.calificaciones[lugar_seleccionado].append({
            "puntos": estrellas,
            "comentario": comentario
        })
        st.success(f"Gracias por tu opinión sobre {lugar_seleccionado} ⭐")

    # Para visualizar los resultados
    if st.checkbox("Ver puntuaciones registradas"):
        if 'calificaciones' in st.session_state:
            for lugar, datos in st.session_state.calificaciones.items():
                st.subheader(lugar)
                for i, d in enumerate(datos, 1):
                    st.write(f"{i}. ⭐ {d['puntos']} - {d['comentario']}") #anidamos los dos resultados

elif pagina_seleccionada == "¿Sin tiempo de elegir?":
    st.title("¿Sin tiempo de elegir?⏰")
    st.info("¿Muy ocupado? Encuentra tu combo perfecto y ahorra tiempo.")
    
    df = pd.read_excel("base.xlsx") 
    #para verificar que la columna existe y evitar errores
    if "combo/pack/promoción" not in df.columns:
        st.error("La columna 'combo/pack/promoción' no existe en la base de datos.")
    else:
        # filtramos los productos que sean combos (donde la columna es 1 por booleanos)
        combos = df[df["combo/pack/promoción"] == 1]

        if combos.empty:
            st.warning("No se encontraron combos o promociones disponibles.")
        else:
            st.subheader("✨ Opciones disponibles:")
            st.dataframe(
                combos[["producto", "descripción", "lugar", "zona pucp", "precio"]].reset_index(drop=True),
                use_container_width=True
            )