# app/cache_manager.py
import threading
import time
import gspread
import pytz
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
from datetime import datetime

from .gsheet_client import GSheetClient
from .config import settings

UpdateTask = Tuple[str, str, str] # (employee_id, "check-in" | "check-out", timestamp_str)
TAIPEI_TZ = pytz.timezone("Asia/Taipei")
# Each task generates 2 cells, so 50 tasks = 100 cells
TASK_BATCH_SIZE = 50

class CacheManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.attendees_cache: Dict[str, Dict[str, Any]] = {}
        self.employee_id_to_row_index: Dict[str, int] = {}
        self.update_queue: deque[UpdateTask] = deque()
        self.last_updated: Optional[float] = None
        self.is_initialized = False
        self.shutdown_event = threading.Event()

        # Threads
        self.cache_reload_thread = threading.Thread(target=self._background_cache_reload, daemon=True)
        self.writer_thread = threading.Thread(target=self._background_writer, daemon=True)


    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def start(self):
        print("Starting CacheManager...")
        self.load_initial_data()
        self.cache_reload_thread.start()
        self.writer_thread.start()
        print("CacheManager started with background writer.")

    def stop(self):
        print("Stopping CacheManager...")
        self.shutdown_event.set()
        self.writer_thread.join()
        print("CacheManager stopped.")


    def load_initial_data(self):
        print("Loading initial data into cache...")
        try:
            gsheet_client = GSheetClient.from_settings()
            worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
            all_values = worksheet.get_all_values()

            if not all_values:
                print("Warning: Google Sheet is empty.")
                self.is_initialized = False
                return

            headers = all_values[0]
            records = [dict(zip(headers, row)) for row in all_values[1:]]

            with self._lock:
                self.attendees_cache = {str(record[settings.COL_UNIQUE_ID]): record for record in records}
                self.employee_id_to_row_index = {
                    str(record[settings.COL_UNIQUE_ID]): index + 2
                    for index, record in enumerate(records)
                }
                self.last_updated = time.time()
                self.is_initialized = True

            print(f"Successfully loaded {len(records)} records into cache.")
        except Exception as e:
            import traceback
            print(f"FATAL: Error loading initial data: {e}")
            traceback.print_exc()
            self.is_initialized = False

    def _background_cache_reload(self):
        while not self.shutdown_event.is_set():
            self.shutdown_event.wait(settings.CACHE_UPDATE_INTERVAL_SECONDS)
            if not self.shutdown_event.is_set():
                print("Running background cache reload...")
                self.load_initial_data()

    def _background_writer(self):
        while not self.shutdown_event.is_set():
            self.shutdown_event.wait(10)
            if not self.update_queue:
                continue

            updates_to_process = []
            with self._lock:
                while self.update_queue:
                    updates_to_process.append(self.update_queue.popleft())

            if not updates_to_process:
                continue

            print(f"Processing {len(updates_to_process)} updates from queue...")

            try:
                gsheet_client = GSheetClient.from_settings()
                worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)
                headers = worksheet.row_values(1)
                header_map = {header: i + 1 for i, header in enumerate(headers)}

                # Chunk tasks into smaller batches before generating cells
                for i in range(0, len(updates_to_process), TASK_BATCH_SIZE):
                    task_batch = updates_to_process[i:i + TASK_BATCH_SIZE]
                    cells_to_update = []

                    for employee_id, update_type, timestamp_str in task_batch:
                        row_index = self.employee_id_to_row_index.get(employee_id)
                        if not row_index:
                            print(f"Warning: Could not find row for employee {employee_id}. Skipping.")
                            continue

                        if update_type == "check-in":
                            status_col = header_map[settings.COL_CHECK_IN_STATUS]
                            time_col = header_map[settings.COL_CHECK_IN_TIME]
                            cells_to_update.append(gspread.Cell(row_index, status_col, "TRUE"))
                            cells_to_update.append(gspread.Cell(row_index, time_col, timestamp_str))
                        elif update_type == "check-out":
                            status_col = header_map[settings.COL_CHECK_OUT_STATUS]
                            time_col = header_map[settings.COL_CHECK_OUT_TIME]
                            cells_to_update.append(gspread.Cell(row_index, status_col, "TRUE"))
                            cells_to_update.append(gspread.Cell(row_index, time_col, timestamp_str))

                    if not cells_to_update:
                        continue

                    try:
                        print(f"Updating a batch of {len(cells_to_update)} cells for {len(task_batch)} tasks...")
                        gsheet_client.batch_update_cells(worksheet, cells_to_update)
                    except Exception as e:
                        print("="*80)
                        print(f"ERROR: Failed to update a batch of {len(task_batch)} tasks. This batch will be re-queued.")
                        print(f"Error Details: {e}")
                        print("="*80)
                        with self._lock:
                            for item in reversed(task_batch):
                                self.update_queue.appendleft(item)

                print(f"Finished processing for this cycle.")

            except Exception as e:
                import traceback
                print("="*80)
                print(f"FATAL: An unexpected error occurred before batch processing. All tasks for this cycle will be re-queued.")
                traceback.print_exc()
                print("="*80)
                with self._lock:
                    for item in reversed(updates_to_process):
                        self.update_queue.appendleft(item)

    def get_attendee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.attendees_cache.get(employee_id)

    def get_all_attendees(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.attendees_cache.values())

    def update_check_in_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            attendee = self.attendees_cache.get(employee_id)
            if not attendee:
                return None

            timestamp_str = datetime.now(TAIPEI_TZ).isoformat()

            attendee[settings.COL_CHECK_IN_STATUS] = "TRUE"
            attendee[settings.COL_CHECK_IN_TIME] = timestamp_str

            self.update_queue.append((employee_id, "check-in", timestamp_str))
            return attendee

    def update_check_out_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            attendee = self.attendees_cache.get(employee_id)
            if not attendee:
                return None

            timestamp_str = datetime.now(TAIPEI_TZ).isoformat()

            attendee[settings.COL_CHECK_OUT_STATUS] = "TRUE"
            attendee[settings.COL_CHECK_OUT_TIME] = timestamp_str

            self.update_queue.append((employee_id, "check-out", timestamp_str))
            return attendee

cache_manager = CacheManager.get_instance()
