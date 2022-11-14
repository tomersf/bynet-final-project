from decimal import Decimal
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy_serializer import SerializerMixin
from abc import ABC, abstractmethod
from Logger import Logger
from encryptor import Encryptor
import os
import pysftp

from attendance import get_attendance_dict_result
from env import env_config


class DB(ABC):
    def __init__(self) -> None:
        self.base = declarative_base()
        self.session = None
        self.engine = None
        self.connected = False

    @abstractmethod
    def connect(self) -> None:
        pass

    def _init_sessionmaker(self) -> None:
        self.session = sessionmaker(self.engine)

    def _init_db_metadata(self) -> None:
        self.base.metadata.create_all(self.engine)

    @abstractmethod
    def _init_model_tables(self) -> None:
        pass


class AttendanceDB(DB):
    def __init__(self) -> None:
        super().__init__()
        self.attendees = None
        self.attendance = None
        self.model_attendee = None
        self.model_attendance = None
        self.connected = False
        self.attendees_changed = False
        self.attendance_changed = False
        self._init_model_tables()

    def _init_model_tables(self):
        class Attendee(self.base, SerializerMixin):
            __tablename__ = 'attendees'
            id = Column(Integer(), primary_key=True)
            name = Column(String(25), nullable=False)
            attendance_duration = Column(DECIMAL(7, 2), nullable=False)
            attendance_percentage = Column(DECIMAL(5, 2), nullable=False)
        self.model_attendee = Attendee

        class Attendance(self.base, SerializerMixin):
            __tablename__ = 'attendance'
            id = Column(Integer(), primary_key=True)
            total_duration = Column(DECIMAL(7, 2), nullable=False)
        self.model_attendance = Attendance

    def connect(self) -> bool:
        try:
            hostname = env_config['SQL_HOST']
            password = env_config['SQL_PASSWORD']
            username = env_config['SQL_USER']
            dbname = env_config['SQL_DBNAME']
            DB_URI = f"mysql://{username}:{password}@{hostname}:3306/{dbname}"
            engine = create_engine(DB_URI, echo=True)
            if not database_exists(engine.url):
                create_database(engine.url)
            self.engine = engine
            self._init_sessionmaker()
            self._init_db_metadata()
            self.connected = True
            return True
        except Exception as ex:
            Logger.ERROR(
                'Unable to connect to database! check env variables / sql server is up')
            Logger.ERROR(
                f"Tried to connect to: mysql://{username}:<PASSWORD>@{hostname}/{dbname}")
            print(ex)
            return False

    def insert_or_update_attendees(self, attendees: dict) -> bool:
        return self._open_session(self._insert_or_update_attendees, attendees)

    def _insert_or_update_attendees(self, local_session, attendees):
        attendees_to_insert = []
        for attendee in attendees.keys():
            if self._attendee_in_table(attendee):
                self._update_attendee_duration(
                    attendees[attendee], attendee)
            else:
                attendees_to_insert.append(self.model_attendee(
                    name=attendee, attendance_duration=Decimal(attendees[attendee]['attendance_duration']), attendance_percentage=Decimal(attendees[attendee]['attendance_percentage'])))
        local_session.add_all(attendees_to_insert)
        local_session.commit()
        return True

    def close_unexpected_db_session(self, exception, local_session):
        Logger.ERROR('EXECUTING ROLLBACK & CLOSING SESSION DUE TO EXCEPTION')
        print(exception)
        local_session.rollback()
        local_session.close_all()

    def _attendee_in_table(self, attendee_name) -> bool:
        return self._open_session(self.__attendee_in_table, attendee_name)

    def __attendee_in_table(self, local_session, attendee_name):
        attendee_entry = local_session.query(self.model_attendee).filter(
            self.model_attendee.name == attendee_name).first()
        if attendee_entry:
            return True
        return False

    def _update_attendee_duration(self, attendee_dict, attendee_name):
        self._open_session(self.__update_attendee_duration,
                            attendee_dict, attendee_name)

    def __update_attendee_duration(self, local_session, attendee_dict, attendee_name):
        attendee_entry = local_session.query(self.model_attendee).filter(
            self.model_attendee.name == attendee_name).first()
        if attendee_entry and attendee_entry.attendance_duration != Decimal(
                attendee_dict['attendance_duration']):
            attendee_entry.attendance_duration = Decimal(
                attendee_dict['attendance_duration'])
            attendee_entry.attendance_percentage = Decimal(
                attendee_dict['attendance_percentage'])
            local_session.commit()

    def insert_or_update_attendance(self, meeting_minutes) -> bool:
        result = self._open_session(
            self._insert_or_update_attendance, meeting_minutes)
        if not result:
            Logger.ERROR('Unable to insert into attendance table!')
            return False
        return True

    def _insert_or_update_attendance(self, local_session, meeting_minutes) -> bool:
        attendance = local_session.query(self.model_attendance).first()
        if attendance:
            attendance.total_duration = meeting_minutes
            local_session.commit()
            return True
        else:
            new_entry = self.model_attendance(
                total_duration=meeting_minutes)
            local_session.add(new_entry)
            local_session.commit()
            return True

    def get_total_meetings_duration(self) -> Decimal:
        self._open_session(self._get_total_meetings_duration)

    def _get_total_meetings_duration(self, local_session):
        attendance = local_session.query(self.model_attendance).first()
        return attendance['total_duration']

    def load_participants(self) -> bool:
        fetched_remote_csv_files = False
        inserted_data_to_db = False
        loaded_local_csv_files = False
        fetched_remote_csv_files = self._save_remote_csv_files_to_csv_files_local_dir()
        if fetched_remote_csv_files:
            fetched_remote_csv_files = True
            inserted_data_to_db = self._insert_csv_files_to_attendance_db('csv_files_remote')
        else:
            Logger.ERROR('Unable to save remote csv files locally!!')
            print('Going to try loading stored csv files locally!')
            try:
                Encryptor().decrypt_local_csv_files()
                inserted_data_to_db = self._insert_csv_files_to_attendance_db(os.path.join('','csv_files_local','decrypted'))
                if inserted_data_to_db:
                    loaded_local_csv_files = True
            except Exception as e:
                Logger.ERROR('Unable to decrypt local csv files!!')
                print(e)
        print(f"""
                Fetching remove csv files status: {fetched_remote_csv_files}
                Loading local csv files status: {loaded_local_csv_files}
                Inserting data to db status: {inserted_data_to_db}
                """)
        return (fetched_remote_csv_files or loaded_local_csv_files) and inserted_data_to_db

    def _save_remote_csv_files_to_csv_files_local_dir(self) -> bool:
        try:
            username = env_config['REMOTE_MACHINE_USERNAME']
            password = env_config['REMOTE_MACHINE_PASSWORD']
            remote_machine_ip = env_config['REMOTE_MACHINE_IP']
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            with pysftp.Connection(remote_machine_ip, username=username, password=password, cnopts=cnopts) as sftp:
                csv_files_path = env_config['REMOTE_MACHINE_CSV_FILES_PATH']
                with sftp.cd(csv_files_path):
                    local_dir = os.path.join(os.getcwd(), 'csv_files_remote')
                    if not os.path.isdir(local_dir):
                        os.mkdir(local_dir)
                    for filename in sftp.listdir('.'):
                        if filename.startswith('participant-') and filename.endswith('.csv'):
                            if not os.path.isfile(os.path.join(local_dir, filename)):
                                sftp.get(
                                    filename, os.path.join(local_dir, filename))
            return True
        except Exception as e:
            Logger.ERROR('Unable to load csv files from remote machine!')
            print(e)
            return False

    def _insert_csv_files_to_attendance_db(self,relative_csv_files_path) -> bool:
        attendance_dict = get_attendance_dict_result(
            os.path.join(os.getcwd(), relative_csv_files_path))
        if not attendance_dict:
            Logger.ERROR('Attendance dict is empty!')
            return False
        else:
            self._fix_and_convert_names_to_eng(attendance_dict)
            total_minutes = attendance_dict['total_meetings_duration']
            attendance_dict.pop('total_meetings_duration')
            is_success_in_insert_or_update_attendees = self.insert_or_update_attendees(
                attendance_dict)
            is_success_in_insert_or_update_attendance = self.insert_or_update_attendance(
                Decimal(total_minutes))
            if not is_success_in_insert_or_update_attendees:
                Logger.ERROR('Unable to insert or update attendees!')
            if not is_success_in_insert_or_update_attendance:
                Logger.ERROR('Unable to insert or update attendance!')
            self.attendees_changed = True
            self.attendance_changed = True
            return True

    def _fix_and_convert_names_to_eng(self, attendance_dict):
        def drop_attendees_from_dict(attendees_names):
            for attendee_name in attendees_names:
                attendance_dict.pop(attendee_name)

        def update_attendance_for_user(og_name, second_name):
            if second_name in attendance_dict and og_name in attendance_dict:
                attendance_dict[og_name]['attendance_duration'] += attendance_dict[second_name]['attendance_duration']
                attendance_dict[og_name]['attendance_percentage'] += attendance_dict[second_name]['attendance_percentage']
                drop_attendees_from_dict([second_name])
        update_attendance_for_user('David', 'ציבולסקי דוד')
        update_attendance_for_user('Yossi Bengaev', 'יוסי בנגייב')
        update_attendance_for_user('Oren', 'אורן גדמו')
        update_attendance_for_user('Batel Bokobza', 'Batel')
        update_attendance_for_user('Yonatan', 'יונתן')
        update_attendance_for_user('Naor', 'Naorf')
        update_attendance_for_user('Sanad Adwan', 'Sanad')
        update_attendance_for_user('Estherwahnon', 'Esther')
        drop_attendees_from_dict(
            ['Dan', 'Callin User', 'Malki', 'Avi Shilon', 'מירב חורש', 'Avi Barell'])

    def get_all_attendees(self) -> list[dict]:
        if not self.connected:
            return []
        if not self.attendees_changed:
            return self.attendees
        return self._open_session(self._set_and_get_attendees)

    def _set_and_get_attendees(self, local_session):
        attendees = local_session.query(self.model_attendee).all()
        result = []
        for attendee in attendees:
            result.append(attendee.to_dict())
        self.attendees_changed = False
        self.attendees = result
        return result

    def get_attendance(self) -> dict:
        if not self.connected:
            return self._empty_attendance_result()
        if not self.attendance_changed:
            return self.attendance
        return self._open_session(self._set_and_get_attendance)

    def _set_and_get_attendance(self, local_session):
        attendance = local_session.query(self.model_attendance).all()
        if attendance:
            self.attendance_changed = False
            self.attendance = attendance[0].to_dict()
            return attendance[0].to_dict()
        return self._empty_attendance_result()

    def _empty_attendance_result(self):
        return {
            'total_duration': 0
        }

    def _open_session(self, callbackFn, *args):
        try:
            with self.session() as local_session:
                return callbackFn(local_session, *args)
        except Exception as e:
            self.close_unexpected_db_session(e, local_session)
            return False

    def reload_data(self):
        is_connected_to_db = False
        if not self.connected:
            is_connected_to_db = self.connect()
        else:
            is_connected_to_db = True
        if not is_connected_to_db:
            return False
        is_participants_loaded = self.load_participants()
        if not is_participants_loaded:
            return False
        return True
        