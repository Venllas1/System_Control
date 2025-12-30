"""
Sistema de Licencias CABELAB 2025
Autor: Sistema de Seguridad
Versión: 1.0 - Implementación con encriptación RSA
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64


class LicenseManager:
    """
    Gestor de licencias con encriptación RSA y binding de hardware
    """
    
    def __init__(self):
        self.license_file = Path('license.dat')
        self.public_key_file = Path('keys/public.pem')
        self.private_key_file = Path('keys/private.pem')
        self.log_file = Path('logs/license_attempts.log')
        
        # Crear directorios necesarios
        Path('keys').mkdir(exist_ok=True)
        Path('logs').mkdir(exist_ok=True)
        
        # Generar claves si no existen (SOLO PRIMERA VEZ)
        if not self.public_key_file.exists():
            self._generate_keys()
    
    def _generate_keys(self):
        """
        Genera par de claves RSA (público/privada)
        IMPORTANTE: Guarda la clave privada en lugar seguro
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Guardar clave privada (MANTENER SECRETA)
        with open(self.private_key_file, 'wb') as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Guardar clave pública (incluir en la app)
        public_key = private_key.public_key()
        with open(self.public_key_file, 'wb') as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        print("🔑 Claves RSA generadas exitosamente")
        print(f"⚠️  IMPORTANTE: Guarda {self.private_key_file} en lugar seguro")
    
    def get_hardware_id(self):
        """
        Obtiene identificador único del hardware
        Combina MAC address + nombre de máquina
        """
        mac = hex(uuid.getnode())[2:].upper()
        machine = os.environ.get('COMPUTERNAME', 'UNKNOWN')
        
        # Hash para ofuscar
        raw = f"{mac}:{machine}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
    
    def generate_license(self, client_name: str, months: int = 1, hardware_id: str = None):
        """
        SOLO TÚ EJECUTAS ESTO - Genera una licencia válida
        
        Args:
            client_name: Nombre del cliente/instalación
            months: Meses de validez (default 1)
            hardware_id: ID de hardware del cliente (obtener con get_hardware_id())
        
        Returns:
            str: Licencia encriptada en base64
        """
        if not self.private_key_file.exists():
            raise Exception("❌ Clave privada no encontrada")
        
        # Datos de la licencia
        issue_date = datetime.now()
        expiry_date = issue_date + timedelta(days=30 * months)
        
        license_data = {
            'client': client_name,
            'hardware_id': hardware_id or self.get_hardware_id(),
            'issued': issue_date.isoformat(),
            'expires': expiry_date.isoformat(),
            'version': '1.0',
            'product': 'CABELAB_2025'
        }
        
        # Serializar y encriptar
        json_data = json.dumps(license_data, sort_keys=True)
        
        # Cargar clave privada
        with open(self.private_key_file, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        
        # Encriptar con RSA
        encrypted = private_key.sign(
            json_data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Combinar datos + firma
        license_package = {
            'data': json_data,
            'signature': base64.b64encode(encrypted).decode()
        }
        
        license_str = base64.b64encode(
            json.dumps(license_package).encode()
        ).decode()
        
        print(f"✅ Licencia generada para: {client_name}")
        print(f"📅 Válida hasta: {expiry_date.strftime('%d/%m/%Y')}")
        print(f"🔒 Hardware ID: {license_data['hardware_id']}")
        
        return license_str
    
    def save_license(self, license_str: str):
        """
        Guarda la licencia en el archivo local
        """
        with open(self.license_file, 'w') as f:
            f.write(license_str)
        print("💾 Licencia guardada correctamente")
    
    def validate_license(self) -> dict:
        """
        Valida la licencia instalada
        
        Returns:
            dict: {'valid': bool, 'message': str, 'data': dict}
        """
        # Verificar que existe el archivo
        if not self.license_file.exists():
            self._log_attempt("FAILED", "Archivo de licencia no encontrado")
            return {
                'valid': False,
                'message': '❌ No se encontró archivo de licencia',
                'data': None
            }
        
        try:
            # Leer licencia
            with open(self.license_file, 'r') as f:
                license_str = f.read().strip()
            
            # Decodificar
            license_package = json.loads(
                base64.b64decode(license_str).decode()
            )
            
            license_data = json.loads(license_package['data'])
            signature = base64.b64decode(license_package['signature'])
            
            # Verificar firma con clave pública
            with open(self.public_key_file, 'rb') as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            
            # Verificar firma RSA
            try:
                public_key.verify(
                    signature,
                    license_package['data'].encode(),
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            except Exception:
                self._log_attempt("FAILED", "Firma de licencia inválida")
                return {
                    'valid': False,
                    'message': '❌ Licencia manipulada o inválida',
                    'data': None
                }
            
            # Verificar hardware ID
            current_hw = self.get_hardware_id()
            if license_data['hardware_id'] != current_hw:
                self._log_attempt("FAILED", f"Hardware ID no coincide: {current_hw}")
                return {
                    'valid': False,
                    'message': '❌ Licencia no válida para este equipo',
                    'data': license_data
                }
            
            # Verificar fecha de expiración
            expiry = datetime.fromisoformat(license_data['expires'])
            now = datetime.now()
            
            if now > expiry:
                days_expired = (now - expiry).days
                self._log_attempt("EXPIRED", f"Expiró hace {days_expired} días")
                return {
                    'valid': False,
                    'message': f'❌ Licencia expirada hace {days_expired} días',
                    'data': license_data
                }
            
            # Licencia válida
            days_remaining = (expiry - now).days
            self._log_attempt("SUCCESS", f"Quedan {days_remaining} días")
            
            return {
                'valid': True,
                'message': f'✅ Licencia válida ({days_remaining} días restantes)',
                'data': license_data,
                'days_remaining': days_remaining
            }
        
        except Exception as e:
            self._log_attempt("ERROR", str(e))
            return {
                'valid': False,
                'message': f'❌ Error al validar licencia: {str(e)}',
                'data': None
            }
    
    def _log_attempt(self, status: str, details: str):
        """
        Registra intentos de acceso en log
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        hw_id = self.get_hardware_id()
        
        log_entry = f"[{timestamp}] {status} | HW: {hw_id} | {details}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def get_license_info(self) -> dict:
        """
        Obtiene información de la licencia sin validar
        """
        result = self.validate_license()
        return result.get('data', {})
    
    def check_expiry_warning(self) -> bool:
        """
        Verifica si la licencia está por vencer (menos de 7 días)
        """
        result = self.validate_license()
        if result['valid']:
            days = result.get('days_remaining', 0)
            return days <= 7
        return False


# ============================================
# FUNCIONES DE UTILIDAD PARA ADMINISTRADOR
# ============================================

def generate_new_license(client_name: str, hardware_id: str, months: int = 1):
    """
    Función de conveniencia para generar licencia
    USO: Solo para ti como administrador
    """
    manager = LicenseManager()
    license_str = manager.generate_license(client_name, months, hardware_id)
    
    # Guardar en archivo para enviar al cliente
    output_file = f"license_{client_name}_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(output_file, 'w') as f:
        f.write(license_str)
    
    print(f"\n📄 Licencia guardada en: {output_file}")
    print(f"📧 Envía este archivo al cliente: {client_name}")
    
    return license_str


def get_client_hardware_id():
    """
    Obtiene el hardware ID del cliente
    El cliente ejecuta esto y te envía el resultado
    """
    manager = LicenseManager()
    hw_id = manager.get_hardware_id()
    print(f"🔑 Hardware ID de este equipo: {hw_id}")
    print(f"📧 Envía este ID al administrador para generar tu licencia")
    return hw_id


def install_license_from_file(license_file_path: str):
    """
    Instala una licencia desde un archivo
    """
    manager = LicenseManager()
    
    with open(license_file_path, 'r') as f:
        license_str = f.read().strip()
    
    manager.save_license(license_str)
    result = manager.validate_license()
    
    print(result['message'])
    return result['valid']


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔐 CABELAB 2025 - Sistema de Licencias")
    print("=" * 70)
    
    # PASO 1: Cliente obtiene su Hardware ID
    print("\n[CLIENTE] Obteniendo Hardware ID...")
    hw_id = get_client_hardware_id()
    
    # PASO 2: Administrador genera licencia
    print("\n[ADMIN] Generando licencia para el cliente...")
    license_str = generate_new_license(
        client_name="CABELAB_SEDE_AREQUIPA",
        hardware_id=hw_id,
        months=1
    )
    
    # PASO 3: Cliente instala la licencia
    print("\n[CLIENTE] Validando licencia instalada...")
    manager = LicenseManager()
    manager.save_license(license_str)
    result = manager.validate_license()
    
    print(f"\n{result['message']}")
    if result['valid']:
        print(f"📅 Expira: {result['data']['expires']}")
        print(f"👤 Cliente: {result['data']['client']}")