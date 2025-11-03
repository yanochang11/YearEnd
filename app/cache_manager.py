# app/cache_manager.py
import threading
import time
import gspread
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
from datetime import datetime, timezone

from .gsheet_client import GSheetClient
from .config import settings

UpdateTask = Tuple[str, str] # (employee_id, "check-in" | "check-out")

class CacheManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.attendees_cache: Dict[str, Dict[str, Any]] = {}
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
            records = worksheet.get_all_records()

            with self._lock:
                self.attendees_cache = {str(record[settings.COL_UNIQUE_ID]): record for record in records}
                self.last_updated = time.time()
                self.is_initialized = True

            print(f"Successfully loaded {len(records)} records into cache.")
        except gspread.exceptions.APIError as e:
            print(f"Error loading initial data: {e}")
            self.is_initialized = False

    def _background_cache_reload(self):
        while not self.shutdown_event.is_set():
            self.shutdown_event.wait(settings.CACHE_UPDATE_INTERVAL_SECONDS)
            if not self.shutdown_event.is_set():
                print("Running background cache reload...")
                self.load_initial_data()

    def _background_writer(self):
        while not self.shutdown_event.is_set():
            self.shutdown_event.wait(10) # Process queue every 10 seconds
            if self.update_queue:
                updates_to_process = []
                with self._lock:
                    while self.update_queue:
                        updates_to_process.append(self.update_queue.popleft())

                if updates_to_process:
                    print(f"Processing {len(updates_to_process)} updates from queue...")
                    try:
                        gsheet_client = GSheetClient.from_settings()
                        worksheet = gsheet_client.get_worksheet(settings.WORKSHEET_NAME)

                        # In a real high-throughput system, you'd batch these updates
                        # For simplicity here, we process them one by one.
                        for employee_id, update_type in updates_to_process:
                            if update_type == "check-in":
                                gsheet_client.update_check_in_status(worksheet, employee_id)
                            elif update_type == "check-out":
                                gsheet_client.update_check_out_status(worksheet, employee_id)
                        print("Finished processing updates.")

                    except gspread.exceptions.APIError as e:
                        print(f"Error processing update queue: {e}")
                        # Re-queue failed updates for next attempt
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

            # Update cache immediately
            attendee[settings.COL_CHECK_IN_STATUS] = "TRUE"
            attendee[settings.COL_CHECK_IN_TIME] = datetime.now(timezone.utc).isoformat()

            # Add to write queue
            self.update_queue.append((employee_id, "check-in"))
            return attendee

    def update_check_out_status(self, employee_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            attendee = self.attendees_cache.get(employee_id)
            if not attendee:
                return None

            # Update cache immediately
            attendee[settings.COL_CHECK_OUT_STATUS] = "TRUE"
            attendee[settings.COL_CHECK_OUT_TIME] = datetime.now(timezone.utc).isoformat()

            # Add to write queue
            self.update_queue.append((employee_id, "check-out"))
            return attendee

cache_manager = CacheManager.get_instance()
