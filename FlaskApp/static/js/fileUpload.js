$("#form").submit(function (event) {
    event.preventDefault();
    var formData = new FormData(this);
    $(".progress").css('visibility', 'visible');

    $.ajax({
        url: 'api/patient-cases/upload',
        dataType: 'json',
        type: 'POST',
        xhr: function () {
            var myXhr = $.ajaxSettings.xhr();

            if (myXhr.upload) {
                // For handling the progress of the upload
                myXhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        $('.upload-bar').css({ "width": (e.loaded * 100 / e.total).toString() + "%" });
                        $('.upload-prct').html("Uploading.." + parseInt(e.loaded * 100 / e.total) + "%");
                    }
                }, false);
            }


            return myXhr;
        },
        success: function (data) {
            Materialize.toast("Upload Completed", 3000, "rounded");
            console.log(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            Materialize.toast(textStatus, 3000, "rounded");
        },
        data: formData,
        cache: false,
        timeout: 3600000,
        contentType: false,
        processData: false
    });
    return false;
});