$(document).ready(function() {
    $("#passwordForm").submit(function(e){
        if($("#passwordInput").val() != $("#passwordCheckInput").val()){
            new PNotify({
                "title":"Passwords don't match",
                "text":"Please re-enter your passwords.",
                "type":"error",
                "styling":"fontawesome"
            });
            e.preventDefault();
            return false;
        }
        return true;
    })
});