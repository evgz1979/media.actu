from __future__ import annotations

import threading

from media_manager.catalog import Catalog
from media_manager.thumbnails import ThumbnailCacheUnavailable, ThumbnailService


class ThumbnailWorkerPool:
    def __init__(
        self,
        catalog: Catalog,
        thumbnails: ThumbnailService,
        *,
        folder_workers: int = 2,
        photos_workers: int = 1,
    ) -> None:
        self.catalog = catalog
        self.thumbnails = thumbnails
        self.folder_workers = folder_workers
        self.photos_workers = photos_workers
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._threads: list[threading.Thread] = []
        self._state_lock = threading.Lock()
        self._states: dict[str, str] = {}

    def start(self) -> None:
        if self._threads:
            return
        self._stop.clear()
        self.catalog.reset_running_thumbnail_jobs()
        self.catalog.enqueue_all_thumbnails()
        kinds = ["folder"] * self.folder_workers + ["photos"] * self.photos_workers
        for index, kind in enumerate(kinds, start=1):
            thread = threading.Thread(
                target=self._work,
                args=(kind,),
                name=f"thumbnail-{kind}-{index}",
                daemon=True,
            )
            with self._state_lock:
                self._states[thread.name] = "starting"
            thread.start()
            self._threads.append(thread)

    def stop(self) -> None:
        self._stop.set()
        self._wake.set()
        for thread in self._threads:
            thread.join(timeout=2)
        self._threads.clear()
        with self._state_lock:
            self._states.clear()

    def wake(self) -> None:
        self._wake.set()

    def status(self) -> dict[str, object]:
        result: dict[str, object] = dict(self.catalog.thumbnail_queue_summary())
        sources = self.catalog.list_sources()
        scanning_kinds = {
            str(source.get("kind") or "folder")
            for source in sources
            if source.get("status") == "scanning"
        }
        alive = sum(thread.is_alive() for thread in self._threads)
        with self._state_lock:
            states = list(self._states.values())
        working = states.count("working")
        waiting = states.count("waiting") + states.count("starting")
        paused_workers = states.count("paused")
        result.update(
            {
                "workers_total": self.folder_workers + self.photos_workers,
                "workers_alive": alive,
                "workers_working": working,
                "workers_waiting": waiting,
                "workers_paused": paused_workers,
                "scanning_kinds": sorted(scanning_kinds),
                "sources": [
                    {
                        "source_id": int(source["id"]),
                        "total": int(source.get("thumbnail_total") or 0),
                        "done": int(source.get("thumbnail_done") or 0),
                        "pending": int(source.get("thumbnail_pending") or 0),
                        "running": int(source.get("thumbnail_running") or 0),
                        "error": int(source.get("thumbnail_error") or 0),
                    }
                    for source in sources
                ],
            }
        )
        return result

    def _work(self, source_kind: str) -> None:
        worker_name = threading.current_thread().name
        while not self._stop.is_set():
            if self.catalog.thumbnail_queue_paused():
                self._set_state(worker_name, "paused")
                self._wait()
                continue
            media_id = self.catalog.claim_thumbnail_job(source_kind)
            if media_id is None:
                self._set_state(worker_name, "waiting")
                self._wait()
                continue
            self._set_state(worker_name, "working")
            try:
                thumbnail = self.thumbnails.get_or_create(media_id)
                if thumbnail is None:
                    raise RuntimeError("Превью недоступно")
            except ThumbnailCacheUnavailable:
                self.catalog.release_thumbnail_job(media_id)
                self._wake.wait(timeout=10)
                self._wake.clear()
            except Exception as error:
                self.catalog.finish_thumbnail_job(media_id, error=str(error)[:1000])
            else:
                self.catalog.finish_thumbnail_job(media_id)
            finally:
                self._set_state(worker_name, "waiting")

    def _wait(self) -> None:
        self._wake.wait(timeout=1)
        self._wake.clear()

    def _set_state(self, worker_name: str, state: str) -> None:
        with self._state_lock:
            self._states[worker_name] = state
