"""Genera un diagrama entidad-relacion Mermaid desde los modelos SQLAlchemy."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.modelos.models import Base


def nombre_tipo(columna) -> str:
    """Convierte el tipo SQLAlchemy a una etiqueta legible para Mermaid."""
    return str(columna.type).upper().split("(")[0]


def generar_diagrama() -> str:
    """Construye el diagrama ER a partir de la metadata declarativa."""
    lineas = ["erDiagram"]

    for tabla in Base.metadata.sorted_tables:
        lineas.append(f"    {tabla.name} {{")
        for columna in tabla.columns:
            atributos = []
            if columna.primary_key:
                atributos.append("PK")
            elif columna.unique:
                atributos.append("UK")
            if not columna.nullable:
                atributos.append("NOT_NULL")
            sufijo = f" \"{' '.join(atributos)}\"" if atributos else ""
            lineas.append(f"        {nombre_tipo(columna)} {columna.name}{sufijo}")
        lineas.append("    }")

    for tabla in Base.metadata.sorted_tables:
        for clave_foranea in tabla.foreign_keys:
            tabla_padre = clave_foranea.column.table.name
            columna_padre = clave_foranea.column.name
            lineas.append(
                f"    {tabla_padre} ||--o{{ {tabla.name} : "
                f'"{columna_padre} referencia {clave_foranea.parent.name}"'
            )

    return "\n".join(lineas) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).with_name("diagrama_entidad_relacion.mmd"),
        help="Archivo Mermaid de salida.",
    )
    args = parser.parse_args()
    args.output.write_text(generar_diagrama(), encoding="utf-8")
    print(f"Diagrama generado en: {args.output}")


if __name__ == "__main__":
    main()
