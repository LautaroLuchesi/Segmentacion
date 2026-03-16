import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans


# =========================
# CONFIGURACIÓN GENERAL
# =========================
RUTA_DATASET = "marketing_campaign.csv"
COLUMNAS_RFM = ["Recency", "total_compras", "gasto_total"]
COLUMNAS_PERFIL = ["Recency", "total_compras", "gasto_total", "Income"]
N_CLUSTERS = 4
RANDOM_STATE = 42


# =========================
# CARGA Y PREPARACIÓN
# =========================
def cargar_y_limpiar_datos(ruta_csv: str) -> pd.DataFrame:
    """
    Carga el dataset, elimina outliers evidentes y crea variables útiles
    para el análisis de segmentación.
    """
    df = pd.read_csv(ruta_csv, sep="\t")

    # Eliminar outlier extremo de ingresos
    df = df[df["Income"] < 200000].copy()

    # Crear variable de gasto total
    df["gasto_total"] = (
        df["MntWines"]
        + df["MntFruits"]
        + df["MntMeatProducts"]
        + df["MntFishProducts"]
        + df["MntSweetProducts"]
        + df["MntGoldProds"]
    )

    # Crear variable de frecuencia de compra
    df["total_compras"] = (
        df["NumWebPurchases"]
        + df["NumCatalogPurchases"]
        + df["NumStorePurchases"]
    )

    return df


# =========================
# ANÁLISIS EXPLORATORIO
# =========================
def mostrar_resumen_variables(df: pd.DataFrame) -> None:
    """
    Muestra ejemplos de las nuevas variables calculadas.
    """
    print("\nPrimeras filas del dataset:")
    print(df.head())

    print("\nResumen de gasto total por cliente:")
    print(df["gasto_total"].head())

    print("\nResumen de total de compras por cliente:")
    print(df["total_compras"].head())


def graficar_ingreso_vs_gasto(df: pd.DataFrame) -> None:
    """
    Grafica la relación entre ingreso y gasto total.
    """
    plt.figure(figsize=(8, 5))
    plt.scatter(df["Income"], df["gasto_total"])
    plt.xlabel("Ingreso")
    plt.ylabel("Gasto total")
    plt.title("Relación entre ingreso y gasto de clientes")
    plt.show()


def graficar_compras_vs_gasto(df: pd.DataFrame) -> None:
    """
    Grafica la relación entre frecuencia de compra y gasto total.
    """
    plt.figure(figsize=(8, 5))
    plt.scatter(df["total_compras"], df["gasto_total"])
    plt.xlabel("Total de compras")
    plt.ylabel("Gasto total")
    plt.title("Relación entre frecuencia de compra y gasto")
    plt.show()


def graficar_distribucion_recency(df: pd.DataFrame) -> None:
    """
    Grafica la distribución de recencia.
    """
    plt.figure(figsize=(8, 5))
    df["Recency"].hist(bins=30)
    plt.title("Distribución de recencia")
    plt.xlabel("Días desde la última compra")
    plt.ylabel("Cantidad de clientes")
    plt.show()


# =========================
# CLUSTERING
# =========================
def segmentar_clientes(df: pd.DataFrame, columnas: list[str], n_clusters: int) -> tuple[pd.DataFrame, StandardScaler, KMeans]:
    """
    Escala las variables seleccionadas, aplica KMeans y asigna
    un segmento a cada cliente.
    """
    scaler = StandardScaler()
    datos_escalados = scaler.fit_transform(df[columnas])

    modelo_kmeans = KMeans(n_clusters=n_clusters, random_state=RANDOM_STATE)
    df["segmento"] = modelo_kmeans.fit_predict(datos_escalados)

    return df, scaler, modelo_kmeans


def mostrar_cantidad_por_segmento(df: pd.DataFrame) -> None:
    """
    Muestra cuántos clientes hay en cada segmento.
    """
    print("\nCantidad de clientes por segmento:")
    print(df["segmento"].value_counts().sort_index())


def graficar_segmentacion(df: pd.DataFrame) -> None:
    """
    Muestra la segmentación en un gráfico de dispersión.
    """
    plt.figure(figsize=(8, 5))
    plt.scatter(df["total_compras"], df["gasto_total"], c=df["segmento"])
    plt.xlabel("Total de compras")
    plt.ylabel("Gasto total")
    plt.title("Segmentación de clientes")
    plt.show()


def mostrar_interpretacion_segmentos() -> None:
    """
    Imprime una interpretación general de los segmentos.
    Nota: el número del cluster puede cambiar entre ejecuciones o datasets,
    por eso la interpretación final siempre debe validarse con la tabla promedio.
    """
    print("\nInterpretación general de segmentos:")
    print("Segmento 0: clientes de bajo valor o baja actividad")
    print("Segmento 1: clientes de alto valor / VIP")
    print("Segmento 2: clientes dormidos o poco activos")
    print("Segmento 3: clientes valiosos en riesgo de abandono")


# =========================
# PERFIL DE SEGMENTOS
# =========================
def calcular_perfil_segmentos(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """
    Calcula el promedio de variables clave por segmento.
    """
    perfil = df.groupby("segmento")[columnas].mean()
    return perfil


def graficar_perfil_normalizado(perfil_segmentos: pd.DataFrame) -> None:
    """
    Normaliza el perfil promedio de cada segmento para comparar
    variables con distintas escalas.
    """
    scaler = MinMaxScaler()

    perfil_normalizado = pd.DataFrame(
        scaler.fit_transform(perfil_segmentos),
        columns=perfil_segmentos.columns,
        index=perfil_segmentos.index
    )

    plt.figure(figsize=(10, 6))
    perfil_normalizado.plot(kind="bar", figsize=(10, 6))
    plt.title("Comparación de segmentos (valores normalizados)")
    plt.xlabel("Segmento")
    plt.ylabel("Escala relativa (0-1)")
    plt.xticks(rotation=0)
    plt.show()


# =========================
# MÉTODO DEL CODO
# =========================
def graficar_metodo_del_codo(df: pd.DataFrame, columnas: list[str]) -> None:
    """
    Aplica el método del codo para estimar una cantidad adecuada de clusters.
    """
    scaler = StandardScaler()
    datos_escalados = scaler.fit_transform(df[columnas])

    inercias = []
    valores_k = range(1, 11)

    for k in valores_k:
        modelo = KMeans(n_clusters=k, random_state=RANDOM_STATE)
        modelo.fit(datos_escalados)
        inercias.append(modelo.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(valores_k, inercias, marker="o")
    plt.title("Método del codo para elegir número de clusters")
    plt.xlabel("Número de clusters")
    plt.ylabel("Inercia")
    plt.show()


# =========================
# PROGRAMA PRINCIPAL
# =========================
def main() -> None:
    # 1. Cargar y preparar datos
    df = cargar_y_limpiar_datos(RUTA_DATASET)

    # 2. Mostrar resumen básico
    mostrar_resumen_variables(df)

    # 3. Gráficos exploratorios
    graficar_ingreso_vs_gasto(df)
    graficar_compras_vs_gasto(df)
    graficar_distribucion_recency(df)

    # 4. Segmentación con KMeans
    df, _, _ = segmentar_clientes(df, COLUMNAS_RFM, N_CLUSTERS)
    mostrar_cantidad_por_segmento(df)
    graficar_segmentacion(df)
    mostrar_interpretacion_segmentos()

    # 5. Perfil promedio por segmento
    perfil_segmentos = calcular_perfil_segmentos(df, COLUMNAS_PERFIL)

    print("\nPerfil promedio por segmento:")
    print(perfil_segmentos)

    graficar_perfil_normalizado(perfil_segmentos)

    # 6. Método del codo
    graficar_metodo_del_codo(df, COLUMNAS_PERFIL)


if __name__ == "__main__":
    main()