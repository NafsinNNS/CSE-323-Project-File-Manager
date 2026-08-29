from core.async_workers import SearchWorker
import pathlib


class SearchEngine:
    def __init__(self):
        self.worker: SearchWorker | None = None

    def start_search(self, root_path: str, query: str, case_sensitive: bool = False,
                     use_regex: bool = False, extension_filter: str = "",
                     recursive: bool = False,
                     result_callback=None, finished_callback=None):
        self.stop_search()
        self.worker = SearchWorker(root_path, query, case_sensitive, use_regex,
                                   extension_filter, recursive)
        if result_callback:
            self.worker.result_found.connect(result_callback)
        if finished_callback:
            self.worker.finished_signal.connect(finished_callback)
        self.worker.start()

    def stop_search(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait(2000)
        self.worker = None
