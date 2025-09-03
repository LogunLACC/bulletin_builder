from bulletin_builder.app_core import importer
from bulletin_builder.app_core import config

class AppStub:
    def __init__(self):
        self.sections_data = []
    def after(self, *args, **kwargs):
        # no-op for UI scheduling
        from bulletin_builder.app_core import importer
        from bulletin_builder.app_core.config import load_events_feed_url


        class AppStub:
            def __init__(self):
                self.sections_data = []

            def after(self, delay_ms, callback=None):
                """Mimic Tk.after: execute callback immediately for this headless runner.

                importer expects app.after to schedule work back on the main thread.
                For this script we call the callback synchronously so the worker's
                _apply runs and updates app.sections_data before the script exits.
                """
                if callback is None and callable(delay_ms):
                    # some code calls app.after(fn) style
                    return delay_ms()
                if callable(callback):
                    try:
                        return callback()
                    except Exception:
                        #!/usr/bin/env python3
                        """Headless runner: invoke import_events_feed synchronously and print a short summary.

                        This script makes the package importable by inserting the project's `src` directory
                        onto sys.path, then constructs an AppStub whose executor runs work synchronously so
                        the importer's threaded worker runs inline and updates `app.sections_data`.
                        """

                        from pathlib import Path
                        import sys
                        import traceback

                        # Ensure local package import via src/ (works when run from project root)
                        ROOT = Path(__file__).resolve().parent
                        sys.path.insert(0, str(ROOT / "src"))

                        try:
                            from bulletin_builder.app_core.importer import import_events_feed
                            from bulletin_builder.app_core.config import load_events_feed_url
                        except Exception:
                            traceback.print_exc()
                            raise


                        class SyncExec:
                            def submit(self, fn):
                                return fn()


                        class AppStub:
                            def __init__(self):
                                self.sections_data = []
                                self._thread_executor = SyncExec()

                            def after(self, ms, cb=None):
                                if cb:
                                    return cb()

                            def _show_progress(self, text):
                                print(f"[progress] {text}")

                            def _hide_progress(self):
                                print("[progress] done")

                            def refresh_listbox_titles(self):
                                pass

                            def show_placeholder(self):
                                pass

                            def update_preview(self):
                                pass

                            def show_status_message(self, msg):
                                print(f"[status] {msg}")


                        def _monkeypatch_messagebox():
                            try:
                                import tkinter.messagebox as _mb

                                _mb.showinfo = lambda title, msg: print(f"[INFO] {title}: {msg}")
                                _mb.showwarning = lambda title, msg: print(f"[WARN] {title}: {msg}")
                                _mb.showerror = lambda title, msg: print(f"[ERROR] {title}: {msg}")
                            except Exception:
                                # if tkinter isn't available, ignore
                                pass


                        def main():
                            _monkeypatch_messagebox()
                            app = AppStub()
                            url = load_events_feed_url() or "https://raw.githubusercontent.com/LogunLACC/bulletin_builder/refs/heads/main/events.json"
                            print(f"Running import_events_feed against: {url}")
                            try:
                                import_events_feed(app, url)
                            except Exception:
                                print("Import raised an exception:")
                                traceback.print_exc()

                            # Summarize results
                            sections = [s for s in app.sections_data if s.get("type") == "community_events"]
                            print(f"community_events sections: {len(sections)}")
                            if sections:
                                sec = sections[0]
                                print(f"title={sec.get('title')}, layout={sec.get('layout_style')}, items={len(sec.get('content') or [])}")
                                if sec.get("content"):
                                    print("first item:", sec.get("content")[0])
                            else:
                                print("No community_events section created.")


                        if __name__ == "__main__":
                            main()
