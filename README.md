A continuación se presenta un **README** que describe la solución final e integra todos los elementos: configuración de DevSecOps (SAST, SCA, Security Hub), despliegue en AWS usando Serverless y GitHub Actions, así como las instrucciones para reproducir el entorno.

---

# DevSecOps Challenge

Este proyecto demuestra la integración de **prácticas DevSecOps** en un flujo de CI/CD, desplegando una aplicación serverless en AWS (Lambda + API Gateway) y enviando hallazgos de seguridad a AWS Security Hub (opcional). Utiliza:

1. **GitHub Actions** como pipeline de CI/CD.  
2. **Serverless Framework** (v3) para gestionar el despliegue en AWS.  
3. **Bandit** (SAST) y **OWASP Dependency-Check** (SCA).  
4. (Opcional) **AWS Security Hub** para centralizar los hallazgos.

## Tabla de Contenidos
1. [Arquitectura General](#arquitectura-general)  
2. [Estructura del Proyecto](#estructura-del-proyecto)  
3. [Pipeline (CI/CD) en GitHub Actions](#pipeline-cicd)  
4. [Despliegue en AWS](#despliegue-en-aws)  
5. [Prácticas DevSecOps](#practicas-devsecops)  
6. [Security Hub (Opcional)](#security-hub-opcional)  
7. [Cómo Ejecutar el Proyecto](#como-ejecutar-el-proyecto)  
8. [Posibles Hallazgos de Seguridad](#hallazgos-de-seguridad)  
9. [Licencia y Notas Finales](#licencia)

---

## 1. Arquitectura General

1. **Desarrollo / Código:**  
   El código (en Python) se encuentra en `app.py`, conteniendo intencionalmente algunos patrones inseguros para generar hallazgos en SAST y SCA.
2. **Repositorio GitHub + Actions:**  
   - Al hacer commit/push a la rama `main`, se dispara el workflow definido en `.github/workflows/ci-cd.yml`.
   - Este workflow realiza:  
     - SAST con **Bandit**  
     - SCA con **OWASP Dependency-Check**  
     - Despliegue serverless a **AWS Lambda** y **API Gateway**  
     - (Opcional) Subida de hallazgos a **AWS Security Hub**  
3. **AWS (Lambda + API Gateway):**  
   La aplicación se despliega como una función Lambda, expuesta vía API Gateway.  
4. **Security Hub:**  
   Se usa para centralizar hallazgos de seguridad. Requiere convertir los reportes de Bandit / Dependency-Check al formato que Security Hub espera y subirlos mediante `aws securityhub batch-import-findings`.

---

## 2. Estructura del Proyecto

```
Reto_DevSecOps/
├── app.py                    # Código Python inseguro (SAST triggers)
├── requirements.txt          # Dependencias (SCA triggers)
├── serverless.yml            # Configuración Serverless
├── README.md                 # Este archivo
└── .github/
    └── workflows/
        └── ci-cd.yml        # Pipeline principal de CI/CD en GitHub Actions
```

### Archivos Clave

- **app.py:** Contiene funciones inseguras (uso de `eval`, `subprocess.run(shell=True)`, `pickle.loads`, etc.) para forzar hallazgos de SAST.  
- **requirements.txt:** Incluye versiones antiguas de Flask y requests, que deberían generar hallazgos de CVEs en SCA.  
- **serverless.yml:** Maneja el despliegue de Lambda y API Gateway en AWS.  
- **ci-cd.yml:** Define el pipeline, pasos de análisis de seguridad, despliegue y (opcional) envío de hallazgos a Security Hub.

---

## 3. Pipeline (CI/CD)

El pipeline se ejecuta en cada push a la rama `main` y consta de los siguientes pasos:

1. **Checkout repo**  
2. **Set up Python** (Instala Python 3.8 en el runner).  
3. **Check AWS Identity (opcional)**  
   - Valida que las credenciales AWS estén correctamente configuradas.  
4. **Install dependencies**  
   - Actualiza pip, instala dependencias del proyecto y **Serverless** v3.  
5. **(Opcional) Set up Java 11** (para Dependency-Check, aunque la acción oficial trae su propio Java).  
6. **Run SAST with Bandit**  
   - Analiza `app.py`, generando hallazgos de seguridad (por ejemplo, uso de `eval` o `md5`).  
   - Puede configurarse para no romper el pipeline (por ejemplo, usando `--exit-zero`).  
7. **Run SCA with OWASP Dependency-Check**  
   - Escanea dependencias definidas en `requirements.txt` (versión antigua de Flask y requests).  
   - Genera un reporte HTML.  
   - Se pueden subir como artefacto si se desea ver el informe.  
8. **Deploy to AWS Lambda**  
   - Usa `serverless deploy` para crear/actualizar el stack CloudFormation y desplegar la función Lambda y API Gateway.  
9. **Send findings to AWS Security Hub (opcional)**  
   - Ejecuta `aws securityhub batch-import-findings --findings file://findings.json` si se convirtieron los hallazgos al formato requerido.

---

## 4. Despliegue en AWS

1. **Serverless** crea un **stack** de CloudFormation y un bucket de despliegue.  
2. **Lambda** se implementa con la lógica de `app.py`.  
3. **API Gateway** expone un endpoint HTTP (ejemplo: `https://xxxxx.execute-api.us-east-1.amazonaws.com/dev/`).  
4. La ejecución del pipeline exige que el usuario IAM tenga permisos adecuados de CloudFormation, Lambda, APIGateway, etc.

**Para probar la app**:  
- Visita el endpoint que aparece en los logs de `serverless deploy` o en la consola de CloudFormation / API Gateway.  
- Deberías ver la respuesta JSON con un mensaje (por ejemplo, `"Hello from insecure code!"`).

---

## 5. Prácticas DevSecOps

1. **SAST (Bandit)**  
   - Detecta patrones inseguros en Python (`eval`, `shell=True`, `pickle.loads`, `hashlib.md5`, etc.).  
2. **SCA (OWASP Dependency-Check)**  
   - Analiza las librerías declaradas en `requirements.txt`. Versiones antiguas generan CVEs conocidas.  
3. **Despliegue Automatizado**  
   - Los cambios se despliegan de forma continua en Lambda a través de GitHub Actions.  
4. **(Opcional) Integración con AWS Security Hub**  
   - Permite centralizar los hallazgos de seguridad en un dashboard unificado, si se importan manualmente.

---

## 6. Security Hub (Opcional)

- Los frameworks nativos de Security Hub (CIS, Foundational, PCI) se centran en **configuraciones de AWS**, no en el código de la app.  
- Para ver hallazgos de SAST/SCA en Security Hub, es necesario:
  1. Generar un reporte en JSON (por ejemplo, `bandit_report.json`).  
  2. Transformarlo al esquema de Security Hub (`securityhub_findings.json`).  
  3. Subirlo: `aws securityhub batch-import-findings --findings file://securityhub_findings.json`.  
- Así se reflejarán tus vulnerabilidades de código/librerías en Security Hub.

---

## 7. Cómo Ejecutar el Proyecto

### Prerrequisitos

1. **Cuenta de AWS** con un usuario IAM que tenga permisos de CloudFormation, IAM, Lambda, APIGateway, etc.  
2. **Variables de entorno**/Secrets configurados en GitHub:  
   - `AWS_ACCESS_KEY_ID`  
   - `AWS_SECRET_ACCESS_KEY`  
   - `AWS_DEFAULT_REGION` (us-east-1 u otra)

### Pasos

1. **Clonar este repositorio**.  
2. **Configurar los secrets** en [Settings > Security > Secrets and variables > Actions] de tu repo:  
   - `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` asociados a un usuario con permisos adecuados.  
3. **Revisar** `.github/workflows/ci-cd.yml`. Ajusta si deseas cambiar región de AWS, flags de Bandit, etc.  
4. **Commit** cualquier cambio a la rama `main`.  
5. **Ver la ejecución** en la pestaña **Actions**. Si todo está correcto, verás pasos completados con éxito (o con warnings si se detectan vulnerabilidades).  
6. **(Opcional) Revisar Security Hub** si importas los findings manualmente.

---

## 8. Posibles Hallazgos de Seguridad

1. **SAST (Bandit)**  
   - B307 (eval usage)  
   - B602 (shell=True)  
   - B301 (pickle.loads)  
   - B303 (md5 hashing)  
   - Hard-coded secrets  
2. **SCA (OWASP Dependency-Check)**  
   - CVEs asociadas a Flask 0.12 y requests 2.8.1 (u otras versiones antiguas).  
3. **Security Hub**  
   - Verás los hallazgos importados con severidad, fecha, descripción, etc., si implementas la conversión y subida de findings.

---

## 9. Licencia y Notas Finales

- El código inseguro está con fines **didácticos** para demostrar el pipeline DevSecOps. **No** usar en producción.  
- Revisa la [documentación de Serverless](https://www.serverless.com/framework/docs) y [Bandit](https://bandit.readthedocs.io/) para más configuraciones.  
- Ajusta las políticas IAM de tu usuario para permitir el despliegue con CloudFormation.  
- Para ver los reportes HTML de Dependency-Check, sube el archivo como artefacto o cámbialo a formato `CONSOLE`.  
- **¡Listo!** Con esto, cumples con un flujo DevSecOps automatizado, detectando vulnerabilidades en cada commit, centralizándolas (si quieres) en Security Hub y desplegando tu app en AWS.

---

¡Gracias por usar este ejemplo! Si tienes preguntas o encuentras problemas al replicarlo, no dudes en abrir un **issue** o comentar en el repositorio. ¡Éxitos en tu reto DevSecOps!