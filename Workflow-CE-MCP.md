graph TD;
    A[Inicio del Chatbot] -->|Carga JSONs| B(Validación del Postulante);
    B -->|Documento Inválido| C[Notificar a RRHH y salir];
    B -->|Documento Válido| D[Confirmar Datos y Puesto];
    D --> E[Aceptación de Términos];
    E -->|No Acepta| X[Salir y Reiniciar];
    E -->|Acepta| F[Mostrar Instrucciones];

    F --> G[Carga de Preguntas];
    G --> H[Presentar Pregunta];
    H -->|Validar Respuesta| I{Cumple Restricciones?};
    I -->|No| H;
    I -->|Sí| J[Generar Repregunta con IA];

    J --> K{Validar Respuesta Final?};
    K -->|No| J;
    K -->|Sí| L[Guardar Respuesta y Avanzar];

    L -->|Más Preguntas?| H;
    L -->|No Más Preguntas| M[Evaluación con Gemini];

    M --> N[Calificar Respuesta];
    N --> O[Generar Explicación y Sentimiento];
    O --> P[Guardar Evaluación];

    P -->|Más Respuestas?| N;
    P -->|No Más Respuestas| Q[Generar Informe Final];

    Q --> R[Mostrar Resultados];
    R -->|Puntaje Alto| S[✅ Aprobado];
    R -->|Puntaje Medio| T[⚠️ Necesita Mejorar];
    R -->|Puntaje Bajo| U[❌ No Aprobado];

    S --> V[Fin del Proceso];
    T --> V;
    U --> V;
