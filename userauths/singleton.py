import threading
from django.contrib.auth import authenticate, login, logout

class AuthenticationSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def login_user(self, request, email, password):
        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return True, "You are logged in."
            else:
                return False, "Username or password does not exist"
        except Exception as e:
            return False, f"An error occurred: {e}"

    def logout_user(self, request):
        logout(request)
        return True, "You have been logged out."