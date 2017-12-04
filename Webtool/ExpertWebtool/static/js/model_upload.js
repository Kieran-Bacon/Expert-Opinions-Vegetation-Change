Dropzone.autodiscover = false;
Dropzone.options.modelUploader = false;

$(document).ready(function() {
    $("#model-uploader").dropzone({
        dictDefaultMessage: 'Drag a model file here to upload, or click to select one',
        init: function() {
            this.maxFiles = 1;
            this.on('success', function( file, resp ) {
                console.log("he")
                console.log( file );
                console.log( resp );
            });

            this.on("addedfile", function(file) {
                console.log('new file added ', file);
            });
        }
    });
    // Dropzone.options.modelUploader = false
    // Dropzone.autodiscover = false;
    // var dz = new Dropzone("#uploader", {
    //     dictDefaultMessage: "Custom message"
    // });
    // Dropzone.options.modelUploader = {
    //     dictDefaultMessage: 'Drag an image here to upload, or click to select one',
    // };
});

function onUpload(file){
    console.log("hello")
    console.log(file)
}