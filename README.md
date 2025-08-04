# Agente Autónomo de Análisis y Síntesis de Documentación Técnica
En este repositorio presenta un agente de IA capaz de recibir una URL de una documentación técnica (por ejemplo, la documentación de una librería, un framework o una API), procesarla, entenderla y responder preguntas complejas sobre ella. El agente se expone a través de una API RESTful y su lógica interna ha sido orquestada mediante LangGraph.

## Descripción General de la Solución

## Arquitectura de la Solución

### Arquitectura General
Documentation Agent es una solución basada en microservicios que implementa un sistema de Retrieval-Augmented Generation (RAG) para consultas sobre documentación. La arquitectura se basa en una aplicación FastAPI con procesamiento asíncrono usando Celery.

### Componentes de Infraestructura
La solución está containerizada usando Docker Compose e incluye los siguientes servicios:

* **Qdrant:** Base de datos vectorial para almacenamiento de embeddings
* **PostgreSQL:** Base de datos relacional principal
* **RabbitMQ:** Message broker para Celery
* **Redis:** Backend de resultados para Celery
* **Worker:** Procesador de tareas asíncronas
* **Flower:** Monitoreo de tareas Celery
<img width="359" height="341" alt="diagram1" src="https://github.com/user-attachments/assets/f91936f8-c6a3-4161-94d3-dc1c36b96b57" />

### API y Routers
La aplicación expone dos routers principales:

1. **Process Router:** Maneja el procesamiento de documentación process_router.py:10-21
2. **Chat Router:** Gestiona las consultas de chat y el historial
<img width="322" height="361" alt="diagram5" src="https://github.com/user-attachments/assets/d51a1ed8-1388-4145-ab3c-4cc5c976389e" />

### Pipeline de Procesamiento de Documentos
El procesamiento asíncrono de documentos se realiza a través de una tarea Celery que:

1. Extrae contenido de URLs
2. Divide el contenido en chunks
3. Genera embeddings usando AWS Bedrock
4. Almacena los vectores en Qdrant
<img width="680" height="353" alt="diagram6" src="https://github.com/user-attachments/assets/c746c439-6890-42c3-bb0a-3395aca585de" />

### Flujo principal
<img width="363" height="654" alt="graph" src="https://github.com/user-attachments/assets/89f2125d-2d62-40b9-978d-8f63cfaf489c" />
El grafo principal de procesamiento de la consulta está construido en langgraph, uan tecnología que permite construir workflow predecibles y flexibles. 
El diagrama muestra la arquitectura del grafo.

### Flujo RAG (Retrieval-Augmented Generation)
<img width="466" height="545" alt="rag-graph" src="https://github.com/user-attachments/assets/21eb956b-94a6-4571-b1c6-a2a058357680" />

La arquitectura implementa un subflujo RAG que deriva del flujo principal, usando LangGraph que incluye:

* **Retrieve:** Búsqueda de documentos relevantes
* **Grade Documents:** Evaluación de relevancia de documentos
* **Generate:** Generación de respuestas
* **Transform Query:** Reescritura de consultas para mejorar resultados
El flujo incluye validaciones para detectar alucinaciones y verificar que las respuestas aborden correctamente las preguntas.  
La arquitectura del grafo implementa el patrón Self-Reflective RAG, una técnica de RAG en la que el modelo no solo genera una respuesta basada en información recuperada, sino que reflexiona sobre su propia respuesta para evaluar su validez y mejorarla si es necesario.
En lugar de limitarse a producir una respuesta directamente, el modelo:
1. Genera una primera respuesta usando los documentos recuperados.
2. Se autoevalúa para juzgar si la respuesta es correcta, relevante y bien fundamentada.
3. Corrige o ajusta la respuesta si encuentra errores, incoherencias o falta de soporte.
Este proceso permite respuestas más precisas, fundamentadas y confiables, al reducir errores como alucinaciones o afirmaciones no respaldadas por la evidencia.
A continuación se presenta el diagrama del flujo empleado como referencia:
<img width="1000" height="358" alt="reflective-2" src="https://github.com/user-attachments/assets/72f07400-7bda-49b9-ac37-9d898979e67d" />

### Servicios de IA
La solución utiliza AWS Bedrock para:

* Generación de embeddings de texto
* Rerank de fragmentos recuperados de la base de datos vectorial
* Consultas al modelo de lenguaje para generar respuestas

### Patrón Arquitectónico
La arquitectura sigue un patrón de microservicios con:

* Separación de responsabilidades (routers, controllers, services)
* Procesamiento asíncrono para operaciones pesadas
* Base de datos vectorial especializada para búsqueda semántica
* Cache y gestión de estado distribuido
<img width="694" height="328" alt="diagram2" src="https://github.com/user-attachments/assets/179e29bf-ef95-4420-9867-14df7fcb9539" />

### Notas
Esta arquitectura está diseñada para manejar consultas sobre documentación de manera escalable, usando tecnologías modernas de IA y procesamiento distribuido. El uso de LangGraph permite implementar flujos complejos de RAG con validaciones y mejoras automáticas de consultas.

## Características y capacidades clave
| Característica                              | Descripción                                                                 | Implementación                                                                 |
|---------------------------------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Procesamiento asincrónico de documentos     | Ingiere y procesa documentos de fuentes web                                | Trabajadores de Celery con el agente de mensajes RabbitMQ                      |
| Búsqueda y recuperación de vectores         | Búsqueda semántica a través de documentos procesados                       | Base de datos vectorial de Qdrant con incrustaciones de AWS Bedrock            |
| Interfaz de chat                            | Sesiones de chat interactivas con contexto de documentos                   | Puntos finales REST de FastAPI con persistencia de PostgreSQL                  |
| Respuestas impulsadas por RAG               | Respuestas contextuales utilizando documentos recuperados                  | Flujos de trabajo de LangGraph con LLM de Google GenAI                         |
| Estado del procesamiento en tiempo real     | Realizar un seguimiento del progreso del procesamiento de documentos       | Almacenamiento en caché de Redis con supervisión de tareas de Celery           |
| Integración de IA multimodelo               | Integración flexible de servicios de IA                                    | Abstracciones de servicios de AWS Bedrock y Google GenAI                       |


## Tecnologías Principales
<img width="754" height="350" alt="diagram3" src="https://github.com/user-attachments/assets/dcb6c03e-3444-4213-969b-b3d7101cf702" />  
El Documentation Agent utiliza una arquitectura de microservicios basada en tecnologías modernas para procesamiento de documentos y chat con IA.  

### Framework Web y API
* **FastAPI:** Framework web principal para la API REST
* **Pydantic:** Gestión de configuración y validación de datos
  
### Procesamiento Asíncrono
* **Celery:** Sistema de colas de tareas para procesamiento en segundo plano
* **RabbitMQ:** Message broker para las colas de Celery
* **Flower:** Monitoreo de workers de Celery
  
### Bases de Datos
* **PostgreSQL:** Base de datos relacional para historial de chats
* **Qdrant:** Base de datos vectorial para embeddings
* **Redis:** Cache y almacenamiento de resultados de tareas
  
### Servicios de IA
* **AWS Bedrock:** Embeddings y reranking de documentos
* **Google AI:** Servicios de inferencia LLM
* **Cohere:** Cliente para embeddings a través de AWS
  
### Procesamiento de Contenido
* **BeautifulSoup:** Extracción de contenido HTML
* **Requests:** Cliente HTTP para obtener documentación web
  
### Infraestructura y Despliegue
* **Docker Compose:** Orquestación de contenedores
* **SQLAlchemy:** ORM para PostgreSQL

El stack seleccionado es ampliamente utilizado en la industria para el desarrollo de aplicaciones con Inteligencia Artificial, ya que permite construir aplicaciones livianas robustas, mantenimiento un alto rendimiento en la ejecución.
Se trata en general de tecnologías open-source con una amplia comunidad y abundante documentación. A continuación se precisan razones adicionales para la selección del stack:

**FastAPI**
Es ideal para construir APIs modernas y asincrónicas gracias a su rendimiento sobresaliente (basado en Starlette y Pydantic), su sintaxis intuitiva y su excelente soporte para documentación automática con OpenAPI.

**Qdrant**
Es una base de datos vectorial optimizada para búsquedas semánticas a gran escala, perfecta para almacenar y recuperar embeddings en flujos RAG como el que utiliza tu aplicación.

**PostgreSQL**
Es una base de datos relacional robusta y altamente confiable, ideal para almacenar de forma estructurada el historial de conversaciones, metadatos y configuraciones del sistema.

**RabbitMQ**
Actúa como un message broker eficaz y maduro, facilitando la comunicación asíncrona entre componentes desacoplados como la API y los workers de procesamiento.

**Celery**
Permite ejecutar tareas pesadas o de larga duración en segundo plano de forma distribuida y escalable, ideal para procesar documentos sin bloquear las solicitudes del usuario.

**Redis**
Es una base de datos en memoria ultrarrápida, ideal como backend de resultados de Celery y para gestionar cachés temporales que mejoran el rendimiento general de la aplicación.

**Docker**
Permite empaquetar cada componente de la aplicación con todas sus dependencias en contenedores aislados, lo que garantiza entornos reproducibles y facilita la portabilidad entre entornos de desarrollo, prueba y producción.

**Docker Compose**
Es ideal para orquestar múltiples contenedores (como la API, Qdrant, Redis, etc.) de manera declarativa y sencilla, lo que acelera el despliegue local y en entornos controlados con una sola instrucción.

**cohere.embed-multilingual-v3**
Es un modelo de generación de embeddings multilingüe de alto rendimiento, que permite representar documentos y consultas en un espacio semántico compartido sin importar el idioma, lo que es crucial para construir un sistema de RAG accesible globalmente.

**cohere.rerank-v3-5:0**
Este modelo mejora la precisión de recuperación reordenando los documentos más relevantes según su pertinencia con la consulta, lo que refina considerablemente la calidad de las respuestas generadas en el flujo RAG.

**LangGraph**
Es una librería diseñada para construir flujos conversacionales y pipelines de razonamiento estructurado como grafos, lo que permite orquestar de forma explícita y controlada procesos complejos como el RAG, con capacidad para incorporar validaciones, ramificaciones lógicas e introspección en tiempo de ejecución.

**AWS Bedrock**
Proporciona acceso a modelos fundacionales líderes (como Cohere, Anthropic, AI21) mediante una API totalmente gestionada, lo que permite integrar capacidades avanzadas de generación y embeddings sin preocuparse por la infraestructura, escalabilidad o mantenimiento de modelos de IA.

## Estructura del Proyecto
```
📦 raiz_del_proyecto/
├── app/
│   ├── celery_tasks/     # Tareas asincrónicas (ej. con Celery)
│   ├── config/           # Configuración general del proyecto
│   ├── controllers/      # Lógica de negocio
│   ├── db/               # Conexión y operaciones con base de datos
│   ├── models/           # Modelos de datos (ORM o Pydantic)
│   ├── routers/          # Definición de endpoints de la API
│   ├── schemas/          # Esquemas Pydantic para validación
│   ├── services/         # Servicios auxiliares y utilitarios
│   └── workflows/        # Definición de grafos con LangGraph
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Documentación del proyecto
└── .env.example          # Variables de entorno de ejemplo
```
## Guía de Instalación y Ejecución
### Requisitos previos
* Docker
* Docker Compose >=2.0
* Credenciales de AWS Bedrock
### Paso a Paso
1. Clonar el repositorio:
```
git clone https://github.com/devmauriciopineda/documentation_agent.git
cd documentation_agent
```
2. Copiar el archivo de variables de entorno:
```
cp .env.example .env
```
3. Editar el archivo .env y completar con las credenciales y configuración necesarias:
```
OPENAI_API_KEY=tu_clave
EMBEDDING_MODEL=text-embedding-3-small
# Agregar aquí otras variables necesarias para el proyecto
```
4. Levantar la aplicación con Docker Compose:
```
docker-compose up --build
```
5. Acceder a la API desde el navegador o un cliente HTTP:
* Documentación Swagger: http://localhost:8002/docs
### Variables de ambiente
En el archivo .env se deben especificar los valores de las variables de ambiente. A continuación se presentan valores de referencia. Las credenciales para usar los modelos de Bedrock deben generarse utilizando el servicio IAM de AWS. Asimismo, para utilizar los modelos de gemini se requiere generar una API_KEY.
```
# AWS
AWS_ACCESS_KEY_ID='YOUR_ACCESS_KEY_ID'
AWS_SECRET_ACCESS_KEY='YOUR_SECRET_ACCESS_KEY'
AWS_REGION='us-east-1'
AWS_EMBEDDINGS_MODEL='cohere.embed-multilingual-v3'
AWS_RERANK_MODEL='cohere.rerank-v3-5:0'
AWS_RERANK_REGION='us-west-2'

# Google
GOOGLE_API_KEY='YOUR_GOOGLE_API_KEY'

# Inference
LLM_NAME='us.anthropic.claude-3-5-sonnet-20241022-v2:0'
TEMPERATURE=0.0
TOKENS=500

# Qdrant
COLLECTION_NAME='tech-docs'
QDRANT_URL='http://qdrant'

# RAG Config
MAX_CHUNKS_RETRIEVED=10
MAX_CHUNKS_RERANKED=3
DEFAULT_CHUNK_SIZE=1200
DEFAULT_CHUNK_OVERLAP=0

# Rabbit
RABBITMQ_DEFAULT_USER='YOUR_RABBIT_USER'
RABBITMQ_DEFAULT_PASS='YOUR_RABBIT_PASS'

# Postgres
POSTGRES_USER='YOUR_POSTGRES_USER'
POSTGRES_PASSWORD='YOUR_POSTGRES_PAA'
POSTGRES_DB='docs_agent'
POSTGRES_HOST='postgres'
POSTGRES_PORT='5432'
```
## Documentación de la API
Una vez que el servidor esté en funcionamiento, puedes acceder a la documentación interactiva de la API proporcionada por FastAPI:
* Swagger UI: http://127.0.0.1:8002/docs
* ReDoc: http://127.0.0.1:8002/redoc
Estas interfaces permiten explorar y probar la API desde el navegador.

## Uso de la API
### POST /api/v1/process-documentation:
Recibe una URL de una documentación y un chatId para iniciar el procesamiento asíncrono. Devuelve una confirmación inmediata y el estado del procesamiento (ej. "En progreso").

### GET /api/v1/processing-status/{chatId}:
Permite consultar el estado del procesamiento de la documentación.

### POST /api/v1/chat/{chatId}:
Permite interactuar con el agente una vez que la documentación ha sido procesada. Recibe una pregunta del usuario y devuelve una respuesta generada por el agente.

### GET /api/v1/chat-history/{chatId}:
Devuelve el historial de la conversación.

Para los detalles el uso de la API, remitirse a la documentación oficial en swagger: http://127.0.0.1:8002/docs
