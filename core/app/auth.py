import bcrypt
import datetime
import jwt
import os
from core.app.client import ScannerClient
from core.app.exceptions import AuthError, ClientError, ClientNotFound
from core.app.utils import app_logger
from core.app.db import Base, ClientRecord, RevokedToken
from jwt import DecodeError, ExpiredSignatureError, InvalidAlgorithmError
from sqlalchemy import or_, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from typing import Union


class AuthManager:
    """A class for managing client authentication."""

    def __init__(self, algorithm="HS256"):
        self.algorithm = algorithm
        self.secret_key = os.environ.get("JWT_SECRET_KEY")
        if not self.secret_key:
            raise RuntimeError("JWT_SECRET_KEY environment variable is not set.")

        db_path = os.environ.get("SQLITE_DB_PATH")
        if not db_path:
            raise RuntimeError("SQLITE_DB_PATH environment variable not set.")

        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
        self.SessionFactory = sessionmaker(bind=engine)

    def _get_session(self) -> Session:
        """Return a new per-request session."""
        return self.SessionFactory()

    def _is_token_revoked(self, session: Session, token: str) -> bool:
        """Check whether a token has been revoked."""
        return session.query(RevokedToken).filter_by(token=token).first() is not None

    def _generate_token(self, client: ScannerClient) -> str:
        """Encode and return a new JWT for the given client."""
        return jwt.encode(
            payload={
                "username": client.username or "",
                "email": client.email or "",
                "exp": datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(hours=1),
            },
            key=self.secret_key,
            algorithm=self.algorithm,
        )

    def update_client_with_token(self, client: ScannerClient) -> dict[str, str]:
        token = self._generate_token(client)
        client.token = token
        return self.generate_client_dict(client)

    def store_client(self, client: ScannerClient) -> dict[str, str]:
        """Store client information in the database."""
        session = self._get_session()
        try:
            if client.username:
                if (
                    session.query(ClientRecord)
                    .filter_by(username=client.username)
                    .first()
                ):
                    raise AuthError(f"The username {client.username} already exists.")
            if client.email:
                if session.query(ClientRecord).filter_by(email=client.email).first():
                    raise AuthError(f"The email address {client.email} already exists.")

            hashed = bcrypt.hashpw(client.password.encode("utf-8"), bcrypt.gensalt())
            session.add(
                ClientRecord(
                    username=client.username, email=client.email, password=hashed
                )
            )
            session.commit()
            return {"username": client.username, "email": client.email}
        except SQLAlchemyError:
            app_logger.error("Failed to store the client record")
            session.rollback()
            raise
        finally:
            session.close()

    def get_client(self, client: ScannerClient) -> ClientRecord:
        """Get a client record, raising ClientNotFound if absent."""
        session = self._get_session()
        try:
            record = (
                session.query(ClientRecord)
                .filter(
                    or_(
                        ClientRecord.username == client.username,
                        ClientRecord.email == client.email,
                    )
                )
                .first()
            )
            if not record:
                raise ClientNotFound(
                    "The username or email does not exist."
                    " Sign up to create an account."
                )
            return record
        except SQLAlchemyError:
            app_logger.error("The user was not found in the database.")
            raise
        finally:
            session.close()

    @staticmethod
    def generate_client_dict(client: ScannerClient) -> dict[str, str]:
        return {
            "username": client.username,
            "email": client.email,
            "token": client.token,
            "logged_in": client.logged_in,
        }

    def login(self, client: ScannerClient) -> dict[str, Union[str, bool]]:
        """Manage client login, issuing a token upon success."""
        record = self.get_client(client)
        if bcrypt.checkpw(client.password.encode("utf-8"), record.password):
            client.logged_in = True
            return self.update_client_with_token(client)
        raise AuthError("Login failed. Verify your username and password.")

    def logout(self, client_dict: dict) -> dict[str, Union[str, bool]]:
        """Logout a client and revoke its token."""
        if not client_dict.get("logged_in"):
            raise ClientError(f"{client_dict} is not logged in")

        result = dict(client_dict)
        token = result.pop("token", None)

        session = self._get_session()
        try:
            if token and not self._is_token_revoked(session, token):
                session.add(RevokedToken(token=token))
                session.commit()
        except SQLAlchemyError:
            session.rollback()
            app_logger.error("Failed to logout the client")
            raise
        finally:
            session.close()

        result["logged_in"] = False
        return result
