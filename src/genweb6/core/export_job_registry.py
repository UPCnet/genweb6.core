# -*- coding: utf-8 -*-
"""Registro persistente de exportaciones asíncronas de ficheros.

Guarda el estado de cada exportación en un JSON junto a la cola Huey para
detectar trabajos interrumpidos tras reinicios de instancia.
"""
import fcntl
import json
import os
from datetime import datetime

STATUS_QUEUED = 'queued'
STATUS_RUNNING = 'running'
STATUS_SUCCESS = 'success'
STATUS_EMPTY = 'empty'
STATUS_ERROR = 'error'
STATUS_INTERRUPTED = 'interrupted'

FINAL_STATUSES = frozenset({
    STATUS_SUCCESS,
    STATUS_EMPTY,
    STATUS_ERROR,
    STATUS_INTERRUPTED,
})


def _jobs_file_path():
    """Ruta del fichero de estado, en el mismo directorio que la cola Huey."""
    url = os.environ.get(
        'HUEY_TASKQUEUE_URL', 'sqlite:///tmp/huey_queue.sqlite')
    if url.startswith('sqlite:///'):
        db_path = url[len('sqlite:///'):]
        dir_path = os.path.dirname(db_path) or '.'
    else:
        dir_path = '/tmp'
    return os.path.join(dir_path, 'export_jobs.json')


def _now_iso():
    return datetime.now().replace(microsecond=0).isoformat()


def _update_jobs(mutator):
    """Lee, modifica y escribe el registro con bloqueo exclusivo."""
    path = _jobs_file_path()
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w') as fh:
            json.dump({'jobs': {}}, fh)

    with open(path, 'r+') as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            fh.seek(0)
            raw = fh.read()
            data = json.loads(raw) if raw.strip() else {'jobs': {}}
            data.setdefault('jobs', {})
            result = mutator(data)
            fh.seek(0)
            fh.truncate()
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write('\n')
            return result
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


def create_job(job_id, **metadata):
    """Registra una exportación encolada."""
    started_at = _now_iso()

    def mutator(data):
        data['jobs'][job_id] = {
            'status': STATUS_QUEUED,
            'started_at': started_at,
            'finished_at': None,
            'interruption_notified': False,
            **metadata,
        }
        return data['jobs'][job_id]

    return _update_jobs(mutator)


def mark_running(job_id):
    """Marca la exportación como en ejecución (incluye reintentos Huey)."""

    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['status'] = STATUS_RUNNING
        return job

    return _update_jobs(mutator)


def mark_finished(job_id, status):
    """Marca la exportación como terminada."""
    if status not in FINAL_STATUSES:
        raise ValueError('Estado final no válido: {0}'.format(status))

    finished_at = _now_iso()

    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['status'] = status
        job['finished_at'] = finished_at
        return job

    return _update_jobs(mutator)


def get_orphaned_jobs():
    """Devuelve exportaciones que quedaron en curso tras un reinicio."""

    def mutator(data):
        orphaned = []
        for job_id, job in data['jobs'].items():
            if job.get('status') in (STATUS_QUEUED, STATUS_RUNNING):
                orphaned.append(dict(job, job_id=job_id))
        return orphaned

    return _update_jobs(mutator) or []


def mark_interrupted(job_id):
    """Marca una exportación como interrumpida."""

    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['status'] = STATUS_INTERRUPTED
        job['finished_at'] = _now_iso()
        return job

    return _update_jobs(mutator)


def mark_interruption_notified(job_id):
    """Indica que ya se envió el correo de interrupción."""

    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['interruption_notified'] = True
        return job

    return _update_jobs(mutator)
