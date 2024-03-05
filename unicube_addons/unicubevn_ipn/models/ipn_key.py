#   Copyright (c) by The UniCube, 2023.
#   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#   These code are maintained by The UniCube.
import hashlib
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives._serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding, rsa
import base64
import json

from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

from odoo import api, fields, models

demo_private_rsa_key = """"-----BEGIN RSA PRIVATE KEY-----
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
-----END RSA PRIVATE KEY-----
"""
demo_public_rsa_key = """-----BEGIN RSA PUBLIC KEY-----
MIICCgKCAgEArcdzHVaFFHBQLAZz1ygSRkHuhzkQ6ovYLK3h2xaWIitwO3Mj02W+
Ak03eg9dk9V+HytCiU2aSG6Oe0MTzJGzQj9ag7GrM4ui0EYbTxnHRrYyg5uagHXs
MOSCmlLYPqtauTsGnZFBXsyZqHAJKiTqOGRW0cEx/A2EAepBqkY+hrmq1qQsBx8U
1ErmIkTRbE036nuuzYHDGenQ0/FdCCO3AZRZDfZCl4SXfCAq5L9+7P5M/nRb8rAY
7xGM/eNOmELc72f57SGnZsgltfl5iiue5MnGGP9uChaQ+X4DkG/eW/1e2eBoOMi2
qtmsTQfgsRBr3jNa9tasXLEn/9Ch3sDG2p3NmWtz3viugzOPQlC+5v6lg34rNFgF
pvoVCbotSmSbtbEdK4vkdMpq/pUb7zWzWsIlUjH7mGy/3USrxPsDvpEjriB4ruAK
dTVbv1EuHvD4yRyEke3i7b4SQgmulfXObCqQgEg4vnH8kj0NfdC16p5ckbwS0ka+
oG+KWIbz4uzEGyhrBD7PY0VgshzRHvbKmRa2SQP0tDJQtL1hIvBxdp2/jNluIxe6
vVD1/dKiZvZvshTwKJ63xsp28KWdgx9slQQQNzY8ArnkDBWo8dspiHMDSU4cDmin
eZToFnt044WDWdmH8CV37G+xEw1tE199mLlq5H9RreizRN81x8IPFq8CAwEAAQ==
-----END RSA PUBLIC KEY-----
"""

demo_symmetric_key = "rtpPxr2kZ1F3QAboJt2CqOVQMTTH5MHuJZEWX3fl1aM="
demo_vector_key = "Bn447+S/5hw1faf10XCwTg=="


class IpnKeys(models.Model):
    _name = "ipn.key"
    _description = "Keys and encrypt/decrypt method"

    payment_method_id = fields.Many2one("payment.method", string="Payment provider", required=True)
    name = fields.Char(string="Provider name", related="payment_method_id.name", store=True)
    code = fields.Char(string="Provider Code", related="payment_method_id.code", store=True)
    encrypt_method = fields.Selection(
        [('rsa_aes_ebc', 'RSA-AES-EBC '), ('rsa_aes_cbc', 'RSA-AES-CBC '),
         ('rsa_sha_256', 'RSA-SHA-256 '), ('md5', 'MD5')], string="Encryption method",
        default="rsa_aes_ebc")
    private_key = fields.Text(string="Private Key / Symmetric Key", default="")
    public_key = fields.Text(string="Public Key / Vector", default="")
    test_message = fields.Char(string="Test Message", default="This is a test message")
    encrypted_message = fields.Char(string="Encrypted Message", default=False)
    test_message_check = fields.Text(string="Result")

    @api.onchange("encrypt_method")
    def _compute_private_key(self):
        print("Private Key / Symmetric Key")
        if self.encrypt_method == 'rsa_sha_256':
            self.private_key = demo_private_rsa_key
        else:
            self.private_key = demo_symmetric_key

    @api.onchange("encrypt_method")
    def _compute_public_key(self):
        print("Default Public Key")
        if self.encrypt_method == 'rsa_sha_256':
            self.public_key = demo_public_rsa_key
        else:
            self.public_key = demo_vector_key

    def sign_message(self, message: str):
        if self.encrypt_method == 'rsa_sha_256':
            private_key_str = (self.private_key or demo_private_rsa_key)
            print("private_key_str : ", private_key_str)
            private_key = serialization.load_pem_private_key(private_key_str.encode(), password=None)
            signature = private_key.sign(message.encode('utf-8'), asym_padding.PKCS1v15(), hashes.SHA256())
            sign = base64.b64encode(signature).decode()
            return sign

    def verify_signature(self, message: str, signature):
        if self.encrypt_method == 'rsa_sha_256':
            public_key_str = (self.public_key or demo_public_rsa_key).encode('utf-8')
            public_key = serialization.load_pem_public_key(public_key_str)
            try:
                public_key.verify(
                    base64.b64decode(signature),
                    message.encode('utf-8'),
                    asym_padding.PKCS1v15(),
                    hashes.SHA256()
                )
                return True
            except:
                return False

    def encrypt(self, message: str):
        if self.encrypt_method == 'rsa_sha_256':
            public_key_str = (self.public_key or demo_public_rsa_key).encode('utf-8')
            public_key = serialization.load_pem_public_key(public_key_str)
            print('message', message)
            data_encrypted = public_key.encrypt(
                message.encode('utf-8'),
                asym_padding.PKCS1v15()
            )
            data_encrypted = base64.b64encode(data_encrypted).decode()
            return data_encrypted
        if self.encrypt_method in ['rsa_aes_ebc', 'rsa_aes_cbc']:
            private_key_str = self.private_key or demo_symmetric_key
            print(private_key_str)
            vector_key = self.public_key or demo_vector_key
            if self.encrypt_method == 'rsa_aes_cbc':
                cipher = Cipher(algorithms.AES(base64.b64decode(private_key_str)),
                                modes.CBC(base64.b64decode(vector_key)), backend=default_backend())
            else:
                cipher = Cipher(algorithms.AES(base64.b64decode(private_key_str)), modes.ECB(),
                                backend=default_backend())
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_plaintext = padder.update(message.encode()) + padder.finalize()
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            return base64.b64encode(ciphertext)

    def decrypt(self, encrypted: str, is_base64_encode=True):
        if self.encrypt_method == 'rsa_sha_256':
            private_key_str = (self.private_key or demo_private_rsa_key).encode('utf-8')
            private_key = serialization.load_pem_private_key(private_key_str, password=None)
            ciphert_text = base64.b64decode(encrypted) if is_base64_encode else encrypted
            print('ciphert_text lenght:', len(ciphert_text))
            data_encrypted = private_key.decrypt(
                ciphert_text,
                asym_padding.PKCS1v15()
            )
            return data_encrypted.decode()
        if self.encrypt_method in ['rsa_aes_ebc', 'rsa_aes_cbc']:
            private_key_str = (self.private_key or demo_symmetric_key).encode('utf-8')
            vector_key = (self.public_key or demo_vector_key).encode('utf-8')
            if self.encrypt_method == 'rsa_aes_cbc':
                cipher = Cipher(algorithms.AES(base64.b64decode(private_key_str)),
                                modes.CBC(base64.b64decode(vector_key)))
            else:
                cipher = Cipher(algorithms.AES(base64.b64decode(private_key_str)), modes.ECB())
            decryptor = cipher.decryptor()
            decrypted_message = decryptor.update(
                base64.b64decode(encrypted) if is_base64_encode else encrypted) + decryptor.finalize()
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            decrypted_message = unpadder.update(decrypted_message) + unpadder.finalize()
            return decrypted_message.decode('utf-8')

    # ===== Actions =====
    def action_genkey(self):
        print('action_genkey:', self.encrypt_method)
        if self.encrypt_method == 'rsa_sha_256':
            if self.private_key:
                private_key = serialization.load_pem_private_key(self.private_key.encode('utf-8'), password=None)
                # Get the public key
                public_key = private_key.public_key()

                # Serialize the public key (PEM format, PKCS#1)
                public_key_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.PKCS1
                )
                self.public_key = public_key_pem.decode('utf-8')
            else:
                # Generate a new RSA key pair
                key_size = 4096
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=key_size,
                    backend=default_backend()
                )

                # Serialize the private key (PEM format, PKCS#1)
                private_key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                # Get the public key
                public_key = private_key.public_key()

                # Serialize the public key (PEM format, PKCS#1)
                public_key_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.PKCS1
                )

                self.private_key = private_key_pem.decode('utf-8')
                self.public_key = public_key_pem.decode('utf-8')
        else:
            self.private_key = base64.b64encode(os.urandom(32)).decode('utf-8')
            self.public_key = base64.b64encode(os.urandom(16)).decode('utf-8')

    def action_test_encrypt(self):
        print('self.encrypt_method:', self.encrypt_method)
        signature = ""
        verify = ""
        data_encrypted = ""
        data_decrypted = ""
        if self.encrypt_method == 'rsa_sha_256':
            # data = {
            #     "otp_code": "123456",
            #     "account_number": "ATO01148427623NQRK",
            # }
            # message = json.dumps(data)

            signature = self.sign_message(self.test_message)
            print('signature: ', signature)
            verify = self.verify_signature(self.test_message, signature)
            print('verify:', verify)
            data_encrypted = self.encrypt(self.test_message)

            data_decrypted = self.decrypt(self.encrypted_message if self.encrypted_message else data_encrypted)
            print(data_encrypted)
            print(data_decrypted)

        if self.encrypt_method in ['rsa_aes_ebc', 'rsa_aes_cbc']:
            data_encrypted = self.encrypt(self.test_message)
            data_decrypted = self.decrypt(data_encrypted)
            print(data_encrypted)
            print(data_decrypted)

        self.test_message_check = f"""
                signature: {signature}
                verify: {verify}
                data_encrypted: {data_encrypted}
                data_decrypted: {data_decrypted}
                check decrypted=test_message: {self.test_message == data_decrypted}
            """
