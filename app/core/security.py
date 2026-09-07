from passlib.context import CryptContext

# Création d'un contexte de chiffrement/hachage des mots de passe avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Transforme un mot de passe en hash sécurisé
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Vérifie si un mot de passe correspond à un hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)