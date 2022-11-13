from cryptography.fernet import Fernet
import os, time

class Encryptor():
    def _generate_key(self):
        key = Fernet.generate_key()
        with open('filekey.key', 'wb') as filekey:
            filekey.write(key)

    def load_key(self):
            with open('filekey.key', 'rb') as filekey:
                key = filekey.read()
                self.key = key
    
    def _encrypt_file(self,file):
        self.load_key()
        fernet = Fernet(self.key)
        with open(file,'rb') as file:
            original_file = file.read()
        encrypted = fernet.encrypt(original_file)
        print(file.name)
        with open(file.name + '.enc', 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
    
    def _decrypt_file(self,file,path_to_save_file):
        self.load_key()
        fernet = Fernet(self.key)
        with open(file, 'rb') as enc_file:
            encrypted = enc_file.read()
        decrypted = fernet.decrypt(encrypted)
        with open(path_to_save_file, 'wb') as dec_file:
            dec_file.write(decrypted)

    def encrypt_csv_files(self, i_dir):
        for dirpath, subdirs, files in os.walk(i_dir):
            for file in files:
                if file.endswith('.csv'):
                    self._encrypt_file(os.path.join('', dirpath, file))

    def decrypt_local_csv_files(self):
        encrypted_csv_files_dir = os.path.join('','csv_files_local','encrypted')
        decrypted_csv_files_dir = os.path.join('','csv_files_local','decrypted')
        for dirpath, subdirs, files in os.walk(encrypted_csv_files_dir):
            for file in files:
                if file.endswith('.enc'):
                    self._decrypt_file(os.path.join('',dirpath,file), os.path.join(decrypted_csv_files_dir, file)[:-4])