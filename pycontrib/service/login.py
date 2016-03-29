
import time
import pycontrib.tornado.web

class LoginRequestHandler(pycontrib.tornado.web.RequestHandler):
    
    def get_current_user(self):
        user = self.get_secure_cookie('user')
        password = self.get_secure_cookie('password')
        if user and password:
            user = user.decode()
            password = password.decode()
        cls = type(self)
        for group in ('admins', 'users'):
            if (user in self.settings.get(group, {}) and self.settings[group][user] == password):            
                return user
        time.sleep(3)
        return None
    
    def current_user_is_superuser(self):
        return (self.current_user in self.settings.get('admins', {}))

class HttpLoginHandler(LoginRequestHandler):
    def get(self):
        self.write('<html><body><form action="{login_url}" method="post">'
                   '<center><br><h1>Authentication is required</h1>'
                   '<b>Login:</b> <input type="login" name="login"><br><br>'
                   '<b>Password:</b> <input type="password" name="password"><br><br>'
                   '<input type="submit" value="Sign in"></center>'.format(**self.settings))
        prev_page = self.request.arguments.get('next')
        if prev_page:
            self.write('<input type="hidden" name="prev_page" value="{0}">'.format(prev_page[0].decode()))
        self.write('</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("login"))
        self.set_secure_cookie("password", self.get_argument("password"))
        self.redirect(self.get_argument('prev_page', "./"))



