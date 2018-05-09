import pyramid.httpexceptions as exc

AUTHORITY = {
    0: "Evaluate Only",
    1: "Annotate",
    2: "Upload CMOs",
    3: "Content Uploader",
    4: "User inviter",
    5: "Admin"
}

def permissions(request, authority = 0, loggedOn = False) -> None:
    """
    Validate the users request redirecting them if necessary. Handle the locking mechanism and
    record intended distination for login 

    Params:
        request (Pyramid request object) - The request object of the user, containing session info
        authority (int) - The authority needed for the request to be fulfilled
    """

    # Collect the status of the user from the sessions.
    status = request.session.get("status", None)

    if status is None:
        # User is not logged in, save intended destinate for redirect after login
        if not loggedOn and not authority: return  # No authority needed, allow access
        request.session["intended_route"] = request.path
        raise exc.HTTPFound(request.route_url("login"))

    if status:
        if request.session["authority"] >= authority:
            # Permission granted
            return None
        else:
            # Permission denied
            alert = {
                "title":"Permission denied",
                "text":"You currently do not have the permission to complete this action.\
 If you believe that you should, then please get in touch with a system admin.",
                "type":"error"
            }
            request.session["alerts"].append(alert)
            raise exc.HTTPFound(request.route_url("index"))

    else:
        # User has locked their current session
        raise exc.HTTPFound(request.route_url("locked"))