# Cheat sheet — IPRE-DICOM en Calfuco

Los comandos marcados como **local** se ejecutan en el Mac. Los marcados como
**Calfuco** se ejecutan después de conectarse por SSH.

## 1. Conexión

```bash
# local
ssh pfayala@146.155.13.94
```

No ejecute entrenamientos como `root`, no cambie CUDA del sistema y compruebe siempre
que la GPU elegida esté libre:

```bash
# Calfuco
nvidia-smi
```

La RTX 3090 física es la GPU 1. Para que un proceso use solamente esa tarjeta:

```bash
CUDA_VISIBLE_DEVICES=1 python script.py
```

Dentro de PyTorch aparecerá como `cuda:0`; eso es esperado.

## 2. Entorno del proyecto

Use Python 3.11 dentro de un entorno aislado. Cuando el administrador habilite el
espacio personal:

```bash
# Calfuco
cd /mnt/workspace/pfayala
python3.11 -m venv ipre-env
source /mnt/workspace/pfayala/ipre-env/bin/activate
cd ~/ipre-dicom
pip install -r requirements-experiment.txt
```

Verificación:

```bash
python --version
python -c 'import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))'
```

## 3. W&B

Crear una cuenta en <https://wandb.ai> y autenticar Calfuco de forma interactiva:

```bash
# Calfuco
wandb login
```

No pegue la API key en scripts, Git, notebooks compartidos ni mensajes. La credencial
queda en la configuración privada del usuario.

Entrenamiento conectado:

```bash
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /ruta/labels.csv \
  --task noise \
  --epochs 15 \
  --batch-size 32 \
  --wandb-mode online \
  --wandb-project ipre-dicom \
  --run-name noise-densenet-baseline
```

Sin Internet o antes de configurar la cuenta:

```bash
WANDB_DIR=/mnt/workspace/pfayala/wandb \
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /ruta/labels.csv \
  --task noise \
  --wandb-mode offline
```

Sincronizar posteriormente:

```bash
wandb sync /mnt/workspace/pfayala/wandb/wandb/offline-run-*
```

Por defecto el proyecto registra hiperparámetros, métricas y el mejor checkpoint. No
registra imágenes ni metadata DICOM para evitar subir información potencialmente
identificadora.

## 4. Jupyter mediante túnel SSH

Primero iniciar Jupyter escuchando solo en la interfaz local del servidor:

```bash
# Calfuco
source /mnt/workspace/pfayala/ipre-env/bin/activate
cd ~/ipre-dicom
jupyter lab --no-browser --ip=127.0.0.1 --port=8888
```

Jupyter mostrará una URL con token. Mantener esa terminal abierta. En otra terminal:

```bash
# local
ssh -N -L 8888:127.0.0.1:8888 pfayala@146.155.13.94
```

Abrir localmente:

```text
http://127.0.0.1:8888/lab?token=EL_TOKEN_MOSTRADO
```

No usar `--ip=0.0.0.0`, no abrir el puerto 8888 públicamente y no compartir el token.
Si 8888 está ocupado, usar 8889 tanto en Jupyter como en ambos lados del túnel.

## 5. Sesiones persistentes con tmux

```bash
# Calfuco
tmux new -s ipre
```

Separarse sin detener el proceso: `Ctrl+B`, luego `D`.

```bash
tmux ls
tmux attach -t ipre
```

## 6. Monitoreo

```bash
watch -n 2 nvidia-smi
ps -u "$USER" -o pid,etime,%cpu,%mem,cmd
du -sh /mnt/workspace/pfayala/*
```

## 7. API remota mediante túnel

En Calfuco:

```bash
MEDMNIST_ROOT=/mnt/workspace/pfayala/medmnist \
CUDA_VISIBLE_DEVICES=1 \
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

En el Mac:

```bash
ssh -N -L 8000:127.0.0.1:8000 pfayala@146.155.13.94
```

Abrir <http://127.0.0.1:8000>. La API tampoco necesita exponerse públicamente.
