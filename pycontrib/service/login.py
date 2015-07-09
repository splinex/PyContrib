
import tornado.web

class LoginRequestHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        password = self.get_secure_cookie("password")
        if (user, password) == (b'human', b'safari'):
            return user
        return None

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
