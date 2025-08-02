from enum import Enum


class ProcessingStatus(str, Enum):
    not_processed = "Sin iniciar"
    processing = "En progreso"
    processed = "Terminado"
    failed = "Falló"
