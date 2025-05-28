import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FolderWatcher(FileSystemEventHandler):
    def __init__(self, on_file_created):
        super().__init__()
        self.on_file_created = on_file_created

    def on_created(self, event):
        if not event.is_directory:
            print(f"🟢 새 파일 발견: {event.src_path}")
            self.on_file_created(event.src_path)

def start_watching(path: str, on_file_created):
    event_handler = FolderWatcher(on_file_created)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"👀 폴더 감시 시작: {path}")
    return observer