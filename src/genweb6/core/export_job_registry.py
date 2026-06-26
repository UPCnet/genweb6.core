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
STATUS_CANCELLED = 'cancelled'

ACTIVE_STATUSES = frozenset({STATUS_QUEUED, STATUS_RUNNING})

FINAL_STATUSES = frozenset({
    STATUS_SUCCESS,
    STATUS_EMPTY,
    STATUS_ERROR,
    STATUS_INTERRUPTED,
    STATUS_CANCELLED,
})


def portal_types_signature(portal_types):
    """Firma estable de los tipos de contenido solicitados."""
    return ','.join(sorted(set(portal_types or [])))


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
    portal_types = metadata.get('portal_types') or []
    metadata.setdefault(
        'portal_types_sig', portal_types_signature(portal_types))

    def mutator(data):
        data['jobs'][job_id] = {
            'status': STATUS_QUEUED,
            'started_at': started_at,
            'finished_at': None,
            'interruption_notified': False,
            'huey_task_id': None,
            **metadata,
        }
        return data['jobs'][job_id]

    return _update_jobs(mutator)


def get_job(job_id):
    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        return dict(job, job_id=job_id)

    return _update_jobs(mutator)


def set_huey_task_id(job_id, huey_task_id):
    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['huey_task_id'] = huey_task_id
        return job

    return _update_jobs(mutator)


def list_jobs(limit=100):
    """Devuelve trabajos ordenados por fecha de inicio (más recientes primero)."""

    def mutator(data):
        jobs = [
            dict(job, job_id=job_id)
            for job_id, job in data['jobs'].items()
        ]
        jobs.sort(key=lambda item: item.get('started_at') or '', reverse=True)
        return jobs[:limit]

    return _update_jobs(mutator) or []


def find_active_job(context_path, portal_types):
    """Busca una exportación activa con la misma carpeta y tipos."""

    signature = portal_types_signature(portal_types)

    def mutator(data):
        for job_id, job in data['jobs'].items():
            if job.get('status') not in ACTIVE_STATUSES:
                continue
            if job.get('context_path') != context_path:
                continue
            if job.get('portal_types_sig') != signature:
                continue
            return dict(job, job_id=job_id)
        return None

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


def mark_cancelled(job_id):
    """Marca una exportación encolada como cancelada."""

    def mutator(data):
        job = data['jobs'].get(job_id)
        if job is None:
            return None
        job['status'] = STATUS_CANCELLED
        job['finished_at'] = _now_iso()
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
