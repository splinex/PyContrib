
import datetime, time
import tornado.web

class LoginRequestHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        password = self.get_secure_cookie("password")
        if (user, password) in [(b'human', b'safari'), (b'export', b'453264')]:
            return user.decode()
        time.sleep(3)
        return None
    
    def current_user_is_superuser(self):
        return (self.current_user=='human')

class HttpLoginHandler(LoginRequestHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   '<center><br><h1>Authentication is required</h1>'
                   '<b>Login:</b> <input type="login" name="login"><br><br>'
                   '<b>Password:</b> <input type="password" name="password"><br><br>'
                   '<input type="submit" value="Sign in"><center>'
                   '</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("login"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.redirect("/")
