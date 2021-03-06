import os

from pyramid.view import view_defaults, view_config
import pyramid.httpexceptions as exc

from . import Helper
from .DatabaseHandler import DatabaseHandler as db

@view_defaults(route_name="login", renderer="templates/login.html")
class LoginHandler:
    """
    Class to aggregate the interactions of logging into a user account
    """

    def __init__(self, request):
        self.request = request

    @view_config(route_name="login")
    def loginGET(self):
        return Helper.pageVariables(self.request)

    @view_config(route_name="loggingIn", request_method='POST')
    def loginPOST(self):

        invalidAlert = [{\
            "title":"Ow no, unable to log in!",\
            "text":"The information provided is invalid.",\
            "type":"error"}]

        # Collect the posted information from the login form
        try:
            username = self.request.params['username']
            password = self.request.params['password']
        except:
            self.request.session["alerts"] = invalidAlert
            raise exc.HTTPFound(self.request.route_url("login"))

        # Collect from the database the salt and password for the user
        try:
            salt, storedPassword = db.executeOne("User_Password",[username])
        except Exception as e:
            self.request.session["username"] = username
            self.request.session["alerts"] = invalidAlert
            raise exc.HTTPFound(self.request.route_url("login"))

        _, password = Helper.hashPassword(password, salt)
        if password == storedPassword:

            # Collect relevant user information
            user = db.executeOne("User_Info", [username])

            # Store the information as session variables.
            self.request.session["authority"] = user["permission"]
            self.request.session["status"] = 1
            self.request.session["username"] = username
            self.request.session["firstname"] = user["firstname"]
            self.request.session["lastname"] = user["lastname"]
            self.request.session["avatar"] = user["avatar"]
            self.request.session["alerts"] = []
            self.request.session["email"] = user["email"]

            # Redirect the client to the new page
            location = self.request.session.get("intended_route",self.request.route_url("index"))
            raise exc.HTTPFound(location)

        self.request.session["username"] = username
        self.request.session["alerts"] = invalidAlert
        raise exc.HTTPFound(self.request.route_url("login"))

@view_config(route_name="logout")
def logout(request):
    request.session.invalidate()
    return exc.HTTPFound(request.route_url("login"))

@view_config(route_name="lock", renderer="templates/lock_screen.html")
def lock(request):
    """ Lock the current user session on the page """
    Helper.permissions(request, loggedOn=True)

    if request.session["status"]:
        request.session["status"] = 0
        request.session["intended_route"] = request.referer

    return Helper.pageVariables(request)

@view_config(route_name="unlock")
def unlock(request):
    """ Unlock the session and direct the user back to the page they locked their session on """
    Helper.permissions(request, loggedOn=True)

    alert = {
        "title": "Invalid",
        "text": "Error when attempting to unlock. This failure has been recorded.",
        "type": "error"
    }

    try:
        password = request.params["password"]
    except:
        request.session["alerts"].append(alert)
        raise exc.HTTPFound(request.route_url("lock"))

    
    salt, storedpassword = db.executeOne("User_Password",[request.session["username"]])
    _, password = Helper.hashPassword(password, salt)

    if password == storedpassword:
        request.session["status"] = 1
        location = request.session["intended_route"]
        raise exc.HTTPFound(location)
    else:
        request.session["alerts"].append(alert)
        raise exc.HTTPFound(request.route_url("lock"))


#@view_defaults()
class PasswordReset:

    privateKeys = {}

    @classmethod
    def storekey(cls, key, user):
        cls.privateKeys[key] = user

    @classmethod
    def key(cls, key):
        return cls.privateKeys[key]

    @classmethod
    def removekey(cls, key):
        del cls.privateKeys[key]

    def __init__(self, request):
        self.request = request

    @view_config(route_name='beginPasswordReset', renderer="json")    
    def beginPasswordReset(self):

        invalidAlert = {"title":"Ow no, unable to find user!",\
                "text":"The information provided is invalid.",\
                "type":"error"}

        # Collect the address passed
        username = self.request.params.get("username", None)

        # Validate the address is valid
        if username is None: return exc.HTTPBadRequest(body="Address not provided")
        
        # Validate if user already exists
        try:
            address = db.executeOne("User_Email", [username])
        except:
            return invalidAlert

        # Create psuedo link
        link = Helper.HiddenPages.newAddress("/password_reset/"+username+"/")
        link = os.path.join(self.request.host, link[1:]) # TODO: when the location is stable swap this line out.

        Helper.email("Reset Password",address,"resetPassword.email",[link])
        
        return {"title":"An e-mail to reset has been sent",\
                "text":"We have just sent an e-mail to the account linked with your username.",\
                "type":"success"}
        
    @view_config(route_name='passwordReset', renderer="templates/general_resetPassword.html")    
    def passwordReset(self):

        if Helper.HiddenPages.validate(self.request.path):
            privatekey, user = self.request.matchdict["privatekey"], self.request.matchdict["username"]
            PasswordReset.storekey(privatekey, user)
            return {"privatekey": privatekey}
        
        raise exc.HTTPNotFound()

    @view_config(route_name='assignmentPasswordReset')    
    def assignmentPasswordReset(self):

        try:
            user = PasswordReset.key(self.request.params["privatekey"])
            password = self.request.params["password"]
        except KeyError as e:
            raise exc.HTTPBadRequest("What you doing fool")

        salt, password = Helper.hashPassword(password)
        db.execute('updatePassword', [salt,password,user])
            
        PasswordReset.removekey(self.request.params["privatekey"])
        Helper.HiddenPages.remove("/password_reset/"+user+"/"+self.request.params["privatekey"])
        self.request.session["alerts"] = [{"title":"Password has been reset", "text":"", "type":"success"}]
        raise exc.HTTPFound(self.request.route_url("login"))